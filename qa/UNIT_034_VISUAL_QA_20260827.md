# Unit 034 visual and PDF QA - 2026-08-27

Status: **PASS WITH WARNINGS**. Exact identity, two-engine decoded-pixel,
metadata, navigation, font, extraction, action/link, geometry, diagnostics,
and all-page visual gates pass. No actionable defect remains.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
| `build/unit-034-final-i/unit-034-bab-4-limit-dan-kompletisasi-grup.pdf` | 136,700 | `970402b3ab3e510c2f72c44723528616eb3456020433ed9cf7b7cce2d56ce83a` |
| `build/unit-034-final-j/unit-034-bab-4-limit-dan-kompletisasi-grup.pdf` | 136,702 | `e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272` |
| `artifacts/unit-034-bab-4-limit-dan-kompletisasi-grup-id.pdf` | 136,702 | `e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272` |

Build J and the artifact are byte-identical; all three PDFs contain 9 pages.

## Rendering gate

Poppler and MuPDF rendered all PDFs at 144 dpi (998 x 1418 pixels per page).
Equality is based on decoded RGB pixels.

- poppler build-i vs build-j: all 9 decoded-RGB pages are identical.
- poppler build-j vs artifact: all 9 decoded-RGB pages are identical.
- mupdf build-i vs build-j: all 9 decoded-RGB pages are identical.
- mupdf build-j vs artifact: all 9 decoded-RGB pages are identical.

All 54 renders have zero ink in the outer three-pixel band.

| Page | Poppler decoded-RGB SHA-256 | MuPDF decoded-RGB SHA-256 |
|---:|---|---|
| 1 | `33f863388bb3e29ec9b91d6d7b973145c438b8fd6e8811a574a519a9c83b914c` | `eb69f5e18f01b3b97eedd0cd4518294fa9693c5b49a35cec86722f35c679358e` |
| 2 | `62aa420e63c173d84324a1213f09319510c56fcc325aaae8dada37787ab216ca` | `13ac62b7b818de321e2d36e109cabc12f04c640fe8dec404eb5efbc6ea781300` |
| 3 | `fb5f7ec889028693b7c07ded885c3ea90ab604e39dde5c99f989e560ef62f5e3` | `a11270ea6eebbb0bb93e2e5306662c9483cdc1fdd8ccef9e8dcc0a25e744fa3d` |
| 4 | `e4c1e26169a6ccd4bff4c650a00b1cad88ef40a489c6e422c360a92990edeb00` | `1c006bfc01e0f672931b4cfcaef549cd5e96ba91e00a90fbeefad387a4b03a75` |
| 5 | `027bbf9d332b187160a150985a1a55c5986a934deea9fee4a978fd7e3bef6c93` | `7fc5df7ad15525c81ad2e01e937ebb4c872a1e50f06f8beadfe44d63d4fed441` |
| 6 | `aa76f754ce8384021ec164199f243ba0d379d4e892f0eeb56819b970659bba1e` | `8668474896bbedc211c25183ea1099a30d65ed6d2320f1912e47ca5e3ba92a91` |
| 7 | `da14bff62334d8d5d354edb1ffd7f7fee11261161b29db9df614514be0d5feb5` | `fc322b7fc7b3dd16c84033ddb235a55bb72bb9a3ca744ef85f6261bdcbb7a64f` |
| 8 | `0dbe86c2d66e9f88217494e0334bd748ca8d32d5f5b1c076811f62ffe91045d5` | `3bd038a814103f03f7bb70dc52579663edfa21100c256ef8eed1b1338f28ed23` |
| 9 | `03ee43a88e0d065dd4c01fa462893bd356e5a12b86c70c44db5ef0f1e71f7caa` | `2fbd6e83abbfcbe563cff16dddd5e94f2a05bd9474a2dc210d3602503b91f5aa` |

## PDF and diagnostic gate

- PDF `%PDF-1.7`; `/Lang id-ID`; unencrypted; exact metadata and outline.
- All 39 named destinations resolve; action inventory is {'/URI': 5, '/GoTo': 20}.
- All 31 font objects are embedded; no active payload or unsafe action is present.
- Final diagnostics are zero for errors, unresolved references/citations, missing characters, empty targets, and overfull boxes. Exactly 0 nonfatal underfull hboxes remain and were visually inspected.

## Full-resolution visual review

Every page was inspected at full readability in both renderer outputs.

| Page | Finding |
|---:|---|
| 1 | Sampul terpusat dan memenuhi bidang baca; judul Pelengkapan Grup, kotak cakupan, kredit, tanggal, dan kata kunci terbaca utuh. |
| 2 | Halaman atribusi, lisensi, identitas edisi, tautan CC BY dan CTAN/Fandol, serta tanda CC tertata seimbang tanpa teks atau objek terpotong; pemberitahuan GPLv3 dengan pengecualian fon terbaca utuh pada kedua renderer. |
| 3 | Pembukaan Bagian 4.10, konstruksi limit proyektif, definisi grup topologis, rumus, dan rujukan tampil lengkap dalam margin. |
| 4 | Kriteria Hausdorff, bukti, diagram lingkungan, dan Lema 4.10.3 terbaca jelas tanpa tumpang-tindih atau glif hilang. |
| 5 | Display basis lingkungan yang direflow menjadi tiga baris terpusat, tidak meluber, dan identik secara semantik pada kedua renderer. |
| 6 | Sifat universal, definisi pelengkapan grup, barisan Cauchy, serta daftar kondisi tertata jelas dan mempertahankan hierarki visual. |
| 7 | Teorema pelengkapan, bukti, catatan, contoh bilangan bulat p-adik, dan awal modul Tate terbaca utuh tanpa pemenggalan janggal. |
| 8 | Konstruksi modul Tate, diagram komutatif, contoh kurva eliptik, dan awal daftar pustaka berada dalam margin dan tetap tajam. |
| 9 | Daftar pustaka, indeks istilah, indeks simbol, pranala, dan nomor halaman tersaji utuh; ruang kosong bawah merupakan akhir unit yang disengaja. |

The PDF is untagged, so no tagged-accessibility claim is made. Stable
mathematics-font extraction limitations, if any, are recorded in the JSON
evidence. Toolchain advisories are retained exactly as {'latex_release': 3, 'xecjk': 1, 'braids': 1, 'fontspec_cjk': 6}.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict:
**PASS WITH WARNINGS; zero actionable defects.**
