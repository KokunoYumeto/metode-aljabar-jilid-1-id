# Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia

Edisi Bahasa Indonesia independen dari *Methods in Algebra, Volume 1* karya Wen-Wei Li. Repositori ini mempertahankan rumus, penomoran, label, rujukan silang, sitasi, diagram, latihan, petunjuk, dan indeks sumber sambil menyediakan lapisan data modular yang terikat hash.

Status saat ini: **Unit 1 — Pendahuluan telah diterjemahkan, diaudit, dibangun, dan diterima. Bab 1–10 masih dalam bahasa sumber dan akan diterjemahkan berurutan.** Repositori ini belum merupakan terjemahan lengkap buku.

[Baca atau unduh PDF Unit 1](artifacts/unit-001-pendahuluan.pdf)

## Identitas sumber

- Karya: Wen-Wei Li, *Methods in Algebra, Volume 1*
- Repositori resmi: <https://github.com/wenweili/AlJabr-1>
- Cabang: `master`
- Komit: `c4f7a01f68f5f407906b4b970640cddbbad85f6b`
- Pohon: `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- PDF resmi: 445 halaman, SHA-256 `dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38`

Edisi ini dibuat secara independen dan tidak disahkan oleh penulis atau penerbit sumber.

## Membangun Unit 1

Prasyarat: PowerShell 7, XeLaTeX, Biber, MakeIndex, serta paket-paket TeX yang dimuat oleh sumber. Font Noto CJK yang diperlukan sudah disertakan dengan lisensi OFL 1.1.

```powershell
pwsh -NoProfile -File scripts/build_unit_001.ps1 -OutputDirectory build/unit-001-replay
```

Skrip menjalankan XeLaTeX tanpa shell escape, Biber, MakeIndex, lalu tiga lintasan XeLaTeX. Tanggal sumber dan seed gambar sampul dipatok. Dua build bersih menghasilkan 21 halaman yang identik piksel demi piksel ketika dirender, meskipun serialisasi kontainer PDF XeTeX belum identik byte di direktori keluaran yang berbeda.

Artefak yang diterima:

- 21 halaman
- 199.917 byte
- SHA-256 `c74ce05494e07cb55e70186f391227d62d7f7da7c984788b9415cefb54083d5d`
- bahasa PDF `id-ID`
- 4 akar outline dan 36 destinasi bernama
- tidak ada galat TeX, sitasi/rujukan tak terdefinisi, destinasi ganda, atau karakter hilang

## Backend modular

`backend/data/unit-001-pendahuluan.json` adalah catatan kanonik Unit 1. ID berbasis UUIDv5 bersifat stabil dan tidak bergantung bahasa. Catatan tersebut memetakan sumber ke target sampai tingkat bagian, konsep, prasyarat, sitasi, diagram, indeks, hak komponen, build, dan peristiwa QA. Enam proyeksi CSV dihasilkan secara deterministik.

Validasi:

```powershell
python scripts/validate_backend.py
```

Validator memeriksa skema, keunikan dan relasi ID, urutan bagian, hash file dan rentang baris, penutupan sitasi/rujukan/diagram/indeks, bukti build, serta kesesuaian byte proyeksi CSV.

## Tata letak repositori

- `repo/source/` — sumber TeX beku dan sumber target yang sedang diterjemahkan
- `repo/fonts/` — font CJK yang diperlukan untuk build
- `artifacts/` — reader PDF yang telah diterima
- `backend/` — JSON, skema, dan proyeksi CSV modular
- `scripts/` — build dan validasi yang dapat diputar ulang
- `qa/` — receipt penerimaan dan bukti build ringkas
- `00_control/` — catatan otoritas, hak, terminologi, dan baseline publik

## Lisensi

Teks sumber dan terjemahan ditangani menurut Creative Commons Attribution 4.0 International (CC BY 4.0). Penutupan repositori memiliki pengecualian komponen yang tidak boleh diratakan menjadi satu klaim lisensi: fragmen teratribusi dalam `AJbook.cls` memerlukan CC BY-SA 3.0, `Lanzhou.png` berasal dari materi CC BY-SA 3.0, dan font Noto memakai SIL OFL 1.1. Lihat [LICENSES.md](LICENSES.md) dan `backend/csv/unit-001-rights.csv` untuk rincian.

## Kemajuan

- [x] Pendahuluan
- [ ] Bab 1 — Teori himpunan
- [ ] Bab 2 — Dasar-dasar teori kategori
- [ ] Bab 3 — Kategori monoidal
- [ ] Bab 4 — Teori grup
- [ ] Bab 5 — Dasar-dasar teori gelanggang
- [ ] Bab 6 — Teori modul
- [ ] Bab 7 — Dasar-dasar aljabar
- [ ] Bab 8 — Perluasan medan
- [ ] Bab 9 — Teori Galois
- [ ] Bab 10 — Valuasi medan

