# Eval Results — UMKM Assistant

Dijalankan via Playground Langflow (flow `UMKM Assistant`, KB `umkm-batik2`,
embedding `gemini-embedding-001`). Dua sesi pengujian:

- **Sesi 1** (LLM `gemini-3.8-flash`): A1 lulus grounded.
- **Sesi 2** (LLM `granite3.3:2b` via Ollama): A1–A8, hasil di bawah.

Daftar pertanyaan lengkap: [eval-questions.md](eval-questions.md).

## Hasil (sesi granite3.3:2b)

| ID | Jawaban inti | Lulus? | Catatan |
|---|---|---|---|
| A1 | Rp 1.850.000, kode BT-MM-001, primissima, pewarna indigo, 2–3 minggu | ✅ | Grounded sempurna, persona Rara konsisten (66,8s) |
| A2 | XXL tersedia (RTW-KM-201) | ✅ | Benar; harga tidak disebut |
| A3 | Langkah order dikarang | ❌ | Muncul "kode berlangganan", "kuota pengiriman" — tidak ada di SOP; frasa Inggris bocor |
| A4 | Mengaku batik tulis "stok ada, bisa dikirim" | ❌ | Salah fatal — made to order 2–3 minggu; kalimat kacau |
| A5 | — | ⚠️ | Belum diuji (tidak ada di file hasil) |
| A6 | Diskon 15% cap/RTW, tulis tidak ikut | ⚠️ | Inti benar, kalimat rusak, kata Belanda "terwijzen" |
| A7 | Ongkir gratis >Rp 500rb (Jawa) / >Rp 1,5jt (luar Jawa) | ⚠️ | Fakta benar + caveat karangan ("kelengkungan jalan pengiriman") |
| A8 | "Warna pastel" | ❌ | Mengarang daftar warna (hijau, kuning, biru) — dokumen hanya "pastel" |

**Kesimpulan sesi 2:** model 2B terlalu lemah — bahasa Indonesia tidak mulus,
mudah mengarang detail pada soal sintesis (A3/A4/A8). Retrieval & simple fact
(A1/A2) bekerja baik. Perlu naik ke `granite3.3:8b` atau model kelas 70B
(Groq) sebelum eval dilanjutkan.
| B1 | | | |
| B2 | | | |
| B3 | | | |
| C1 | | | |
| C2 | | | |
| C3 | | | |
| C4 | | | |
| C5 | | | |
| C6 | | | |
| C7 | | | |
| D1 | | | |
| D2 | | | |

## Catatan teknis

- Pesan pertama di Playground ("hi") pernah gagal dengan "An error occurred"
  (transien, run kedua normal). Pantau bila terulang.
- Waktu respons A1: ±39 detik (2.0K token). Untuk demo, pertimbangkan pertanyaan
  pendek agar tetap dalam durasi video.
