# Unit 029 visual and PDF QA — 2026-08-25

Status: **PASS WITH WARNINGS**. No actionable defect was found. Exact identity, same-renderer decoded-pixel, structure, metadata, navigation, font, text, action/link, clipping, and final-build-log gates pass.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
| `build/unit-029-clean-i/unit-029-bab-4-teorema-sylow.pdf` | 99,695 | `5f9ae471aa1e20598d48bd5705ae0f89ed911304f5f89da30136d975240aafe1` |
| `build/unit-029-clean-j/unit-029-bab-4-teorema-sylow.pdf` | 99,689 | `64fde52948525fc5b159f76fbed6571c150e4184a87e47e715164aec135e5012` |
| `artifacts/unit-029-bab-4-teorema-sylow-id.pdf` | 99,689 | `64fde52948525fc5b159f76fbed6571c150e4184a87e47e715164aec135e5012` |
| `qa/UNIT_029_BUILD_FINAL.log` | 77,013 | `606a707d5aad534f58af25333f3fbffe964ab7c7f1a260b3ffe9c1f1bce8364e` |

Build J and the final artifact are byte-identical. All three PDFs have six pages.

## Rendering gate

Poppler and MuPDF rendered every PDF at 144 dpi (998 × 1418 pixels per page). Equality uses decoded RGB pixels rather than PNG compression.

- poppler build-i vs build-j: keenam halaman RGB terdekode identik.
- poppler build-j vs artifact: keenam halaman RGB terdekode identik.
- mupdf build-i vs build-j: keenam halaman RGB terdekode identik.
- mupdf build-j vs artifact: keenam halaman RGB terdekode identik.

All 36 renders have zero ink pixels in their outer three-pixel band. Six contact sheets and every PNG/decoded-pixel identity are recorded in `qa/unit-029-evidence/render-hash-inventory.json`.

| Page | Poppler decoded-RGB SHA-256 | MuPDF decoded-RGB SHA-256 |
|---:|---|---|
| 1 | `b3483d386ffe03092dc5a56ac618aa2900f20e86e4c4d5f83d3378ef4d624438` | `49aa68ea1db7baba1b0397414068aee8c0111807ac495b98775743074f512c00` |
| 2 | `727720e702c0c381ec84445c8c7b5e7cbac6ec8a08abbd87835b421dd79ad73a` | `62b31cf5fa50811dc364ae9575156725d0c162372b0fc4254a6f9c6f5adb71ed` |
| 3 | `8753ac1b2370e6f85d59fce0ef24cd1fc4a34bfd8f56e940a24eac5bbd5b9897` | `2c4df7105b47d904c2bee607cd0a8565a32b5cb8ec53cf04b6ea5d5b52132501` |
| 4 | `1551165e4f49ed8ee918c01e93d62360251648e593fac602f56c32b1e64d34d0` | `08135873f01e86d57932f6660a343a0339e3e52014b469d6ec6a03325c0b39d7` |
| 5 | `3ee68c5fd8de01c549cca0d0f55d32ee97b59c0baf17d797e7c1a06b411ba487` | `421636c49c430c552980bb000b2cd1d0997fde15ad79bf6276086afd7988cb3e` |
| 6 | `1c948b7528ee1834b473c556d85892daa5e307674da0817b18ea775347c8681e` | `cf89de33e7d9d81aa1e427c2ac5abc288af5e8bb4b89cbbb9fa8f5a12b7d94aa` |

## PDF gate

- PDF `%PDF-1.7`; `/Lang id-ID`; six pages; unencrypted; exact metadata; no form, JavaScript, additional action, or embedded file.
- The three-entry outline resolves to Section 4.5 on page 3, with the bibliography and term index both on page 6. All 36 named destinations resolve.
- All nine `/GoTo` actions close over the destination inventory; all five `/URI` actions use HTTPS. `/OpenAction` is a safe direct page destination.
- Link rectangles and MuPDF text blocks are in bounds. All 25 pypdf font objects and 25 `pdffonts` rows are embedded.
- pypdf, Poppler layout text, and MuPDF text hashes match separately across I, J, and artifact. There are no replacement characters; Poppler has no NULs, while pypdf has four and MuPDF one at stable mathematics-font loci without complete Unicode maps.
- The published final log is a byte-verified sanitizer replay of build J: 252 local MiKTeX prefixes map to `<MIKTEX_ROOT>`, 8 wrapped absolute build prefixes map to `build\unit-029-clean-j`, all 2276 line records are preserved, and Windows user-path/profile-name occurrences are both zero.

## Independent full-resolution review

All pages were reviewed in Poppler and MuPDF. The body uses the centered 142 mm text block and fills pages naturally; the cover uses one prose scope panel, not an ambiguous alternating filled/unfilled progress-block system.

| Page | Finding |
|---:|---|
| 1 | Hierarki sampul, judul Unit 29, panel ruang lingkup, tanggal, dan margin seimbang serta mudah dibaca. |
| 2 | Atribusi edisi dan sumber, ISBN, lisensi, non-endorsement, provenance model, tautan, dan lencana CC tampil utuh tanpa tabrakan. |
| 3 | Judul Bagian 4.5, definisi p-grup dan subgrup Sylow, Teorema Cauchy, serta rumus binomial tersusun jelas dengan lebar teks terpusat. |
| 4 | Bukti dengan aksi grup, normalizer, dan hasil-hasil antara mengalir alami; kotak teorema, simbol, dan rujukan tidak terpotong. |
| 5 | Tiga Teorema Sylow dan argumen konjugasi terbaca jelas; tampilan matematika terpusat dan tidak melampaui area hidup. |
| 6 | Bagian akhir bukti, sitasi, daftar pustaka, dan indeks istilah run-in mengisi halaman secara alami; kedua entri indeks terbaca dan margin bawah tetap aman. |

No clipping, overflow, collision, broken mathematical stroke, missing label, tofu box, unintended sparse page, ambiguous progress block, or edge contact was found.

## Warnings

1. `/Lang id-ID` is correct, but the PDF is untagged; no tagged-accessibility claim is made.
2. dvipdfmx assigns volatile six-letter subset tags, so builds I and J are not byte-identical. Their normalized structures, three text surfaces, and all same-renderer decoded pixels agree; build J and the artifact are byte-identical.
3. The final log has 3 LaTeX release warnings, 1 xeCJK warning, 1 frozen `braids` warning, 6 fontspec CJK advisories, one visually benign underfull hbox (badness 10000), and one visually benign underfull vbox (badness 1515). Fatal/error, unresolved-reference/citation, missing-character, and overfull diagnostics are zero.
4. Two mathematics fonts lack complete Unicode maps. The stable pypdf/MuPDF NUL census is disclosed; Poppler extraction and visible rendering pass.
5. Poppler reports the absent optional Adobe-GB1 language pack and dependent F37/show-space diagnostics during layout-text extraction. The extracted text has no replacement characters or NULs, and both renderers visibly reproduce every page.

Evidence: `structure-and-pdf-qa.json` records exact structures, metadata, destinations, actions, fonts, text hashes, geometry, and final-log checks. `render-hash-inventory.json` records all 36 render identities, comparisons, edge results, and six contact-sheet identities.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict: **PASS WITH WARNINGS; zero actionable defects.**
