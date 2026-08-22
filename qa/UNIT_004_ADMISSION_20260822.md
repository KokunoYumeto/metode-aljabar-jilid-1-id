# Unit 004 admission receipt - Bab 1: Rekursi Transfinit dan Penerapannya

Date: 2026-08-22

Decision: admitted as the fourth independently buildable `id-ID` reader unit.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit/tree: `c4f7a01f68f5f407906b4b970640cddbbad85f6b` / `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Complete frozen `chapter1.tex`: 49,874 bytes; SHA-256 `3405949f78c539e5e5c3c778e0460f2fde45ad3cb246d82a97e5a9492f95fe92`.
- Complete Section 1.3 source boundary, lines 205-287: 8,167 bytes; SHA-256 `706aea86166b77533e64415628976d325c0da0f23ffa24854117019fbacef5c6` under `sha256-utf8-lines-lf-v1`.
- Current target `repo/source/chapter1.tex`: 59,061 bytes; SHA-256 `d204b73232eb14ecc22df93ab22fc24f256bd0575ce84d5b028c77cfec867079`.
- Indonesian target boundary, lines 205-287: 10,397 bytes; SHA-256 `ab4bc0aadaecf2ac665dd4ff03358e57980e35a721c931f83b655c525a26dc33` under `sha256-utf8-lines-lf-v1`.

## Translation and mathematical audit

The complete source-order section was translated into formal Indonesian. Its protected topology matches the frozen source exactly: four theorem environments, one proposition, one remark, five proofs, four labels, nine reference occurrences over eight unique keys, three brace-aware index entries, twenty-one item tokens, 138 inline mathematics fragments, and two displays. The normalized inline and display mathematics multisets are identical. This unit contains no citation, exercise, hint, answer, solution, or diagram.

Independent topology, mathematical, semantic, and Indonesian-language reviews found no remaining P1 or P2 defect. All accepted P3 copyedits were applied and the protected checks were repeated. The final span has zero Han-script residue and zero replacement characters.

### Disclosed editorial correction

Correction `O013-LI-U004-COR-001` is deliberate and provenance-bound. Source line 206 says that every class of ordinals has a minimal element, but omits the logically necessary nonempty condition. The cited Theorem `prop:On-wellorder` explicitly assumes that condition. The Indonesian target therefore says `setiap kelas tak kosong`; this is a documented editorial repair, not silently attributed upstream wording.

## Exact admitted build

- Driver: `repo/source/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.tex`, 3,780 bytes, SHA-256 `e1932d2c618ffc55f6f7cf79f42499116f13124c8ff139532f369f1b42711594`
- Interface localization: `repo/source/locale-ui-id.tex`, 2,972 bytes, SHA-256 `9d6c6aa162d11ce8f491703f640a808cdcf61280b300f22032d4caaa0035f3b9`; upstream `AJbook.cls` remains byte-identical.
- Cover: `repo/source/coverpage-id-unit-004.tex`, 4,398 bytes, SHA-256 `4e89423fd267f6d8629355838e7e850f78c08347259b10cd390044eb700f67cd`
- Frozen cross-reference witness: `repo/source/unit-004-crossrefs.aux`, 521 bytes, SHA-256 `c70b9f161ef1ad6768da54708f10bb158881a514221d068c4b63ce10a9757d88`
- Build script: `scripts/build_unit_004.ps1`, 2,757 bytes, SHA-256 `ab14ef97d14c1b8657ace8e402af017d80f115486134b8791d96a39c0b3b67c5`
- Reader: `artifacts/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf`, 8 pages, 107,332 bytes, SHA-256 `e48aa97d15ad9c192df5d744bfc8290fc816c4b681322295352517a02e267c13`
- Final log: 86,437 bytes, SHA-256 `850b2c4a31244e558b11c8cda9870fde976ab40001cada95a5debab403e610c2`
- Replay PDF: 107,340 bytes, SHA-256 `a3e0ba4f0ebd64178f5779e5b3a778cc5498a3abcc703cec21e105d9722ad29b`; 8/8 MuPDF pages are pixel-identical at 144 dpi.

The final log has zero TeX errors, undefined citations/references, duplicate destinations, missing characters, or overfull boxes. Six suppressed empty-target warnings are intentional for the frozen standalone cross-unit references, and one underfull cover-table line is visually acceptable. Deterministic rendered pages are established; bit-identical XeTeX PDF containers across output directories are not claimed.

## PDF and all-page visual QA

The exact PDF has catalog language `id-ID`, eight nonblank pages, four outline roots/four total outline entries, 37 named destinations, ten internal GoTo actions, three intentional URI actions, and no GoToR, Launch, JavaScript, form, or encryption. Extracted text contains no literal `??`, replacement character, NUL, Han-script residue, or unlocalized Chinese environment heading. MuPDF and Poppler rendered every page; all pages were inspected. The standalone reader fills the readable page area without print-only blank versos. No clipping, collision, missing glyph, unreadable text, malformed formula, broken link target, or index defect remains. The PDF remains untagged; that inherited accessibility limitation stays open and is not represented as passing tagged-PDF conformance.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with Wen-Wei Li credited and independent, non-endorsed derivative status stated. The attributed `AJbook.cls` fragment remains CC BY-SA 3.0 and bundled Noto fonts remain OFL 1.1. No component rights are flattened.

## Cursor

Unit 004 is admitted. The next contiguous source-order boundary is complete Section 1.4, `chapter1.tex:289-434`, `Kardinal`. Its frozen source and still-identical target slice is 11,170 bytes, SHA-256 `fa1fec18021ed96b4fcbcbbf4e887741c566862fa2b7d407059b2c4b89bff518` under `sha256-utf8-lines-lf-v1`.
