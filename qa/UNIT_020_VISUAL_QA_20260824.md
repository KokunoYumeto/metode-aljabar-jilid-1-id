# Unit 020 visual/PDF QA — 2026-08-24

**Verdict: PASS.** The frozen final PDFs are structurally and semantically equivalent and produce page-identical output within each renderer. All five pages pass visual inspection in both Poppler and MuPDF.

## Exact inputs

- `build/unit-020-final-e/unit-020-bab-3-keketatan-dan-teorema-koherensi.pdf` — 93,054 bytes; SHA-256 `e3f7f2b1ae8da6dea90f10a62cd1b9b0d272b2b4f0b386bb7eafc765a40e8057`.
- `build/unit-020-final-f/unit-020-bab-3-keketatan-dan-teorema-koherensi.pdf` — 93,053 bytes; SHA-256 `8d8a7c8f537681525d97952a7f163f95a5063275047989c26f0387f50172e1ed`.

Both are PDF 1.7, unencrypted, five pages, and 498.9 × 708.66 pt. Their metadata, page boxes, page labels (`1, 2, 1, 2, 3`), content streams, outlines, destinations, links, and extracted text are identical. Their shared aggregate page-content-stream SHA-256 is `8963a75d1994cdca6551b39af26788542d96bd14360bd826802b4226885877ae`.

## Rendering and visual inspection

- Every page was rendered at 144 dpi with Poppler 24.04.0 and MuPDF 1.23.0, twice per PDF and renderer: 40 page PNGs total. Eight contact sheets cover all renderer/build combinations.
- All four within-renderer replay comparisons and both cross-build comparisons are decoded-pixel-identical and PNG-byte-identical on every page. Poppler aggregate raw-RGB/PNG-set hashes are `dc69de2b1916491fc1eafc599e3f13488b68d7f343b5d1a69174a0034426ca4a` / `5f198ac6bd5d4a05fd7c5a4495eb309ad0f07d08e3b0fce13556ddb0752bcec8`; MuPDF hashes are `b25d4735ac29bac8145fac411a682dc95d81a435b97ad7b933b8553699568f64` / `2fb749c6e322e9ee62f4edbcb4aac58aa12ac57e68da7acea224104bf22a5578`.
- All pages were inspected for clipping, overlap, missing/tofu glyphs, sparse or off-center composition, broken diagrams/arrows, bad pagination, and blank versos. No defect was found. No render has ink in its outer three-pixel border, and no extracted text box leaves the page bounds.
- The centered cover states the partial Chapter 3 scope explicitly without ambiguous progress blocks. The content begins with the canonical heading `3.2 Keketatan dan Teorema Koherensi`. The pentagonal coherence diagram and naturality square on page 4 are intact and legible.
- Final page 5 cleanly combines the section conclusion, three-entry bibliography, and two-entry term index. The local reflow eliminates the orphaned/sparse generated index page while preserving legible typography and balanced remaining white space.

## PDF structure and text

- Each PDF has four valid outline entries: Chapter 3, §3.2, bibliography, and term index. There are 21 named destinations and 14 valid links (10 internal/named and four URI); no invalid target was found.
- The catalog open action is a direct initial-view destination. There are no additional actions, JavaScript name trees, embedded files, forms, encryption, or strict-reader warnings. All 24 fonts are embedded and subset. The PDF declares `id-ID`, every page contains extractable text, and the untagged state is reported honestly.
- PyPDF, PyMuPDF, pdfplumber-layout, and Poppler-layout extraction are identical between final builds. Their SHA-256 hashes are `799b60200e582386434a55482b79142df3fd0ddb74506e94bd59252b6c4f3715`, `18b07968764adc422660087758bb5ac91e3b3193150689b115882443a116ae42`, `812d8b892abee8251a79ebaf6359d4dc7cd47fa45f7ce6e576aa6fe557130151`, and `d6ca72827bf0754f1ddb7c085ec3d25e00d23cf4ffee9b158b925799448b26e7`.
- Across all extraction outputs: zero unresolved reference/template/editor tokens, replacement characters, NULs, or unexpected control characters.

## Evidence

Machine-readable visual evidence is `build/unit-020-visual-qa/qa-manifest.json` — 94,395 bytes; SHA-256 `47591ec00e8452c2f40a99ea631e7ff3d12e48bf7a6caaa993cc35807d7a6956`. Admission-oriented evidence is `qa/unit-020-evidence/structure-and-pdf-qa.json` — 9,044 bytes; SHA-256 `26c1a5c433f519afd10b0bc1b378d81b8d6bb1791c91fc3816f151015adaa9b1`. Its bounded render inventory hash-binds five admitted Poppler PNGs and five admitted MuPDF PNGs stored under `qa/unit-020-evidence/{poppler,mupdf}-final-f/`.
