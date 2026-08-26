# Unit 031 visual and PDF QA — 2026-08-26

Status: **PASS WITH WARNINGS**. Exact identity, decoded-pixel, metadata,
navigation, font, extraction, action/link, geometry, diagnostics, and all-page
visual gates pass. No actionable defect remains.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
| `build/unit-031-clean-i/unit-031-bab-4-grup-solvabel-dan-nilpoten.pdf` | 126,051 | `9802661e5558d1879616703538f848a3091b668383fa2b0679c8913337566a43` |
| `build/unit-031-clean-j/unit-031-bab-4-grup-solvabel-dan-nilpoten.pdf` | 126,053 | `313667c3f87439ccaac3f8708653bb352af0ba7a16c9d09b159ad1b836cc32fb` |
| `artifacts/unit-031-bab-4-grup-solvabel-dan-nilpoten-id.pdf` | 126,053 | `313667c3f87439ccaac3f8708653bb352af0ba7a16c9d09b159ad1b836cc32fb` |
| `qa/UNIT_031_BUILD_FINAL.log` | 77,142 | `47dd6cc5677888afeee4b7e0e7fb4800f16790125746b0f32c9a40216a79a548` |

Build J and the release artifact are byte-identical. All three PDFs contain
9 pages.

## Rendering gate

Poppler and MuPDF rendered all PDFs at 144 dpi
(998 × 1418 pixels per page). Equality uses decoded RGB
pixels, not PNG compression.

- poppler build-i vs build-j: seluruh 9 halaman RGB terdekode identik.
- poppler build-j vs artifact: seluruh 9 halaman RGB terdekode identik.
- mupdf build-i vs build-j: seluruh 9 halaman RGB terdekode identik.
- mupdf build-j vs artifact: seluruh 9 halaman RGB terdekode identik.

All 54 renders have zero ink in their outer three-pixel band.
Six contact sheets and every render identity are recorded in
`qa/unit-031-evidence/render-hash-inventory.json`.

| Page | Poppler decoded-RGB SHA-256 | MuPDF decoded-RGB SHA-256 |
|---:|---|---|
| 1 | `df8cd0f70761e39bbb232079cf199a299b4edd5ab48fd179a324b2d7a446b2a6` | `dd554569658635c4ec997eeb212835cb03106645668e96316c76ee11618baa76` |
| 2 | `12a438711a9a29e4df40b4e76461d2d26f79f431d42b5330cd9b234bcdac5531` | `d9fdfe95166dcc17518a0bb301830021664b43b03e9c1511f335af75935a2502` |
| 3 | `8c265915a932cad2b98bbd4011cef129c87fb7ee7a2c87a1ceda82b64351b644` | `f9290b7f2679b08a6338e389baec6e7089e24059723d469734cdb3ff03307358` |
| 4 | `c4f7ef0370eb59b9fcb3fc844bb66786f46a12d24756984fd671ef82b964edfd` | `afd4e3eea6cd77b89de51ed8b41ec5969b6d9fab2175de350006ab1bbbea5d5c` |
| 5 | `2764cbd92be9e460c4295fb7c59bb20db98e9b2ada33ffb71410e878fe10bf15` | `988a2fa229263d7cfb8b42147d0384c1852066076a896e557c791bd3f6e3b28f` |
| 6 | `9adec2e950c92385d5649dacd07c1c779aa928c8c37f12c6da1c853cf4fd3b25` | `36d338d21496d6b992b04cb4ebc86a50f2a41705e99860a8b0796e4568cce0cc` |
| 7 | `3bb2e302735415a25f2aa84a6d5780bc07f043bf871ccca4d6fc1dc77e20d6e8` | `9eb53672e2a67ebdab1a380caf45cfb80beed771e9f9794b99588d286b7f7668` |
| 8 | `9e6e012be071b16b83e387b91f0a544c1b234aa0f3f8bad80840fb144e7ca4cc` | `c175e37da41d6b33edaba1d34e16bea1d0346889dd80a8f06c5bdaba3192c891` |
| 9 | `f9b7b21a4110bf5ed64a35d7f77e7d36b3cc1ccd22861a5f3ac81d0189f8a19f` | `8559357165a87fa1afb4bed2c8917bf72a6968c072d48925378279f19e99942b` |

## PDF and diagnostic gate

- PDF `%PDF-1.7`; `/Lang id-ID`; 9 pages; unencrypted;
  exact metadata; no form, JavaScript, additional action, or embedded file.
- The outline has 4 entries and all
  37 named destinations resolve.
- Action inventory is exact: {'/GoTo': 14, '/URI': 3}. Every `/GoTo` closes
  over the destination inventory and every URI is HTTPS.
- Link rectangles and MuPDF text blocks are in bounds. All
  29 pypdf font objects and
  29 `pdffonts` rows are embedded.
- pypdf, Poppler layout text, and MuPDF text agree independently across both
  builds and the artifact. No extractor contains a replacement character;
  Poppler and MuPDF contain no NUL, while pypdf has the exact stable count of
  17 from unmapped mathematics-font glyphs disclosed in the JSON evidence.
- The final log is byte-reproduced from the build-J log after path
  sanitization. Fatal/error, unresolved reference/citation, missing-character,
  empty-target, overfull, and underfull diagnostics are all zero.

## Full-resolution visual review

Every page was inspected at full readability in both renderer outputs.

| Page | Finding |
|---:|---|
| 1 | Hierarki judul dan subjudul terpusat; panel cakupan berupa prosa eksplisit, terbaca jelas, dan bukan blok kemajuan terisi/kosong yang ambigu. |
| 2 | Identitas edisi dan sumber, hak, non-endorsement, provenance model, tautan, dan ikon CC seluruhnya terbaca, berada dalam batas halaman, dan tidak bertabrakan. |
| 3 | Judul Bagian 4.7, definisi awal, daftar, rumus komutator, serta kedua diagram kurung deret tersusun jelas tanpa tumpang tindih. |
| 4 | Diagram abelianisasi, lema, rujukan, teks pembuktian, dan tanda akhir bukti tetap tajam serta memiliki jarak yang aman. |
| 5 | Lema dan pembuktian yang padat, perbaikan pembuktian yang dinyatakan, serta deret-deret tampil utuh tanpa orphan, tabrakan, atau tepi terpotong. |
| 6 | Sitasi Feit--Thompson, kedua tampilan matriks segitiga, rumus ruang vektor, dan prosa sekelilingnya mengalir alami dalam lebar teks. |
| 7 | Tampilan empat suku yang diperbaiki seimbang dalam dua baris; tanda sama dengan, seluruh tanda tambah, dan keempat suku utuh, sementara rumus sejajar berikutnya tetap muat. |
| 8 | Deret sentral menaik, bukti p-grup, konstruksi Heisenberg, dan semua tampilan matematis terbaca jelas dengan margin aman. |
| 9 | Rumus penutup, bibliografi, indeks istilah enam entri, dan indeks simbol tiga entri terbaca pada satu halaman yang terisi wajar tanpa halaman kesepuluh yang jarang. |

No clipping, overlap, edge contact, broken glyph, unresolved reference,
unreadable formula, overfull/underfull residue, or unintended blank page remains.

## Disclosed warnings

The PDF is untagged, so no tagged-accessibility claim is made. pypdf exposes
17 stable NUL placeholders for unmapped mathematics-font glyphs; Poppler and
MuPDF expose none, all extractors have zero replacement characters, and both
renderers visibly reproduce the affected mathematics. Fixed toolchain
advisories are recorded exactly as {'latex_release': 3, 'xecjk': 1, 'braids': 1, 'fontspec_cjk': 6}; they do not concern
content, references, glyphs, or page layout. Build I and J may differ in
volatile font-subset tags, but normalized structure, extraction, and
same-renderer decoded pixels agree; build J and the artifact are byte-identical.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict:
**PASS WITH WARNINGS; zero actionable defects.**
