# Unit 003 admission receipt - Bab 1: Struktur Urutan dan Ordinal

Date: 2026-08-22

Decision: admitted as the third independently buildable `id-ID` reader unit.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit/tree: `c4f7a01f68f5f407906b4b970640cddbbad85f6b` / `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Complete frozen `chapter1.tex`: 49,874 bytes; SHA-256 `3405949f78c539e5e5c3c778e0460f2fde45ad3cb246d82a97e5a9492f95fe92`
- Complete Section 1.2 source boundary, lines 87-203: 9,976 bytes; SHA-256 `8f2a42d8b623e59bed488bed085c029d340bec42601e4bd2a3a862dbea4e56a4` under `sha256-utf8-lines-lf-v1`.
- Current target `repo/source/chapter1.tex`: 56,831 bytes; SHA-256 `eedc388ca9ea681701e4306095674fcadcf93a82bc6a1c02dfcfe5d1a528a10a`.
- Indonesian target boundary, lines 87-203: 12,927 bytes; SHA-256 `42c74a19d42f0aa6d02256d041d32ed14ca83c704327095a33c18ccbcc2d869d` under `sha256-utf8-lines-lf-v1`.

## Translation and mathematical audit

The complete source-order section was translated into formal Indonesian. Its protected topology matches the frozen source exactly: six definitions, two examples, two lemmas, one theorem, one proposition, three proofs, ten labels, two forward references, three citation keys (`Je03`, `HY14`, `DN00`), sixteen brace-aware index entries, seventeen item tokens, 194 inline mathematics spans, and one display. The normalized mathematics multiset is identical after allowing only the two intentional localized `\text{...}` payloads.

An independent semantic review found no P1, P2, or P3 mathematical defect. A separate Indonesian-language review identified bounded calques and ambiguities; accepted copyedits were applied and all protected topology and mathematics checks were repeated. The final span has zero Han-script residue and zero replacement characters. This unit contains no exercise, hint, answer, solution, or diagram.

## Exact admitted build

- Driver: `repo/source/unit-003-bab-1-struktur-urutan-dan-ordinal.tex`, 3,854 bytes, SHA-256 `1a649ecc5de9e3d81715f5545fcc16e44bc23f3a110960d2d8068fdcee80f593`
- Interface localization: `repo/source/locale-ui-id.tex`, 2,972 bytes, SHA-256 `9d6c6aa162d11ce8f491703f640a808cdcf61280b300f22032d4caaa0035f3b9`; upstream `AJbook.cls` remains byte-identical.
- Cover: `repo/source/coverpage-id-unit-003.tex`, 4,371 bytes, SHA-256 `db1f9cf8a998457da1a7464b1382f9eeda85bd4d0ffea4025961ee408f5f544f`
- Frozen forward-reference witness: `repo/source/unit-003-crossrefs.aux`, 351 bytes, SHA-256 `d4ab7c2fa0ca05dbc2cfadb6c8d248a08482bd18a581d895d9bd636a6d3623d0`
- Build script: `scripts/build_unit_003.ps1`, 2,857 bytes, SHA-256 `5cb07bf6c5b9ecabb88f36d8fdfaacd3edc231fff14d9f9b2e502d3fa3e242aa`
- Reader: `artifacts/unit-003-bab-1-struktur-urutan-dan-ordinal.pdf`, 11 pages, 147,784 bytes, SHA-256 `67f3b0594f65917cf78361886aef6616c0875bc584a95758f06e4d11b182082c`
- Final log: 86,225 bytes, SHA-256 `f3aa36d9c2cad3ed0e7a50448b2e03cbda454638fae094f3236dd785e28cc3f7`
- Replay PDF: 147,773 bytes, SHA-256 `4f0a19d47a74ff4bb7415bc8772ca7f5b7e40384cb27fb839176bbd7ff5aaee3`; 11/11 MuPDF pages are pixel-identical at 144 dpi.

The final log has zero TeX errors, undefined citations/references, duplicate destinations, missing characters, or overfull boxes. Two suppressed empty-target warnings are intentional for the frozen forward references, and one underfull cover-table line is visually acceptable. As with earlier units, deterministic rendered pages are established while bit-identical XeTeX PDF containers across output directories are not claimed.

## PDF and all-page visual QA

The exact PDF has catalog language `id-ID`, 11 nonblank pages, five outline roots/six total outline entries, 43 named destinations, 28 internal GoTo actions, three intentional URI actions, and no GoToR or Launch action. Extracted text contains no literal `??`, replacement character, or unlocalized Chinese environment heading. MuPDF and Poppler rendered all 11 pages; every page was inspected. The section is centered and fills the readable page area, theorem and proof headings are Indonesian, and no clipping, collision, unreadable glyph, unintended blank page, broken formula, or index defect remains.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with Wen-Wei Li credited and independent, non-endorsed derivative status stated. The attributed `AJbook.cls` fragment remains CC BY-SA 3.0 and bundled Noto fonts remain OFL 1.1. No component rights are flattened.

## Cursor

Unit 003 is admitted. The next contiguous source-order boundary is Section 1.3, `chapter1.tex:205-287`, beginning `Transfinite Recursion and Its Applications`; it remains untranslated at this receipt boundary.
