# Unit 002 admission receipt - Bab 1: Ikhtisar aksioma ZFC

Date: 2026-08-22  
Decision: admitted as the second independently buildable `id-ID` reader unit. The corrected 12-page digital reflow recorded below supersedes the original 15-page standalone rendering without changing the admitted translation span. Earlier 15-page figures in this receipt are retained as historical admission evidence only.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit: `c4f7a01f68f5f407906b4b970640cddbbad85f6b`
- Upstream tree: `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Complete frozen source `chapter1.tex`: 49,874 bytes; SHA-256 `3405949f78c539e5e5c3c778e0460f2fde45ad3cb246d82a97e5a9492f95fe92`
- Frozen source boundary lines 1–86: 11,351 bytes; SHA-256 `7084d69f11f213ec10c2fcef49da5e467e5d1df29f95fecb13f2873998fd45e3`
- Translated content span: source and target lines 9–85; the target-only guard at line 86 stops the standalone reader before untranslated Section 1.2 without affecting a full-book build.
- Current target `repo/source/chapter1.tex`: 53,880 bytes; SHA-256 `61d85d23378185edc836e67bbb00a7acb90c36914040228bcacfae8a15ae0dee`
- Target boundary lines 1–86: 15,356 bytes; SHA-256 `2e4045bc02ea751cbe0896ab370e4d26fa113048a651aef49e5608c049b698d4`

## Translation and mathematical audit

The chapter orientation and complete Section 1.1 were reviewed in source order against the frozen Chinese source. All environment order, 18 item tokens, 131 mathematics blocks (128 inline and three displayed), labels `sec:ZFC` and `eqn:infinity-axiom`, forward references `hyp:universe`, `sec:Grot-universe`, and `sec:order`, five unique citation keys, and twelve index entries are retained. The three symbol-index payloads remain mathematical source forms; the nine default-index sort keys are localized for Indonesian lookup while their original keys remain provenance data.

An independent semantic audit found and corrected three translation defects: Cantor's phrase now refers to perception rather than intuition; the separation/replacement axiom families, rather than their predicates/functions, are identified as schemas; and the closing assessment retains the source's “fortunately or unfortunately” force. A separate structural audit found no mathematical or topology discrepancy. Permitted source-language residue in the active span is limited to Wen-Wei Li's name in a comment; Chinese bibliographic titles remain correctly preserved as source metadata. This unit contains no diagram, exercise, hint, answer, or solution.

## Frozen forward-reference boundary

The three references leaving this reader are frozen from the authoritative full Chapter 1 witness: Section 1.2, Section 1.5, and Hypothesis 1.5.{2}. `repo/source/unit-002-crossrefs.aux` contains only those verified numbers and an empty external-document URL. Consequently, the displayed numbers are correct while the standalone PDF creates no false links to a missing external file.

## Exact admitted build

- Driver: `repo/source/unit-002-bab-1-zfc.tex`, 2,585 bytes, SHA-256 `d665bf1ad9706dbe1fc1e34511bb336197166ba4711df9a67a57460a24a342cc`
- Target-only interface localization: `repo/source/locale-ui-id.tex`, 575 bytes, SHA-256 `f5ad48e65aed9de1a036c19fd04408077965948f82901ef73d8cadd32ee67100`; upstream `AJbook.cls` remains byte-identical to the frozen closure.
- Cover: `repo/source/coverpage-id-unit-002.tex`, 4,357 bytes, SHA-256 `3428c60e35170b5133cc547e6b3c8b6025a6d78fae26aa33603fddd1fd3425af`
- Localized title wrapper: `repo/source/titles-setup-id.tex`, 329 bytes, SHA-256 `db020adff03242f1f2fe8bcb6ec74b6072d9db6bd44971caadde3ce231a51f1b`
- Frozen reference witness: `repo/source/unit-002-crossrefs.aux`, 372 bytes, SHA-256 `57c7132d2579ed6240a310a0792250adde2d6302b1deb7942dc2d1d3229bcb6d`
- Build script: `scripts/build_unit_002.ps1`, 2,843 bytes, SHA-256 `6698ea811ea2ef9676a99eb3bbf15797dbc6cbc1985d03ff115a4b7b63ac3570`
- Reader: `artifacts/unit-002-bab-1-zfc.pdf`, 161,687 bytes, SHA-256 `df709d43505dabd365d04fd8f9a90dac7d9c4ab686d677bbae50bed7bf7d61d2`
- Portable build-log summary: `qa/unit-002-evidence/build-log-summary.txt`.
- Toolchain witness: MiKTeX 26.5 XeLaTeX, Biber 2.21, both default and `sym1` MakeIndex passes, then three convergence passes; shell escape disabled.
- Result: 15 pages; zero TeX errors, undefined citations, undefined references, duplicate destinations, missing-character warnings, literal `??`, replacement characters, or imported untranslated tail text.
- Navigation: catalog language `id-ID`; five outline roots and six total outline entries; 35 named destinations; 29 internal GoTo actions, six intentional URI actions, no GoToR/Launch action, and no unresolved named internal destination.
- Two small overfull boxes (largest 7.93658 pt) are visually contained. Three suppressed empty-target messages are the intended false-link prevention for frozen forward references.

`SOURCE_DATE_EPOCH=1787356800` fixes the compilation timestamp. Two clean builds in different output directories rendered to 15 pairwise pixel-identical 144-dpi MuPDF pages. XeTeX serialized the containers to different byte lengths and hashes, so bit-identical PDF reproduction across output directories is not claimed.

## Visual and portability audit

The exact admitted PDF was rendered in full with MuPDF and Poppler: 15/15 pages from each renderer. MuPDF produced no stderr and was the authoritative visual witness. The installed Poppler emitted only its known local Adobe-GB1 CMap/font warnings; the MuPDF render shows the embedded bibliographic CJK text correctly. Visual review caught the class-generated Chinese reading-box label and the target now emits `Petunjuk membaca` through a target-only interface wrapper; the frozen source class remains unchanged. Every page and the three dense reader pages were then inspected at full resolution. No clipping, collision, unintended blank content, broken formula, bad header, unreadable index, or pagination defect was found. Blank recto pages before the chapter and indexes are deliberate book-class transitions.

Local all-page evidence is under `qa/unit-002-final-r7/`; the deterministic replay evidence is under `qa/unit-002-final-r7-replay/`; compact portable evidence is under `qa/unit-002-evidence/`.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with Wen-Wei Li credited and the independent, non-endorsed derivative status stated. Component exceptions remain separately recorded: the source-map fragment in `AJbook.cls` and `Lanzhou.png` are CC BY-SA 3.0, while bundled Noto fonts use OFL 1.1. Admission does not flatten these component rights.

## Corrected digital-reader boundary

After the original admission, the shared target interface exposed that all
theorem-family headings inherited Chinese labels from `AJbook.cls`, and the
standalone digital reader retained three print-only blank verso pages. The
target-only wrapper now localizes the reading box, theorem, proof, example,
exercise, bibliography, and index labels while preserving the frozen upstream
class byte-for-byte. The driver maps `cleardoublepage` to `clearpage` for this
standalone reader only.

- Current shared target `repo/source/chapter1.tex`: 56,831 bytes, SHA-256
  `eedc388ca9ea681701e4306095674fcadcf93a82bc6a1c02dfcfe5d1a528a10a`.
  Unit 002's live ranged boundary remains lines 9-85 with normalized SHA-256
  `f67693ca54f1881c8f91f20655e82d89a08833611eafc41ce352a6dfddec67d0`.
- Corrected driver: 2,705 bytes, SHA-256
  `b502a4ea48b6affce447e78ad148681458a1fac778d9146a9bd56d4d3f6802d4`.
- Corrected localization wrapper: 2,972 bytes, SHA-256
  `9d6c6aa162d11ce8f491703f640a808cdcf61280b300f22032d4caaa0035f3b9`.
- Corrected reader: 12 pages, 161,147 bytes, SHA-256
  `ff2eb3fd1ec5abaa7989d0c29c419c04f99368dc3f278799be460e30042bfe58`.
- Final log: 83,917 bytes, SHA-256
  `4891c6c8f1c802a59792c1bbda102bb64544b02c95792c149560faab275d264e`.
- Replay PDF: 161,147 bytes, SHA-256
  `6f28396b9a37c115939272c400ac7789791aa3c3c867f9e612520e84e56413ef`;
  all 12 MuPDF pages are pixel-identical at 144 dpi.

The corrected PDF has catalog language `id-ID`, 12 nonblank pages, five
outline roots/six total entries, 33 named destinations, 29 internal GoTo
actions, six intentional URI actions, and no GoToR or Launch action. It has no
literal `??`, replacement character, or Chinese environment heading. The log
has no TeX error, undefined citation/reference, duplicate destination, or
missing character. Two overfull boxes, largest 7.93658 pt, remain visually
contained; three suppressed empty-target warnings are intentional frozen
forward-reference behavior. MuPDF and Poppler rendered all 12 pages, and every
page was re-inspected without clipping, collision, broken formula, unreadable
glyph, unintended blank page, or index defect.

## Cursor

Unit 002 is admitted. The next contiguous translation cursor is Section 1.2 of `repo/source/chapter1.tex`, beginning after the standalone-reader guard; the remainder of Chapter 1 and Chapters 2–10 stay in the source language until reviewed and admitted in later units.
