# Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia

Edisi Bahasa Indonesia independen dari *Methods in Algebra, Volume 1* karya Wen-Wei Li. Repositori ini mempertahankan rumus, penomoran, label, rujukan silang, sitasi, diagram, latihan, petunjuk, dan indeks sumber sambil menyediakan lapisan data modular yang terikat hash.

Status saat ini: **Pendahuluan, seluruh Bab 1, pengantar Bab 2, serta Bagian 2.1-2.6 telah diterjemahkan, diaudit, dibangun, diterima, dan dipublikasikan dalam empat belas unit pembaca. Unit 10 menyajikan fungtor dan transformasi natural; Unit 11 kategori fungtor; Unit 12 sifat universal dan kategori koma; Unit 13 fungtor representabel dan Lema Yoneda; Unit 14 dasar-dasar fungtor adjoin. Contoh-contoh pada `chapter2.tex:910-1110` menjadi span terjemahan berikutnya; Bagian 2.7 dimulai pada baris 1111.** Repositori ini belum merupakan terjemahan lengkap buku.

[Baca atau unduh checkpoint pembaca 0.3.0 (96 halaman; Unit 1-9)](output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-0.3.0-reader.pdf)

[Baca atau unduh checkpoint pembaca 0.4.0 (128 halaman; Unit 1-12)](output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-0.4.0-reader.pdf)

[Baca atau unduh PDF Unit 1](artifacts/unit-001-pendahuluan.pdf)

[Baca atau unduh PDF Unit 2](artifacts/unit-002-bab-1-zfc.pdf)

[Baca atau unduh PDF Unit 3](artifacts/unit-003-bab-1-struktur-urutan-dan-ordinal.pdf)

[Baca atau unduh PDF Unit 4](artifacts/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf)

[Baca atau unduh PDF Unit 5](artifacts/unit-005-bab-1-kardinal.pdf)

[Baca atau unduh PDF Unit 6](artifacts/unit-006-bab-1-semesta-grothendieck.pdf)

[Baca atau unduh PDF Unit 7](artifacts/unit-007-bab-1-latihan.pdf)

[Baca atau unduh PDF Unit 8](artifacts/unit-008-bab-2-pengantar-teori-kategori.pdf)

[Baca atau unduh PDF Unit 9](artifacts/unit-009-bab-2-kategori-dan-morfisme.pdf)

[Baca atau unduh PDF Unit 10](artifacts/unit-010-bab-2-fungtor-dan-transformasi-natural.pdf)

[Baca atau unduh PDF Unit 11](artifacts/unit-011-bab-2-kategori-fungtor.pdf)

[Baca atau unduh PDF Unit 12](artifacts/unit-012-bab-2-sifat-universal-dan-kategori-koma.pdf)

[Baca atau unduh PDF Unit 13](artifacts/unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.pdf)

[Baca atau unduh PDF Unit 14](artifacts/unit-014-bab-2-fungtor-adjoin-dasar.pdf)

Versi preservasi `0.3.0` yang memuat checkpoint gabungan 96 halaman, kesembilan reader, sumber yang dapat dibangun, backend modular, bukti ringkas, dan manifest hash tersedia pada [Zenodo DOI 10.5281/zenodo.22062228](https://doi.org/10.5281/zenodo.22062228). Seluruh pembaruan tetap berada dalam [concept DOI 10.5281/zenodo.22059759](https://doi.org/10.5281/zenodo.22059759), bukan membuat seri duplikat. Rilis `0.4.0` yang sama dengan reader Unit 1-12 sudah byte-verified di GitHub pada commit `f47d290117001a16d0d765bb5f83b3c73bc9a8f3`; pembaruan DOI tertahan oleh blocker eksternal yang dicatat dalam [`qa/ZENODO_PUBLICATION_BLOCKED_20260823.md`](qa/ZENODO_PUBLICATION_BLOCKED_20260823.md).

Checkpoint pembaca sebelumnya juga memiliki item karya pada [Figshare DOI 10.6084/m9.figshare.33314766.v3](https://doi.org/10.6084/m9.figshare.33314766.v3). Rute `0.4.0` mempertahankan reader-first PDF, paket sumber/backend ringkas, pemberitahuan hak, manifest, dan checksum, tetapi pembaruan publik saat ini tertahan karena kredensial Figshare lokal mengembalikan `InactiveAccount` dan artikel lama perlu diverifikasi ulang; lihat [`qa/FIGSHARE_PUBLICATION_BLOCKED_20260823.md`](qa/FIGSHARE_PUBLICATION_BLOCKED_20260823.md). Lisensi teks utama/adaptasi adalah CC BY 4.0; `Lanzhou.png` dan fragmen `AJbook.cls` yang dikreditkan tetap CC BY-SA 3.0, sedangkan font Noto tetap OFL 1.1, sebagaimana dirinci dalam `LICENSES.md`.

## Identitas sumber

- Karya: Wen-Wei Li, *Methods in Algebra, Volume 1*
- Repositori resmi: <https://github.com/wenweili/AlJabr-1>
- Cabang: `master`
- Komit: `c4f7a01f68f5f407906b4b970640cddbbad85f6b`
- Pohon: `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- PDF resmi: 445 halaman, SHA-256 `dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38`

Edisi ini dibuat secara independen dan tidak disahkan oleh penulis atau penerbit sumber.

Catatan provenance: penerjemahan, penataan ulang digital, QA, dan backend edisi
ini dikerjakan atas instruksi pengguna. Model: OpenAI Codex gpt-5.6-sol, Ultra.
Keterangan ini tidak menggantikan kredit Wen-Wei Li sebagai penulis karya
sumber maupun kredit dan lisensi setiap komponen yang dipertahankan di bawah.

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
pwsh -NoProfile -File scripts/build_unit_009.ps1 -OutputDirectory build/unit-009-replay
pwsh -NoProfile -File scripts/build_unit_010.ps1 -OutputDirectory build/unit-010-replay
pwsh -NoProfile -File scripts/build_unit_011.ps1 -OutputDirectory build/unit-011-replay
pwsh -NoProfile -File scripts/build_unit_012.ps1 -OutputDirectory build/unit-012-replay
pwsh -NoProfile -File scripts/build_unit_013.ps1 -OutputDirectory build/unit-013-replay
pwsh -NoProfile -File scripts/build_unit_014.ps1 -OutputDirectory build/unit-014-replay
```

Skrip menjalankan XeLaTeX tanpa shell escape, indeks dan bibliografi yang dibutuhkan setiap unit, lalu lintasan konvergensi XeLaTeX. Tanggal sumber dan seed gambar sampul dipatok. Dua build bersih untuk setiap unit menghasilkan halaman yang identik piksel demi piksel ketika dirender, meskipun serialisasi kontainer PDF XeTeX belum identik byte di direktori keluaran yang berbeda.

Artefak Unit 1 yang diterima:

- 21 halaman
- 199.926 byte
- SHA-256 `b3fca2af76b793a19877ffc822d6ec89c2494641f7e1dfa468b158c7bec30a3e`
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
- 100.805 byte
- SHA-256 `0db18bfbae3ffd2194447781a77effb4f57f8bd8521baa3acb334b474f0773cd`
- bahasa PDF `id-ID`
- 2 entri outline, 10 destinasi bernama, 8 tautan internal, dan 7 URI yang disengaja
- label `sec:category`, tiga rujukan buku-global, empat sitasi, 8 fragmen matematika sebaris, dan 1 blok display terpelihara
- tabel empat-baris lima-kolom ditata ulang menjadi `tabularx` selebar teks dan dipasangkan dengan semantik pembacaan linear di backend; kotak petunjuk tetap utuh pada satu halaman
- QA terminologi primer membakukan `fungtor` dan `transformasi natural` tanpa mengubah matematika, struktur, atau paginasi
- label peran bibliografi telah dilokalkan; tidak ada galat TeX, rujukan/sitasi tak terdefinisi, kotak meluber, karakter hilang, halaman kosong, atau residu aksara Han

Artefak Unit 9 yang diterima:

- 13 halaman; tidak ada halaman kosong
- 143.207 byte
- SHA-256 `1a71610ba997348ce22db69944fec3529d9d6e6c2ef6ece48faa30df90ac5ce6`
- bahasa PDF `id-ID`
- 4 entri outline, 49 destinasi bernama, 42 tautan internal, dan 3 URI yang disengaja
- tujuh label, sepuluh kemunculan rujukan, lima kemunculan sitasi, 31 entri indeks, 268 permukaan matematika, empat diagram `tikzcd`, dan satu gambar `tikzpicture` terpelihara
- rantai ordinal yang lebar ditata ulang secara tipografis agar terpusat dan terbaca tanpa mengubah matematika; koreksi, catatan sumber, dan klarifikasi diperinci dalam receipt penerimaan
- QA terminologi primer membakukan `fungtor`; matematika, identitas, topologi, dan paginasi tetap sama
- tidak ada galat TeX, rujukan/sitasi tak terdefinisi, kotak meluber, karakter hilang, halaman kosong, atau residu aksara Han pada halaman isi

Artefak Unit 10 yang diterima secara lokal:

- 15 halaman; 153.352 byte; SHA-256 `a06c4152e6233270cfa138b6c99ae9f307246fe2e1eac6b72a9533c9d74bfce4`
- target Section 2.2 28.112 byte; SHA-256 `84cd01f4bfb9b2dcf6720991b72d714335e3f977e2bee88d40b2b64733572053`
- backend 98.251 byte; SHA-256 `d89f4487c7b1610d267068b70f429d9ac0d1f1ddc9136b8370fe8fec447eda4d`
- 291 permukaan matematika, 13 label, 7 rujukan, 2 rujukan persamaan, 2 sitasi, 15 indeks, dan 19 diagram terpelihara; dua build serta replay visual lulus.

Artefak Unit 11 yang diterima secara lokal:

- 7 halaman; 105.391 byte; SHA-256 `f18ea37d945b08961f14e49581dd13a3a3024307fe3d33a77c7d5bb5631859fe`
- target kategori fungtor 8.004 byte; SHA-256 `a848cb6d7dfdd7edc1f5b07be14f421ed075a8124723ab9b73a207f86216e105`
- backend 51.063 byte; SHA-256 `998c47db6bd6692347c16be7d13762395a00b3ca90635dc6d7ee87ef878c1b36`
- 102 permukaan matematika, 4 label, 5 rujukan, 1 rujukan persamaan, 8 indeks, dan satu diagram terpelihara; dua build serta replay visual lulus. Lima peringatan Hyperref untuk target kosong disengaja untuk menekan tautan eksternal palsu.

Artefak Unit 12 yang diterima secara lokal:

- 10 halaman; 121.388 byte; SHA-256 `1671beea4ab78c848d577f9b8428d5717de2ac55f309f4f075c455409fd878a9`
- target sifat universal dan kategori koma 11.056 byte; SHA-256 `26a2e9a638fae91a1108c9a263a89b64b71ba5d351cae1bfae72eef6eba0649b`
- backend 59.781 byte; SHA-256 `d3caeab3c47f8323b7acd9883464babad604e6cffa0fa52bcca9b843deb7e63b`
- 159 permukaan matematika, 7 label, 6 rujukan, 1 sitasi, 6 indeks, dan 8 diagram `tikzcd` terpelihara; dua build serta replay visual 10/10 halaman lulus.
- tiga target eksternal kosong tetap ditekan secara sengaja oleh witness `unit-012-crossrefs.aux`; tidak ada rujukan/sitasi tak terdefinisi, kotak meluber, halaman kosong, atau residu aksara Han pada span terjemahan.

Artefak Unit 13 yang diterima secara lokal:

- 7 halaman; 106.154 byte; SHA-256 `4db806c3a0c42449b1333e25109d135176931880a48982a70b776e04be7ffa2a`
- target fungtor representabel dan Lema Yoneda 8.643 byte; SHA-256 `eeb6bbb2aca0ea17277e7afea39492729996cd9d8648deccc94bcebe9111327d`
- backend 53.887 byte; SHA-256 `c4e484a039d5ea034b3bb1eba1d54364f795061b6fbc950ddf17d03c9f448cc3`
- 98 permukaan matematika, 7 label, 10 rujukan, 3 rujukan persamaan, 5 indeks, dan 2 diagram `tikzcd` terpelihara setelah dua koreksi sumber yang didokumentasikan.
- isomorfisme Yoneda yang panjang ditata sebagai display dan kedua indeks digabung pada satu halaman akhir; dua build serta replay visual 7/7 halaman lulus tanpa kotak meluber, rujukan tak terdefinisi, halaman kosong, atau residu aksara Han.

Artefak Unit 14 yang diterima secara lokal:

- 9 halaman; 121.651 byte; SHA-256 `a8acee26ef75f172336d4e729e055ca6c8d222c548748d9c4a58a4ee976cb403`
- target dasar-dasar fungtor adjoin pada `chapter2.tex:766-909` adalah 11.655 byte; SHA-256 `5526e8eb99dba9dc3e0eebbd1ddd278eb6343fd50a1d18cf0f6715f09f6e1ed2`; file target lengkap 155.822 byte; SHA-256 `bcf19c8d261947fa619c0257351c29217f401bc1c9453ad91286ff96c1bd69a5`
- dua build dan replay visual MuPDF/Poppler 9/9 halaman lulus; seluruh halaman diperiksa. Dua kotak meluber yang sangat kecil tidak memotong margin aman dan telah diperiksa secara visual; tidak ada rujukan/sitasi tak terdefinisi, destinasi ganda, karakter hilang, atau galat TeX fatal.
- reflow digital memakai spasi baris 1,45 agar diagram dan kesimpulan tetap bersama tanpa membuat halaman isi akhir yang hampir kosong; matematika dan struktur sumber tidak diubah.
- empat koreksi sumber yang diungkapkan memperbaiki indeks komponen `\varphi_{V,W}`, kategori lawan pada dualitas berdimensi hingga, notasi `Vect_f(k)`, dan indeks komponen counit oleh `Y \in \Obj(C_2)`.
- Unit 14 dipublikasikan pada commit `9c927ba19b14898a8cd8a3cadef30ee309510c8c`; 30 path eksplisit / 923.499 byte cocok dengan byte dan SHA-256 lokal pada pembacaan balik anonim.

## Backend modular

`backend/data/unit-001-pendahuluan.json` sampai `backend/data/unit-014-bab-2-fungtor-adjoin-dasar.json` adalah catatan kanonik empat belas unit yang telah diterima secara lokal. ID berbasis UUIDv5 bersifat stabil dan tidak bergantung bahasa. Catatan tersebut memetakan sumber ke target sampai tingkat bagian, konsep, prasyarat, sitasi, diagram, indeks, hak komponen, build, dan peristiwa QA. Enam proyeksi CSV per unit dihasilkan secara deterministik. Karena skema v1.1.0 belum memiliki larik latihan/petunjuk kelas pertama, Unit 7 mempertahankan keenam latihan sebagai entitas bagian terurut dan setiap subbagian/petunjuk sebagai entitas stabil yang tertaut ke latihan induknya. Unit 8 memakai identitas kompatibel yang ditandai eksplisit untuk label, rujukan eksternal, tabel teks-native, dan semantik aksesibilitas linear. Unit 9 memakai identitas kemunculan yang stabil untuk rujukan dan sitasi berulang serta mengikat kelima diagram dan seluruh 31 entri indeks ke rentang sumber/target yang tepat. Unit 10-14 memakai identitas yang sama untuk permukaan matematika, diagram, rujukan eksternal, indeks, sitasi, serta provenance model; Unit 10 dan 11 sudah dipublikasikan pada commit `17dac5e2984604c3f2010a04f6021f36e3eb3586`, sedangkan bukti Unit 12-14 ada pada receipt penerimaan masing-masing.

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
python scripts/validate_backend.py --data backend/data/unit-009-bab-2-kategori-dan-morfisme.json
python scripts/validate_backend.py --data backend/data/unit-010-bab-2-fungtor-dan-transformasi-natural.json
python scripts/validate_backend.py --data backend/data/unit-011-bab-2-kategori-fungtor.json
python scripts/validate_backend.py --data backend/data/unit-012-bab-2-sifat-universal-dan-kategori-koma.json
python scripts/validate_backend.py --data backend/data/unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.json
python scripts/validate_backend.py --data backend/data/unit-014-bab-2-fungtor-adjoin-dasar.json
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
  - [x] Bagian 2.1 — Kategori dan Morfisme
  - [x] Bagian 2.2 — Fungtor dan transformasi natural
  - [x] Bagian 2.3 — Kategori fungtor
  - [x] Bagian 2.4 — Sifat universal dan kategori koma
  - [x] Bagian 2.5 — Fungtor representabel dan Lema Yoneda
  - [x] Bagian 2.6 — Dasar-dasar fungtor adjoin
  - [ ] Contoh-contoh `chapter2.tex:910-1110`
  - [ ] Bagian 2.7 dan seterusnya
- [ ] Bab 3 — Kategori monoidal
- [ ] Bab 4 — Teori grup
- [ ] Bab 5 — Dasar-dasar teori gelanggang
- [ ] Bab 6 — Teori modul
- [ ] Bab 7 — Dasar-dasar aljabar
- [ ] Bab 8 — Perluasan medan
- [ ] Bab 9 — Teori Galois
- [ ] Bab 10 — Valuasi medan
