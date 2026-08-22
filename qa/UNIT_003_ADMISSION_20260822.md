# Unit 003 admission receipt - Bab 1: Struktur Urutan dan Ordinal

Date: 2026-08-22

Decision: admitted as the third independently buildable `id-ID` reader unit.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit/tree: `c4f7a01f68f5f407906b4b970640cddbbad85f6b` / `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Complete frozen `chapter1.tex`: 49,874 bytes; SHA-256 `3405949f78c539e5e5c3c778e0460f2fde45ad3cb246d82a97e5a9492f95fe92`
- Complete Section 1.2 source boundary, lines 87-203: 9,976 bytes; SHA-256 `8f2a42d8b623e59bed488bed085c029d340bec42601e4bd2a3a862dbea4e56a4` under `sha256-utf8-lines-lf-v1`.
- Current target `repo/source/chapter1.tex`: 61,677 bytes; SHA-256 `2beca35786cece83ecb252c1052dbdbcadfcd902de6eb37aaaf5bc2c97cf67b4`.
- Indonesian target boundary, lines 87-203: 12,926 bytes; SHA-256 `72be84fda07c748407e7d46e77d2a3709bb1203519d161ae278cbee40ed680a8` under `sha256-utf8-lines-lf-v1`.

## Translation and mathematical audit

The complete source-order section was translated into formal Indonesian. Its protected topology matches the frozen source exactly: six definitions, two examples, two lemmas, one theorem, one proposition, three proofs, ten labels, two forward references, three citation keys (`Je03`, `HY14`, `DN00`), sixteen brace-aware index entries, seventeen item tokens, 194 inline mathematics spans, and one display. The normalized mathematics multiset is identical after allowing only the two intentional localized `\text{...}` payloads. A post-admission terminology correction changed the prose form `Lemma` to standard Indonesian `Lema` without altering any protected surface.

An independent semantic review found no P1, P2, or P3 mathematical defect. A separate Indonesian-language review identified bounded calques and ambiguities; accepted copyedits were applied and all protected topology and mathematics checks were repeated. The final span has zero Han-script residue and zero replacement characters. This unit contains no exercise, hint, answer, solution, or diagram.

## Exact admitted build

- Driver: `repo/source/unit-003-bab-1-struktur-urutan-dan-ordinal.tex`, 4,527 bytes, SHA-256 `dc65c78696fe0ad5b7bb7b50de0ef6c7dea32bb4e7853128d0a8f3c6d0b87a32`. It adds target-only standard `Lema`, bundled Noto CJK portability, and Indonesian bibliography-back-reference overrides.
- Interface localization: `repo/source/locale-ui-id.tex`, 2,972 bytes, SHA-256 `9d6c6aa162d11ce8f491703f640a808cdcf61280b300f22032d4caaa0035f3b9`; upstream `AJbook.cls` remains byte-identical.
- Cover: `repo/source/coverpage-id-unit-003.tex`, 4,343 bytes, SHA-256 `f297bf2b2b025e45465e6b0a8c40aa118a5d5a39ef3a86aee49736136d52197e`; the redundant Chinese parenthetical author form was removed while the complete Latin attribution remains.
- Frozen forward-reference witness: `repo/source/unit-003-crossrefs.aux`, 351 bytes, SHA-256 `d4ab7c2fa0ca05dbc2cfadb6c8d248a08482bd18a581d895d9bd636a6d3623d0`
- Build script: `scripts/build_unit_003.ps1`, 2,857 bytes, SHA-256 `5cb07bf6c5b9ecabb88f36d8fdfaacd3edc231fff14d9f9b2e502d3fa3e242aa`
- Reader: `artifacts/unit-003-bab-1-struktur-urutan-dan-ordinal.pdf`, 11 pages, 134,858 bytes, SHA-256 `031e231bc5d2ac74cada865700d8f76dda327941c7f442e6d47324b848103df8`
- Final log: 87,326 bytes, SHA-256 `865d8a751433de561c29f33ee984c25be54eb3203a4987aebbc451e79abe25c4`
- Replay PDF: 134,858 bytes, SHA-256 `16ecbf617e307079c9d46b7628cebf0d973d2455131a0edff2ad76a042ec4a8c`; 11/11 MuPDF pages are pixel-identical at 144 dpi.
- Replay log: 87,335 bytes, SHA-256 `ccd36e39f41fbdc5f2a1660e7f7be5c725a08f5fd27059fe9914bcef74cacd15`.

The final log has zero TeX errors, undefined citations/references, duplicate destinations, missing characters, or overfull boxes. Two suppressed empty-target warnings are intentional for the frozen forward references, and one underfull cover-table line is visually acceptable. As with earlier units, deterministic rendered pages are established while bit-identical XeTeX PDF containers across output directories are not claimed.

## PDF and all-page visual QA

The exact PDF has catalog language `id-ID`, 11 nonblank pages, five outline roots/six total outline entries, 43 named destinations, 28 internal GoTo actions, three intentional URI actions, and no GoToR, Launch, JavaScript, form, or encryption. Extracted text contains no literal `??`, replacement character, NUL, `Lemma`, Chinese bibliography-back-reference phrase, or unlocalized Chinese environment heading. Its 60 Han characters are intentional source-language author/title/publisher metadata in the two Chinese bibliography entries; bundled Noto CJK now renders them identically in MuPDF and Poppler. MuPDF and Poppler rendered all 11 pages; every page and the corrected bibliography surface were inspected. The section is centered and fills the readable page area, theorem and proof headings are Indonesian, and no clipping, collision, unreadable glyph, unintended blank page, broken formula, or index defect remains.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with Wen-Wei Li credited and independent, non-endorsed derivative status stated. The attributed `AJbook.cls` fragment remains CC BY-SA 3.0 and bundled Noto fonts remain OFL 1.1. No component rights are flattened.

## Cursor

Unit 003 remains admitted with the portability/terminology correction above. Its mathematics and source boundary are unchanged. The live production cursor is maintained separately in `00_control/CURRENT_CURSOR.json` and now follows admitted Unit 005.
