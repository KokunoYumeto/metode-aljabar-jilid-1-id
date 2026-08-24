# Unit 005 standalone equation-number repair

Date: 2026-08-23

Status: admitted

Correction ID: `O013-LI-U005-READER-COR-001`

## Defect and repair

The frozen complete Chapter 1 source establishes `eqn:infinity-axiom` as equation (1.1) at line 49, before the Unit 005 span at lines 289-434. The prior standalone driver began its equation counter at zero, so `eqn:cardinal-infinite-sum` and `eqn:cardinal-infinite-prod` incorrectly printed as (1.1) and (1.2). The repair inserts `\setcounter{equation}{1}` immediately before the unchanged source-span input. `eqn:cardinal-infinite-sum` prints as (1.2), and `eqn:cardinal-infinite-prod` prints as (1.3), matching the complete-book sequence.

The Indonesian source span remains 13,786 bytes with SHA-256 `57a5051ca741afdeb2d1e9c88413908442844b7eadff5a464fa79e453dc683af`; no translation, formula, label, reference, citation, diagram, index, exercise, hint, answer, or solution content changed.

## Independent clean-build evidence

- Build A: `build/unit-005-equation-fix-a`; PDF 128,553 bytes, SHA-256 `2f3f23f16b4f3f39edaad41509730afbcc7ca28f6b16e97e6281e864291fb34c`; log 87,110 bytes, SHA-256 `8718bbb92ed41833cd308892ae149b9432e55942f859339be7096f534fb80e1e`; AUX 3,772 bytes, SHA-256 `ee43180f1b3c9bda07d81d8beefd44d4bbadf804d6f54715ec1c1220758d6e22`.
- Build B: `build/unit-005-equation-fix-b`; PDF 128,554 bytes, SHA-256 `205359b6c3b406a4f6595908381147e2bb3dba6aab8fdc9057436b11bec252de`; log 87,110 bytes, SHA-256 `2de97988ca56557b50822f4fbaef60784fbc21b7c3b32d184eab87236c058748`; AUX 3,772 bytes, SHA-256 `ee43180f1b3c9bda07d81d8beefd44d4bbadf804d6f54715ec1c1220758d6e22`.
- Both AUX files contain `eqn:cardinal-infinite-sum` as (1.2) on content page 2 and `eqn:cardinal-infinite-prod` as (1.3) on content page 2.
- Both final logs report 12 pages and have zero TeX errors, undefined controls, undefined references/citations, missing characters, overfull boxes, fatal errors, or emergency stops. The two intentionally suppressed empty-target links and the previously accepted one underfull hbox/one underfull vbox remain unchanged.
- Functional replay is 12/12 pixel-identical pages in Poppler and 12/12 in MuPDF at 144 dpi. Ordered-page concatenated SHA-256 values are `2c2e8981e885a53d6ceae78451e8d949150e5c65ee5406dff1b5f05c82f241a0` (Poppler) and `93743c1b9ef867ea1948abe8a0385bb2aad8d7b98194064cd60fd3e8836b1bd6` (MuPDF).
- All 12 pages were inspected in both renderers. The corrected equation page visibly shows (1.2) and (1.3); no clipping, collision, missing glyph, unreadable text, blank page, or malformed formula was found. No visual uncertainty remains.

## Installed identities and provenance

- Reader: 12 pages, 128,554 bytes, SHA-256 `205359b6c3b406a4f6595908381147e2bb3dba6aab8fdc9057436b11bec252de`.
- Final log: 87,110 bytes, SHA-256 `2de97988ca56557b50822f4fbaef60784fbc21b7c3b32d184eab87236c058748`.
- Source author: Wen-Wei Li. Principal text and Indonesian translation: CC BY 4.0. Credited AJbook.cls fragment: CC BY-SA 3.0. Bundled Noto fonts: OFL 1.1. This remains an independent, non-endorsed derivative; component rights are not flattened.
- Production provenance: OpenAI Codex gpt-5.6-sol, Ultra.

The correction is admitted locally. Git commit, push, public-byte readback, and publication receipt remain for the owning O013 task; this bounded repair performed no Git or publication action.
