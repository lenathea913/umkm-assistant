# UMKM Assistant — Asisten Bisnis Pintar berbasis RAG untuk UMKM Indonesia

> Tema: **Productivity & Smart Business** — Hacktiv8 National Hackathon 2026 × IBM SkillsBuild

## Masalah

Pemilik UMKM kewalahan melayani pertanyaan pelanggan yang berulang (harga, stok,
cara order, garansi) — terutama di luar jam operasional. Informasinya sebenarnya
sudah ada, tapi tersebar di dokumen: katalog produk, price list, FAQ, SOP.
Pelanggan yang bertanya lewat chat harus menunggu balasan manual.

## Solusi

Asisten AI yang "membaca" dokumen bisnis. Pemilik UMKM cukup upload PDF/daftar
produk, dan asisten langsung menjawab pertanyaan pelanggan secara akurat dalam
**Bahasa Indonesia — 24/7 — hanya berdasarkan isi dokumen resmi** (teknik RAG),
sehingga risiko jawaban ngarang (halusinasi) minimal. Pertanyaan di luar cakupan
dokumen tidak dijawab karangan; asisten menawarkan eskalasi ke pemilik bisnis.

## Teknologi IBM

| Layer | Teknologi |
|---|---|
| Pipeline RAG visual | IBM Langflow (File → Split → Embed → Vector Store → Retriever) |
| Model bahasa | IBM Granite (watsonx.ai) |
| AI SDLC partner | IBM Bob (MCP client → flow sebagai MCP server) |
| Eksekusi lokal | Langflow di localhost, diekspos via MCP ke Bob |

## Struktur repo

```
umkm-assistant/
├── README.md                  ← file ini
├── knowledge-base/            ← dokumen bisnis contoh (di-upload ke flow)
│   ├── katalog-produk.md
│   ├── price-list.md
│   └── faq-sop.md
├── langflow/
│   ├── BUILD-GUIDE.md         ← langkah membangun flow RAG di Langflow
│   └── agent-system-prompt.md ← system prompt komponen agent (masuk ke Langflow)
├── evals/
│   └── eval-questions.md      ← 15+ pertanyaan uji, termasuk tes anti-halusinasi
├── bob/
│   ├── agent-instructions.md  ← instruksi Bob sebagai delegator
│   └── mcp-config.example.json
└── submission/
    └── pitch-draft.md         ← draf narasi submission per kriteria rubrik
```

## Cara menjalankan (ringkas)

1. Buka Langflow → flow baru → ikuti `langflow/BUILD-GUIDE.md`.
2. Upload file di `knowledge-base/` sebagai sumber knowledge.
3. Tempel `langflow/agent-system-prompt.md` ke komponen agent.
4. Ekspose flow sebagai MCP server → daftarkan di Bob (`bob/mcp-config.example.json`).
5. Uji dengan `evals/eval-questions.md` — semua jawaban wajib merujuk dokumen.

## Peta ke rubrik penilaian

| Kriteria | Buktinya |
|---|---|
| Problem Clarity | Masalah layanan pelanggan UMKM 24/7 — rinci di `submission/pitch-draft.md` |
| Innovation | RAG berbahasa Indonesia yang menolak mengarang + eskalasi manusia |
| User Impact | UMKM tanpa tim CS tetap responsif 24/7; setup hanya upload dokumen |
| Technical Execution | Flow RAG Langflow + Granite + MCP/Bob end-to-end, teruji via eval suite |
| Responsible AI | Grounding wajib ke dokumen, penolakan di luar cakupan, no PII leakage |

## Roadmap

- [x] Ide final & peta rubrik
- [ ] Flow RAG dibangun di Langflow (BUILD-GUIDE.md)
- [ ] Bob terhubung sebagai MCP client
- [ ] Eval suite lulus (termasuk tes anti-halusinasi)
- [ ] Demo video + narasi submission
