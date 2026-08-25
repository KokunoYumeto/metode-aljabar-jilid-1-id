# Unit 028 final independent admission audit — 2026-08-25

Status: **PASS_WITH_WARNINGS — no actionable admission defect found.** This
audit was performed after canonical source and terminology integration,
reader construction, dual-renderer all-page evidence, and deterministic
backend generation. The two remaining warnings are disclosed accessibility
and extraction limitations: the PDF is untagged, and the installed Poppler
layout-text extractor lacks its optional Adobe-GB1 mapping and consequently
emits dependent `F37`/show-space diagnostics. Neither warning changes the
visible mathematics, source binding, or admission result. This record does not
claim that Chapter 4, Li Volume 1, or the composite O013 course is complete.

Production and audit provenance is **OpenAI Codex gpt-5.6-sol, Ultra**, acting
on the user's instruction. This is separate from Wen-Wei Li's authorship and
all retained human and component credits.

## Independently replayed gates

The following commands were rerun against the live files and all returned exit
code 0:

```text
python scripts/check_unit_028_candidate.py
python scripts/check_unit_028_structure.py
python scripts/validate_unit_028_backend.py
python scripts/validate_backend.py --data backend/data/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan.json
```

The candidate gate reports 148 authority records / 10,550 bytes / SHA-256
`af7b91d4650e637505555cc188056656cd02f400bc6e1dd1ded0f619040a80db`,
147 target records / 13,017 bytes / SHA-256
`027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd`,
and next authority boundary `chapter4.tex:666`. The authority file itself is
154,744 bytes / SHA-256
`63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
The selected boundary is authority lines 518–665; line 665 is the blank
section separator, so substantive lines 518–664 map one-for-one to the
candidate.

The structure gate reports canonical `repo/source/chapter4.tex` as 1,897 LF
records / 168,678 bytes / SHA-256
`33ab68b169fad0f45815cbfa528e03eaa12efbb2add9a4599049a9823c86b0b3`.
Target lines 518–664 are candidate-identical. Authority Section 4.5 begins at
line 666 with `\section{Sylow 定理}\label{sec:Sylow}`; because the blank line
665 was omitted, that untouched sentinel occurs at target line 665.
The 25-row terminology delta is 4,052 bytes / SHA-256
`601944b6058b9506655eca969d4d85506e59c24d9779d38567c19cb84bde41d7`.
It is the exact tail of the 408-row controlled glossary, which is 64,585 bytes
/ SHA-256
`fdd00a574f7f93837688e2d9bc9707677c889eab1174b8f0121a119498557fe7`.

## Content, mathematics, and correction reconciliation

Coverage is complete and in source order: monoid and group actions;
equivariant maps and isomorphisms; left and right actions; permutation,
linear, function-space, and heat-semigroup examples; fixed points, orbits,
stabilizers, and orbit decomposition; the orbit–stabilizer cardinal formula;
faithful, free, semiregular, transitive, and multiply transitive actions;
homogeneous spaces and torsors; translation, double-coset, and conjugation
actions; the isomorphism bitorsor; and the bijective torsor criterion.

The exact formal census is 24 active environment pairs / 48 ordered markers,
five labels, seven ordinary references plus one equation reference, two
citations (`Zh2`, then `Zh1`), 213 protected mathematical zones, **16 active
list items**, one `tikzcd` diagram with two arrows, and nine index entries.
The 16-item count was independently obtained directly from the 16 active
`\item` records in the candidate and agrees with the canonical backend. The
span contains no exercise, hint, answer, solution, assessment, Han prose,
placeholder, or Section 4.5 content.

Exactly one logical source correction is present and separately typed:
`O013-LI-U028-COR-001` repairs authority lines 533 and 535. The source has
already declared `f:X\to Y` but then uses undefined objects `M_1,M_2`; the
translation restores `X,Y` in the diagram and `\identity_X,\identity_Y` in the
inverse conditions. This is not conflated with the three protected-text
localizations: `pemetaan`, `unsur-unsur berbeda`, and `isomorfisme` translate
the Chinese text inside `\text{...}` at authority lines 557, 610, and 646
without changing surrounding mathematics. The disabled upstream comment at
authority line 542 remains disabled.

## Reader, build, and visual evidence

- Driver: 6,077 bytes / SHA-256
  `883ae7140934727fbc6ae90b6d3195b9285a3f0de1d99f04d668bc23515eb3fe`.
- Cover: 3,690 bytes / SHA-256
  `0785896485fb7cc92dca4a42f4bdb651f3c4c1cdadc5c30a3b0860812c2ba7cd`.
- External-reference witness: 200 bytes / SHA-256
  `f8cf71f988d1027e344d3a13547149ba2b877c79c55d76fc16c393b703ba852b`.
- Build script: 5,848 bytes / SHA-256
  `eaa5b98bfd96690add2635aee6e180a1ec220a110d047a9b12536c6a6239f4a2`.
- Final build log: 78,086 bytes / SHA-256
  `e34377e726cef55c50ead5b7a5e056ca332d653b0603a3e214f7b56d44594120`.
- Final reader: seven pages / 108,689 bytes / SHA-256
  `50c40ddefa870866568f8d1621d5fc204a1fd0fd0a45bdfc74659197c585790a`.
- Structure/PDF evidence: 55,099 bytes / SHA-256
  `e3907e0035f514b44180c6796ab44b5980ddd58c7110e1f7f6e4c4217d4d3426`.
- Render inventory: 35,181 bytes / SHA-256
  `c622cde057eff3a70e0301d60fc6b46d3b3924153d7c01c2d4b7a206427ac310`.
- Visual receipt: 6,209 bytes / SHA-256
  `5ef33e044cd6c4e0b7cde33432a238d00ad835804ec4edbd7fd2deb7623bde73`.

Build D and the artifact are byte-identical. Build C is 108,700 bytes /
SHA-256
`ea6f6dea8bab77faf52f05517ad094fbabfb5e6f5294285269e565ab6edc084a`;
its byte difference is limited to volatile dvipdfmx subset tags. All 14
C-to-D and all 14 D-to-artifact same-renderer decoded-RGB comparisons pass in
Poppler and MuPDF. Forty-two full-page renders have clear outer three-pixel
bands. This audit independently inspected all seven full-resolution Poppler
pages and both seven-page renderer contact sheets; no clipping, collision,
overflow, broken symbol or diagram stroke, tofu, missing label, or unintended
sparse page was found.

The final log has zero fatal/error, unresolved-reference/citation,
missing-character, empty-link-target, or overfull diagnostics. The PDF is
unencrypted PDF 1.7 with `id-ID` metadata, four outline entries, 38 closed
named destinations, safe internal and HTTPS actions, embedded fonts, and no
form, JavaScript, embedded file, or unsafe additional action. It is untagged,
so no tagged-accessibility claim is made. Poppler's missing Adobe-GB1 mapping
and dependent `F37`/show-space extraction messages are retained as a warning;
extracted text has no replacement character or Poppler/MuPDF NUL, and both
renderers visibly reproduce every page.

## Modular backend and rights

Canonical backend JSON is 278,411 bytes / SHA-256
`840eb52c05ac6b1bcc8a9755a8d2ee3fcfaa0e4f4479f2c4501d921f358635ab`.
It validates against the shared schema, contains 382 audited UUIDv5 entities
including 322 concept-compatible entities, and records 77 binding occurrences
over 39 paths, 20 prerequisite records, 17 QA events, one section, two
citations, one diagram, nine indexes, one correction, three localizations,
and the exact 16-item census. Two deterministic regenerations and the shared
validator pass without mutating outputs. Backend validation evidence is 5,799
bytes / SHA-256
`be9cc26a09fd096530f73497ba8b9c2acd5039fb5b92a649890f1dd7d37f0bc3`.

All six CSV projections parse and exactly reproduce the JSON:

| Projection | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `unit-028-bindings.csv` | 77 | 15,952 | `a0e95582f3bd2371b162b48bcc3e69f85151ecd64a085d9425a80e3bfb68234f` |
| `unit-028-entities.csv` | 382 | 82,561 | `e4e8cfad54e7f0ce1922b4b0041e89d55ce2a12828d810cd3c4cb4acef75f75b` |
| `unit-028-qa.csv` | 17 | 6,641 | `2da398d6aaa9c57d6290c251d7517e61f0a6038967f9a7be1d9be5f008cd9a39` |
| `unit-028-relations.csv` | 713 | 206,110 | `c3e52c181109db608a5a07a875faa4c60c8031ff00e4f3203503c99bea172b07` |
| `unit-028-rights.csv` | 4 | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
| `unit-028-surfaces.csv` | 13 | 3,107 | `ec1397d1b01ca68e4a99d40cd47c2e79dad10dcc51467278af02244c153d483c` |

Rights remain non-flattened. Principal source text and Indonesian translation
are CC BY 4.0; the credited `AJbook.cls` fragment is CC BY-SA 3.0; bundled
Noto fonts are OFL 1.1. `Lanzhou.png` remains CC BY-SA 3.0 but is not used by
this reader. Attribution, change disclosure, component treatment, production
provenance, and explicit non-endorsement are present in the reader and
backend; no blanket license or author endorsement is implied.

Conclusion: Unit 028 satisfies the source, translation, mathematics,
terminology, topology, correction/localization provenance, build, reader,
dual-renderer visual, warning disclosure, modular-backend, deterministic CSV,
rights, and non-endorsement gates. It is fit for local admission and narrow
GitHub publication. GitHub publication and anonymous byte readback are the
next gate. Zenodo remains at version `0.6.0`, covering the complete Chapter 3
checkpoint through Unit 024. The next canonical Li cursor is
`chapter4.tex:666`, Section 4.5.
