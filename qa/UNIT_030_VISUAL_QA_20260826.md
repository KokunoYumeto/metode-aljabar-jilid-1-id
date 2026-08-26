# Unit 030 visual and PDF QA — 2026-08-25

Status: **PASS WITH WARNINGS**. No actionable defect was found. Exact identity, same-renderer decoded-pixel, structure, metadata, navigation, font, text, action/link, clipping, and final-build-log gates pass.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
| `build/unit-030-clean-i/unit-030-bab-4-deret-komposisi-grup.pdf` | 91,960 | `cb5b2c5279e7c5574457846873a456cb644d2a1d54ace7ddc975378e036e00cd` |
| `build/unit-030-clean-j/unit-030-bab-4-deret-komposisi-grup.pdf` | 91,961 | `43ad2ffa2516f2f4394bcb82ad2e585f21c1e9e36a87870f4406a78597f18d74` |
| `artifacts/unit-030-bab-4-deret-komposisi-grup-id.pdf` | 91,961 | `43ad2ffa2516f2f4394bcb82ad2e585f21c1e9e36a87870f4406a78597f18d74` |
| `qa/UNIT_030_BUILD_FINAL.log` | 76,370 | `728d7f4f2845e87132e6bf494784a16eced1b9f9f2644f97a10ae477a9df43f9` |

Build J and the final artifact are byte-identical. All three PDFs have seven pages.

## Rendering gate

Poppler and MuPDF rendered every PDF at 144 dpi (998 × 1418 pixels per page). Equality uses decoded RGB pixels rather than PNG compression.

- poppler build-i vs build-j: ketujuh halaman RGB terdekode identik.
- poppler build-j vs artifact: ketujuh halaman RGB terdekode identik.
- mupdf build-i vs build-j: ketujuh halaman RGB terdekode identik.
- mupdf build-j vs artifact: ketujuh halaman RGB terdekode identik.

All 42 renders have zero ink pixels in their outer three-pixel band. Six contact sheets and every PNG/decoded-pixel identity are recorded in `qa/unit-030-evidence/render-hash-inventory.json`.

| Page | Poppler decoded-RGB SHA-256 | MuPDF decoded-RGB SHA-256 |
|---:|---|---|
| 1 | `7154a9f72e9fa29c6168ec2195461af4fded233d5c9ee605fc7df97bc5d7309f` | `a2976583ff0620442d3f334506b869f831938d1d57da7a37179c63fadac0ad7c` |
| 2 | `fe1cf0a92c60b6624fefcc7710de29c6343602de9c516825e4ed95be77b2ba17` | `91f89455b14b7f1d29940fc3e1d12ee8e449ce43774e5e258e39fd75ead94d70` |
| 3 | `f2bd25610007f2e499970224c05241482a0269ceb95f0f00b0c8c98faed0674b` | `174dadfaf627325831bdb534d768a05e19b479076c3d66cf861eeb471f55866b` |
| 4 | `bbda4031df668cb9bce1c29fc712ff22caddf8f211831bec4c53afa1243e2a97` | `9d8c4a3827ee5ee7d4e81c3a534b2cc6aca8b9c698b2fb815151b7496134ee63` |
| 5 | `2d582735d436dcffc5b465f3b530f2e5527b208f544c70a726fa7fdbdcd14c33` | `aaefb29e7713c572749cd8d830130a61336474dc0f581528baf928bf6e9b9cd8` |
| 6 | `73b8dfc8ab203c0f4f1f2d9d11fbb9caf2a61abdac33684ae01b3003ef2d5c08` | `026913ef91a678f7aa088836cb5fdd7e75d176c6b478ae7017e7e7dff3e73bc5` |
| 7 | `fd5fea524574c3c2182dbbfbd8aa4e747a4d0637c6458acc20c51579fb2c91a4` | `27610ccfe39f6f688565c2e7cabf5452d1393eaf19fd66d949c4752b9d89cc85` |

## PDF gate

- PDF `%PDF-1.7`; `/Lang id-ID`; seven pages; unencrypted; exact metadata; no form, JavaScript, additional action, or embedded file.
- The three-entry outline resolves to Section 4.6 on page 3, with the bibliography and term index both on page 7. All 25 named destinations resolve.
- All eleven `/GoTo` actions close over the destination inventory; all three `/URI` actions use HTTPS. `/OpenAction` is a safe direct page destination.
- Link rectangles and MuPDF text blocks are in bounds. All 21 pypdf font objects and 21 `pdffonts` rows are embedded.
- pypdf, Poppler layout text, and MuPDF text hashes match separately across I, J, and artifact. There are no replacement characters or NULs in any extractor.
- The published final log is a byte-verified sanitizer replay of build J: 252 local MiKTeX prefixes map to `<MIKTEX_ROOT>`, 0 wrapped absolute build prefixes map to `build\unit-030-clean-j`, all 2269 line records are preserved, and Windows user-path/profile-name occurrences are both zero.

## Independent full-resolution review

All pages were reviewed in Poppler and MuPDF. The body uses the centered 142 mm text block and fills pages naturally; the cover uses one prose scope panel, not an ambiguous alternating filled/unfilled progress-block system.

| Page | Finding |
|---:|---|
| 1 | Hierarki sampul, judul Unit 30, panel ruang lingkup, tanggal, dan margin seimbang serta mudah dibaca. |
| 2 | Atribusi edisi dan sumber, ISBN, lisensi, non-endorsement, provenance model, tautan, dan lencana CC tampil utuh tanpa tabrakan. |
| 3 | Judul Bagian 4.6 serta definisi deret normal, sentral, dan komposisi tersusun jelas dengan lebar teks terpusat. |
| 4 | Lema Zassenhaus dan keenam diagram tikzcd terbaca jelas; label subgrup dan subgrup normal terlokalisasi tanpa merusak topologi. |
| 5 | Teorema Penghalusan Schreier, relasi Jordan--Hölder, dan rumus-rumus terkait mengalir alami; kotak teorema dan rujukan tidak terpotong. |
| 6 | Bukti faktor komposisi grup abelian, daftar pustaka kosong yang dinyatakan, dan indeks istilah run-in mengisi halaman akhir secara alami dengan margin aman. |
| 7 | Halaman indeks dan penutup tetap memiliki margin bawah aman; tidak ada ruang kosong yang mengganggu atau elemen yang terpotong. |

No clipping, overflow, collision, broken mathematical stroke, missing label, tofu box, unintended sparse page, ambiguous progress block, or edge contact was found.

## Warnings

1. `/Lang id-ID` is correct, but the PDF is untagged; no tagged-accessibility claim is made.
2. dvipdfmx assigns volatile six-letter subset tags, so builds I and J are not byte-identical. Their normalized structures, three text surfaces, and all same-renderer decoded pixels agree; build J and the artifact are byte-identical.
3. The final log has 3 LaTeX release warnings, 1 xeCJK warning, 1 frozen `braids` warning, 5 fontspec CJK advisories, one visually benign underfull hbox (badness 10000), and four visually benign underfull vboxes (badness values [10000, 10000, 10000, 4913]). Fatal/error, unresolved-reference/citation, missing-character, and overfull diagnostics are zero.
4. All embedded fonts have complete extraction maps for this unit; pypdf, Poppler, and MuPDF report no NUL or replacement characters.
5. Poppler reports the absent optional Adobe-GB1 language pack and dependent F37/show-space diagnostics during layout-text extraction. The extracted text has no replacement characters or NULs, and both renderers visibly reproduce every page.

Evidence: `structure-and-pdf-qa.json` records exact structures, metadata, destinations, actions, fonts, text hashes, geometry, and final-log checks. `render-hash-inventory.json` records all 42 render identities, comparisons, edge results, and six contact-sheet identities.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict: **PASS WITH WARNINGS; zero actionable defects.**
