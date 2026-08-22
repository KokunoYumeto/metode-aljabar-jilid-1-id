# Unit 005 admission receipt - Bab 1: Bilangan Kardinal

Date: 2026-08-22

Decision: admitted as the fifth independently buildable `id-ID` reader unit.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit/tree: `c4f7a01f68f5f407906b4b970640cddbbad85f6b` / `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Complete frozen `chapter1.tex`: 49,874 bytes; SHA-256 `3405949f78c539e5e5c3c778e0460f2fde45ad3cb246d82a97e5a9492f95fe92`.
- Complete Section 1.4 source boundary, lines 289-434: 11,170 bytes; SHA-256 `fa1fec18021ed96b4fcbcbbf4e887741c566862fa2b7d407059b2c4b89bff518` under `sha256-utf8-lines-lf-v1`.
- Current target `repo/source/chapter1.tex`: 61,676 bytes; SHA-256 `83c2f7c0abe4964dfdf61225757feba2f442cf020364fd511df1dd3deb2fc58e`.
- Indonesian target boundary, lines 289-434: 13,786 bytes; SHA-256 `57a5051ca741afdeb2d1e9c88413908442844b7eadff5a464fa79e453dc683af` under `sha256-utf8-lines-lf-v1`.

## Translation and mathematical audit

The complete source-order section was translated into formal Indonesian. Its protected topology matches the frozen source exactly: 27 balanced environments, including three definitions, three theorems, six proofs, one lemma, one proposition, one corollary, one example, two `align*`, two `gather`, two `tikzpicture`, and the remaining list/display wrappers; ten labels; six reference occurrences; one citation (`Je03`); seven item tokens; and five brace-aware index entries. All 163 inline mathematics fragments match in normalized sequence and multiset. The two TikZ pictures at source/target lines 395-406 remain byte-identical over their complete shared block: 481 bytes, SHA-256 `104335d1e15c5bddb8d69fd37680b5df6acc4f46d80e6889a2a69d75e96c8508`. The unit contains no exercise, hint, answer, or solution.

Independent topology, mathematical, semantic, and Indonesian-language reviews found no remaining P1 or P2 defect. Accepted language edits were applied, and all protected checks were repeated. The final translated span contains no Han-script residue, replacement character, or NUL.

### Disclosed source interventions

- `O013-LI-U005-COR-001`: source line 379 reverses the historical roles of Gödel and Cohen. The target states the standard result accurately: Gödel's 1940 constructibility result establishes relative non-refutability of the continuum hypothesis, while Cohen's 1963 forcing result establishes relative non-provability. This is a documented editorial correction, not silently attributed source wording.
- `O013-LI-U005-CLR-001`: source line 304 tacitly replaces the first injection by its left composition with the second map when replacing `Y` by `g(Y)`. The target makes that necessary adjustment explicit without altering the protected mathematics-token sequence. This is a disclosed clarification of an implicit step.

## Exact admitted build

- Driver: `repo/source/unit-005-bab-1-kardinal.tex`, 4,357 bytes, SHA-256 `cdf7f235f4c4e000a0c063dae0ab0d24f7b76d5218e80d9d5e870933ae038733`
- Shared interface: `repo/source/locale-ui-id.tex`, 2,972 bytes, SHA-256 `9d6c6aa162d11ce8f491703f640a808cdcf61280b300f22032d4caaa0035f3b9`; the driver adds target-only `Lema`, Noto CJK portability, and Indonesian bibliography-back-reference overrides. Upstream `AJbook.cls` remains byte-identical.
- Cover: `repo/source/coverpage-id-unit-005.tex`, 4,386 bytes, SHA-256 `fc754187209c46b9a39731510004c6aa0645036dcc4ef003c693d4f6ca37fc11`
- Frozen cross-reference witness: `repo/source/unit-005-crossrefs.aux`, 340 bytes, SHA-256 `cd05c6135e62cb225eefdc49e49d04c3c9a9c7098633c7935fb89ac9b988407d`
- Build script: `scripts/build_unit_005.ps1`, 2,838 bytes, SHA-256 `9e82eee4e4688d1b7add4026f850bdd3dc30bc7d9012e3e42cd054409b895f01`
- Backend generator: `scripts/generate_unit_005_backend.py`, 17,428 bytes, SHA-256 `2e2cf4fa4f9c2aee35839c04e910b8e8350e52721a7f940982b47861f875e8b7`
- Reader: `artifacts/unit-005-bab-1-kardinal.pdf`, 12 pages, 128,556 bytes, SHA-256 `232d41f4e7f03123818ae14272958c8269242ebcbec68b832aaaf7ba295ebf3e`
- Final log: `qa/UNIT_005_BUILD_FINAL.log`, 87,065 bytes, SHA-256 `9292dfda9928a49fd397f0e44fa7e57a2d8a7cce40f6038bd61f8b8608b04f63`
- Public build-log summary: `qa/unit-005-evidence/build-log-summary.txt`, 2,851 bytes, SHA-256 `ae02a0622ed73a1ec71f74ff003505099afb3de3edef2e0b7a29ee3994086689`
- Replay PDF: 128,553 bytes, SHA-256 `1e6770a30e0872a581235e5fd8a1a9f98cbdb90d15ec3488018eb018b7920342`; 12/12 MuPDF pages are pixel-identical at 144 dpi.
- Replay log: 87,074 bytes, SHA-256 `d90073eba3ce06685a466a6a9c3faf9c932ad9c423973726d6775336ee66243f`.

The final log has zero TeX errors, undefined citations/references, duplicate destinations, missing characters, or overfull boxes. Two suppressed empty-target warnings are intentional for frozen references outside this standalone unit. One underfull cover-table alignment and one underfull section-ending page are visually acceptable. Deterministic rendered pages are established; bit-identical XeTeX PDF containers across output directories are not claimed.

## PDF and all-page visual QA

The exact PDF has catalog language `id-ID`, 12 nonblank pages, six outline entries, 42 named destinations, 17 internal GoTo actions, three intentional URI actions, and no GoToR, Launch, JavaScript, form, or encryption. Extracted text contains no literal `??`, replacement character, NUL, Han-script residue, `Lemma`, or Chinese bibliography-back-reference phrase; the localized forms `Lema` and `dirujuk pada hlm.` are present. MuPDF and Poppler rendered every page, and all pages were inspected. The standalone reader fills the readable page area without print-only blank versos. No clipping, collision, missing glyph, unreadable text, malformed formula, broken link target, or index defect remains. The PDF remains untagged; that inherited accessibility limitation stays open and is not represented as passing tagged-PDF conformance.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with Wen-Wei Li credited and independent, non-endorsed derivative status stated. The attributed `AJbook.cls` fragment remains CC BY-SA 3.0 and bundled Noto fonts remain OFL 1.1. No component rights are flattened.

## Cursor

Unit 005 is admitted. The next contiguous source-order boundary is complete Section 1.5, `chapter1.tex:436-506`, `Semesta Grothendieck`. Its frozen source and still-identical target slice is 6,245 bytes, SHA-256 `4f1e14be25a0387c335ad11850aea1e3d71314e8578fa642ffecb6dbf80ffe05` under `sha256-utf8-lines-lf-v1`. Chapter-end exercises at lines 508-536 follow as a separate coherent unit so their exercise and hint identities remain explicit.
