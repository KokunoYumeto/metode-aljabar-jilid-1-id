# Unit 022 visual/PDF QA — 2026-08-24

**Verdict: PASS.** Unit 022 is a self-contained nine-page `id-ID` reader for
the complete Section 3.4, *Kategori Diperkaya*. The installed artifact is
byte-identical to clean build F. Clean builds E and F and a fresh scripted
replay have different PDF-container bytes but identical extracted content and
page-identical output within both Poppler and MuPDF. Every page was inspected
in both renderer families. This boundary performs no Git or publication action.

## Exact source boundary and reader closure

- Canonical `repo/source/chapter3.tex` — 86,033 bytes; SHA-256
  `b395e1014becb462dae95eda5fde37da9b4edd0b477df8f0b5cefef43edbefa2`;
  910 LF records.
- Canonical lines 512–721 — 210 LF records, 17,541 bytes; SHA-256
  `e1fa8da94c0c2431660f690aa9b2193e3c966e2d71b9d5a029da12a76bc0e255`.
  This is the complete Section 3.4 plus its terminating blank record. Line 722
  begins the excluded Section 3.5 and has SHA-256
  `26cf19a66c488255e23a0fa8774aca285f48b9049a6111bf2c6fe8d746bdced7`.
- The driver loads `chapter3.tex` lines 512–721 directly. Neither the driver nor
  `scripts/build_unit_022.ps1` mentions or depends on the isolated candidate;
  the candidate is retained only as a byte-identity review witness.
- Driver — 5,786 bytes; SHA-256
  `86a6d37846d21d06932f90dd09b202afdb2d6e29aa9e9b0453f0eb66a532c97d`.
  Cover — 3,620 bytes; SHA-256
  `1f19df06c7d317b4804caafbfc7a5c7dd7a535f8e8be3f110bccb7899d107ac4`.
  Minimal cross-reference AUX — 613 bytes; SHA-256
  `53b87b5f35aa1a0ae2988e9a4d6ca154391e9a51fbb299f4040db1befbe53625`.
  Build script — 4,803 bytes; SHA-256
  `33c46a2c59b0e02e4745863cc9a7e7425a0947bb5b669dda8652cf9898956aad`.

The isolated span has eleven local labels, fifteen reference occurrences, two
citations, ten index entries, three `tikzpicture` and six `tikzcd` environments.
The nine genuinely external labels are closed with printed-number-only stubs:
`def:category` 2.1.1, `con:U-small` 2.1.4, `eg:categories` 2.1.5,
`def:universal-objects` 2.4.1, `def:zero-morphism` 2.4.3, `sec:limits`
2.7, `prop:product-associativity` 2.7.11, `eg:monoidal-cat` 3.1.3,
and `prop:Mod-cat-additive` 6.2.4. Their empty cross-document targets
deliberately prevent false links. The bibliography closes `Ke05` and `May99`
as G. M. Kelly and J. P. May respectively.

## Builds, reflow, and visual inspection

- Clean E — 117,921 bytes; SHA-256
  `97492ad2ca5ce180add809d5a88b6263d7e7ebfc3a51cbb71b3e51e558f03494`.
- Clean F — 117,933 bytes; SHA-256
  `a9144221d3a4d8d01e186d5f7a81714b0ec240590f23dd9ea1dbf06b5252a323`.
- Fresh replay — 117,922 bytes; SHA-256
  `4f4b190ad3bf12e38cc4fc65db76f4e8a99d33bbe41d841bb9dc5c67e4542b14`.
- Installed `artifacts/unit-022-bab-3-kategori-diperkaya-dan-aditif.pdf` —
  117,933 bytes; SHA-256
  `a9144221d3a4d8d01e186d5f7a81714b0ec240590f23dd9ea1dbf06b5252a323`.

The QA probe records 72 page renders at 144 dpi and eight contact sheets over
two clean builds, two renderers, and two render passes. The admitted nine-page
Poppler and nine-page MuPDF raster sets were separately compared against clean
E, clean F, and the fresh replay: every decoded page and every PNG is
byte-identical within its renderer. Poppler aggregate raw-RGB/PNG-set hashes
are `6ae07380d9519bcd3be4b2ee8c13d117d686a4764a61d0d6fc8f7b7d85e411af`
and `9429725575c0a2e4a914775534fb686bd1412697172fee13f26639d0bf810b67`;
MuPDF hashes are
`3cf6be4b0a09f6687d6fe2c4b5914738017fba534712798a69541730f7f37dd8`
and `59586715aafc7f7dde1f395035d16e87e1841c95dc1c4b33d6c8a90f062568df`.

All pages were inspected for clipping, overlap, tofu or missing glyphs, broken
arrows/diagrams, off-center composition, blank versos, and poor pagination.
No defect was found, and no page has ink in the outer three-pixel border. The
cover is centered, states the partial Chapter 3 scope in prose, and contains no
ambiguous filled/unfilled progress blocks. Pages 3–9 preserve the enriched
composition and unit diagrams, the enriched naturality square, biproduct
arrows, and matrix formulas. A forced back-matter page break initially created
a sparse page 10; suppressing only that break lets the two-entry bibliography
and both short indexes use the open lower portion of page 9 legibly, with zero
overfull boxes.

## PDF structure, text, and safety

The artifact is PDF 1.7, unencrypted, nine pages of 498.9 × 708.66 pt, with
catalog language `id-ID`, no form, JavaScript, embedded file, additional or
unsafe action, and no out-of-bounds text. All 28 fonts are embedded and subset.
Five outline entries navigate to Chapter 3, Section 3.4, bibliography, term
index, and symbol index. There are 47 named destinations and 20 valid links:
17 `/GoTo` and three intentional `/URI` actions. The catalog open action is a
safe page-fit destination array.

Every page has extractable text. Clean E, clean F, and replay have identical
PyPDF extraction, SHA-256
`250fbed3644fea08d7f2f378cda82b91ab64b8a9015ce7822f8717e822e4972e`.
Final-F PyMuPDF, pdfplumber-layout, and Poppler-layout hashes are
`ce729750539f76e6be7c2ba3cd8a09100d655224208e9c30a4efa66871f3f070`,
`26a242b10ac65879d374640fa8e845cf58ab7346f68f3c0aef8199b96c1299d0`,
and `caaf727a15d251e171e207661e26d1082c861c398f27c2aeb3b3ead1eb3b3ec5`.
PyPDF alone maps one visibly rendered tensor-product glyph on PDF page 3 to
NUL; Poppler, PyMuPDF, and pdfplumber contain zero NUL/replacement/control
characters. This parser-specific ToUnicode limitation and the untagged PDF
state are disclosed rather than hidden.

The sanitized final log has zero overfull boxes, undefined references,
undefined citations, undefined control sequences, missing characters, fatal
errors, or emergency stops. It records eight harmless underfull hboxes, two
underfull vboxes, and twelve expected suppressed-link occurrences produced by
repeated references to the nine external printed-number stubs.

## Evidence and rights

- Visual manifest — 62,244 bytes; SHA-256
  `9e0dbdf6808cbdadcda2c9cea1e9c5f440d73316eb60e3ee8e2a125e29308412`.
- Structure/PDF evidence — 17,953 bytes; SHA-256
  `b461ee52823e8e919006750d0b69ba3b100b0f71d0551b21762945369c2f0bfd`.
- Render inventory — 10,132 bytes; SHA-256
  `0511d0f65e2e9e5d0cff76ea7285acfde7f9a31bf1cd9407913b38a410bb47ac`.
- Build summary — 1,286 bytes; SHA-256
  `874d78fbd04112da3a9579c5d12721ccc6e202059d2d9fe53d3fda126fa04408`.
- Sanitized final build log — 85,480 bytes; SHA-256
  `ddec6e07c0e42bf938346e3490252a0e6f3acba7a3a0bcdd1e9974b995cd66e3`.
- Evidence generator — 26,705 bytes; SHA-256
  `c96804cd29dc26eae5f1d287ec8e2e6dd01a4724703ffc6994432f6d68ae249d`.

Wen-Wei Li remains the source author. The principal source text and independent,
non-endorsed Indonesian translation are CC BY 4.0. The credited AJbook fragment
retains CC BY-SA 3.0, and bundled Noto fonts retain SIL OFL 1.1. Production
provenance is recorded separately from authorship as
`OpenAI Codex gpt-5.6-sol, Ultra`.
