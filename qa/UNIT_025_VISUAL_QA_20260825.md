# Unit 025 reader visual QA — 2026-08-25

Status: **PASS**

Artifact: `artifacts/unit-025-bab-4-semigrup-monoid-dan-grup-id.pdf`, 10 pages,
123,117 bytes, SHA-256
`511d1c0889c0882639be49d00580c0634de7e3074c757616ac10a3f2fa854615`.

## Inspection basis

Every physical page 1--10 was inspected at 998 x 1418 pixels in both renderer
families:

- Poppler (`pdftoppm`, 144 dpi);
- MuPDF (`mutool draw`, 144 dpi), with PyMuPDF independently used for PDF text,
  page geometry, and out-of-bounds-block inspection.

The inspected artifact contact sheets are:

- `build/unit-025-final-visual-20260825/contact-sheets/artifact-poppler.png`,
  813,118 bytes, SHA-256
  `119cbadaa97bc67fdd837f3caa56ac5d378624e55a4bc06b775c8ba66523a7f4`;
- `build/unit-025-final-visual-20260825/contact-sheets/artifact-mupdf.png`,
  813,297 bytes, SHA-256
  `08b80de4fd8c109d2708b7884b2a2c1bec36ee2ccd6fb75800b7f12cede4ab50`.

The H, clean replay I, and artifact page rasters are PNG-byte-identical and
decoded-pixel-identical within each renderer family. The 60 page renders and 6
contact sheets are inventoried in
`qa/unit-025-evidence/render-hash-inventory.json`.

## Page-by-page adjudication

| Physical page | Inspection finding in both renderers |
|---:|---|
| 1 | Cover is centered and balanced. The prose scope box truthfully states partial Bab 4 coverage and complete Bagian 4.1 coverage; no ambiguous filled/unfilled progress blocks remain. |
| 2 | Attribution, CC BY 4.0 notice, component notices, independent/non-endorsed status, and `OpenAI Codex gpt-5.6-sol, Ultra` provenance are legible and unclipped. |
| 3 | The Bab 4 opening fills the centered 142 mm measure legibly. The complete orientation is present, and the reading-guidance box is not stranded at the foot. |
| 4 | The complete `Petunjuk membaca` box begins and ends coherently, followed by the Bagian 4.1 opening and its first two bullets. No split-box fragment or orphan display remains. |
| 5 | Associativity, cancellation, product, identity, invertibility, and Definisi 4.1.1 are legible. Displays are centered and the page transition is coherent. |
| 6 | Group definitions, inverse identities, conventions, and Contoh 4.1.4--4.1.5 are intact. No cross-page hyphenated word, overlap, or overflow remains. |
| 7 | General-linear and symmetric-group examples and subgroup/simple-group definitions are complete, with stable mathematical glyphs, references, and citations. |
| 8 | Generated, normal, and cyclic subgroup material, corrected integer-subgroup example `O013-LI-U025-COR-001`, cosets, and the start of Lema 4.1.12 are present without clipping. |
| 9 | Lema 4.1.12, Proposisi 4.1.13, both proofs, Definisi 4.1.14, and Catatan 4.1.15 remain together. The former sparse final-content page is eliminated. |
| 10 | Bibliography, localized term index, and symbol index share one readable page. No untranslated `yaobanqun`/`qun` hierarchy heads remain, and all live page links are visible. |

Pages inspected: `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`.

Renderers inspected: `Poppler`, `MuPDF (mutool and PyMuPDF)`.

## Reflow decision

Earlier layouts retained a narrow print-column feel and produced a lone display
fragment, a cross-page hyphenated word, a stranded definition, untranslated
Pinyin index heads, a split reading-guidance box, and a sparse final-content
page. The admitted driver uses a centered 142 mm by 198 mm digital-reader
measure, 1.16 leading, a twelve-line `Needspace` guard for the guidance box, and
a three-line local page enlargement for the sole final remark. The result is ten
physical pages without reducing the type size or changing mathematical content,
with zero overfull boxes, zero empty-target warnings, zero broken destinations,
and no clipping, overlap, tofu, edge contact, orphan heading/display, or sparse
content page.

## Deterministic and PDF checks

- Canonical target lines 1--178 are byte-identical to the isolated candidate:
  178 LF records, 20,464 bytes, SHA-256
  `5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a`.
  The complete target is 159,681 bytes, SHA-256
  `b1b055416d392a66708047afb20a14175566c7839286979baac6289d3d125419`.
- Protected structure passes for 280 math spans, 10 labels, 11 references, 3
  citations, 25 index entries, 24 item markers, 7 definitions, 4 examples, 1
  lemma, 1 proposition, 1 remark, 2 proofs, and 1 convention. All nine external
  references resolve through the frozen cross-reference witness.
- Clean H differs from replay I only through regenerated six-letter embedded-font
  subset prefixes. Extracted-text hashes, normalized font families, PDF
  structure, and every decoded page pixel are identical. Same-renderer pixel
  mismatches are Poppler 0 and MuPDF 0; replay I is byte-identical to the frozen
  artifact.
- PDF safety checks found no encryption, AcroForm, JavaScript, embedded files,
  catalog additional actions, unsafe actions, out-of-bounds text, replacement
  characters, unresolved tokens, missing characters, or Han residue. All 25
  fonts are embedded. `/Lang` is `id-ID`; the PDF is not structurally tagged.
- One parser-specific extraction discrepancy was explicitly adjudicated: pypdf
  maps the visible Unicode minus in `−x` to one NUL, while PyMuPDF and Poppler
  recover all 17 Unicode minus signs and pdfplumber identifies the same glyph as
  its sole `(cid:0)`. The other 16 minus signs and all surrounding text agree;
  this is a pypdf glyph-mapping limitation, not missing or malformed reader text.
- Navigation is coherent: outlines are `4 Teori Grup`, `4.1 Semigrup, Monoid,
  dan Grup`, `Daftar Pustaka`, `Indeks Istilah`, and `Indeks Simbol`; 50 named
  destinations, 32 internal `GoTo` actions, and 6 safe HTTPS URI actions are
  present. The broken-destination and unsafe-action inventories are empty.
- The sanitized final build log is `qa/UNIT_025_BUILD_FINAL.log`, 85,827 bytes,
  SHA-256
  `ee9a4e064edf0cf8cc4710e32c89eda7a8623bceb5ec5fbc75d8ef663826cd2a`.
  It contains zero overfull boxes, zero undefined references/citations, zero
  missing characters, and zero fatal/emergency errors. Its three underfull
  horizontal boxes cause no visible defect on either rendered contact sheet.

Structured evidence: `qa/unit-025-evidence/structure-and-pdf-qa.json`, 38,927
bytes, SHA-256
`235a69a3fbb0841707faef94f0c3d968c7d0c5a1833a4c98b1b4b2fc896ccab3`.

Render inventory: `qa/unit-025-evidence/render-hash-inventory.json`, 14,979
bytes, SHA-256
`ec007cc1a58aeb14dcc413aa759c5b75cfda727a645e66c878095a94a2f4c080`.
