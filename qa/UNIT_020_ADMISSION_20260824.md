# Unit 020 admission — Keketatan dan Teorema Koherensi

Status: **admitted locally** after independent source/translation review,
fail-closed mathematics and topology comparison, terminology adjudication,
two clean builds, PDF structure and safety checks, deterministic backend
replay, and all-page visual QA in both Poppler and MuPDF.

## Frozen content and boundary

- Authority: Wen-Wei Li, *Methods of Algebra*, Volume 1, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Range: complete Section 3.2, `chapter3.tex:228-306`. Authority line 306 is
  the included blank separator; line 307 begins Section 3.3 on braiding and is
  excluded.
- Authority span: 79 LF records, 6,071 bytes, SHA-256
  `86f02abb667e1f03a99e89f34982527fbb715eb55496f9c76c576e041076d737`.
- Indonesian target span: `repo/source/chapter3.tex:227-305`, 79 LF records,
  7,266 bytes, SHA-256
  `25f8aa41663253a28ac27c3cf635470ac2e20e69d48b168d98cb025a3a792270`.
- Full current target: 80,889 bytes, SHA-256
  `64d334af911539cbe844a250ab41c3e6d537e2c827919c21d41547e1f5782d7a`.
  Target lines 1-226 retain the admitted Unit 019 identity, while target lines
  306-910 are byte-identical to authority lines 307-911.
- Independent continuous review:
  `qa/UNIT_020_TRANSLATION_SOURCE_REVIEW_20260824.md`, 7,282 bytes, SHA-256
  `e3edf18ac72fc56ca13102f6bb1d469f6c7cc80e3898eb75727b0f96d6ef912c`.

## Mathematics, topology, and declared correction

The fail-closed checks preserve thirteen ordered environment pairs, ten
items, three labels, five references, three citation occurrences, 64 inline
mathematics surfaces, five bracket displays, one five-node/five-edge TikZ
pentagon, one four-arrow `tikzcd` square, and two index entries. The target
span contains no Han residue. The independent audit is
`qa/UNIT_020_MATH_STRUCTURE_AUDIT_20260824.md`, 6,653 bytes, SHA-256
`fec00992eed71e9b62d65a2b5a28e9e5ba2d83b00e7e4753109d171bc8dfdad3`.

`O013-LI-U020-COR-001` replaces the undefined datum `(F,m)` at authority line
299 with the already defined object datum `(F,\rho)`. Authority lines 254-255
define the objects and the family `\rho`; no datum `m` is introduced. The
target contains zero `(F,m)` signatures and exactly the defining and corrected
`(F,\rho)` signatures. No other mathematical command or formula changes. The
dedicated provenance record is `qa/UNIT_020_SOURCE_CORRECTION_20260824.md`,
3,406 bytes, SHA-256
`1fd9438599ba395f4125e2b3b981ec13c142b3225377c29a0ace03cccbb7a62c`.

The canonical checker is `scripts/check_unit_020_structure.py`, 21,048 bytes,
SHA-256
`a4bdd19b4104d799cbb28a235898b8883aafecfbdb0bb5cca1e83d7e4f7b96b8`.
The isolated-candidate checker and an independent second implementation agree
with it; argument overrides and any topology or boundary drift fail closed.

## Terminology gate

Exactly four specialized Unit 020 rows are admitted: `kategori monoidal
ketat`, `keketatan`, `koherensi`, and `teorema koherensi Mac Lane`. The
bounded audit explicitly records that the retained 2008 mathematics glossary
offers abstract `coherence -> kekoherenan`. This edition keeps `koherensi`
because the admitted Chapter 2 corpus already uses that category-theoretic
form and the theorem title is fixed consistently; it does not claim direct or
majority same-field Indonesian attestation.

The audit is `qa/UNIT_020_TERMINOLOGY_AUDIT_20260824.md`, 4,117 bytes,
SHA-256
`99514b0bb83a81364dabb257a74c44fb6c2164c46a327a292c6cc03e59dea5fc`.
The controlled glossary is 37,771 bytes, SHA-256
`3afc80895bec2d3710cbbd26de8451063ce53445c081b276670a0b3568f0c983`;
no candidate row remains at this boundary.

## Reader, reflow, build, and PDF QA

The admitted reader is
`artifacts/unit-020-bab-3-keketatan-dan-teorema-koherensi.pdf`: five pages,
93,053 bytes, SHA-256
`8d8a7c8f537681525d97952a7f163f95a5063275047989c26f0387f50172e1ed`.
Its centered cover states the exact partial scope in prose and uses no
ambiguous filled/unfilled progress blocks. The canonical heading is `3.2`.
The concluding proof, three-entry bibliography, and two-entry term index share
one legible final page instead of producing an orphaned sparse index page.

Clean builds E and F have different raw PDF containers: 93,054 bytes,
SHA-256
`e3f7f2b1ae8da6dea90f10a62cd1b9b0d272b2b4f0b386bb7eafc765a40e8057`,
and the admitted artifact identity above. Their page-content streams,
metadata, navigation, links, extracted text, and all rendered pages are
identical. Forty page renders and eight contact sheets cover two builds, two
renderers, and two runs; every within-renderer replay and cross-build
comparison is decoded-pixel- and PNG-byte-identical.

The reader declares `id-ID`, preserves Wen-Wei Li as author, and has four
outline entries, 21 named destinations, ten internal links, four intentional
URI links, and 24 embedded subset fonts. It is unencrypted and has no form,
JavaScript, embedded file, additional action, invalid destination, unresolved
token, or blank page. The untagged state is recorded honestly.

The final log is `qa/UNIT_020_BUILD_FINAL.log`, 83,675 bytes, SHA-256
`80363df3e3bf9186d2265305f1a4d908da645b446a0504b7d186247de8df7617`;
it contains no overfull box, undefined control/reference/citation, missing
character, fatal error, or emergency stop. Structured evidence is
`qa/unit-020-evidence/structure-and-pdf-qa.json`, 9,044 bytes, SHA-256
`26c1a5c433f519afd10b0bc1b378d81b8d6bb1791c91fc3816f151015adaa9b1`.
The independent visual report is `qa/UNIT_020_VISUAL_QA_20260824.md`, 4,085
bytes, SHA-256
`ecab989428e0b5815db6241662198e88e028f42784d289e9ce92f36112b012e4`.

## Modular backend

The canonical record
`backend/data/unit-020-bab-3-keketatan-dan-teorema-koherensi.json` is
120,409 bytes, SHA-256
`d965d9ade3ea06a230ce5e3501585da50ddad29c9a1b902dfefcebf88773e226`.
It contains 173 stable entities, including 128 concept-compatible entities,
three labels, five references, three citation occurrences over three native
bibliography records, ten items, 69 formula entities, two diagrams, four
arrows, five nodes, one path, five edges, two index entries, four terminology
bindings, one declared correction, and eighteen prerequisites.

The six deterministic CSV projections are:

- `unit-020-bindings.csv`: 10,500 bytes, SHA-256
  `fef7591dfdb86e8ca35e71109a9d4f75decc9d07aae9c7302157bbeaaefbb7f7`;
- `unit-020-entities.csv`: 31,079 bytes, SHA-256
  `550207d48a8172c7b7283ff2a5b01fbada11794aa2670145c02c524cd8503b07`;
- `unit-020-qa.csv`: 4,099 bytes, SHA-256
  `eff6e8c34237366d89840bf6a738044c35061f85a378c23e23f5db41d10bfbc4`;
- `unit-020-relations.csv`: 81,517 bytes, SHA-256
  `306f1301cc3c8fda9a2d326ee2195dbbb035974d4fc08df769163ed195666ce4`;
- `unit-020-rights.csv`: 1,287 bytes, SHA-256
  `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e`;
- `unit-020-surfaces.csv`: 1,864 bytes, SHA-256
  `dc8682fc9fdeed36e8cf0cae899691015bf375204005e45dd3ff51f744b8e109`.

Repeated generator and validator runs reproduced all seven backend outputs
byte-for-byte. The Unit 020 validator invokes the shared schema, UUIDv5,
relation, ordering, live-hash, rights, build, terminology, correction, and QA
validator. Its evidence is
`qa/unit-020-evidence/backend-validation.json`, 3,613 bytes, SHA-256
`38d94810c0612d10f1d2eb04140dabe29d294e5311ff11b7e5767baefc777567`.

## Rights and provenance

Wen-Wei Li remains the source author. Principal source text and Indonesian
translation are CC BY 4.0. The credited `AJbook.cls` fragment retains CC
BY-SA 3.0; `Lanzhou.png` in the wider closure also retains CC BY-SA 3.0 but is
not used by this reader; bundled Noto fonts retain OFL 1.1. Rights are not
flattened into one blanket claim. This is an independent, non-endorsed
derivative.

Production provenance is separate from authorship and records the exact
identification `OpenAI Codex gpt-5.6-sol, Ultra`.
