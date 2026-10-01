#!/usr/bin/env python3
"""
run_evals.py — jalankan eval UMKM Assistant langsung via API Langflow
(tanpa Playground, tanpa copy-paste manual).

Cara pakai:
  export LANGFLOW_API_KEY="sk-..."   # dari Langflow: ikon profil > Settings > Langflow API
  python run_evals.py --inspect      # cek config flow (model & prompt)
  python run_evals.py --ids A1 A3    # jalankan soal tertentu
  python run_evals.py --all          # jalankan semua 20 soal (lambat!)

Hasil: dicetak ke layar + disimpan (merge per ID) ke evals/eval-run-latest.json.
Jangan pernah commit API key — selalu lewat environment variable.
"""
import argparse
import gzip
import json
import os
import time
import urllib.error
import urllib.request

BASE = os.environ.get("LANGFLOW_BASE_URL", "http://localhost:7860")
KEY = os.environ.get("LANGFLOW_API_KEY", "")
FLOW_NAME_PREFIX = os.environ.get("LANGFLOW_FLOW_NAME", "umkm").lower()
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "eval-run-latest.json")

# 20 soal eval (sumber kebenaran: eval-questions.md)
QUESTIONS = {
    "A1": ("grounding", "Berapa harga Batik Tulis Mega Mendung Premium?"),
    "A2": ("grounding", "Ada stok kemeja Parang Rusak ukuran XXL?"),
    "A3": ("grounding", "Cara ordernya gimana, Kak?"),
    "A4": ("grounding", "Batik tulis bisa langsung kirim hari ini?"),
    "A5": ("grounding", "Kalau beli 10 pcs campur buat dijual lagi, ada harga khusus?"),
    "A6": ("grounding", "Gimana cara ngerawat batik tulisnya?"),
    "A7": ("grounding", "Gratis ongkir nggak ke luar Jawa?"),
    "A8": ("grounding", "Motif buketan yang klasik warnanya gimana?"),
    "B1": ("multi-doc", "Dress Buketan ukuran S ada nggak, harganya berapa?"),
    "B2": ("multi-doc", "Mega Mendung cap sama tulis, beda harga berapa jauh?"),
    "B3": ("multi-doc", "Beli kemeja + dress dapat potongan nggak?"),
    "C1": ("anti-halusinasi", "Batik tulisnya bisa diskon 50% nggak?"),
    "C2": ("anti-halusinasi", "Toko ini buka cabang di Bandung nggak?"),
    "C3": ("anti-halusinasi", "Kode promo apa yang aktif bulan ini?"),
    "C4": ("anti-halusinasi", "Nomor WhatsApp adminnya berapa?"),
    "C5": ("anti-halusinasi", "Rekomendasi obat batuk apa yang bagus?"),
    "C6": ("anti-halusinasi", "Batik Parang Rusak boleh dicuci mesin?"),
    "C7": ("anti-halusinasi", "Harga Mega Mendung Premium kalau dibayar tunai diskon 10%?"),
    "D1": ("bahasa", "Gan, batiknya ready?"),
    "D2": ("bahasa", "Is the Mega Mendung Premium available?"),
}


def api(path, method="GET", payload=None, timeout=300):
    req = urllib.request.Request(
        BASE + path,
        method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "x-api-key": KEY,
            "Content-Type": "application/json",
            "Accept-Encoding": "identity",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if raw[:2] == b"\x1f\x8b":  # respons ter-gzip
            raw = gzip.decompress(raw)
        return json.loads(raw.decode())


def find_flow():
    flows = api("/api/v1/flows/")
    if isinstance(flows, dict):
        flows = flows.get("flows", [])
    for f in flows:
        if f.get("name", "").lower().startswith(FLOW_NAME_PREFIX):
            return f["id"], f.get("name", "?")
    raise SystemExit(f"Flow dengan nama berawalan '{FLOW_NAME_PREFIX}' tidak ditemukan.")


def inspect_flow(flow_id):
    f = api(f"/api/v1/flows/{flow_id}")
    nodes = f.get("data", {}).get("nodes", [])
    print(f"Flow: {f.get('name')} (id={flow_id}) — {len(nodes)} node\n")
    for n in nodes:
        nd = n.get("data", {})
        ntype = nd.get("type", "?")
        name = nd.get("node", {}).get("display_name", "?")
        print(f"== {ntype} :: {name}")
        tmpl = nd.get("node", {}).get("template", {})
        for k, v in tmpl.items():
            if k.startswith("_") or not isinstance(v, dict):
                continue
            val = v.get("value")
            if val in (None, "", [], {}):
                continue
            kl = k.lower()
            if "model" in kl or "instructions" in kl or "template" in kl or "knowledge" in kl:
                s = json.dumps(val, ensure_ascii=False)
                marker = ""
                if isinstance(val, str) and "LARANGAN TAMBAHAN" in val:
                    marker = "   <<< PROMPT BARU (hardening) TERPASANG"
                print(f"   {k} = {s[:240]}{marker}")
        print()


def extract_text(resp):
    try:
        o = resp["outputs"][0]["outputs"][0]
        msg = o.get("results", {}).get("message")
        if isinstance(msg, dict):
            return msg.get("text", "")
        if isinstance(msg, str):
            return msg
        msgs = o.get("messages") or []
        if msgs:
            return msgs[0].get("message", "")
        return ""
    except Exception:
        return ""


def run_one(flow_id, qid, timeout):
    cat, q = QUESTIONS[qid]
    payload = {
        "input_value": q,
        "session_id": f"eval-{qid}-{int(time.time())}",
        "output_type": "chat",
        "input_type": "chat",
    }
    t0 = time.time()
    try:
        resp = api(f"/api/v1/run/{flow_id}?stream=false", "POST", payload, timeout=timeout)
        answer = extract_text(resp).strip()
        err = None
    except urllib.error.HTTPError as e:
        answer, err = "", f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        answer, err = "", f"{type(e).__name__}: {e}"
    rec = {
        "id": qid,
        "kategori": cat,
        "soal": q,
        "jawaban": answer,
        "durasi_detik": round(time.time() - t0),
        "error": err,
        "model_catatan": "sesuai config flow saat dijalankan",
    }
    return rec


def save_results(new_records):
    allr = {}
    if os.path.exists(RESULTS_PATH):
        try:
            with open(RESULTS_PATH, encoding="utf-8") as f:
                for r in json.load(f):
                    allr[r["id"]] = r
        except Exception:
            pass
    for r in new_records:
        allr[r["id"]] = r
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(allr.values()), f, ensure_ascii=False, indent=2)
    print(f"\n>> {len(new_records)} hasil disimpan/merge ke {RESULTS_PATH}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inspect", action="store_true", help="cukup tampilkan config flow")
    ap.add_argument("--ids", nargs="+", help="ID soal, contoh: --ids A3 C1")
    ap.add_argument("--all", action="store_true", help="jalankan semua soal")
    ap.add_argument("--timeout", type=int, default=280, help="detik per soal")
    args = ap.parse_args()

    if not KEY:
        raise SystemExit("Set LANGFLOW_API_KEY dulu: export LANGFLOW_API_KEY=\"sk-...\"")

    flow_id, name = find_flow()
    print(f"Flow ditemukan: {name} (id={flow_id})\n")

    if args.inspect:
        inspect_flow(flow_id)
        return

    if args.all:
        ids = list(QUESTIONS)
    elif args.ids:
        ids = [i.upper() for i in args.ids]
        unknown = [i for i in ids if i not in QUESTIONS]
        if unknown:
            raise SystemExit(f"ID tidak dikenal: {unknown}. Pilihan: {', '.join(QUESTIONS)}")
    else:
        raise SystemExit("Pilih --ids ... atau --all (lihat --help)")

    records = []
    for qid in ids:
        cat, q = QUESTIONS[qid]
        print(f"[{qid}|{cat}] {q}")
        rec = run_one(flow_id, qid, args.timeout)
        records.append(rec)
        save_results([rec])  # simpan inkremental — aman bila proses terputus
        jaw = (rec["jawaban"] or rec["error"] or "").replace("\n", " ")
        print(f"  ({rec['durasi_detik']}s) {jaw[:260]}{'...' if len(jaw) > 260 else ''}\n", flush=True)


if __name__ == "__main__":
    main()
