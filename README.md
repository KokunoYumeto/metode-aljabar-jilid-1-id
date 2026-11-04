# Metode Aljabar, Jilid 1: terjemahan Bahasa Indonesia *Methods in Algebra, Volume 1* karya Wen-Wei Li

Terjemahan Bahasa Indonesia yang lengkap dari *Methods in Algebra, Volume 1* karya Wen-Wei Li: pendahuluan dan Bab
1–10 (teori himpunan, teori kategori, kategori monoidal, teori grup, gelanggang, modul, dasar-dasar aljabar,
perluasan medan, teori Galois, dan valuasi medan). Repositori ini juga memuat tiga komponen pendamping yang terpisah:
catatan teori representasi Alexander Duncan, enam pilihan aljabar komutatif dari CRing Project, serta rute
pembelajaran dan tugas penguasaan.

## Cara pembuatan

Penerjemahan, penataan ulang digital, QA, dan backend dikerjakan oleh AI: OpenAI Codex gpt-5.6-sol, Ultra. Rumus,
penomoran, label, rujukan silang, sitasi, diagram, latihan, petunjuk, dan indeks sumber dipertahankan. Lapisan data
modular di `backend/` memetakan sumber ke terjemahan sampai tingkat bagian, konsep, prasyarat, sitasi, diagram,
indeks, dan latihan. Setiap unit dibangun ulang, dirender, dan diperiksa halaman demi halaman; bukti build dan QA ada
di `qa/`. Rute pembelajaran dan tugas penguasaan disusun oleh model yang sama.

## Status

Keempat bagian lengkap: edisi Li (pendahuluan dan Bab 1–10), catatan Duncan (tujuh akar sumber berlisensi), enam
pilihan CRing, dan lapisan rute dan penguasaan. Masih mungkin ada kesalahan.

## Isi dan cara memulai

- [Edisi lengkap Li (PDF, 521 halaman)](artifacts/metode-aljabar-jilid-1-id-lengkap.pdf)
- [Catatan teori representasi Alexander Duncan (PDF, 114 halaman)](artifacts/catatan-teori-representasi-duncan-id.pdf)
- [Enam pilihan aljabar komutatif dari CRing Project (PDF, 74 halaman)](artifacts/pilihan-aljabar-komutatif-cring-id.pdf)
- [Rute pembelajaran, diagnostik, dan tugas penguasaan (PDF, 7 halaman)](artifacts/o013-rute-pembelajar-dan-penguasaan-id.pdf)
- PDF per unit ada di [artifacts/](artifacts); pembaca checkpoint yang lebih awal ada di `output/pdf/`.

Tata letak repositori:

- `repo/source/`: sumber TeX beku dan sumber terjemahan;
- `repo/components/duncan/`, `repo/components/cring/`, `repo/components/original/`: komponen Duncan, CRing, dan
  lapisan rute dan penguasaan, masing-masing dengan backend dan bukti build;
- `repo/fonts/`: font CJK yang diperlukan untuk build;
- `backend/`: JSON, skema, dan proyeksi CSV modular;
- `scripts/`: build dan validasi; `qa/`: bukti build dan pemeriksaan; `00_control/`: catatan otoritas, hak,
  terminologi, dan baseline.

Prasyarat build: PowerShell 7, XeLaTeX, Biber, MakeIndex, dan paket TeX yang dimuat sumber; font Noto CJK disertakan,
dan Fandol 0.3 diperlukan sebagai dependensi sistem. Pembaca lengkap dibangun dengan:

```powershell
pwsh -NoProfile -File scripts/build_li_complete.ps1
```

Setiap unit juga dapat dibangun sendiri (`scripts/build_unit_001.ps1` dan seterusnya, dengan
`-OutputDirectory build/unit-001-replay`). Backend divalidasi dengan `python scripts/validate_backend.py`, yang memeriksa
skema, keunikan dan relasi ID, urutan bagian, hash berkas dan rentang baris, penutupan sitasi, rujukan, diagram, dan
indeks, serta kesesuaian proyeksi CSV.

## Sumber dan atribusi

- Wen-Wei Li, *Methods in Algebra, Volume 1*: repositori resmi <https://github.com/wenweili/AlJabr-1>, cabang `master`,
  commit `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree `0f9fd52748165ec89a85ba602ccb949a2ce04694`; PDF resmi 445
  halaman, SHA-256 `dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38`.
- Alexander Duncan, *Representation Theory Notes*: tujuh akar TeX dari repositorinya (lembar tugas di situs penulis
  tidak termasuk).
- *CRing Project*: enam rentang terpilih, dengan sembilan perbaikan dan sisipan orisinal yang ditandai dalam manifest.
- Fragmen `DeclareSourcemap` dalam `repo/source/AJbook.cls`: jawaban TeX.StackExchange tahun 2013 oleh Guido dengan
  suntingan dpprdan; `repo/source/Lanzhou.png`: diturunkan dari SVG Wikimedia Commons karya Chk2011.
- Font: Noto CJK; Fandol 0.3 karya Clerk Ma dan Jie Su.
- Edisi ini dibuat secara independen dan tidak disahkan oleh penulis atau penerbit sumber.

## Hak

Teks Li dan Duncan beserta terjemahannya, serta lapisan rute dan penguasaan, tersedia menurut CC BY 4.0; pilihan CRing
menurut GFDL 1.2 atau versi lebih baru, tanpa Bagian Invarian dan tanpa Teks Sampul; fragmen AJbook dan `Lanzhou.png`
menurut CC BY-SA 3.0; Noto CJK menurut OFL 1.1; Fandol 0.3 menurut GPLv3 dengan pengecualian font. Tidak ada lisensi
payung; rinciannya ada di [LICENSES.md](LICENSES.md).
