# Unit 005 admission receipt - Bab 1: Bilangan Kardinal

Date: 2026-08-22

Last repaired and re-admitted: 2026-08-23

Status: admitted

Decision: admitted as the fifth independently buildable `id-ID` reader unit.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit/tree: `c4f7a01f68f5f407906b4b970640cddbbad85f6b` / `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Complete frozen `chapter1.tex`: 49,874 bytes; SHA-256 `3405949f78c539e5e5c3c778e0460f2fde45ad3cb246d82a97e5a9492f95fe92`.
- Complete Section 1.4 source boundary, lines 289-434: 11,170 bytes; SHA-256 `fa1fec18021ed96b4fcbcbbf4e887741c566862fa2b7d407059b2c4b89bff518` under `sha256-utf8-lines-lf-v1`.
- Current target `repo/source/chapter1.tex`: 64,180 bytes; SHA-256 `f40dcba1bc87d886f6b83bd6962e9cd044d0b39282c17e326e6afbedd4f6ceee`.
- Indonesian target boundary, lines 289-434: 13,786 bytes; SHA-256 `57a5051ca741afdeb2d1e9c88413908442844b7eadff5a464fa79e453dc683af` under `sha256-utf8-lines-lf-v1`.

## Translation and mathematical audit

The complete source-order section was translated into formal Indonesian. Its protected topology matches the frozen source exactly: 27 balanced environments, including three definitions, three theorems, six proofs, one lemma, one proposition, one corollary, one example, two `align*`, two `gather`, two `tikzpicture`, and the remaining list/display wrappers; ten labels; six reference occurrences; one citation (`Je03`); seven item tokens; and five brace-aware index entries. All 163 inline mathematics fragments match in normalized sequence and multiset. The two TikZ pictures at source/target lines 395-406 remain byte-identical over their complete shared block: 481 bytes, SHA-256 `104335d1e15c5bddb8d69fd37680b5df6acc4f46d80e6889a2a69d75e96c8508`. The unit contains no exercise, hint, answer, or solution.

Independent topology, mathematical, semantic, and Indonesian-language reviews found no remaining P1 or P2 defect. Accepted language edits were applied, and all protected checks were repeated. The final translated span contains no Han-script residue, replacement character, or NUL.

### Disclosed source interventions

- `O013-LI-U005-COR-001`: source line 379 reverses the historical roles of Gödel and Cohen. The target states the standard result accurately: Gödel's 1940 constructibility result establishes relative non-refutability of the continuum hypothesis, while Cohen's 1963 forcing result establishes relative non-provability. This is a documented editorial correction, not silently attributed source wording.
- `O013-LI-U005-CLR-001`: source line 304 tacitly replaces the first injection by its left composition with the second map when replacing `Y` by `g(Y)`. The target makes that necessary adjustment explicit without altering the protected mathematics-token sequence. This is a disclosed clarification of an implicit step.
- `O013-LI-U005-READER-COR-001`: the original standalone driver omitted the earlier Chapter 1 equation count established by `eqn:infinity-axiom` at source line 49. The repaired driver initializes the equation counter to 1 immediately before loading lines 289-434. `eqn:cardinal-infinite-sum` prints as (1.2), and `eqn:cardinal-infinite-prod` prints as (1.3), matching the complete-book source order. No translated source content changed.

## Exact admitted build

- Driver: `repo/source/unit-005-bab-1-kardinal.tex`, 4,383 bytes, SHA-256 `bf58ec7ab2c9903b419ed4240d6fa134f0a2e0bfbd14051d0176cea9fcb0fc75`
- Shared interface: `repo/source/locale-ui-id.tex`, 2,972 bytes, SHA-256 `9d6c6aa162d11ce8f491703f640a808cdcf61280b300f22032d4caaa0035f3b9`; the driver adds target-only `Lema`, Noto CJK portability, and Indonesian bibliography-back-reference overrides. Upstream `AJbook.cls` remains byte-identical.
- Cover: `repo/source/coverpage-id-unit-005.tex`, 4,386 bytes, SHA-256 `fc754187209c46b9a39731510004c6aa0645036dcc4ef003c693d4f6ca37fc11`
- Frozen cross-reference witness: `repo/source/unit-005-crossrefs.aux`, 340 bytes, SHA-256 `cd05c6135e62cb225eefdc49e49d04c3c9a9c7098633c7935fb89ac9b988407d`
- Build script: `scripts/build_unit_005.ps1`, 2,838 bytes, SHA-256 `9e82eee4e4688d1b7add4026f850bdd3dc30bc7d9012e3e42cd054409b895f01`
- Backend generator: `scripts/generate_unit_005_backend.py`, 22,744 bytes, SHA-256 `1a1073a217d98536cd9a344a3227b70f6ed69ce5612859c70a881cb3a77436bf`
- Reader: `artifacts/unit-005-bab-1-kardinal.pdf`, 12 pages, 128,554 bytes, SHA-256 `205359b6c3b406a4f6595908381147e2bb3dba6aab8fdc9057436b11bec252de`
- Final log: `qa/UNIT_005_BUILD_FINAL.log`, 87,110 bytes, SHA-256 `2de97988ca56557b50822f4fbaef60784fbc21b7c3b32d184eab87236c058748`
- Public build-log summary: `qa/unit-005-evidence/build-log-summary.txt`, 3,537 bytes, SHA-256 `2fcb8f6f0a1d5061fb0611b28c28cd6c71b8692446aa536823ee85a6f2b76d82`
- Equation-number evidence: `qa/unit-005-evidence/equation-number-map.txt`, 1,072 bytes, SHA-256 `0705f9685c03210d058c7ae5db5be136ec2bbbddb2e2309ddfbf1075a10a4c28`
- Correction receipt: `qa/UNIT_005_EQUATION_NUMBER_REPAIR_20260823.md`, 3,379 bytes, SHA-256 `0e0fa9ac000da47eae95d6fd863c7e3374e9ffcc6d7d5bacfb2d4f8dee35305a`
- Replay PDF: 128,553 bytes, SHA-256 `2f3f23f16b4f3f39edaad41509730afbcc7ca28f6b16e97e6281e864291fb34c`; 12/12 Poppler and 12/12 MuPDF pages are pixel-identical at 144 dpi.
- Replay log: 87,110 bytes, SHA-256 `8718bbb92ed41833cd308892ae149b9432e55942f859339be7096f534fb80e1e`.

The final log has zero TeX errors, undefined citations/references, duplicate destinations, missing characters, or overfull boxes. Two suppressed empty-target warnings are intentional for frozen references outside this standalone unit. One underfull cover-table alignment and one underfull section-ending page are visually acceptable. Both clean AUX files independently prove the exact equation map `(1.2)` / `(1.3)`. Deterministic rendered pages are established in both Poppler and MuPDF; bit-identical XeTeX PDF containers across output directories are not claimed.

## PDF and all-page visual QA

The exact PDF has catalog language `id-ID`, 12 nonblank pages, six outline entries, 42 named destinations, 17 internal GoTo actions, three intentional URI actions, and no GoToR, Launch, JavaScript, form, or encryption. Extracted text contains no literal `??`, replacement character, NUL, Han-script residue, `Lemma`, or Chinese bibliography-back-reference phrase; the localized forms `Lema` and `dirujuk pada hlm.` and corrected equation numbers `(1.2)` and `(1.3)` are present. MuPDF and Poppler rendered every page, and all 12 pages were inspected in both engines. The standalone reader fills the readable page area without print-only blank versos. No clipping, collision, missing glyph, unreadable text, malformed formula, broken link target, or index defect remains. The PDF remains untagged; that inherited accessibility limitation stays open and is not represented as passing tagged-PDF conformance.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with Wen-Wei Li credited and independent, non-endorsed derivative status stated. The attributed `AJbook.cls` fragment remains CC BY-SA 3.0 and bundled Noto fonts remain OFL 1.1. No component rights are flattened. Production provenance records `OpenAI Codex gpt-5.6-sol, Ultra` separately from source authorship and human credit.

## Cursor

Unit 005 is admitted. The next contiguous source-order boundary is complete Section 1.5, `chapter1.tex:436-506`, `Semesta Grothendieck`. Its frozen source and still-identical target slice is 6,245 bytes, SHA-256 `4f1e14be25a0387c335ad11850aea1e3d71314e8578fa642ffecb6dbf80ffe05` under `sha256-utf8-lines-lf-v1`. Chapter-end exercises at lines 508-536 follow as a separate coherent unit so their exercise and hint identities remain explicit.
