# Unit 028 admission — 2026-08-25

Status: **PASS_WITH_WARNINGS — admitted locally; GitHub publication and
anonymous byte readback are the next gate.** Unit 028 is the complete
contiguous Indonesian translation of Section 4.4 of Wen-Wei Li, *Methods in
Algebra, Volume 1*: group and monoid actions, equivariant maps, orbits and
stabilizers, orbit counting, homogeneous spaces, torsors, translations,
double cosets, conjugation, and bitorsors. Translation, mathematical topology,
terminology, correction provenance, canonical integration, reader,
component-rights separation, modular backend, deterministic projections,
clean build, dual-renderer all-page QA, and independent final audit pass.

The disclosed non-blocking warnings are that the PDF is untagged and that the
installed Poppler text extractor lacks the optional Adobe-GB1 mapping and
emits dependent `F37`/show-space messages. No tagged-accessibility claim is
made, and no visible, mathematical, source-binding, or publication defect was
found.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**, acting on the
user's instruction. This is separate from Wen-Wei Li's authorship and all
retained human/source/component credits.

## Frozen source and canonical translation

- Authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`,
  154,744 bytes / SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Exact authority boundary: physical lines 518–665 inclusive, 148
  normalized-LF records / 10,550 bytes / SHA-256
  `af7b91d4650e637505555cc188056656cd02f400bc6e1dd1ded0f619040a80db`.
  Line 665 is the blank section separator; substantive lines 518–664 map
  one-for-one to the target.
- Reviewed candidate:
  `build/unit-028-candidate/chapter4-group-actions-counting-id.tex`, 147
  records / 13,017 bytes / SHA-256
  `027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd`.
- Canonical target: `repo/source/chapter4.tex`, 1,897 LF records / 168,678
  bytes / SHA-256
  `33ab68b169fad0f45815cbfa528e03eaa12efbb2add9a4599049a9823c86b0b3`.
  Target lines 518–664 are candidate-identical. The untouched Section 4.5
  sentinel occurs at target line 665 and corresponds to authority line 666.
- Controlled glossary: 408 data rows / 64,585 bytes / SHA-256
  `fdd00a574f7f93837688e2d9bc9707677c889eab1174b8f0121a119498557fe7`.
  The exact 25-row Unit 028 delta is 4,052 bytes / SHA-256
  `601944b6058b9506655eca969d4d85506e59c24d9779d38567c19cb84bde41d7`.

The fail-closed candidate and integration checkers pass. They preserve 24
active environment pairs / 48 ordered markers, five labels, seven ordinary
references and one equation reference, two citations, 213 protected
mathematical zones, **16 active list items**, one `tikzcd` diagram with two
arrows, and nine index entries. The 16-item census was directly re-counted in
the candidate and agrees with the backend. There are no exercises, hints,
answers, solutions, assessments, placeholders, Han prose, or Section 4.5
records in the admitted span.

## Correction and localization boundary

Exactly one source correction is disclosed:
`O013-LI-U028-COR-001`. Authority lines 533 and 535 use undefined
`M_1,M_2` after declaring `f:X\to Y`; the target restores the intended `X,Y`
diagram objects and `\identity_X,\identity_Y` inverse identities.

The three changes inside protected `\text{...}` zones are language
localizations, not mathematical corrections: `pemetaan` at authority line
557, `unsur-unsur berbeda` at line 610, and `isomorfisme` at line 646. Their
surrounding mathematical topology is unchanged. The disabled upstream comment
at line 542 remains disabled. No second correction is claimed.

## Reader, build, and all-page QA

- Driver: 6,077 bytes / SHA-256
  `883ae7140934727fbc6ae90b6d3195b9285a3f0de1d99f04d668bc23515eb3fe`.
- Cover: 3,690 bytes / SHA-256
  `0785896485fb7cc92dca4a42f4bdb651f3c4c1cdadc5c30a3b0860812c2ba7cd`.
- Cross-reference witness: 200 bytes / SHA-256
  `f8cf71f988d1027e344d3a13547149ba2b877c79c55d76fc16c393b703ba852b`.
- Build script: 5,848 bytes / SHA-256
  `eaa5b98bfd96690add2635aee6e180a1ec220a110d047a9b12536c6a6239f4a2`.
- Reader:
  `artifacts/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan-id.pdf`, seven
  pages / 108,689 bytes / SHA-256
  `50c40ddefa870866568f8d1621d5fc204a1fd0fd0a45bdfc74659197c585790a`.
- Final build log: 78,086 bytes / SHA-256
  `e34377e726cef55c50ead5b7a5e056ca332d653b0603a3e214f7b56d44594120`.
- Structure/PDF evidence: 55,099 bytes / SHA-256
  `e3907e0035f514b44180c6796ab44b5980ddd58c7110e1f7f6e4c4217d4d3426`.
- Render inventory: 35,181 bytes / SHA-256
  `c622cde057eff3a70e0301d60fc6b46d3b3924153d7c01c2d4b7a206427ac310`.
- Visual receipt: 6,209 bytes / SHA-256
  `5ef33e044cd6c4e0b7cde33432a238d00ad835804ec4edbd7fd2deb7623bde73`.

Build D and the final artifact are byte-identical. Build C differs only in
volatile dvipdfmx subset tags; every same-renderer decoded pixel agrees across
the 14 C-to-D and 14 D-to-artifact comparisons. The evidence contains 42
full-page Poppler/MuPDF renders, all with clear outer edge bands. All seven
pages were independently inspected at full resolution and in both contact
sheets. No clipping, collision, overflow, missing label, broken symbol or
diagram stroke, tofu, or unintended sparse page was found.

The final build has zero fatal/error, unresolved reference/citation,
missing-character, empty-link-target, and overfull diagnostics. The exact
artifact is unencrypted PDF 1.7 with `id-ID` metadata, four outline entries,
38 resolved named destinations, safe internal and HTTPS actions, embedded
fonts, and no form, JavaScript, embedded file, or unsafe additional action.
The untagged status and Poppler Adobe-GB1/`F37` extraction limitation remain
explicit warnings; both independent renderers show every visible glyph.

## Modular backend

Canonical JSON:
`backend/data/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan.json`, 278,411
bytes / SHA-256
`840eb52c05ac6b1bcc8a9755a8d2ee3fcfaa0e4f4479f2c4501d921f358635ab`.
It contains 382 audited UUIDv5 entities, including 322 concept-compatible
entities, plus 20 prerequisite records, 17 QA events, and 77 binding
occurrences over 39 live paths. It exactly models the source/target boundary,
the 16 list items, terminology, citations, diagram, indexes, one correction,
three protected-text localizations, build surfaces, provenance, and component
rights.

The dedicated validator performs two deterministic regenerations, checks the
shared schema and UUIDv5 namespace, reproduces all CSV bytes, verifies all
full-file and line-span bindings, and reports no output mutation. The shared
validator also passes. Backend validation evidence is 5,799 bytes / SHA-256
`be9cc26a09fd096530f73497ba8b9c2acd5039fb5b92a649890f1dd7d37f0bc3`.

| Projection | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `unit-028-bindings.csv` | 77 | 15,952 | `a0e95582f3bd2371b162b48bcc3e69f85151ecd64a085d9425a80e3bfb68234f` |
| `unit-028-entities.csv` | 382 | 82,561 | `e4e8cfad54e7f0ce1922b4b0041e89d55ce2a12828d810cd3c4cb4acef75f75b` |
| `unit-028-qa.csv` | 17 | 6,641 | `2da398d6aaa9c57d6290c251d7517e61f0a6038967f9a7be1d9be5f008cd9a39` |
| `unit-028-relations.csv` | 713 | 206,110 | `c3e52c181109db608a5a07a875faa4c60c8031ff00e4f3203503c99bea172b07` |
| `unit-028-rights.csv` | 4 | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
| `unit-028-surfaces.csv` | 13 | 3,107 | `ec1397d1b01ca68e4a99d40cd47c2e79dad10dcc51467278af02244c153d483c` |

The final independent audit is
`qa/UNIT_028_FINAL_AUDIT_20260825.md`, 9,126 bytes / SHA-256
`62a4889e67b43c04cf7f6a1da78cd8b6f94d369d63a65633121890ce67c79da9`.

## Rights, architecture, and next gate

Principal source text and Indonesian translation remain CC BY 4.0. The
credited `AJbook.cls` fragment remains CC BY-SA 3.0; bundled Noto fonts remain
OFL 1.1. `Lanzhou.png` remains CC BY-SA 3.0 and is not used by this reader.
The edition identifies translation and changes, retains component attribution,
and expressly disclaims source-author endorsement. No blanket license or
endorsement is implied.

The final O013 architecture remains unchanged: complete Li Volume 1 first;
then Alexander Duncan's pinned CC BY 4.0 representation-theory repository;
then only the six selected repaired CRing GFDL spans; then separately
provenanced connective/mastery material. Etingof remains reference-only.

Unit 028 is source-bound, reproducible, warning-disclosed, independently
audited, and locally admitted. GitHub publication and anonymous byte readback
are next. Zenodo version `0.6.0` remains the latest chapter-complete checkpoint
through Unit 024 (complete Chapter 3); this single Section 4.4 unit does not
replace or duplicate that checkpoint. The next canonical Li cursor is
`chapter4.tex:666`, Section 4.5 (the Sylow theorems).
