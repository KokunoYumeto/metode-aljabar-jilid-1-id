# Unit 017 admission - Kelengkapan

Status: admitted locally after independent source/translation review,
fail-closed structural and mathematical comparison, the bounded Indonesian
terminology gate, two clean builds, PDF safety and navigation checks,
deterministic backend replay, and all-page visual QA in both Poppler and MuPDF.

## Frozen content

- Authority: Wen-Wei Li, *Methods of Algebra*, Volume 1, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Range: complete `chapter2.tex:1406-1602`, all of Section 2.8 and its trailing
  separator, but no part of the Chapter 2 exercise block. Line 1603 begins
  `\begin{Exercises}` and is the next source-order boundary.
- Authority span: 197 line records, 15,810 UTF-8 bytes, SHA-256
  `ccc5a17cbf856e59e7b8abbff8fd542c5deb399e58b6fc7a5a0f448c7c019e92`.
- Indonesian span: 197 line records, 18,633 UTF-8 bytes, SHA-256
  `e27dba97355122446714b8e58f71f80edbb1d74e6160f99ba0b8160e7c3ec30b`.
- Full current target `repo/source/chapter2.tex`: 165,139 bytes, SHA-256
  `be7c571d574e7c8608f535f59627c47118cdb7f00a44aaf1e7d85eb11ea60e35`.
- Independent review:
  `qa/UNIT_017_TRANSLATION_SOURCE_REVIEW_20260824.md`, 9,189 bytes, SHA-256
  `abfe9f4121cf7e01897e5c19a65f1d34c4c1a626fe251f48edabd814e4b38bde`.

## Mathematics, topology, and declared corrections

The fail-closed checker preserves all 197 line records and the blank-line
boundary, 749 active commands, 39 active environment pairs, eleven labels,
32 active ordinary references (35 raw occurrences), five equation references,
nine index entries, 21 items, 185 active inline-math surfaces (199 raw), four
bracketed displays, three `equation` environments, two `align*` environments,
nine `tikzcd` diagrams, and 47 arrows. The target has no Han residue. Whole
math-span relocations required by Indonesian syntax were adjudicated by exact
per-line mathematical multisets; formulas and protected topology remain
unchanged except for the six disclosed source repairs below. The checker is
`scripts/check_unit_017_structure.py`, 29,897 bytes, SHA-256
`688d3e0e55df8f6db75ce8e5adc686b28b75e510fd4c5aaf36e40e233beab4fd`.

- `O013-LI-U017-COR-001` changes the comparison-leg label at source line 1525
  from `\alpha(j)` to `\alpha(i)`, matching its domain `F\alpha(i)`.
- `O013-LI-U017-COR-002` changes the coproduct of abelian groups at line 1554
  from “direct product” to the mathematically correct “direct sum.”
- `O013-LI-U017-COR-003` changes `\Obj(i)` at line 1585 to `\Obj(I)`.
- `O013-LI-U017-COR-004` changes two Hom domains at lines 1588-1589 from
  `\cate{C}_1` to `\cate{C}_2`, as required by the objects in those terms.
- `O013-LI-U017-COR-005` replaces two unjustified surjective projection arrows
  at lines 1589-1590 by ordinary arrows; the argument proves commutativity,
  not surjectivity.
- `O013-LI-U017-COR-006` restores the missing functor application at line 1547,
  changing `\varprojlim\beta` to `\varprojlim(F\beta)`.

All six repairs are separately disclosed as `O013-ADV-0043` through
`O013-ADV-0048` in `00_control/ADVERSE_LEDGER.jsonl`; none is silently
attributed to the source author.

## Terminology gate

The finite official arXiv search found no representative Indonesian source in
this field with downloadable TeX. The recorded fallback therefore uses the
openly readable four-page UNDIP category-theory thesis chapter (163,251 bytes,
SHA-256 `611b78c88407037489f22814bf054e00ff0f283c702a06082a3a583e9ab35fcb`)
and seven-page UGM algebra article (382,376 bytes, SHA-256
`4099c3d8aff59e723470f69b4d152b037261bc26d54ef74f1365377f05c25834`),
with the official Indonesian mathematics glossary used for adjudication. The
fallback is reported honestly and is not claimed to attest every specialized
limit term.

The Unit 017 delta adds sixteen controlled completeness, pullback/pushout,
direct-product/direct-sum, free-product, and difference-kernel terms. No
earlier admitted reader required a terminology correction. Exact evidence and
decisions are in
`qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md`, 16,797 bytes,
SHA-256 `ec6fdf9bee950fd7ba7ce48a779b5da0475f8cb6cd29489c963c0b01c1f03333`,
and `authority/terminology-qa-20260822/MANIFEST.json`, 8,113 bytes, SHA-256
`85b8e6fb9b540d170fd8aad23995e28ae199c06e302d5d0abff756523e3ee70d`.
The controlled glossary is 31,697 bytes, SHA-256
`4cdef514de666a002681f593cb5578322dc19c3e9101da20f2caabc415d4cd08`.

## Reader, reflow, and build QA

The admitted reader is `artifacts/unit-017-bab-2-kelengkapan.pdf`: nine pages,
112,236 bytes, SHA-256
`bfcec32b3ba20f8c170a3389a1b651613f1fa437945662ca32dd62fcf0edba5e`.
It declares `id-ID`, preserves Wen-Wei Li as author, and has exactly two
outline entries (`2.8 Kelengkapan` and `Indeks Istilah`), 36 named
destinations, seventeen internal `GoTo` links, and three URI links. All 21
fonts are embedded and subset. The PDF is unencrypted, has no form or
JavaScript, and has extractable nonempty text on every page. It is honestly
recorded as untagged; language metadata, outlines, destinations, and text
extraction are present but are not misrepresented as a tagged structure tree.

The standalone digital reader uses 1.25 line spacing. The generated term index
was reflowed onto the final prose page instead of creating a nearly empty tenth
page; no mathematical, semantic, reference, diagram, or index surface was
removed. The resulting text block and index are centered, legible, and
unclipped.

Clean builds F and G have different PDF containers (112,241 bytes, SHA-256
`83ea6217a19f0576a7410287e85aef2a2b2a8beb76c3ac1f3b50dd1edeecc5e6`;
and the admitted artifact identity above), so byte-identical PDFs are not
claimed. Their layout-preserving text is byte-identical, SHA-256
`11333ab6db1c982579b217a57c4fe500a45df08f280ebeff1c499a2d6ec299d7`.
All 9/9 Poppler page rasters and all 9/9 MuPDF page rasters are byte-identical
within renderer across the two builds, and every final page was inspected in
both renderers. There is no clipping, collision, malformed formula or arrow,
broken index entry, missing glyph, blank page, or anomalous answer field.

The complete sanitized final log is `qa/UNIT_017_BUILD_FINAL.log`, 86,651
bytes, SHA-256
`106cbc3802e4144912cafcedd78ae79b30b3d3e6fee40645e28ce31c7cfa3b72`.
Sanitization replaces only the complete machine-local home prefix and removes
no diagnostic line. The log has zero overfull boxes, undefined control
sequences/references/citations, missing characters, fatal errors, and emergency
stops. Three underfull hboxes, one underfull vbox, 27 deliberately suppressed
empty external-document link targets, and one final MakeIndex reminder are
nonblocking and were visually checked. Deterministic evidence is under
`qa/unit-017-evidence/`; its structure/PDF record is 7,547 bytes, SHA-256
`7b8191fc9b261285046b9d335c14eadd32fbbb9accdcd6f4a2c8b0571d04065c`.

## Modular backend

The canonical record `backend/data/unit-017-bab-2-kelengkapan.json` is 245,910
bytes, SHA-256
`06571ea0d8a1a76f93e54dbe78fb3fc24f2692ba104b0b96d94e2da690fd47d4`.
It contains 353 stable entities and 304 concept-compatible entities, including
209 formula surfaces, all eleven labels, 35 ordinary-reference occurrences,
five equation-reference occurrences, nine diagrams, nine index entries, six
corrections, and eighteen prerequisites. This source section has no exercises,
hints, answers, solutions, or citations; the backend records zero rather than
inventing them.

The six deterministic CSV projections are:

- `unit-017-bindings.csv`: 17,225 bytes, SHA-256
  `5fe01e7e75a400f124089fcbb01b8b49497d7cab3a68e161139b0f4284da63b4`;
- `unit-017-entities.csv`: 68,736 bytes, SHA-256
  `11f10bcdc90bc155a977a3e684fdacc497ac26bdf6ea4f015d9c2b4b29e0dc14`;
- `unit-017-qa.csv`: 1,755 bytes, SHA-256
  `fe4818c3664cf7f0abd453468d191399322e6bb90b937979d05722af48db59f5`;
- `unit-017-relations.csv`: 169,082 bytes, SHA-256
  `0216ad5e8e2f8871e5734f6a2c40e702e1b9f66318ea485fd0eab8f4a9c2c229`;
- `unit-017-rights.csv`: 1,287 bytes, SHA-256
  `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e`;
- `unit-017-surfaces.csv`: 4,142 bytes, SHA-256
  `000c8062ea172724e07a8e3b40e050c245320cc2198428e2ecbfe63b41787668`.

Consecutive generator/validator runs reproduced all seven backend outputs
byte-for-byte. The generic schema validator and Unit 017 fail-closed validator
pass against live source, target, reader, final log, structured QA, rights,
corrections, and exact model provenance. The validation record is 2,264 bytes,
SHA-256 `05442272d0f68cfc1da2487a78223afec9ca13e8500f22f8bf2bcc3bdee30770`.

## Rights and provenance

Wen-Wei Li remains the source author. Principal source text and Indonesian
translation are CC BY 4.0. The credited `AJbook.cls` fragment retains CC
BY-SA 3.0; `Lanzhou.png` in the wider closure also retains CC BY-SA 3.0 but is
not used by this reader; bundled Noto fonts retain OFL 1.1. Rights are not
flattened into one blanket claim. This is an independent, non-endorsed
derivative.

Production provenance is separate from authorship and every human credit and
records the exact identification `OpenAI Codex gpt-5.6-sol, Ultra`.
