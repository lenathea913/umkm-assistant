# Pitch Draft — UMKM Assistant

## Elevator pitch (±60 detik)

"Di Indonesia ada lebih dari 64 juta UMKM, tapi hampir semuanya tidak punya tim
customer service. Pertanyaan pelanggan yang sama — harga, stok, cara order —
dijawab manual berulang kali, dan malam hari pertanyaan dibiarkan menganggur.
Padahal jawabannya sudah ada, di dokumen bisnis mereka sendiri.

UMKM Assistant mengubah dokumen itu menjadi asisten AI yang aktif 24/7:
pemilik cukup upload katalog, price list, dan FAQ, lalu asisten menjawab
pertanyaan pelanggan dalam Bahasa Indonesia — hanya berdasarkan dokumen resmi.
Kalau informasinya tidak ada, asisten jujur dan meneruskan pertanyaan ke
pemilik, bukan mengarang jawaban.

Semua dibangun dengan stack IBM: pipeline RAG visual di IBM Langflow, model
IBM Granite, dan pengembangan dibantu IBM Bob sebagai AI SDLC partner."

## Narasi per kriteria rubrik

### Problem Clarity
- Persona: pemilik butik UMKM (contoh nyata: butik batik Pekalongan di knowledge
  base kami).
- Pain point konkret: pertanyaan berulang, waktu respons lambat, pelanggan hilang
  di luar jam operasional, admin kewalahan.
- Kesenjangan: informasi sudah ada dalam dokumen, tapi tidak bisa "bicara"
  kepada pelanggan.

### Innovation
- RAG berbahasa Indonesia dengan grounding ketat: asisten menolak mengarang dan
  menawarkan eskalasi manusia — kebalikan dari chatbot generik yang membludak.
- Setup tanpa kode: cukup upload dokumen (bukan training, bukan konfigurasi
  rumit) — cocok untuk pemilik UMKM non-teknis.
- Human-in-the-loop sebagai fitur, bukan kelemahan: pertanyaan abu-abu
  diteruskan ke pemilik pada jam kerja.

### User Impact
- UMKM tanpa tim CS menjadi responsif 24/7.
- Hemat waktu admin dari pertanyaan berulang ke pertanyaan bernilai tinggi.
- Pelanggan mendapat jawaban akurat dari dokumen resmi, bukan janji kosong.
- Replikabel ke UMKM lain: ganti dokumen, asisten baru jalan.

### Technical Execution
- Dua flow Langflow: ingestion (chunking + embedding + FAISS) dan assistant
  (retrieval + Granite + prompt grounding).
- Embedding multilingual Granite untuk Bahasa Indonesia.
- End-to-end teruji lewat Bob sebagai MCP client dengan eval suite
  (`evals/eval-questions.md`), termasuk kasus anti-halusinasi yang wajib lulus.
- Arsitektur terbuka: vector store lokal, prompt terdokumentasi.

### Responsible AI
- Grounding wajib: jawaban hanya dari dokumen bisnis (dibuktikan di demo).
- Anti-halusinasi teruji: 7 kasus negatif di eval suite harus menolak/mengeskalasi.
- Transparansi: asisten menyatakan dirinya asisten AI dan batas pengetahuannya.
- Privasi: tidak meminta/menyimpan data pribadi pelanggan; dokumen contoh tidak
  memuat data nyata.

## Rencana demo (±3 menit)

1. Tunjukkan dokumen bisnis (katalog, price list, FAQ) → upload di flow ingestion.
2. Tanya Bob: "Berapa harga Mega Mendung Premium?" → jawaban akurat + grounded.
3. Kasus negatif: "Nomor WhatsApp admin berapa?" → asisten jujur tidak tahu +
   eskalasi. (Momen pembeda — tekankan.)
4. Tunjukkan arsitektur flow di Langflow dan eval suite yang lulus.

## Angka/klaim yang perlu diverifikasi sebelum submit

- [ ] Statistik jumlah UMKM (sumber terbaru, cantumkan sumbernya).
- [ ] Nama model Granite final yang dipakai di flow (samakan di semua dokumen).
- [ ] Hasil eval suite dijalankan penuh + dicatat di `eval-results.md`.
