# Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia

Edisi Bahasa Indonesia independen dari *Methods in Algebra, Volume 1* karya Wen-Wei Li. Repositori ini mempertahankan rumus, penomoran, label, rujukan silang, sitasi, diagram, latihan, petunjuk, dan indeks sumber sambil menyediakan lapisan data modular yang terikat hash.

Status saat ini: **Unit 1 - Pendahuluan, Unit 2 - pembukaan Bab 1 dan Bagian 1.1 tentang aksioma ZFC, Unit 3 - Bagian 1.2 tentang struktur urutan dan ordinal, serta Unit 4 - Bagian 1.3 tentang rekursi transfinit dan penerapannya telah diterjemahkan, diaudit, dibangun, dan diterima. Bagian 1.4 dan seterusnya masih dalam bahasa sumber dan akan diterjemahkan berurutan.** Repositori ini belum merupakan terjemahan lengkap buku.

[Baca atau unduh PDF Unit 1](artifacts/unit-001-pendahuluan.pdf)

[Baca atau unduh PDF Unit 2](artifacts/unit-002-bab-1-zfc.pdf)

[Baca atau unduh PDF Unit 3](artifacts/unit-003-bab-1-struktur-urutan-dan-ordinal.pdf)

[Baca atau unduh PDF Unit 4](artifacts/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf)

## Identitas sumber

- Karya: Wen-Wei Li, *Methods in Algebra, Volume 1*
- Repositori resmi: <https://github.com/wenweili/AlJabr-1>
- Cabang: `master`
- Komit: `c4f7a01f68f5f407906b4b970640cddbbad85f6b`
- Pohon: `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- PDF resmi: 445 halaman, SHA-256 `dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38`

Edisi ini dibuat secara independen dan tidak disahkan oleh penulis atau penerbit sumber.

## Membangun unit pembaca

Prasyarat: PowerShell 7, XeLaTeX, Biber, MakeIndex, serta paket-paket TeX yang dimuat oleh sumber. Font Noto CJK yang diperlukan sudah disertakan dengan lisensi OFL 1.1.

```powershell
pwsh -NoProfile -File scripts/build_unit_001.ps1 -OutputDirectory build/unit-001-replay
pwsh -NoProfile -File scripts/build_unit_002.ps1 -OutputDirectory build/unit-002-replay
pwsh -NoProfile -File scripts/build_unit_003.ps1 -OutputDirectory build/unit-003-replay
pwsh -NoProfile -File scripts/build_unit_004.ps1 -OutputDirectory build/unit-004-replay
```

Skrip menjalankan XeLaTeX tanpa shell escape, indeks dan bibliografi yang dibutuhkan setiap unit, lalu lintasan konvergensi XeLaTeX. Tanggal sumber dan seed gambar sampul dipatok. Dua build bersih untuk setiap unit menghasilkan halaman yang identik piksel demi piksel ketika dirender, meskipun serialisasi kontainer PDF XeTeX belum identik byte di direktori keluaran yang berbeda.

Artefak Unit 1 yang diterima:

- 21 halaman
- 199.917 byte
- SHA-256 `c74ce05494e07cb55e70186f391227d62d7f7da7c984788b9415cefb54083d5d`
- bahasa PDF `id-ID`
- 4 akar outline dan 36 destinasi bernama
- tidak ada galat TeX, sitasi/rujukan tak terdefinisi, destinasi ganda, atau karakter hilang

Artefak Unit 2 yang diterima:

- 12 halaman; halaman verso kosong khusus cetak telah dihapus dari reader digital
- 161.147 byte
- SHA-256 `ff2eb3fd1ec5abaa7989d0c29c419c04f99368dc3f278799be460e30042bfe58`
- bahasa PDF `id-ID`
- 5 akar outline, 33 destinasi bernama, indeks istilah, dan indeks simbol
- tidak ada galat TeX, sitasi/rujukan tak terdefinisi, destinasi ganda, karakter hilang, atau tautan eksternal palsu

Artefak Unit 3 yang diterima:

- 11 halaman; tidak ada halaman kosong
- 147.784 byte
- SHA-256 `67f3b0594f65917cf78361886aef6616c0875bc584a95758f06e4d11b182082c`
- bahasa PDF `id-ID`
- 5 akar outline, 43 destinasi bernama, indeks istilah, dan indeks simbol
- judul definisi, lema, teorema, proposisi, contoh, dan bukti telah dilokalkan ke bahasa Indonesia
- tidak ada galat TeX, sitasi/rujukan tak terdefinisi, destinasi ganda, karakter hilang, halaman kosong, atau tajuk lingkungan berbahasa Tionghoa

Artefak Unit 4 yang diterima:

- 8 halaman; tidak ada halaman kosong
- 107.332 byte
- SHA-256 `e48aa97d15ad9c192df5d744bfc8290fc816c4b681322295352517a02e267c13`
- bahasa PDF `id-ID`
- 4 akar outline, 37 destinasi bernama, dan indeks istilah
- 138 fragmen matematika sebaris dan 2 blok display terpelihara; koreksi kecil syarat `tak kosong` pada baris sumber 206 didokumentasikan secara eksplisit
- tidak ada galat TeX, sitasi/rujukan tak terdefinisi, destinasi ganda, karakter hilang, halaman kosong, atau residu aksara Han

## Backend modular

`backend/data/unit-001-pendahuluan.json`, `backend/data/unit-002-bab-1-zfc.json`, `backend/data/unit-003-bab-1-struktur-urutan-dan-ordinal.json`, dan `backend/data/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.json` adalah catatan kanonik unit yang telah diterima. ID berbasis UUIDv5 bersifat stabil dan tidak bergantung bahasa. Catatan tersebut memetakan sumber ke target sampai tingkat bagian, konsep, prasyarat, sitasi, diagram, indeks, hak komponen, build, dan peristiwa QA. Enam proyeksi CSV per unit dihasilkan secara deterministik.

Validasi:

```powershell
python scripts/validate_backend.py
python scripts/validate_backend.py --data backend/data/unit-002-bab-1-zfc.json
python scripts/validate_backend.py --data backend/data/unit-003-bab-1-struktur-urutan-dan-ordinal.json
python scripts/validate_backend.py --data backend/data/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.json
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

Teks sumber dan terjemahan ditangani menurut Creative Commons Attribution 4.0 International (CC BY 4.0). Penutupan repositori memiliki pengecualian komponen yang tidak boleh diratakan menjadi satu klaim lisensi: fragmen teratribusi dalam `AJbook.cls` memerlukan CC BY-SA 3.0, `Lanzhou.png` berasal dari materi CC BY-SA 3.0, dan font Noto memakai SIL OFL 1.1. Lihat [LICENSES.md](LICENSES.md) dan proyeksi `backend/csv/*-rights.csv` untuk rincian.

## Kemajuan

- [x] Pendahuluan
- [ ] Bab 1 — Teori himpunan
  - [x] Pembukaan bab dan Bagian 1.1 — Ikhtisar aksioma ZFC
  - [x] Bagian 1.2 — Struktur Urutan dan Ordinal
  - [x] Bagian 1.3 — Rekursi Transfinit dan Penerapannya
  - [ ] Bagian 1.4 dan seterusnya
- [ ] Bab 2 — Dasar-dasar teori kategori
- [ ] Bab 3 — Kategori monoidal
- [ ] Bab 4 — Teori grup
- [ ] Bab 5 — Dasar-dasar teori gelanggang
- [ ] Bab 6 — Teori modul
- [ ] Bab 7 — Dasar-dasar aljabar
- [ ] Bab 8 — Perluasan medan
- [ ] Bab 9 — Teori Galois
- [ ] Bab 10 — Valuasi medan
