# Unit 016 admission - Limit

Status: admitted locally after independent source comparison, protected-topology
and semantic review, the bounded Indonesian terminology gate, two clean builds,
PDF safety checks, deterministic backend validation, and all-page visual QA in
both Poppler and MuPDF.

## Frozen content

- Authority: Wen-Wei Li, *Methods of Algebra*, Volume 1, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Range: complete `chapter2.tex:1111-1405`, all of Section 2.7 and no part of
  Section 2.8. Line 1406 begins `\section{完备性}` and is the next source-order
  boundary.
- Authority span: 295 line records, 24,790 UTF-8 bytes, SHA-256
  `48abd6c33ecdc32591a05ecfbdc7381637027963a61cb3015016909a8faacf82`.
- Indonesian span: 295 line records, 28,854 UTF-8 bytes, SHA-256
  `fe5e54d56824e8f1a76f93e1732220813c654ab16eb2d7c8daa8dcdde17f5c81`.
- Full current target `repo/source/chapter2.tex`: 162,316 bytes, SHA-256
  `644f98e065dae5761ae6cd41a334704ca890837537e4eb0d90fb2ed794536a0b`.
- Independent translation/source review:
  `qa/UNIT_016_TRANSLATION_SOURCE_REVIEW_20260824.md`, 6,711 bytes, SHA-256
  `d9ea4d0b501d76c4210834752a4a7f9f9199c534e0263687eee7a6654786cecc`.

## Mathematics, topology, and declared corrections

The fail-closed structural checker preserves the complete 295-line and
blank-line topology, 287 inline-math surfaces, twelve bracketed display blocks,
66 environment pairs, seventeen labels, 21 ordinary references, seven equation
references, one citation, thirteen indexes, nine items, 23 `tikzcd` diagrams,
and 98 arrows. Label/reference/citation argument order and every diagram are
unchanged. The target has no Han residue. Its 1,384 TeX command tokens differ
from the source's 1,382 only by the two explicit `\in` binders in correction
003, after two legitimate `\emph` relocations required by Indonesian word
order. The checker is `scripts/check_unit_016_structure.py`, 23,287 bytes,
SHA-256
`0b5534fa3f7b427ec416a9ab45d236ec20135215f43bcffc89effb3b0ef824b7`.

- `O013-LI-U016-COR-001` is typographic: authority line 1177 duplicates
  `p_i:` immediately before the arrow already labelled `p_i`; the target
  removes only the redundant prefix.
- `O013-LI-U016-COR-002` repairs prose/order: authority lines 1338-1343
  construct the right iterated-limit term first but call it the left term. The
  Indonesian prose names the right term first without altering the formula.
- `O013-LI-U016-COR-003` binds the free index in authority line 1348 by writing
  `\varinjlim_{i \in I}\alpha(i)` and
  `\varprojlim_{i \in I}\beta(i)`.

The live and archived source errata were also checked. The frozen authority
already contains the corrected cone/cocone order and both corrected `\mapsto`
arrows after Equation (2.11), so the target preserves them and does not count
them again as new repairs.

## Terminology gate

The official bounded arXiv queries found no suitable Indonesian same-field
source with downloadable TeX. The honest PDF fallback remains the four-page
UNDIP category-theory chapter (163,251 bytes, SHA-256
`611b78c88407037489f22814bf054e00ff0f283c702a06082a3a583e9ab35fcb`)
and seven-page UGM algebra article (382,376 bytes, SHA-256
`4099c3d8aff59e723470f69b4d152b037261bc26d54ef74f1365377f05c25834`).
All eleven pages had been inspected directly. They support the controlled
field-language family `fungtor`, `transformasi natural`, `kategori`, and
`gelanggang`; no claim is made that they directly attest every specialized
limit term.

The Unit 016 delta adds the controlled limit, colimit, cone/cocone,
equalizer/coequalizer, filtered-category, finite-limit, quotient/subspace
topology, and associativity/commutativity-constraint families. Exact identities
and decisions are in
`qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md`, 14,847 bytes,
SHA-256
`cefc74a37195e635ba560e1b0d1fd08ffd78ab48d1386eeab771d1d11d422924`,
and `authority/terminology-qa-20260822/MANIFEST.json`, 6,727 bytes, SHA-256
`5654685c2d43697c8cad9783bbc2ec514da318f473d2ae9e9d0bddcca59886fd`.
No earlier admitted reader required a terminology correction at this gate.

## Reader and build QA

The admitted reader is `artifacts/unit-016-bab-2-limit.pdf`: sixteen pages,
159,462 bytes, SHA-256
`6d6838019efca962d7282c7be3df136f32abed3a8f111f2e4e5996bbeb4d789b`.
It declares `id-ID`, correct source-author and work metadata, four outline
entries, 36 annotations, extractable text on every page, and 25 embedded,
subsetted fonts. It is not encrypted and contains no form or JavaScript.

Two clean builds B and C produced, respectively, 159,461-byte container hash
`c8b4a4b88c8740e56e25a2f3946ef695d9af6505401b6cd1da1461ebed65be9a`
and the admitted hash above. Container identity is therefore not claimed. The
layout-preserving text extraction is byte-identical with SHA-256
`c7586018f2b5ebc9cef75adc3b559539eb48cb2a228934129f11618dfb853615`,
and all 16 Poppler and all 16 MuPDF page rasters are byte-identical within each
renderer across the two clean builds.

Every page was inspected at original rendered resolution in both renderers.
No clipping, collision, malformed formula or arrow, broken index entry,
missing glyph, blank page, or anomalous answer-field box is present. The
mathematical pages use the live text area legibly and remain centered. Pages
13-16 are intentionally sparse because the section ends and the bibliography
and two generated indexes begin on conventional separate back-matter pages;
this is not a crop or reflow failure.

The final public log is `qa/UNIT_016_BUILD_FINAL.log`, 85,426 bytes, SHA-256
`b24d68481c1429e700767be361ee64b9b61b50389fc8100065195111c42e9b08`.
It is a deterministic complete transcript of the final build with only the
machine-local home-directory prefix replaced by `${USER_HOME}`; no diagnostic
line is removed.
It contains no overfull box, undefined control sequence/reference/citation,
missing character, fatal error, or emergency stop. Two underfull hboxes, three
underfull vboxes, ten intentionally suppressed empty external-document link
targets, and two final MakeIndex reminders are nonblocking and were visually
checked. Machine-readable build, render, structure, and visual evidence is
under `qa/unit-016-evidence/`.

## Modular backend

The canonical record `backend/data/unit-016-bab-2-limit.json` is 330,876 bytes,
SHA-256
`65843e899406b6d450fe913d6d99985a8a019e6a8f7a1805b79482382fab1db9`.
It contains 461 stable entities and 394 concept-compatible entities, including
313 formula surfaces, all seventeen labels, 21 ordinary and seven equation
references, one citation, 23 diagrams, thirteen indexes, three corrections,
and seventeen prerequisites. This source section has no exercises, hints, or
solutions, and the backend records zero rather than inventing them.

The six deterministic CSV projections are:

- `unit-016-bindings.csv`: 27,419 bytes, SHA-256
  `4509f8fa227da8a9e4bf7c706a227aafaf5bb7e2414490895fdd8168b2fa059e`;
- `unit-016-entities.csv`: 92,169 bytes, SHA-256
  `4e9add6aeaaad6f3b21f37b93d0244121ce64d73be1dd706ba58092b09ce89ad`;
- `unit-016-qa.csv`: 1,671 bytes, SHA-256
  `8b760abdbdf34d9aaa34351c9fde8358842e8866725028a1d798d1b4d512e44f`;
- `unit-016-relations.csv`: 212,640 bytes, SHA-256
  `e5a986098da84a1322a3ca5f897eac08262e140e74611a5f00f53ec99f66051d`;
- `unit-016-rights.csv`: 1,287 bytes, SHA-256
  `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e`;
- `unit-016-surfaces.csv`: 7,991 bytes, SHA-256
  `a39e8f17f83214a65284d6c4958f3af13304dda4f186303ce0521834163827e5`.

Two consecutive generator runs reproduced all seven backend files byte for
byte. Both the generic schema validator and the unit-specific fail-closed
validator pass against the live source, target, PDF, log, QA evidence, rights,
and model-provenance bindings.

## Rights and provenance

Wen-Wei Li remains the source author. The principal source text and Indonesian
translation are CC BY 4.0. The credited `AJbook.cls` fragment retains CC
BY-SA 3.0; `Lanzhou.png` in the wider closure retains CC BY-SA 3.0 but is not
used by this reader; bundled Noto fonts retain OFL 1.1. Rights are not flattened
into one blanket claim. This is an independent, non-endorsed derivative.

Production provenance is separate from authorship and human credit and records
the exact identification `OpenAI Codex gpt-5.6-sol, Ultra`.
