# Unit 019 admission — Kategori Monoidal: Definisi Dasar

Status: **admitted locally** after independent source/translation review,
fail-closed mathematics and topology comparison, terminology promotion, two
clean builds, PDF structure and safety checks, deterministic backend replay,
and all-page visual QA in both Poppler and MuPDF.

## Frozen content and boundary

- Authority: Wen-Wei Li, *Methods of Algebra*, Volume 1, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Range: the complete Chapter 3 opening and complete Section 3.1,
  `chapter3.tex:1-227`. Authority line 227 is the trailing blank separator;
  authority line 228 begins Section 3.2 and is excluded.
- Authority span: 227 LF line records, 21,745 UTF-8 bytes, SHA-256
  `4aecde3d61fb173087ae3e7ab64cc84f7bd4f3fbc0dcbfa8a2c3d6bab1201a8a`.
- Indonesian target span: `repo/source/chapter3.tex:1-226`, 25,868 UTF-8
  bytes, SHA-256
  `6b42291293a06d15b64034a26ed25aeac3cb41465bf9533e069bc9ac65d9b8ac`.
- Full current target `repo/source/chapter3.tex`: 79,694 bytes, SHA-256
  `bfe5d4745f9a3ac1062b79ee429356a17f3d5bff9be02ef0093eab6978f98e60`.
  Target line 227 and everything after it remain byte-identical to authority
  lines 228 onward.
- Independent continuous review:
  `qa/UNIT_019_TRANSLATION_SOURCE_REVIEW_20260824.md`, 9,617 bytes,
  SHA-256
  `4e79fffff9762ad8398a7c772eb8e9458931a82069fba390e25239169267d0ac`.

## Mathematics, topology, and declared correction

The fail-closed checker preserves 45 ordered environment pairs, 16 labels, 15
ordinary references, 13 equation references, four citation occurrences, 13
items, 167 inline-math surfaces, nine bracketed displays, one `align`, six
`equation`, one `equation*`, three `tikzpicture` diagrams, fifteen `tikzcd`
diagrams, 75 arrows, eleven nodes, one path, and eleven index surfaces. The
target span contains no Han residue. The complete independent audit is
`qa/UNIT_019_MATH_STRUCTURE_AUDIT_20260824.md`, 8,737 bytes, SHA-256
`5927895f6191e43f68c60eccfa82c2da8ccd756217677e2ad22f0a22fd970add`.

`O013-LI-U019-COR-001` repairs the lower-right node of the Kelly coherence
diagram at authority line 155. The source writes the literal `1` where the
adjacent vertices, associator, and section notation require the defined
monoidal-unit macro `\munit`; the target replaces only that occurrence. This
restores the arrow's mathematical source and target without changing the
proof. The correction was first recorded as `O013-ADV-0051` and is closed at
this admission boundary by a separate append-only ledger entry.

The executable checker is `scripts/check_unit_019_structure.py`, 24,362 bytes,
SHA-256
`7cba44c81b5fd73d027bdde81338df4f68a41328fb95d8275b6e2a570cbe6100`;
it passes on the admitted identities and fails closed on path overrides or any
boundary/topology change.

## Terminology gate

The earlier bounded same-field terminology check and the complete seven-page
Indonesian tensor-product fallback remain disclosed in the two terminology QA
receipts. They support the corpus register but are not misrepresented as
direct attestation for every specialized monoidal term.

Exactly fifteen Unit 019 rows were promoted from `candidate` to `admitted`
only after translation, structure, build, and visual gates passed: `objek
satuan`, `kendala satuan`, `aksioma segilima Mac Lane`, `aksioma segitiga
kategori monoidal`, `subkategori monoidal`, `kategori kepang`, `kategori
diperkaya`, `kategori aditif`, `biproduk`, `fungtor monoidal`, `fungtor
monoidal kuat`, `fungtor monoidal longgar-kanan`, `fungtor monoidal
longgar-kiri`, `ekuivalensi monoidal`, and `kategori tensor`. The controlled
glossary is now 36,770 bytes, SHA-256
`1aaf02e1146b6a47b29090ac58cb0c8436a5b97708d23969b8253f07a99a98a3`;
no candidate row remains at this boundary.

## Reader, reflow, build, and PDF QA

The admitted reader is `artifacts/unit-019-bab-3-definisi-dasar.pdf`: twelve
pages, 125,710 bytes, SHA-256
`af7a4561db5e8ab1798d4475c589beb42f9fb84795bd167c0ffc17241866783a`.
It declares `id-ID`, preserves Wen-Wei Li as author, and has five outline
entries, 52 named destinations, 35 internal links, and three intentional URI
links. All 25 fonts are embedded and subset. The PDF is unencrypted, has no
form, JavaScript, embedded file, or unsafe action, and every page has
extractable text. It is honestly recorded as untagged rather than claiming a
structure tree it does not contain.

The centered digital cover states the exact partial scope in prose and uses no
ambiguous filled/unfilled progress blocks. Chapter pages use the reading
width appropriately. The final reflow combines the short two-entry
bibliography, two-column term index, and one-entry symbol index on one legible
concluding page instead of leaving sparse generated back matter.

Clean builds C and D have different raw PDF containers: 125,698 bytes,
SHA-256
`c4904fb64633a24476225f461bf2e09bcb1d92a0a13fc5d836ad1e6dfad5b1ac`,
and the admitted artifact identity above. Byte-identical PDF serialization is
therefore not claimed. Their layout-preserving extracted text is byte-identical
at 25,537 bytes, SHA-256
`a835887e63a0f578a80d092fad2291d397dec52e1ef5efabbd60d76b6cb6d8a5`.
All 12/12 Poppler pages and all 12/12 MuPDF pages are pixel- and PNG-byte-
identical within renderer across both builds and repeated renders. The
independent visual run comprises 96 page renders and passes every page without
clipping, collision, broken formula/diagram, missing glyph, blank verso, or
unsafe link. Its receipt is `qa/UNIT_019_VISUAL_QA_20260824.md`, 4,068 bytes,
SHA-256
`dfd641abfa074bfc1f8928412622ee4aa83bdcb86b1afd23f19d910a04e2c55e`.

The complete sanitized final log is `qa/UNIT_019_BUILD_FINAL.log`, 85,982
bytes, SHA-256
`b7df3a77892563e590bdc5158197a06b3677b2d2fb0e88e2658a71d599358634`.
It has zero overfull boxes, undefined controls/references/citations, missing
characters, fatal errors, and emergency stops. Twelve deliberately suppressed
external-reference targets prevent false standalone links and were checked
against the frozen printed-number witness. Structured PDF/build evidence is
`qa/unit-019-evidence/structure-and-pdf-qa.json`, 6,607 bytes, SHA-256
`0311ab0fa8f6f12e1ff2952328be7f993bf10224fbbce792c4b235126a2ae624`.

## Modular backend

The canonical record `backend/data/unit-019-bab-3-definisi-dasar.json` is
295,265 bytes, SHA-256
`888ec61fc4b1229ffab4f480d12a8ced60e4f5d32734dca3d314903917b8a215`.
It contains 437 stable entities, including 369 concept-compatible entities,
16 labels, 28 reference occurrences, four citation occurrences over two
native bibliography records, 13 items, 184 formula entities, 18 diagrams, 75
arrows, eleven nodes, one path, eleven index entries, fifteen admitted
terminology bindings, one declared correction, and eighteen prerequisites.

The six deterministic CSV projections are:

- `unit-019-bindings.csv`: 24,287 bytes, SHA-256
  `6f9821169016d371dfb12e58faee3848eb95b7572cbe990ab91b04c79c28a7c5`;
- `unit-019-entities.csv`: 80,106 bytes, SHA-256
  `ebcf26dd2867566496bc04467b909dafb79639ba657aa09f39de3eedba50218f`;
- `unit-019-qa.csv`: 3,431 bytes, SHA-256
  `49021e9a2e543261b34c176e8549f8b31801b16242f1a6f51a783e267e2b84a4`;
- `unit-019-relations.csv`: 212,895 bytes, SHA-256
  `ac4d2c87d4b06da25bd511d11316b393162413e0ed4c2e34b28d337ff0a289e6`;
- `unit-019-rights.csv`: 1,287 bytes, SHA-256
  `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e`;
- `unit-019-surfaces.csv`: 6,923 bytes, SHA-256
  `971a71240d2765a3fd07018249e9b4b4f3f19b2fe62eab4e10f397063157b7a3`.

Consecutive generator and validator runs reproduced all seven backend outputs
byte-for-byte. The Unit 019 validator invokes the shared schema, UUIDv5,
relation, ordering, live-hash, rights, build, terminology, and QA validator.
Its concise evidence is `qa/unit-019-evidence/backend-validation.json`, 3,213
bytes, SHA-256
`a8808bf6b26fd541e1fa27fcdcd0375b25d277338c3c78513b3159a743268012`.

## Rights and provenance

Wen-Wei Li remains the source author. Principal source text and Indonesian
translation are CC BY 4.0. The credited `AJbook.cls` fragment retains CC
BY-SA 3.0; `Lanzhou.png` in the wider closure also retains CC BY-SA 3.0 but is
not used by this reader; bundled Noto fonts retain OFL 1.1. Rights are not
flattened into one blanket claim. This is an independent, non-endorsed
derivative.

Production provenance is separate from authorship and every human credit and
records the exact identification `OpenAI Codex gpt-5.6-sol, Ultra`.

