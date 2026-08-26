# Unit 033 visual and PDF QA - 2026-08-26

Status: **PASS WITH WARNINGS**. Exact identity, two-engine decoded-pixel,
metadata, navigation, font, extraction, action/link, geometry, diagnostics,
and all-page visual gates pass. No actionable defect remains.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
| `build/unit-033-final-m/unit-033-bab-4-grup-simetris.pdf` | 118,969 | `3705b36a3d0f7a1bf74214919229d9cfd6134b28dbd19832802f0ff8043d03e4` |
| `build/unit-033-final-n/unit-033-bab-4-grup-simetris.pdf` | 118,964 | `0af07d45c9aee57e28a6f27fe6162afda253e15c44779ccf07ac591516bd1f1d` |
| `artifacts/unit-033-bab-4-grup-simetris-id.pdf` | 118,964 | `0af07d45c9aee57e28a6f27fe6162afda253e15c44779ccf07ac591516bd1f1d` |

Build J and the artifact are byte-identical; all three PDFs contain 10 pages.

## Rendering gate

Poppler and MuPDF rendered all PDFs at 144 dpi (998 x 1418 pixels per page).
Equality is based on decoded RGB pixels.

- poppler build-i vs build-j: all 10 decoded-RGB pages are identical.
- poppler build-j vs artifact: all 10 decoded-RGB pages are identical.
- mupdf build-i vs build-j: all 10 decoded-RGB pages are identical.
- mupdf build-j vs artifact: all 10 decoded-RGB pages are identical.

All 60 renders have zero ink in the outer three-pixel band.

| Page | Poppler decoded-RGB SHA-256 | MuPDF decoded-RGB SHA-256 |
|---:|---|---|
| 1 | `90269f88f2e0a3b601f92fbae2e9fb2770989fb4c5baf20639c46a3620a38e31` | `f927e29708771ce923c0afdb0cdd20160ac7f409163a401395b5aca42e9dbd44` |
| 2 | `7e45d7364ac2c53458fa30a65a0a0302836869c2d0dc7db4dd96386593444cdd` | `094a1b813dafa03fe3672fc190b83f442325cefd098fba23220deaf5a06d11d3` |
| 3 | `cc30f1700fdd288176d1cfae2bffa6c4bf2a32b3709915ccd00a0bb0836a5db4` | `3738f8316fdc44ae2a76505e4267bd3c0b5d77ab537c8c4a70cca088b1f2961a` |
| 4 | `930f6acffe05604e8eda89374e7798bdeff1ae1d209c4d54e3044c119aa6b88f` | `5414310c83faffa66949ce8fde6ce0fef5862e4e03c2bedbce13a89c88eea0a6` |
| 5 | `07fb55e8a7126b53792b78833331b2a5e229a132b0c9a4c1f5d14444e66741f5` | `b787f2de5dcd2f910808565c9cc6af20baa41a1ebfb20357cc358c4cabaf00b2` |
| 6 | `2b1e377d467453ecb681b84adb5a555b8bcc5ad17e64edbfe3a17f5693ce683c` | `079666735ea76d721530fb4a98d24afda04cf085434296f3dfc72bfb25abf4da` |
| 7 | `28b825a18f2a9bdc33fe5ad403c56ca3e75faf662e668b2bf4d12051ed4a4b5e` | `f7d4846affccb24fd330e37e9102dd80386c5f45be3c23f66e9bf3de444ee735` |
| 8 | `f13f104e9c1f3562cbf1105637d896847e279d70226f17342951a2d38c99815e` | `1f8198b02b7743459fad873de9038dc919210ecb9fa2d037c386ea69fcb99bf2` |
| 9 | `c936735dc6f6627249da9be9a4593c822a2000de36b03f569709001653fdd791` | `dd3f311f1918bf658878e8f29d57f47d1269f9e3434bab93715410f6ec120cd1` |
| 10 | `02e2c9f4937abcddea72e2e6de9055eaab002552ee8840b329ce82c5a09e0bc8` | `02203905ac477048b4f199d7bc33344932caf484b1750f60ff7e21465cf123b2` |

## PDF and diagnostic gate

- PDF `%PDF-1.7`; `/Lang id-ID`; unencrypted; exact metadata and outline.
- All 35 named destinations resolve; action inventory is {'/URI': 3, '/GoTo': 22}.
- All 27 font objects are embedded; no active payload or unsafe action is present.
- Final diagnostics are zero for errors, unresolved references/citations, missing characters, empty targets, and overfull boxes. Exactly 1 nonfatal underfull hboxes remain and were visually inspected.

## Full-resolution visual review

Every page was inspected at full readability in both renderer outputs.

| Page | Finding |
|---:|---|
| 1 | Sampul terpusat dan memenuhi bidang baca; kotak cakupan, judul, kredit, tanggal, serta dua baris kata kunci terbaca utuh tanpa pemenggalan janggal. |
| 2 | Halaman atribusi, lisensi, identitas edisi, tautan, dan tanda CC tertata seimbang; tidak ada teks, glif, atau objek yang terpotong. |
| 3 | Pembukaan Bagian 4.9, definisi, proposisi, rumus, dan tanda akhir bukti memiliki margin, spasi, serta hierarki visual yang konsisten. |
| 4 | Uraian tipe siklus, konjugasi, pembangkit, dan homomorfisme tanda tetap terbaca meski padat; rumus dan rujukan tidak melampaui bidang teks. |
| 5 | Definisi grup selang-seling, daftar sifat, rumus kasus, pranala, dan simbol matematika tampil lengkap tanpa tumpang-tindih atau glif hilang. |
| 6 | Bukti kesederhanaan serta display subgrup Klein yang direflow terpusat dan tidak terpotong; perpindahan halaman mempertahankan alur kalimat. |
| 7 | Semua diagram kepang terbaca; kesamaan berlabel diluruskan kini terlihat, terpusat, dan identik secara semantik pada render Poppler serta MuPDF. |
| 8 | Presentasi grup kepang, diagram ujung, diagram komutatif, nomor persamaan, dan relasi pembangkit tersusun jelas tanpa overflow. |
| 9 | Relasi Coxeter, ikon kepang inline, rujukan silang, display pembuktian, dan tanda akhir bukti seluruhnya berada dalam margin dan terbaca jelas. |
| 10 | Daftar sifat penutup, indeks istilah, indeks simbol, dan nomor halaman tersaji utuh; ruang kosong bawah merupakan akhir bagian yang disengaja. |

The PDF is untagged, so no tagged-accessibility claim is made. Stable
mathematics-font extraction limitations, if any, are recorded in the JSON
evidence. Toolchain advisories are retained exactly as {'latex_release': 3, 'xecjk': 1, 'braids': 1, 'fontspec_cjk': 5}.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict:
**PASS WITH WARNINGS; zero actionable defects.**
