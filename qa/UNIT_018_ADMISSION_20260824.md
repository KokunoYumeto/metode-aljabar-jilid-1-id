# Unit 018 admission - Latihan Bab 2

Status: admitted locally after independent source/translation review,
fail-closed structural and mathematical comparison, the bounded Indonesian
terminology gate, two clean builds, PDF safety and navigation checks,
deterministic backend replay, and all-page visual QA in both Poppler and MuPDF.

## Frozen content

- Authority: Wen-Wei Li, *Methods of Algebra*, Volume 1, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Range: complete Chapter 2 exercise block, `chapter2.tex:1603-1645`, including
  all thirteen top-level exercises, five nested items, and the sole source
  hint. Line 1645 closes `Exercises`; Chapter 3 is the next source-order
  boundary.
- Authority span: 43 LF line records, 5,197 UTF-8 bytes, SHA-256
  `24417872734a2dc72c1d52d0df30246a427c5bbb714faf5238679e19c8dd7cce`.
- Indonesian span: 43 LF line records, 6,523 UTF-8 bytes, SHA-256
  `d69667baae061a5d06a57dcc25033b6a971986ea704c72a0f53d687707837b55`.
- Full current target `repo/source/chapter2.tex`: 166,465 bytes, SHA-256
  `3ef0e0dd3a8a30f4e44d7f87d94a4a4343ac7097a1862180c8becaf3631cda16`.
- Independent review:
  `qa/UNIT_018_TRANSLATION_SOURCE_REVIEW_20260824.md`, 8,540 bytes, SHA-256
  `1f0728e3f4842620eeebc41b9690473f5722e651a9bda837893b19a5b2e6625b`.

## Mathematics, topology, and declared corrections

The fail-closed checker preserves all 18 `\item` nodes: thirteen top-level
exercise sections and five nested subparts. It also preserves the one hint,
80 inline-math surfaces, two bracketed displays, one `align*` display with a
`cases` construction, one `tikzcd` diagram, ten arrows, and three references.
The backend deliberately represents the mathematical surface at a slightly
finer granularity and therefore records 83 formula entities. The target has no
Han residue. No answer or solution has been invented.

- `O013-LI-U018-COR-001` removes the duplicated field predicate at source line
  1640. The source repeats the same requirement twice; the target states it
  once without changing the mathematical condition.
- `O013-LI-U018-COR-002` binds the previously free forgetful-functor symbol
  `U` at source line 1644, making the functor named in the exercise explicit.

Both repairs are separately disclosed as `O013-ADV-0049` and
`O013-ADV-0050` in `00_control/ADVERSE_LEDGER.jsonl`; neither is silently
attributed to the source author. The checker is
`scripts/check_unit_018_structure.py`, 15,157 bytes, SHA-256
`9b8a165adbd31532c7a7f6458d7e5c0a86f224e699188bce403d55ad7e8d76c2`.

## Terminology gate

The finite official arXiv search found no representative Indonesian source in
this field with downloadable TeX. The recorded fallback therefore uses the
openly readable four-page UNDIP category-theory thesis chapter (163,251 bytes,
SHA-256 `611b78c88407037489f22814bf054e00ff0f283c702a06082a3a583e9ab35fcb`)
and seven-page UGM algebra article (382,376 bytes, SHA-256
`4099c3d8aff59e723470f69b4d152b037261bc26d54ef74f1365377f05c25834`),
with the official Indonesian mathematics glossary used for adjudication. The
fallback is reported honestly and is not claimed to attest every specialized
term.

Eight Unit 018 terminology rows are admitted. Fifteen additional monoidal
rows prepared for the following Chapter 3 candidate remain explicitly marked
`candidate`; they are not treated as Unit 019 admission. No earlier admitted
reader required a terminology correction. Exact evidence and decisions are in
`qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md`, 18,608 bytes,
SHA-256 `cc6400d922951ab474cf1dee0df3d12dc93183267723df0119b2b93731bb16e5`,
and `authority/terminology-qa-20260822/MANIFEST.json`, 10,890 bytes, SHA-256
`b7693af6ac42028a8de495ee044c26cc1106837487f371b7402f7fb88134007a`.
The controlled glossary is 35,880 bytes, SHA-256
`8d1ee2c145a76b000f57264fa5e80abb3a9781ffd21b57f0b98d91b52c2c0bc9`.

## Reader, reflow, and build QA

The admitted reader is `artifacts/unit-018-bab-2-latihan.pdf`: four pages,
83,578 bytes, SHA-256
`4fc2997e6eafc8f2e74d8a03e3351cb49d99a95ae96ff254a211fbf505f6e00c`.
It declares `id-ID`, preserves Wen-Wei Li as author, and has one outline
(`Latihan`), eighteen named destinations, and three intentional URI links.
All 23 fonts are embedded and subset. The PDF is unencrypted, has no form or
JavaScript, and has extractable nonempty text on every page. It is honestly
recorded as untagged; language metadata, outline, destinations, and text
extraction are present but are not misrepresented as a tagged structure tree.

The digital cover was reflowed into a centered title hierarchy and an explicit
plain-language coverage panel stating that the reader contains thirteen
exercises and the hint for Exercise 8. The ambiguous filled/unfilled decorative
blocks were removed. All exercise pages use the available text width, and the
reader ends with Exercise 13 rather than sparse generated back matter.

Clean builds D and E have different PDF containers (83,564 bytes, SHA-256
`f36ecf4ba755bf44c61c6d9070b11a50f4c5e2763d82f8e4aa7bd88a98444486`;
and the admitted artifact identity above), so byte-identical PDFs are not
claimed. Their layout-preserving text is byte-identical, SHA-256
`abc664dc1a3a85a2c26caa91a4da38155f55f9bac558e7dbacb84d204f92b3ac`.
All 4/4 Poppler page rasters and all 4/4 MuPDF page rasters are byte-identical
within renderer across the two builds, and every final page was inspected in
both renderers. There is no clipping, collision, malformed formula or arrow,
missing glyph, blank page, or anomalous answer field.

The complete sanitized final log is `qa/UNIT_018_BUILD_FINAL.log`, 77,518
bytes, SHA-256
`5a4cbdacbed40af2576f6a7c85fe365eaa26a02f9298635e63f62b8823bc8398`.
Sanitization replaces only the complete machine-local home prefix and removes
no diagnostic line. The log has zero overfull boxes, undefined control
sequences/references/citations, missing characters, fatal errors, and emergency
stops. Three underfull front-matter boxes and three deliberately suppressed
empty external-reference targets are nonblocking and were visually checked.
Deterministic evidence is under `qa/unit-018-evidence/`; its structure/PDF
record is 3,988 bytes, SHA-256
`9831012cae24bfa33f59add2de7b884b4e8c835c0162818cb1cea8978e7b29fe`.

## Modular backend

The canonical record `backend/data/unit-018-bab-2-latihan.json` is 136,912
bytes, SHA-256
`c761b3b1fbdceb0930d9e6d19fc23885c1b21a019db4d48cbf35bb57cedea794`.
It contains 172 stable entities and 127 concept-compatible entities, including
thirteen exercise sections, five nested items, one hint, 83 formula entities,
three reference entities, one diagram, two corrections, and eighteen
prerequisites. It records zero citations, answers, and solutions rather than
inventing them.

The six deterministic CSV projections are:

- `unit-018-bindings.csv`: 14,549 bytes, SHA-256
  `e463509cfeed286af367155a31e30ab34589bf11e3e0a9de831af2662c5e91af`;
- `unit-018-entities.csv`: 31,546 bytes, SHA-256
  `e95bba10c1e639a96c4c25ea75a939ab1fceb5d8f4f0bca8d5917e16f256c251`;
- `unit-018-qa.csv`: 2,001 bytes, SHA-256
  `19e62ccfe5dac6d03c65f59b9050a76a15d4bf0e9ab5ae2e2a34a168b0a67893`;
- `unit-018-relations.csv`: 103,647 bytes, SHA-256
  `411ef794b36ad87ed5a42fa41420dae0766e148e472c7a2ef9f1979f8a514993`;
- `unit-018-rights.csv`: 1,287 bytes, SHA-256
  `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e`;
- `unit-018-surfaces.csv`: 482 bytes, SHA-256
  `a25fcc3b922f7240fce820f0648563197a484d7706829aacd89d0237f99b05ce`.

Consecutive generator/validator runs reproduced all seven backend outputs
byte-for-byte. The generic schema validator and Unit 018 fail-closed validator
pass against live source, target, reader, final log, structured QA, rights,
corrections, terminology, and exact model provenance. The validation record is
3,042 bytes, SHA-256
`72ddd58cad3414a28bf2e57a6a8f9247b700466887491599b27c79b27bc25179`.

## Rights and provenance

Wen-Wei Li remains the source author. Principal source text and Indonesian
translation are CC BY 4.0. The credited `AJbook.cls` fragment retains CC
BY-SA 3.0; `Lanzhou.png` in the wider closure also retains CC BY-SA 3.0 but is
not used by this reader; bundled Noto fonts retain OFL 1.1. Rights are not
flattened into one blanket claim. This is an independent, non-endorsed
derivative.

Production provenance is separate from authorship and every human credit and
records the exact identification `OpenAI Codex gpt-5.6-sol, Ultra`.
