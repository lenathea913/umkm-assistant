# Folder Screenshot Submission

Folder ini untuk menampung **3–5 screenshot** yang di-upload ke form submission
(maks 10 MB/file, format PNG/JPG). Simpan semua file di folder ini dengan nama
yang persis seperti daftar di bawah.

## Daftar file yang wajib ada

### `01-chat-playground.png` — Jawaban grounded (wajib)
Di Langflow → flow `UMKM Assistant` → **Playground**.
- Tanya: `Berapa harga Batik Tulis Mega Mendung Premium?`
- Pastikan terlihat: pertanyaan + jawaban berisi **Rp 1.850.000** dan persona Rara.
- 💡 Usahakan model `granite3.3:8b` sedang aktif — jawaban lebih meyakinkan.

### `02-anti-halusinasi.png` — Buktinya AI jujur (paling menentukan!)
Masih di Playground, sesi yang sama atau baru.
- Tanya: `Harga Mega Mendung Premium kalau dibayar tunai diskon 10%?`
- Pastikan terlihat: jawaban **menolak menghitung** + menyebut harga tetap
  Rp 1.850.000 + tawaran meneruskan ke admin.
- 💡 Ini pembeda Responsible AI — pastikan teks jawabannya terbaca jelas.

### `03-langflow-workflow.png` — Arsitektur flow
Canvas flow `UMKM Assistant` (zoom to fit / Ctrl+Shift+F).
- Pastikan terlihat: rantai lengkap Chat Input → Knowledge → Parser → Prompt →
  Agent (nama model Granite/Ollama terbaca) → Chat Output, dan semua kabel nyambung.
- 💡 Buat panel side bar tertutup supaya canvas lega & nama flow di header terlihat.

### `04-knowledge-base.png` — Sumber pengetahuan
Halaman **Projects → Knowledge**.
- Pastikan terlihat: KB `umkm-batik2`, status **Ready**, 5 chunks, embedding model.

### `05-eval-suite.png` — Kualitas terukur
Terminal berisi hasil `python evals/run_evals.py` (beberapa soal cukup, tidak
harus --all penuh).
- Pastikan terlihat: ID soal (A1/C7 dll), durasi, dan potongan jawaban.

## Tips umum

- Ukuran & keterbacaan: screenshot di 125–150% zoom biasanya paling tajam.
- Hapus informasi pribadi (email, nama lengkap di header, API key — apapun itu).
- Nama file jangan diubah (memudahkan reviewer).
- Total ukuran folder jaga di bawah ±8 MB supaya aman saat upload satu per satu.

## Status

- [ ] 01-chat-playground.png
- [ ] 02-anti-halusinasi.png
- [ ] 03-langflow-workflow.png
- [ ] 04-knowledge-base.png
- [ ] 05-eval-suite.png
