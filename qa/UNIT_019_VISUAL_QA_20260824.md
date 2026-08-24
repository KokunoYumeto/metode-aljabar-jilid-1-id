# Unit 019 visual/PDF QA — 2026-08-24

**Verdict: PASS.** The frozen final PDFs are structurally and semantically equivalent and produce page-identical output within each renderer. All 12 pages pass visual inspection in both Poppler and MuPDF.

## Exact inputs

- `build/unit-019-final-c/unit-019-bab-3-definisi-dasar.pdf` — 125,698 bytes; SHA-256 `c4904fb64633a24476225f461bf2e09bcb1d92a0a13fc5d836ad1e6dfad5b1ac`.
- `build/unit-019-final-d/unit-019-bab-3-definisi-dasar.pdf` — 125,710 bytes; SHA-256 `af7a4561db5e8ab1798d4475c589beb42f9fb84795bd167c0ffc17241866783a`.

Both are PDF 1.7, unencrypted, 12 pages, 498.9 × 708.66 pt, with identical metadata, page boxes, labels (`1, 2, 1…10`), page content streams, outlines, destinations, links, and extracted text. Their shared aggregate page-content-stream SHA-256 is `7bd94af665d24015dd768b8e6c509bceaaa5f947b1c2af9a4ed57f01fa34f1ed`.

## Rendering and visual inspection

- Rendered every page at 144 dpi with Poppler 24.04.0 and MuPDF 1.23.0, twice per PDF and renderer: 96 page PNGs total. Exact render hierarchy: `build/unit-019-visual-qa/{poppler,mupdf}/{final-c,final-d}/run-{1,2}/page-XX.png`. Twelve contact sheets cover all render/build combinations.
- All four within-renderer replay comparisons are decoded-pixel-identical and PNG-byte-identical on all 12 pages. Poppler aggregate raw-RGB/PNG-set hashes are `fefafe3e7d4c189046f8ae535f88099d98de821b84a3e93cac69cf3cbb4299dd` / `f0c7f9e50f61fbf4d25af9f0f7dd889e18076beff9fa073580b2aa5fb5216742`; MuPDF hashes are `5c459edfc17f6e256c7593cb0a746c240ce2a3a83da8e8abbde907e97b2e77de` / `f2a92531e771b2c0415a71753bc980611c396bc946d35242f7c075acafb900f0`.
- Final C and Final D are pixel-identical and PNG-byte-identical page-for-page in each renderer. Cross-renderer differences are normal antialiasing/rasterization differences; geometry is identical at 998 × 1418 px and both renderers show the same content.
- All pages were inspected for clipping, overlap, missing/tofu glyphs, sparse or off-center composition, broken diagrams/arrows, bad pagination, and blank versos. No defect was found. No page has ink in the outer 3-pixel border, and no extracted text box leaves the page bounds.
- Final page 12 legibly and cleanly combines `Daftar Pustaka`, the two-column `Indeks Istilah`, and the one-entry `Indeks Simbol`. Headings, entries, links, column spacing, and remaining white space are balanced; there is no orphaned or print-style blank page. All diagrams and equation labels on pages 5–10 are intact and legible.

## PDF structure and text

- Each PDF has five valid outline entries: chapter 3, §3.1, bibliography, term index, and symbol index. All three back-matter entries target physical page 12. There are 52 named destinations and 38 valid links (35 internal/named and 3 URI); no invalid target was found.
- The catalog open action is a direct initial-view destination. There are no additional actions, JavaScript name trees, embedded files, forms, encryption, or strict-reader warnings. `pdfinfo`, `pdffonts`, `pdfimages`, and `mutool info` all return success with empty stderr.
- PyPDF, PyMuPDF, pdfplumber-layout, and Poppler-layout extraction are identical between final builds. Their respective SHA-256 hashes are `383d5a86b0c2705a00b1e3f28a6a778fa94af945c512e6b7a89ef93dabc1611a`, `762ad122f154c510ebb67dc935335160af04904f2f3e47af1cb0d4ee0d1fad35`, `c1aa43a91b4c200a962bdd6ee745722c55514dd3ca84e747838fb2a71f53649e`, and `a835887e63a0f578a80d092fad2291d397dec52e1ef5efabbd60d76b6cb6d8a5`.
- Across all eight extraction outputs: zero unresolved-reference/template/editor tokens, zero replacement characters, zero NULs, and zero unexpected control characters. Every page contains extractable text.

## Evidence

Machine-readable evidence is in `build/unit-019-visual-qa/qa-manifest.json` — 174,639 bytes; SHA-256 `9f0d571d88ae0a0d66b64b192b8106cc7fa6f9880407554c20c2b06f952d8aa5`. The bounded evidence directory contains 96 page renders, 12 contact sheets, eight text extractions, the manifest, and the reproducible probe script.
