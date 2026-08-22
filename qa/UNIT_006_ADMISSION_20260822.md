# Unit 006 admission receipt - Bab 1: Semesta Grothendieck

Date: 2026-08-22

Decision: admitted as the sixth independently buildable `id-ID` reader unit.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit/tree: `c4f7a01f68f5f407906b4b970640cddbbad85f6b` / `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Complete frozen `chapter1.tex`: 49,874 bytes; SHA-256 `3405949f78c539e5e5c3c778e0460f2fde45ad3cb246d82a97e5a9492f95fe92`.
- Complete Section 1.5 source boundary, lines 436-506: 6,245 bytes; SHA-256 `4f1e14be25a0387c335ad11850aea1e3d71314e8578fa642ffecb6dbf80ffe05` under `sha256-utf8-lines-lf-v1`.
- Current target `repo/source/chapter1.tex`: 63,465 bytes; SHA-256 `30205d23cfaf29ae97ac63e4edb94ccb908fe23e29bef343907129b28b217c04`.
- Indonesian target boundary, lines 436-506: 8,034 bytes; SHA-256 `f255debb4b19eab59c524ea80c24b0dd3320e0b899b20d77c1d4a874645c0324` under `sha256-utf8-lines-lf-v1`.

## Translation and mathematical audit

The complete source-order section was translated into natural formal Indonesian. Its protected topology matches the frozen source: 11 balanced environments in the same nesting and order, including two definitions, two enumerations, one itemized list, one hypothesis, one `align*`, one proposition, one proof, one theorem, and one remark; two labels; four reference occurrences; six citation occurrences over the keys `SGA4-1`, `Je03`, and `Shu08`; four brace-aware index entries; twelve item tokens; one `align*` display; and one bracket display. The 99 normalized inline mathematics fragments have an identical multiset; the only sequence differences are harmless prose-driven reorderings at target lines 478, 480, and 482. The shared normalized multiset digest is `3c77b73d23456ae7fbbade66ac07c4477d3a5e16a5ae0f425dd865c6da2cbeb8`. The canonicalized `align*` displays share SHA-256 `45416cd9260e5ee1e8b08afafe1ad10de91562e1e2311a3f5c0379f68a822572`. The unit contains no exercise, hint, answer, solution, or diagram.

Independent structural, mathematical, semantic, and Indonesian-language reviews found no remaining P1 or P2 defect. Accepted copyedits were applied and all protected checks were repeated. The final translated span contains no Han-script residue, replacement character, or NUL.

### Disclosed source intervention

`O013-LI-U006-COR-001`: the frozen source index gloss at line 465 spells the English term `cumulative hierachy`. The target corrects this to `cumulative hierarchy` while localizing the index path to `teori himpunan!hierarki kumulatif`. This is recorded as an editorial correction rather than silently attributed to the source.

## Exact admitted build

- Driver: `repo/source/unit-006-bab-1-semesta-grothendieck.tex`, 4,394 bytes, SHA-256 `6cc523e0a13c366045513f46f703a5aeaf01d825946ca0fdcac4066dd7d61458`
- Shared interface: `repo/source/locale-ui-id.tex`, 2,972 bytes, SHA-256 `9d6c6aa162d11ce8f491703f640a808cdcf61280b300f22032d4caaa0035f3b9`; the driver adds target-only `Lema`, Noto CJK portability, Indonesian bibliography `in` and back-reference strings, and digital reflow. Upstream `AJbook.cls` remains byte-identical.
- Cover: `repo/source/coverpage-id-unit-006.tex`, 4,336 bytes, SHA-256 `06390c2127b5caf5ac95d0b158196c3406af5121c935b6df02a744cacad64d15`
- Frozen cross-reference witness: `repo/source/unit-006-crossrefs.aux`, 367 bytes, SHA-256 `ff3508473c788979e314fcbe1f9470a99bbc2b83bf618aa15247350703301963`
- Build script: `scripts/build_unit_006.ps1`, 2,850 bytes, SHA-256 `68d6dd118d0e4ef467c9eeedd72f52debc37cf5307bba1c42c7e80fb9ebb90ff`
- Backend generator: `scripts/generate_unit_006_backend.py`, 19,646 bytes, SHA-256 `33fa7d6117e10e21130f36d1f5388d68d0c9941d4877adcd6a53d36bd6d7a148`
- Reader: `artifacts/unit-006-bab-1-semesta-grothendieck.pdf`, 9 pages, 120,808 bytes, SHA-256 `1fe15c59de6021b376643269423f2ef12e7b986f048ae39a31d8b1df9f7562c4`
- Final log: `qa/UNIT_006_BUILD_FINAL.log`, 87,260 bytes, SHA-256 `e583f5da15d010cfcf9ff6cdc94bc8bbd056647afbdee711865b2f5af58233bc`
- Public build-log summary: `qa/unit-006-evidence/build-log-summary.txt`, 2,958 bytes, SHA-256 `de1618aef885047cd41b26e63d7e000271c06a1980bf2d733178a386d0c2065f`
- Replay PDF: 120,804 bytes, SHA-256 `c802b8d5b09470c6772e7311b4ddcb1a861d1af32f6fff5de31f5b1a09cc551e`; 9/9 MuPDF pages are pixel-identical at 144 dpi.
- Replay log: 87,269 bytes, SHA-256 `0c54cfcb3da92c4c9d700526da7141beff67451de3399397166ed56fc8cfb439`.

The final log has zero TeX errors, undefined citations or references, duplicate destinations, missing characters, or overfull boxes. Three suppressed empty-target warnings are intentional for frozen references outside this standalone unit. One underfull cover-table alignment is visually acceptable. Deterministic rendered pages are established; bit-identical XeTeX PDF containers across output directories are not claimed.

## PDF and all-page visual QA

The exact PDF has catalog language `id-ID`, nine nonblank pages, four outline roots/five total outline entries, 31 named destinations, 21 internal GoTo actions, and four intentional URI actions. It has no unresolved internal destination, GoToR, Launch, JavaScript, form, encryption, or structure tree. Extracted text contains no literal `??`, replacement character, NUL, Han-script residue, or unlocalized Chinese bibliography label; `Dalam:` and Indonesian back-reference strings are present. MuPDF and Poppler rendered every page, and all pages were inspected. The standalone reader fills the readable page area without print-only blank versos. No clipping, collision, missing glyph, unreadable text, malformed formula, broken link target, or index defect remains. The PDF remains untagged; that inherited accessibility limitation stays open and is not represented as passing tagged-PDF conformance.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with Wen-Wei Li credited and independent, non-endorsed derivative status stated. The attributed `AJbook.cls` fragment remains CC BY-SA 3.0 and bundled Noto fonts remain OFL 1.1. No component rights are flattened.

## Cursor

Unit 006 is admitted. The next contiguous source-order boundary is the complete Chapter 1 exercise set, `chapter1.tex:508-536`. Its normalized source and target slices are identical: 2,962 bytes, SHA-256 `2a2dd555d54526fe8ccd88413210fc6d63b7365cd198cd623248a96014e2702e` under `sha256-utf8-lines-lf-v1`. The authority file omits the final EOF newline while the target currently retains it; semantic line content is unchanged. This exercise unit must preserve all six top-level exercises, six enumerated subparts, and six source hints before the cursor advances into Chapter 2.
