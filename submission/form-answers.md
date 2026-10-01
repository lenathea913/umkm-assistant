# Jawaban Form Submission — Hacktiv8 National Hackathon 2026

> Semua jawaban siap tempel. Fakta disesuaikan kondisi nyata project:
> flow Langflow + KB `umkm-batik2` + Granite 3.3 8B (Ollama) + eval 20 kasus (18✅ 2⚠️ 0❌).

---

## 1. Masalah spesifik apa yang ingin diselesaikan?

**Kondisi sebelum solusi:** Pemilik UMKM melayani pertanyaan pelanggan secara
manual lewat chat/WhatsApp, satu per satu, sendirian. Informasi yang dibutuhkan
untuk menjawab (harga, stok, cara order, garansi) sebenarnya sudah lengkap di
dokumen bisnis — katalog, price list, FAQ — tapi dokumen itu "tidak bisa bicara".

**Pain point:** (1) pertanyaan yang sama dijawab berulang-ulang setiap hari,
memakan waktu admin; (2) di luar jam operasional, pertanyaan dibiarkan menganggur
berjam-jam sampai calon pembeli membatalkan niat beli; (3) saat admin lelah,
jawaban bisa tidak konsisten atau salah — yang berujung komplain.

**Mengapa penting:** layanan responsif adalah faktor penentu keputusan beli
pelanggan chat. Untuk UMKM tanpa tim CS, hilangnya satu pembeli karena balasan
lambat adalah kerugian nyata. Masalah ini menimpa puluhan juta UMKM Indonesia,
dan sebagian besar solusi chatbot yang ada terlalu mahal/rumit atau mudah
"mengarang" jawaban yang merusak kepercayaan pelanggan.

## 2. Target User

**Pengguna utama: pemilik UMKM** (khususnya bisnis ritel/kerajinan/fashion yang
melayani pelanggan lewat chat dan punya dokumen produk: katalog, price list, FAQ).
Contoh konkret yang kami pakai: butik batik Pekalongan.

**Pengguna sekunder (end user): pelanggan UMKM** yang bertanya — mereka yang
menerima jawaban cepat & akurat 24/7. **Pengguna ketiga: admin/CS UMKM** yang
terbebas dari pertanyaan repetitif dan hanya menangani kasus eskalasi.

## 3. Mengapa Solusi Ini Dibutuhkan?

Dibanding cara sekarang (balas manual): jawaban instan 24/7 tanpa menunggu jam
kerja, konsisten selalu sesuai dokumen resmi, dan admin hanya mengurus kasus
eskalasi. Dibanding chatbot generik/GPT biasa: chatbot umum berbasis pengetahuan
model yang bisa mengarang harga/kebijakan — fatal untuk bisnis. UMKM Assistant
memakai RAG dengan grounding ketat: hanya menjawab dari dokumen resmi, jujur
menolak di luar cakupan, dan meneruskan pertanyaan ke manusia. Dibanding solusi
chatbot komersial: setup tanpa kode (cukup upload dokumen), gratis berjalan di
infrastruktur lokal/open-source, dan kualitasnya **terukur** lewat 20 kasus uji
otomatis — bukan sekadar klaim.

## 4. Fitur Utama Project

1. **Document Q&A (RAG Bahasa Indonesia)** — pelanggan bertanya apa saja tentang
   produk; sistem mencari bagian dokumen paling relevan dan menjawab hanya dari
   sana (harga, stok, ukuran, cara order, perawatan, promo).
2. **Anti-Halusinasi + Eskalasi Human-in-the-Loop** — jika informasi tidak ada
   di dokumen, asisten jujur mengatakan belum menemukan info dan meneruskan
   pertanyaan ke pemilik/admin, bukan mengarang. Terbukti: 7/7 kasus jebakan lulus.
3. **Knowledge Base dari Upload Dokumen (tanpa kode)** — pemilik cukup upload
   katalog/price list/FAQ (PDF/Markdown); dokumen otomatis di-chunk, di-embed
   (multilingual), dan disimpan ke vector store. Ganti dokumen = asisten baru.
4. **Adaptasi Bahasa & Persona** — pertanyaan santai/gaul atau bahasa Inggris
   tetap dijawab ramah dalam Bahasa Indonesia dengan sapaan khas UMKM ("Kak").
5. **Eval Suite Otomatis** — 20 kasus uji (grounding, multi-dokumen,
   anti-halusinasi, bahasa) dijalankan lewat script; kualitas jawaban terjaga
   setiap kali prompt/flow berubah.

## 5. Alur Penggunaan Project

**Setup (pemilik UMKM):** Upload dokumen bisnis → Langflow Knowledge Base
(chunk → embedding → vector store) → asisten siap dipakai.

**Pemakaian harian (pelanggan):**
Pertanyaan Pelanggan → Chat Input → Langflow (Knowledge Retrieval → Prompt
Grounding → AI Agent IBM Granite) → Jawaban Grounded / Penolakan + Eskalasi →
Pelanggan mendapat jawaban; pertanyaan tak terjawab masuk daftar untuk admin.

**Verifikasi developer:** IBM Bob → (MCP) → flow Langflow sebagai tool → hasil
eval & demo end-to-end.

## 6. Penggunaan IBM Langflow

Langflow adalah **tulang punggung seluruh sistem** — seluruh pipeline AI dibangun
visual di sana sebagai satu flow bernama `UMKM Assistant`:

- **Komponen/workflow:** `Chat Input` → `Knowledge` (mode Retrieve, knowledge
  base `umkm-batik2`, embedding `gemini-embedding-001`, Chroma local) →
  `Parser` (format hasil retrieval) → `Prompt` (template grounding:
  KONTEKS DOKUMEN + pertanyaan) → `Agent` (IBM Granite 3.3 8B via Ollama,
  system prompt grounding + few-shot anti-halusinasi) → `Chat Output`.
- **Input:** teks pertanyaan pelanggan. **Output:** jawaban grounded Bahasa
  Indonesia, atau penolakan jujur + tawaran eskalasi ke admin.
- **Proses AI Agent:** menerima konteks hasil retrieval + pertanyaan; diinstruksi
  HANYA menjawab dari konteks; dilarang menghitung diskon yang tidak tertulis
  (dengan contoh konkret); wajib menjawab semua bagian pertanyaan majemuk;
  menolak topik di luar cakupan bisnis.
- **Fungsi Langflow dalam sistem:** orkestrator RAG sekaligus API server — flow
  diekspos sebagai REST endpoint (`/api/v1/run/...`) dan sebagai MCP server,
  sehingga bisa dipakai frontend maupun IBM Bob tanpa menulis kode backend.

## 7. Penggunaan IBM Bob

**Fungsi:** IBM Bob (extension VS Code) adalah partner AI SDLC sekaligus **MCP
client** untuk menguji sistem end-to-end seperti pengguna nyata.

**Proses/task dengan Bob:** (1) mengembangkan & memperbaiki kode project selama
pengembangan; (2) mendaftarkan flow Langflow sebagai MCP server di konfigurasi
Bob (`mcp-config.example.json`); (3) memberi Bob instruksi delegasi
(`bob/agent-instructions.md`): terima pertanyaan pelanggan → kirim apa adanya ke
tool `umkm-assistant` → laporkan hasil tanpa mengarang.

**Interaksi dengan sistem:** Bob memanggil flow Langflow melalui protokol MCP
(streamable HTTP ke `localhost:7860/api/v1/mcp/project/...`), menjalankan
pertanyaan uji satu per satu, dan meneruskan jawaban asisten apa adanya.

**Output:** verifikasi end-to-end bahwa pertanyaan dari "sisi luar" dijawab
benar oleh pipeline (termasuk kasus anti-halusinasi yang harus ditolak) — bukti
integrasi berfungsi sebelum frontend dibangun.

## 8. Bagaimana IBM Langflow dan IBM Bob Terintegrasi?

Keduanya membentuk pola **MCP client → MCP server**:

- **Langflow** menjadi MCP server: semua flow dalam project otomatis terekspos
  sebagai tool MCP (tool `umkm-assistant`) di endpoint
  `/api/v1/mcp/project/<id>/sse`. Di dalamnya, Langflow menjalankan seluruh RAG:
  retrieval knowledge base → prompt grounding → Agent Granite → jawaban.
- **Bob** menjadi MCP client dan pengendali: sesuai instruksi delegasinya, Bob
  TIDAK menjawab sendiri, melainkan memanggil tool `umkm-assistant` dengan
  pertanyaan pengguna apa adanya.
- **Aliran data:** pertanyaan user → Bob (MCP client) → MCP endpoint Langflow →
  flow RAG → jawaban JSON → Bob → user. Bob tidak pernah memodifikasi jawaban,
  sehingga sifat grounded-nya terjaga dari sumber hingga user.
- **Output akhir integrasi:** jalur pengujian end-to-end yang merepresentasikan
  pengguna nyata — dipakai untuk menjalankan eval suite dan mendemonstrasikan
  bahwa sistem menjawab akurat DAN jujur menolak di luar cakupan.

## 9. Project File / Link

- **GitHub:** https://github.com/lenathea913/umkm-assistant
  (README, arsitektur, panduan build Langflow, system prompt, knowledge base,
  eval suite + hasil, konfigurasi Bob, export flow JSON, draf pitch).
- ⚠️ **TODO sebelum submit:** ubah repo menjadi **public**
  (`gh repo edit lenathea913/umkm-assistant --visibility public --accept-visibility-change-consequences`)
  agar reviewer bisa mengakses.

## 10. Pitching Deck

⚠️ **TODO:** buat slide (maks 10 MB) — kerangka sudah ada di
`submission/pitch-draft.md`: Cover → Problem → Solution → Demo/Arsitektur →
AI Agent → Responsible AI → Impact → Roadmap.

## 11. Project / Prototype Screenshot

⚠️ **TODO — 3–5 screenshot, usulan nama file:**
1. `01-chat-playground.png` — Playground: pertanyaan A1 + jawaban grounded Rp 1.850.000
2. `02-anti-halusinasi.png` — kasus C7: jujur menolak hitung diskon tunai
3. `03-langflow-workflow.png` — canvas flow UMKM Assistant utuh
4. `04-knowledge-base.png` — halaman Knowledge, KB `umkm-batik2` status Ready (5 chunks)
5. `05-eval-suite.png` — terminal `run_evals.py` berjalan / tabel hasil eval

## 12. Dampak yang Dihasilkan

- **Waktu respons:** dari menunggu balasan admin (menit–jam, rata-rata tertunda
  sampai jam kerja) → **instan, 24/7** — cakupan layanan naik dari ±9 jam/hari
  (6 hari/minggu) menjadi **168 jam/minggu penuh** (±19× lipat).
- **Akurasi terukur:** 20 kasus uji otomatis → 18 lulus penuh, 2 minor wording,
  **0 fakta karangan**; 7/7 kasus anti-halusinasi ditolak dengan benar
  (asisten tidak pernah mengarang harga/nomor/kebijakan).
- **Penghematan waktu admin:** pertanyaan repetitif (harga/stok/order/perawatan)
  terjawab otomatis — admin hanya menangani eskalasi; pada knowledge base uji
  (3 dokumen, 5 chunk), seluruh pertanyaan tipikal pelanggan butik tercakup.
- **Waktu setup:** < 30 menit dari nol (upload dokumen → asisten siap), tanpa
  satu baris kode bagi pemilik UMKM.

## 13. Potensi Pengembangan & Skalabilitas

- **Channel pelanggan nyata:** integrasi WhatsApp Business / Instagram DM agar
  pelanggan bertanya dari aplikasi yang sudah mereka pakai.
- **Multi-tenant SaaS:** satu deployment melayani banyak UMKM — tiap pemilik
  upload dokumennya sendiri (knowledge base terpisah per toko, sudah didukung
  arsitektur Knowledge Base Langflow).
- **Industri lain:** klinik (info layanan & jadwal), sekolah/bimbel (FAQ PPDB),
  komunitas/desa (info UMKM setempat) — polanya identik: ganti dokumen.
- **Bahasa daerah:** embedding multilingual + fine-tune prompt membuka dukungan
  Jawa/Sunda dan lainnya.
- **Enterprise:** migrasi LLM ke watsonx.ai (Granite cloud) + vector store
  terkelola untuk skala & keamanan lebih besar.

## 14. Apa yang Membuat Project Ini Berbeda?

1. **Kejujuran sebagai fitur utama, terukur:** bukan sekadar chatbot yang bisa
   bicara, tapi asisten yang *terbukti tidak mengarang* — 7 skenario jebakan
   (diskon fiktif, nomor telepon, cabang, promo) semuanya ditolak dengan elegan
   dan dieskalasi ke manusia. Kualitas diverifikasi eval otomatis, bukan klaim.
2. **Bahasa Indonesia end-to-end dengan persona lokal:** dokumen Indonesia,
   pertanyaan gaul/Inggris pun dijawab santun khas UMKM ("Kak") — bukan
   terjemahan kaku dari chatbot Inggris.
3. **Tanpa kode & replikabel:** pemilik UMKM tidak menyentuh prompt maupun
   server — upload dokumen, asisten siap; pindah ke UMKM lain cukup ganti dokumen.
   Dibangun penuh di stack IBM (Langflow + Granite + Bob) dengan biaya nol
   (infrastruktur lokal).

## 15. Kemampuan AI Agent

Agent ("Rara", Granite 3.3 8B) menjalankan secara otomatis:

- **Menjawab pertanyaan pelanggan** dari knowledge base: harga, ketersediaan
  ukuran/stok, cara order, garansi/retur, perawatan produk, promo, ongkir.
- **Sintesis multi-dokumen:** menggabungkan info dari katalog + price list +
  FAQ dalam satu jawaban (mis. "ukuran S ada, harganya Rp 465.000").
- **Deteksi & penolakan di luar cakupan:** pertanyaan yang tidak terjawab oleh
  dokumen (nomor kontak, cabang, promo fiktif) dijawab jujur + **eskalasi
  semi-otomatis**: pertanyaan dicatat untuk diteruskan ke admin di jam kerja.
- **Penolakan topik di luar bisnis** (medis, hukum, data pribadi) dengan sopan,
  lalu mengarahkan kembali ke produk.
- **Adaptasi bahasa:** memahami bahasa gaul & bahasa Inggris, selalu menjawab
  Bahasa Indonesia yang konsisten dengan persona toko.

Semi-otomatis (butuh manusia): pertanyaan eskalasi dijawab admin; pemilik
memperbarui knowledge base dengan upload dokumen baru.

---

## ✅ Checklist pengiriman

- [ ] Repo GitHub di-**public**-kan
- [ ] Pitch deck dibuat (maks 10 MB) — kerangka di `pitch-draft.md`
- [ ] 3–5 screenshot diambil & dinamai sesuai daftar di atas
- [ ] Semua jawaban di atas di-paste ke form
- [ ] Video/demo (bila diminta panitia)
