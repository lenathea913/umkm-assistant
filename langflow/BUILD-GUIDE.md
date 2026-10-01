# Build Guide — Flow RAG UMKM Assistant di Langflow

Target akhir: flow chat RAG berbahasa Indonesia yang diekspos sebagai MCP server
dan dipanggil oleh IBM Bob.

## Prasyarat

- Langflow berjalan di `http://localhost:7860` (infrastruktur yang sama dengan
  saat Meeting Action Assistant — sudah terbukti jalan).
- Kredensial **watsonx.ai**: API key + Project ID, untuk model **IBM Granite**.
  (Fallback tanpa watsonx: provider model lain; komponennya sama, hanya ganti
  model. Untuk submission, Granite = nilai plus di Technical Execution.)

## ⚠️ Addendum — Langflow versi baru: template "Vector Store RAG"

Langflow terbaru menyediakan template **Vector Store RAG** yang memakai komponen
**Knowledge** (bukan File→Split→Embedding→FAISS terpisah). Strukturnya:

| Komponen template | Peran | Setelan |
|---|---|---|
| **Chat Input** | Pertanyaan pelanggan | default oke |
| **Knowledge** | Ingest / Retrieve ke knowledge base | Pilih KB dari dropdown (harus dibuat dulu — lihat bawah); **Retrieve** untuk chat |
| **Parser** | Format hasil retrieval jadi teks | `Text: {content}` — biarkan |
| **Prompt** | Template grounding `{context}` + `{question}` | Ganti dengan template grounding (bawah) |
| **Agent** | LLM + instruksi | **Wajib pilih model**; instruksi = persona Rara; **Tools dibiarkan kosong** |
| **Chat Output** | Jawaban ke Playground | default oke |

Urutan kerja: **buat + isi KB dari halaman Projects** (bukan dari dropdown komponen!) →
di flow pilih KB di komponen Knowledge (mode **Retrieve**) → lengkapi Prompt &
Agent → uji Playground.

### Membuat & mengisi knowledge base (dari halaman Projects)

1. Klik **Starter Project** di breadcrumb kiri atas → halaman Projects.
2. Klik **Knowledge** di bawah daftar project → **Add Knowledge**.
3. Pane *Create Knowledge Base*:
   - Nama: `umkm-batik`
   - **Embedding model**: pilih yang **multilingual** (penting untuk Bahasa
     Indonesia). ⚠️ Setelah KB dibuat, embedding model **tidak bisa diganti**
     (harus hapus + buat ulang).
   - DB Provider: default (Chroma lokal) — tidak perlu diubah.
4. **Configure Sources** → **Add Sources** → upload 3 file dari
   `umkm-assistant/knowledge-base/` → setelan chunk default cukup →
   **Next Step**.
5. *Review & Build*: cek preview chunk → **Create** → tunggu status **Ready**.
6. Balik ke flow → komponen Knowledge → dropdown → **Refresh list** → pilih
   `umkm-batik`. Pastikan `Search Query` ter-wire dari Chat Input.

Template Prompt grounding (tempel di komponen Prompt):

```
=== KONTEKS DOKUMEN ===
{context}
=== AKHIR KONTEKS ===

Pertanyaan pelanggan: {question}
```

Instruksi Agent (tempel di kolom Agent Instructions):

```
Kamu adalah "Rara", asisten layanan pelanggan UMKM Batik Larasati Pekalongan.

ATURAN GROUNDING (ketat):
1. Jawab HANYA berdasarkan konteks dokumen yang diberikan di prompt.
2. Jika informasi tidak ada di konteks: katakan jujur belum menemukan
   informasinya, lalu tawarkan meneruskan pertanyaan ke admin (jam kerja
   Senin–Sabtu 08.00–17.00 WIB).
3. JANGAN PERNAH mengarang harga, stok, nama produk, tanggal, nomor telepon,
   atau kebijakan.
4. Jangan menghitung diskon/ongkir/total KECUALI ketentuannya tertulis di
   konteks.
5. Pertanyaan di luar cakupan bisnis → tolak sopan, kembalikan ke produk toko.

Gaya: Bahasa Indonesia santun, sapaan "Kak", singkat (maks 3–4 kalimat kecuali
daftar produk). Harga tulis persis seperti di dokumen (contoh: Rp 385.000).
Jangan menggunakan tools atau pengetahuan di luar konteks.
```

Catatan: dokumentasi klasik di bawah tetap berlaku untuk Langflow versi lama
(komponen terpisah). Konsepnya identik: Knowledge = vector store + embedding.

## Arsitektur: dua flow

| Flow | Fungsi | Dijalankan |
|---|---|---|
| 1. **Ingestion** | Baca dokumen → potong → embed → simpan ke vector store | Sekali per dokumen / saat update |
| 2. **Assistant (RAG chat)** | Terima pertanyaan → cari konteks → jawab ter-grounding | Setiap chat; ini yang diekspos ke MCP |

Dipisah supaya ingestion tidak ikut jalan setiap chat — flow chat tetap ringan.

## Langkah 1 — Project Langflow

1. New Project, beri nama `UMKM Assistant`.
2. Catat **Project ID** dari URL browser — dipakai di MCP URL langkah 5.

## Langkah 2 — Flow Ingestion

Komponen (urut dari kiri ke kanan):

1. **File** — upload dokumen dari `knowledge-base/` (mulai dari `katalog-produk.md`).
2. **Split Text** — chunk size 1000, overlap 200 (dokumen Markdown pendek boleh 800/150).
3. **Embedding Model** — `ibm/granite-embedding-278m-multilingual` (multilingual:
   bagus untuk Bahasa Indonesia). Fallback: HuggingFace Embeddings lokal.
4. **Vector Store (FAISS, local)** — mode **ingest**, folder persist misal
   `./faiss_umkm`.

Wiring: `File → Split Text → Embedding → Vector Store`.

Jalankan flow ini satu kali per dokumen. Ulangi tiap file knowledge-base.

> **Penting:** flow Assistant **wajib memakai embedding model & folder vector
> store yang sama** dengan flow Ingestion, kalau tidak hasil pencarian kosong.

## Langkah 3 — Flow Assistant (RAG chat)

Komponen:

1. **Chat Input**
2. **Embedding Model** — sama dengan langkah 2.
3. **Vector Store (FAISS, local)** — mode **search**, `n_results = 4`, folder sama.
4. **Prompt Template** — susun:

   ```
   Kamu adalah asisten layanan pelanggan UMKM. Jawab HANYA berdasarkan
   konteks dokumen berikut.

   === KONTEKS DOKUMEN ===
   {context}
   === AKHIR KONTEKS ===

   Pertanyaan pelanggan: {question}
   ```

5. **Language Model** — IBM Granite via watsonx.ai
   (`ibm/granite-3-3-8b-instruct` atau setara). Temperature rendah (0.2–0.4)
   supaya jawaban konsisten dengan dokumen.
6. **Chat Output**

Tempel **system prompt** dari [agent-system-prompt.md](agent-system-prompt.md)
ke komponen Language Model / Agent.

Uji di Playground dengan pertanyaan dari `../evals/eval-questions.md` sebelum
lanjut ke MCP. Cek dulu kasus anti-halusinasi (bagian C) — itu pembeda utama
kita di rubrik Responsible AI.

## Langkah 4 — Ekspose flow ke MCP

**Cara A — otomatis per project (pola yang sama dengan sample):**
Semua flow dalam satu project otomatis jadi MCP tool di:

```
http://localhost:7860/api/v1/mcp/project/<PROJECT_ID>/sse
```

Nama tool mengikuti nama flow — beri nama flow Assistant: `umkm-assistant`.

**Cara B — komponen MCP Server** (bila versi Langflow-mu menyediakan):
tambahkan komponen *MCP Server* ke flow Assistant dan perhatikan tool yang
terdaftar.

## Langkah 5 — Hubungkan Bob sebagai MCP client

1. Salin `../bob/mcp-config.example.json` ke konfigurasi Bob, ganti
   `<PROJECT_ID>` dengan Project ID langkah 1.
2. Buat agent Bob baru dengan instruksi `../bob/agent-instructions.md`.
3. Uji end-to-end: tanya Bob "berapa harga Batik Pekalongan Mega Mendung?"
   → Bob harus memanggil tool `umkm-assistant`, bukan menjawab sendiri.

## Mengganti LLM ke IBM Granite (watsonx.ai)

Gemini dipakai hanya untuk development. Untuk submission, LLM-nya diganti ke
**IBM Granite via watsonx.ai** — memperkuat cerita IBM stack di rubrik.

### A. Siapkan kredensial IBM (±10 menit, sekali saja)

1. **Akun IBM Cloud** (cloud.ibm.com) — pakai plan gratis (Lite).
2. **watsonx.ai**: buka dataplatform.cloud.ibm.com → buat/aktifkan **watsonx.ai**
   → buat project, misal `umkm-assistant`.
3. **Project ID**: di project → tab **Manage** → **General** → salin *Project ID*.
4. **API key**: cloud.ibm.com → Manage → Access (IAM) → **API keys** → Create →
   salin sekali (tidak bisa dilihat lagi).
5. **Region**: catat region project (default Dallas = `us-south`) — URL API harus
   cocok: `https://api.us-south.watsonx.ai` (Frankfurt: `eu-de`, London:
   `eu-gb`, Tokyo: `jp-tok`).

### B. Konfigurasi di Langflow

1. Sidebar → **Models & Agents** (atau search "watsonx") → drag komponen
   **IBM watsonx.ai** ke canvas. Kalau tidak ketemu: **Discover more components**
   → pasang bundle **IBM** → restart Langflow.
2. Isi parameter komponen:
   - **url**: `https://api.us-south.watsonx.ai` (sesuaikan region)
   - **project_id**: dari langkah A3
   - **api_key**: dari langkah A4
   - **model_name**: klik refresh → pilih **`ibm/granite-3-3-8b-instruct`**
     (atau varian Granite 4 terbaru yang muncul)
   - **temperature**: 0.1–0.3 (rendah = konsisten dengan dokumen)
3. **Wiring**: tarik output **Language Model** komponen watsonx → ke
   **Language Model** pada komponen **Agent** (menggantikan dropdown gemini).
   Jangan ubah kabel lain.
4. **Playground** → ulangi A1 ("Berapa harga Batik Tulis Mega Mendung
   Premium?") → jawaban tetap harus Rp 1.850.000.

### C. Catatan biaya & fallback

- Plan Lite watsonx.ai gratis namun berkuota ketat — cukup untuk demo, tapi
  jangan boros saat eval; simpan kuota untuk pertanyaan penting (A1 + C1–C7).
- Simpan Gemini sebagai **fallback**: kalau watsonx bermasalah menjelang demo,
  tinggal putuskan kabel watsonx dari Agent dan pilih model dari dropdown lagi.
- Embedding KB tetap `gemini-embedding-001` (embedding KB tidak bisa diganti
  tanpa buat ulang KB — tidak perlu, karena embedding bukan bagian cerita IBM
  yang dinilai; LLM Granite-lah yang utama).

## Alternatif: Granite lokal via Ollama (tanpa akun & kartu)

Jika tidak ingin verifikasi kartu untuk watsonx, Granite tetap bisa dipakai
**lokal** — gratis, offline, tanpa kuota:

1. Install **Ollama** (ollama.com) → server jalan di `http://localhost:11434`.
2. Pull model: `ollama pull granite3.3:2b` (±1,5 GB). RAM ≥16 GB boleh ambil
   `granite3.3:8b` (±5 GB) untuk kualitas lebih baik.
3. Langflow → **Settings → Model Providers → Ollama** → Base URL
   `http://localhost:11434` → Connect.
4. **Agent → Language Model → Ollama → granite3.3:2b.** Knowledge base tidak
   perlu diubah (tetap KB yang ada — pemilih embedding KB hanya menampilkan
   model embedding, bukan model generasi, jadi "0 models" di situ wajar).
5. Catatan kualitas: model 2B kadang kurang patuh persona/bahasa. Kalau Rara
   mulai menjawab Inggris atau mengabaikan grounding, perkuat instruksi bahasa
   di Agent Instructions, atau naik ke 8B.

## Troubleshooting

| Gejala | Kemungkinan sebab | Perbaikan |
|---|---|---|
| Jawaban "tidak menemukan info" terus-menerus | Vector store kosong / beda folder / beda embedding | Jalankan ulang Ingestion; samakan model embedding & folder |
| Jawaban mengarang (halusinasi) | System prompt grounding tidak aktif / konteks kosong | Tempel ulang prompt; periksa hasil search di Playground |
| Jawaban berbahasa Inggris | Instruksi bahasa lemah | Perkuat baris bahasa Indonesia di system prompt |
| Bob menjawab sendiri tanpa tool | Instruksi delegasi Bob belum dipasang | Pastikan `bob/agent-instructions.md` dipakai sebagai instruksi agent |
