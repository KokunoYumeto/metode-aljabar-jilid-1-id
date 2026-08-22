# Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia

Edisi Bahasa Indonesia independen dari *Methods in Algebra, Volume 1* karya Wen-Wei Li. Repositori ini mempertahankan rumus, penomoran, label, rujukan silang, sitasi, diagram, latihan, petunjuk, dan indeks sumber sambil menyediakan lapisan data modular yang terikat hash.

Status saat ini: **Pendahuluan, seluruh Bab 1, serta pengantar Bab 2 telah diterjemahkan, diaudit, dibangun, dan diterima dalam delapan unit pembaca. Unit 8 memperkenalkan teori kategori, mempertahankan seluruh rujukan dan sitasi sumber, serta menata ulang tabel perbandingan agar memenuhi lebar area teks. Bagian 2.1 dan bagian-bagian selanjutnya masih dalam bahasa sumber dan akan diterjemahkan berurutan.** Repositori ini belum merupakan terjemahan lengkap buku.

[Baca atau unduh PDF Unit 1](artifacts/unit-001-pendahuluan.pdf)

[Baca atau unduh PDF Unit 2](artifacts/unit-002-bab-1-zfc.pdf)

[Baca atau unduh PDF Unit 3](artifacts/unit-003-bab-1-struktur-urutan-dan-ordinal.pdf)

[Baca atau unduh PDF Unit 4](artifacts/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf)

[Baca atau unduh PDF Unit 5](artifacts/unit-005-bab-1-kardinal.pdf)

[Baca atau unduh PDF Unit 6](artifacts/unit-006-bab-1-semesta-grothendieck.pdf)

[Baca atau unduh PDF Unit 7](artifacts/unit-007-bab-1-latihan.pdf)

[Baca atau unduh PDF Unit 8](artifacts/unit-008-bab-2-pengantar-teori-kategori.pdf)

Versi preservasi `0.2.0` yang memuat kedelapan reader, sumber yang dapat dibangun, backend modular, bukti ringkas, dan manifest hash tersedia pada [Zenodo DOI 10.5281/zenodo.22060005](https://doi.org/10.5281/zenodo.22060005). Seluruh pembaruan tetap berada dalam [concept DOI 10.5281/zenodo.22059759](https://doi.org/10.5281/zenodo.22059759), bukan membuat seri duplikat.

Checkpoint pembaca yang sama tersedia sebagai item karya publik pada [Figshare DOI 10.6084/m9.figshare.33314766.v2](https://doi.org/10.6084/m9.figshare.33314766.v2). PDF gabungan 83 halaman tampil sebagai berkas pertama, disertai paket sumber/backend ringkas, pemberitahuan hak, manifest, dan checksum. Lisensi item CC BY 4.0 berlaku pada teks utama dan adaptasi Indonesia; `Lanzhou.png` dan fragmen `AJbook.cls` yang dikreditkan tetap CC BY-SA 3.0, sedangkan font Noto tetap OFL 1.1, sebagaimana dirinci dalam `LICENSES.md`.

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
pwsh -NoProfile -File scripts/build_unit_005.ps1 -OutputDirectory build/unit-005-replay
pwsh -NoProfile -File scripts/build_unit_006.ps1 -OutputDirectory build/unit-006-replay
pwsh -NoProfile -File scripts/build_unit_007.ps1 -OutputDirectory build/unit-007-replay
pwsh -NoProfile -File scripts/build_unit_008.ps1 -OutputDirectory build/unit-008-replay
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
- 134.858 byte
- SHA-256 `031e231bc5d2ac74cada865700d8f76dda327941c7f442e6d47324b848103df8`
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

Artefak Unit 5 yang diterima:

- 12 halaman; tidak ada halaman kosong
- 128.556 byte
- SHA-256 `232d41f4e7f03123818ae14272958c8269242ebcbec68b832aaaf7ba295ebf3e`
- bahasa PDF `id-ID`
- 6 entri outline, 42 destinasi bernama, 17 tautan internal, 3 URI yang disengaja, dua diagram, indeks istilah, dan indeks simbol
- 163 fragmen matematika sebaris terpelihara; koreksi sejarah hipotesis kontinuum dan klarifikasi komposisi injeksi didokumentasikan secara eksplisit
- tidak ada galat TeX, sitasi/rujukan tak terdefinisi, destinasi ganda, karakter hilang, halaman kosong, residu aksara Han, atau tajuk `Lemma`

Artefak Unit 6 yang diterima:

- 9 halaman; tidak ada halaman kosong
- 120.808 byte
- SHA-256 `1fe15c59de6021b376643269423f2ef12e7b986f048ae39a31d8b1df9f7562c4`
- bahasa PDF `id-ID`
- 5 entri outline, 31 destinasi bernama, 21 tautan internal, dan 4 URI yang disengaja
- 99 fragmen matematika sebaris dan seluruh struktur Bagian 1.5 terpelihara; koreksi ejaan indeks sumber `cumulative hierachy` didokumentasikan
- label bibliografi telah dilokalkan ke `Dalam:`; tidak ada galat TeX, rujukan/sitasi tak terdefinisi, karakter hilang, halaman kosong, atau residu aksara Han

Artefak Unit 7 yang diterima:

- 4 halaman; tidak ada halaman kosong
- 100.435 byte
- SHA-256 `e7d4d6745f88b56c7ef840499c8e1d759b2bbbc14a245e8fc477fb0a6504a2b1`
- bahasa PDF `id-ID`
- 2 entri outline, 17 destinasi bernama, dan 3 URI yang disengaja
- enam latihan, enam subbagian, enam petunjuk, 64 fragmen matematika sebaris, dan 3 blok display terpelihara; koreksi tipe matematis pada petunjuk baris sumber 519 didokumentasikan
- daftar isi satu halaman yang jarang serta permukaan bibliografi/indeks kosong ditiadakan khusus untuk reader digital; tidak ada galat TeX, rujukan/sitasi tak terdefinisi, kotak meluber, karakter hilang, halaman kosong, atau residu aksara Han

Artefak Unit 8 yang diterima:

- 5 halaman; tidak ada halaman kosong atau baris tunggal yang terdampar
- 100.795 byte
- SHA-256 `d4234cb0080a60ad06fcb004d4d75e7daea85b3846bbbd05f0261b03e9f66258`
- bahasa PDF `id-ID`
- 2 entri outline, 10 destinasi bernama, 8 tautan internal, dan 7 URI yang disengaja
- label `sec:category`, tiga rujukan buku-global, empat sitasi, 8 fragmen matematika sebaris, dan 1 blok display terpelihara
- tabel empat-baris lima-kolom ditata ulang menjadi `tabularx` selebar teks dan dipasangkan dengan semantik pembacaan linear di backend; kotak petunjuk tetap utuh pada satu halaman
- label peran bibliografi telah dilokalkan; tidak ada galat TeX, rujukan/sitasi tak terdefinisi, kotak meluber, karakter hilang, halaman kosong, atau residu aksara Han

## Backend modular

`backend/data/unit-001-pendahuluan.json` sampai `backend/data/unit-008-bab-2-pengantar-teori-kategori.json` adalah catatan kanonik kedelapan unit yang telah diterima. ID berbasis UUIDv5 bersifat stabil dan tidak bergantung bahasa. Catatan tersebut memetakan sumber ke target sampai tingkat bagian, konsep, prasyarat, sitasi, diagram, indeks, hak komponen, build, dan peristiwa QA. Enam proyeksi CSV per unit dihasilkan secara deterministik. Karena skema v1.1.0 belum memiliki larik latihan/petunjuk kelas pertama, Unit 7 mempertahankan keenam latihan sebagai entitas bagian terurut dan setiap subbagian/petunjuk sebagai entitas stabil yang tertaut ke latihan induknya. Unit 8 memakai identitas kompatibel yang ditandai eksplisit untuk label, rujukan eksternal, tabel teks-native, dan semantik aksesibilitas linear.

Validasi:

```powershell
python scripts/validate_backend.py
python scripts/validate_backend.py --data backend/data/unit-002-bab-1-zfc.json
python scripts/validate_backend.py --data backend/data/unit-003-bab-1-struktur-urutan-dan-ordinal.json
python scripts/validate_backend.py --data backend/data/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.json
python scripts/validate_backend.py --data backend/data/unit-005-bab-1-kardinal.json
python scripts/validate_backend.py --data backend/data/unit-006-bab-1-semesta-grothendieck.json
python scripts/validate_backend.py --data backend/data/unit-007-bab-1-latihan.json
python scripts/validate_backend.py --data backend/data/unit-008-bab-2-pengantar-teori-kategori.json
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
- [x] Bab 1 — Teori himpunan
  - [x] Pembukaan bab dan Bagian 1.1 — Ikhtisar aksioma ZFC
  - [x] Bagian 1.2 — Struktur Urutan dan Ordinal
  - [x] Bagian 1.3 — Rekursi Transfinit dan Penerapannya
  - [x] Bagian 1.4 — Bilangan Kardinal
  - [x] Bagian 1.5 - Semesta Grothendieck
  - [x] Latihan Bab 1
- [ ] Bab 2 — Dasar-dasar teori kategori
  - [x] Pengantar bab dan petunjuk membaca
  - [ ] Bagian 2.1 dan seterusnya
- [ ] Bab 3 — Kategori monoidal
- [ ] Bab 4 — Teori grup
- [ ] Bab 5 — Dasar-dasar teori gelanggang
- [ ] Bab 6 — Teori modul
- [ ] Bab 7 — Dasar-dasar aljabar
- [ ] Bab 8 — Perluasan medan
- [ ] Bab 9 — Teori Galois
- [ ] Bab 10 — Valuasi medan
