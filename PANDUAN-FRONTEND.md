# Panduan Onboarding — Frontend UMKM Assistant

> Dokumen ini untuk **kamu** yang akan menjalankan dan melanjutkan project ini
> dari sisi frontend. Baca sampai habis sebelum koding — semuanya penting. 🙂

## 1. Project dalam 60 detik

**UMKM Assistant** = asisten AI layanan pelanggan untuk UMKM Indonesia.
Pemilik bisnis upload dokumen (katalog, price list, FAQ) → asisten ("Rara")
menjawab pertanyaan pelanggan 24/7 dalam Bahasa Indonesia, **hanya berdasarkan
isi dokumen** (teknik RAG). Kalau info tidak ada di dokumen, asisten jujur
menolak dan menawarkan eskalasi ke manusia — inilah pembeda utama kita di
rubrik Responsible AI.

- **Konteks**: submission Hacktiv8 National Hackathon 2026 (tema *Productivity
  & Smart Business*), kolaborasi IBM SkillsBuild.
- **Stack sekarang**: IBM Langflow (pipeline RAG visual) + IBM Granite via
  Ollama lokal (fallback: Gemini) + Chroma local sebagai vector store.
- **Peranmu**: membangun chat UI + integrasi ke flow Langflow. Semua
  "kecerdasan" sudah ada di flow — tugas frontend: kirim pertanyaan, tampilkan
  jawaban, buat pengalaman upload dokumen untuk pemilik UMKM.

## 2. Arsitektur (yang perlu kamu tahu)

```
Pelanggan
   │  chat
   ▼
FRONTEND (kamu) ──HTTP──► Langflow API (/api/v1/run/…)   ◄── inilah integrasimu
                              │
                              ├─ Knowledge Base (Chroma lokal)  ◄─ 3 dokumen bisnis
                              └─ LLM (Granite 8B via Ollama / Gemini)
                              │
                              ▼
                        Jawaban grounded (+ penolakan + eskalasi)
```

- **IBM Bob (MCP)** = alat developer untuk testing end-to-end. **Bukan bagian
  produk akhir** — frontend tidak perlu Bob sama sekali.
- Folder `bob/` di repo hanya dokumentasi; abaikan dulu.

## 3. Struktur repo

| Path | Isi |
|---|---|
| `README.md` | Overview project + peta rubrik penilaian |
| `langflow/BUILD-GUIDE.md` | **Cara membangun/replikasi flow dari nol** — baca ini |
| `langflow/agent-system-prompt.md` | System prompt "Rara" (sumber kebenaran; kalau diubah di flow, sinkronkan ke sini) |
| `knowledge-base/` | 3 dokumen bisnis contoh (butik batik "Larasati") — di-upload ke Knowledge Base |
| `evals/eval-questions.md` | 20 pertanyaan uji (A–D). **Kasus C = anti-halusinasi, wajib lulus semua** |
| `evals/eval-results.md` | Hasil eval per model — update setiap kali uji ulang |
| `submission/pitch-draft.md` | Narasi submission — sinkronkan dengan fitur yang didemokan |
| `bob/` | Konfigurasi IBM Bob (developer tooling, bukan produk) |

## 4. Setup dari nol (±30 menit)

1. **Install Langflow** (Desktop app, versi 1.12.x yang dipakai sekarang) →
   jalan di `http://localhost:7860`.
2. **Bangun flow**: ikuti `langflow/BUILD-GUIDE.md` — pakai template
   **Vector Store RAG**, lalu:
   - Buat Knowledge Base: halaman **Projects → Knowledge → Add Knowledge** →
     nama `umkm-batik`, embedding **multilingual** (mis. `gemini-embedding-001`),
     DB Provider **Chroma Local** → **Configure Sources** → upload 3 file dari
     `knowledge-base/` → Create → tunggu status **Ready**.
     ⚠️ **KB tersimpan di mesin yang membuatnya** — tidak ikut repo. Ini langkah
     wajib di laptopmu sendiri.
   - Di flow: komponen **Knowledge → pilih KB** (mode Retrieve), lengkapi kabel
     (panduan wiring ada di BUILD-GUIDE), tempel **prompt grounding** & **Agent
     Instructions** dari file prompt.
3. **Pilih LLM** (Agent → Language Model):
   - **Ollama lokal** (gratis, offline): install Ollama → `ollama pull
     granite3.3:8b` → provider Ollama di Settings → Model Providers →
     `http://localhost:11434` → pilih `granite3.3:8b`. Kecepatan: CPU ±1–2
     menit/jawaban (jalankan pertanyaan berurutan agar model tetap hangat).
   - **Gemini** (cepat, kadang 503 saat ramai): tempel API key-mu di Settings →
     Model Providers.
4. **Tes Playground**: *"Berapa harga Batik Tulis Mega Mendung Premium?"* →
   jawaban benar: **Rp 1.850.000**. Gagal = ulangi langkah 2, cek wiring.

## 5. Integrasi Frontend ↔ Langflow (bagian terpenting) ⭐

Flow diekspos sebagai REST API. Endpoint yang kamu panggil:

```http
POST http://localhost:7860/api/v1/run/{FLOW_ID}?stream=false
```

- **Cara ambil `FLOW_ID`**: buka flow di Langflow → lihat URL browser
  (`.../flow/<FLOW_ID>`), atau klik ikon **API** di pojok flow → salin contoh
  cURL (menunjukkan endpoint + body yang persis untuk flow-mu).
- Nama flow juga bisa dipakai: `/api/v1/run/UMKM%20Assistant`.

**Contoh fetch (JS/TS):**

```ts
const res = await fetch("http://localhost:7860/api/v1/run/" + FLOW_ID + "?stream=false", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    input_value: pertanyaanDariUser,        // teks pertanyaan pelanggan
    session_id: sessionIdPerSesiChat,       // penting: memory per sesi
    output_type: "chat",
    input_type: "chat",
  }),
});
const data = await res.json();
const jawaban =
  data.outputs?.[0]?.outputs?.[0]?.results?.message?.text ?? "";
```

- Verifikasi struktur respons lewat tab **API / cURL** di flow — bentuknya bisa
  sedikit beda antar versi Langflow.
- **Streaming**: ganti ke `stream=true` → respons SSE per token (UX lebih
  hidup). Saran: selesaikan dulu versi non-streaming, streaming menyusul.
- **CORS**: kalau browser diblokir, proxy lewat backend tipis (Next.js route
  handler / Express) — jangan dimatikan keamanannya.
- **Memory percakapan**: selalu kirim `session_id` yang sama dalam satu sesi
  chat, beda sesi = beda `session_id`.

## 6. Aturan main produk (wajib — ini dinilai juri)

1. Tampilkan indikator bahwa ini **asisten AI** (disclaimer kecil di chat).
2. Tampilkan jawaban apa adanya — termasuk saat asisten bilang *"informasi
   belum ditemukan, diteruskan ke admin"*. Itu **fitur**, jangan disembunyikan.
3. Sediakan tombol **"Hubungi admin"** (eskalasi manusia) di chat.
4. **Jangan pernah minta/menyimpan data pribadi pelanggan** di frontend.
5. Semua teks UI dalam **Bahasa Indonesia**, nada ramah (sapaan "Kak").
6. Setiap kali mengubah prompt/flow → jalankan ulang `evals/eval-questions.md`,
   **kasus C wajib lulus semua**, catat di `evals/eval-results.md`, lalu commit.

## 7. Status & roadmap

**Sudah jalan:**
- ✅ Flow RAG end-to-end (Knowledge + Parser + Prompt grounding + Agent)
- ✅ KB `umkm-batik2` (gemini-embedding-001, Chroma Local) — di mesin developer saat ini
- ✅ Eval A1–A8 sesi pertama (catatan + pelajaran di `evals/eval-results.md`)
- ✅ Granite lokal via Ollama (`granite3.3:2b` & `8b` sudah ter-pull)

**Sedang dikerjakan (backend):**
- 🔄 Ulangi eval dengan `granite3.3:8b` + prompt yang diperkuat (A3/A4/A5/A8)
- 🔄 Kasus anti-halusinasi C1–C7 belum lulus penuh

**Untuk kamu (frontend) — urutan saran:**
- [ ] Chat UI dasar (Next.js/React): input + bubble chat + state loading
- [ ] Integrasi `/api/v1/run/` + `session_id`
- [ ] Tampilkan sumber jawaban (nama dokumen) bila tersedia di respons
- [ ] Halaman pemilik UMKM: upload dokumen → (lanjutan) otomatis update Knowledge Base
- [ ] Panel eskalasi: daftar pertanyaan yang tak terjawab oleh asisten
- [ ] Responsif mobile (pelanggan UMKM banyak dari HP)
- [ ] (Opsional) streaming + indikator "Rara sedang mengetik…"

## 8. Konvensi tim

- Repo: `github.com/lenathea913/umkm-assistant`, branch `main`, commit pesan
  ringkas dalam Bahasa Indonesia/Inggris — bebas, yang penting jelas.
- **DILARANG commit kredensial** (API key, token). Pakai `.env` + tambahkan ke
  `.gitignore`. File konfigurasi contoh cukup `.example`.
- Kalau mengubah flow/prompt: **export flow JSON** → simpan ke `langflow/`
  agar semua orang punya versi terbaru, dan sinkronkan prompt dengan
  `langflow/agent-system-prompt.md`.
- File yang wajib kamu baca sebelum mulai: `langflow/BUILD-GUIDE.md`,
  `langflow/agent-system-prompt.md`, `evals/eval-questions.md`,
  `submission/pitch-draft.md`.

## 9. Troubleshooting cepat

| Gejala | Sebab umum | Solusi |
|---|---|---|
| Selalu "tidak menemukan informasi" | KB kosong / KB dari mesin lain tidak ada | Buat ulang KB (langkah 4), pastikan terpilih di komponen Knowledge |
| 503 Service Unavailable | Server model cloud sedang ramai | Retry; atau ganti model (Ollama lokal) |
| Jawaban bahasa Inggris / mengarang | Model lemah atau prompt lama | Pakai `granite3.3:8b`+ / pastikan prompt versi terbaru dari `agent-system-prompt.md` |
| Ollama "0 models" | Model belum di-pull / filter embedding | `ollama pull granite3.3:8b`; pane embedding KB memang tidak menampilkan model generasi |
| Jawaban lambat (>1 menit) | CPU inference | Normal untuk 8B lokal; pakai model cloud untuk demo, atau jalankan pertanyaan berurutan |

---

Selamat bergabung! Kalau ada yang bikin bingung, mulai dari `langflow/BUILD-GUIDE.md`
— kalau masih buntu, tanya pemilik repo ini (dia tahu seluruh sejarah flow-nya). 🚀
