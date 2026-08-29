# Lisensi dan atribusi komponen

Repositori ini adalah karya gabungan. Tidak ada satu label lisensi yang menggantikan hak setiap komponennya.

## Teks buku dan terjemahan

*Methods in Algebra, Volume 1* oleh Wen-Wei Li dan adaptasi/terjemahan Bahasa Indonesia didistribusikan menurut [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). Pertahankan atribusi kepada Wen-Wei Li, tautan lisensi, indikasi perubahan/terjemahan, dan pernyataan bahwa edisi ini independen serta tidak disahkan oleh penulis atau penerbit sumber.

Salinan pemberitahuan sumber terdapat di `repo/source/LICENSE`.

## Catatan teori representasi Duncan

Tujuh akar TeX yang dipilih dari repositori *Representation Theory Notes* karya Alexander Duncan beserta terjemahan Bahasa Indonesianya didistribusikan menurut [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). Enam lembar tugas di situs penulis, 49 soal di dalamnya, dan satu solusi parsial berada di luar repositori berlisensi dan tidak disertakan. Sumber, pemberitahuan, backend, serta manifest build ada di `repo/components/duncan/`.

## Pilihan CRing Project

Enam rentang yang dipilih dari *CRing Project*, terjemahan Bahasa Indonesia, dan integrasi pembacanya merupakan komponen termodifikasi menurut [GNU Free Documentation License 1.2 atau versi lebih baru](https://www.gnu.org/licenses/old-licenses/fdl-1.2.html), tanpa Bagian Invarian, tanpa Teks Sampul Depan, dan tanpa Teks Sampul Belakang. Salinan penuh lisensi ada di `repo/components/cring/support/GFDL-1.2-or-later.tex` dan disertakan di dalam PDF pembaca. Sembilan perbaikan serta sisipan orisinal ditandai dalam manifest/backend; enam rentang tepat tidak boleh disalahartikan sebagai terjemahan seluruh CRing Project.

## Lapisan rute dan penguasaan orisinal

`repo/components/original/` adalah materi edisi-orisinal yang disusun oleh `OpenAI Codex gpt-5.6-sol, Ultra`, atas instruksi pengguna. Materi ini disediakan menurut CC BY 4.0 dan tidak diatributkan kepada Li, Duncan, Mathew, CRing Project, atau penulis sumber lain. Rujukan ke komponen sumber tidak mengubah hak komponen tersebut.

## Komponen CC BY-SA 3.0

- Fragmen `DeclareSourcemap` di `repo/source/AJbook.cls` berasal dari jawaban TeX.StackExchange tahun 2013 oleh Guido dan suntingan dpprdan; perlakukan fragmen tersebut menurut CC BY-SA 3.0 dan pertahankan kredit sumber di dalam file.
- `repo/source/Lanzhou.png` diturunkan dari SVG Wikimedia Commons karya Chk2011; perlakukan gambar dan turunannya menurut CC BY-SA 3.0. Gambar ini tidak digunakan oleh reader Unit 1, tetapi tetap ada dalam penutupan sumber buku.

## Font

Font Noto CJK di `repo/fonts/` memakai SIL Open Font License 1.1. Teks lisensi lengkap terdapat di `repo/fonts/OFL-1.1-Noto-CJK.txt`.

Penutupan XeLaTeX juga memakai Fandol 0.3 karya Clerk Ma dan Jie Su. Fandol memakai GNU GPL versi 3 dengan pengecualian font yang menyatakan bahwa penyematan font atau bagian font yang tidak diubah ke dalam dokumen tidak dengan sendirinya menjadikan dokumen itu tercakup GPL. Salinan otoritatif `COPYING` dan `README` dari paket CTAN tersedia sebagai `repo/fonts/GPL-3.0-with-Fandol-font-exception.txt` dan `repo/fonts/FANDOL-README.txt`; identitas paket dan font yang dipakai build tercatat di `repo/fonts/FANDOL-AUTHORITY.json`. Perlakukan Fandol sebagai komponen tersendiri, bukan sebagai bagian berlisensi CC BY 4.0 atau OFL 1.1.

## Metadata dan kode baru

Metadata, skrip build/validasi, dan dokumentasi baru dalam repositori ini tidak mengubah atau memperluas izin komponen pihak ketiga. Jika materi baru kelak diberi lisensi terpisah, catatan hak komponen di backend harus menyatakannya secara eksplisit.
