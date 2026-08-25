# Unit 029 final independent admission audit — 2026-08-26

Status: **PASS_WITH_WARNINGS — no actionable admission defect found.** This
audit was performed after the final canonical-source repair, terminology
integration, centered-reader build, dual-renderer all-page evidence,
privacy sanitization, and deterministic backend generation. The only two
admission warnings are disclosed limitations: the PDF is untagged, and the
installed Poppler text extractor lacks its optional Adobe-GB1 mapping. No
tagged-accessibility claim is made. Neither warning changes the visible
mathematics, source binding, navigation, privacy result, or fitness for narrow
publication. This record does not claim that Chapter 4, Li Volume 1, or the
composite O013 course is complete.

Production and audit provenance is **OpenAI Codex gpt-5.6-sol, Ultra**, acting
on the user's instruction. This is separate from Wen-Wei Li's authorship and
all retained source and human-contributor credits.

## Independently replayed gates

The following live commands were rerun after all repairs and returned exit
code 0:

```text
python -B scripts/check_unit_029_candidate.py
python -B scripts/check_unit_029_structure.py
python -B scripts/validate_unit_029_backend.py
python -B scripts/validate_backend.py --data backend/data/unit-029-bab-4-teorema-sylow.json
```

The dedicated backend validator itself performed two deterministic
regenerations and invoked the shared schema/UUIDv5/CSV validator. It proved
that validation did not mutate the generated outputs. Thus the shared backend
gate passed both inside the dedicated replay and again as the separately
invoked fourth command.

## Source boundary, translation, and terminology

The frozen authority `chapter4.tex` is 154,744 bytes / SHA-256
`63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
Its exact Unit 029 slice is physical lines 666–795: 130 normalized-LF records /
8,043 bytes / SHA-256
`760366ac81aff9bd6170c96996ae16c29a02a93034a77f7d4c7f01485bbf3163`.
Authority line 795 is only the blank separator, so substantive authority lines
666–794 map one-for-one to the 129-record Indonesian candidate.

The candidate is 10,028 bytes / SHA-256
`234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d`.
The canonical `repo/source/chapter4.tex` is 1,896 LF records / 170,663 bytes /
SHA-256
`8cbd766360a3c7cd214876e297c45de3b8938daa9a3623192efdf1d6ebc766fc`.
Canonical lines 665–793 are byte-identical to the candidate. Direct inspection
also confirms that untouched Section 4.6 begins at target line 794 and at
authority line 796; no later-unit record entered this admission.

The formal topology is complete: 25 active environment pairs / 50 ordered
markers, six labels, 16 ordinary references, one `Lang02` citation with its
locator, two active list items, 211 protected mathematical zones, and two
index entries. There are zero diagrams, exercises, hints, answers, solutions,
assessments, placeholders, active source comments, or residual Han prose.
Exactly one protected `\text{...}` fragment translates `子集` as
`subhimpunan`; surrounding set notation is unchanged. No mathematical source
correction is needed or claimed. The final candidate also omits the
authority-absent period that an earlier build placed alone after a display;
the candidate gate now rejects that regression.

The five-row terminology delta is 1,030 bytes / SHA-256
`e0e00678dc46fd8c702c17614ea2d1e1e71ee6ff622f8986097dfd296e759ecc`.
It is the exact tail of the 413-row controlled glossary, which is 65,573 bytes /
SHA-256
`adc2152dc08131e0098ac159137378aa50cd7b54cb282a8e713899662d335ca3`.
The admitted terms are `p-grup`, `p-subgrup`, `subgrup Sylow p`, `koefisien
binomial`, and `saling koprima`; each remains semantically distinct where the
source requires it.

## Reader, build, and independent visual inspection

- Driver: 6,028 bytes / SHA-256
  `7f2f677d9f5b54f0fe802d5367990bf3b62bf46c04f2087fbd4f91c5f265a08f`.
- Cover: 3,590 bytes / SHA-256
  `4a66895d41b7ad3c73f2f7ab244a93e042bb365ca706d38b1b62d3cf956f104b`.
- External-reference witness: 355 bytes / SHA-256
  `12856b4cc11ee6aabd903791ce89bc097ae0746473b6bb5ce3035a2896483ba6`.
- Build script: 5,007 bytes / SHA-256
  `a8dca51981509d80a2902b5ef7ba52e9505008bf7cfd03866cd0a5d022d5d80c`.
- Sanitized final build log: 77,013 bytes / SHA-256
  `606a707d5aad534f58af25333f3fbffe964ab7c7f1a260b3ffe9c1f1bce8364e`.
- Final reader: six pages / 99,689 bytes / SHA-256
  `64fde52948525fc5b159f76fbed6571c150e4184a87e47e715164aec135e5012`.
- Structure/PDF evidence: 61,120 bytes / SHA-256
  `23b61663269b592c232752b88409f48acd999eae20dd513eefa546d0a3835e1f`.
- Render inventory: 30,170 bytes / SHA-256
  `689ff5198ccc43b61ef755dbde902747f5cc70a8366dc68c520db086eebd8452`.
- Visual receipt: 6,319 bytes / SHA-256
  `adfbada7eb878fa23c49e66ffd9499c9297f38c596bdb3a2e1a3efd587637ae6`.

Build J and the artifact are byte-identical. Build I differs only in volatile
font-subset tags; all six same-renderer decoded-RGB page comparisons agree in
both Poppler and MuPDF. The two final artifact contact sheets were inspected
at full image detail (Poppler SHA-256
`58be306b3cb0fb6ecd254dd3bfbc44e66533cdf679cb375e761beb1a4447307c`;
MuPDF SHA-256
`977aaec3835415bf01b25effbfacde63bc8f0df34bd29d0d65715aae8158267b`).
All six artifact pages were then independently inspected at full resolution
in each renderer, for 12 page-level inspections. The exact published PNG
identities are:

| Page | Poppler PNG SHA-256 | MuPDF PNG SHA-256 |
|---:|---|---|
| 1 | `c4631572566460e87f65f6d80b47553455c24e60ad44cf550999a1eb85b3dada` | `d519dad4974e6cbd7a159ce2460743a3ad52ccf4dd2a67ed96df75fd4ed71e84` |
| 2 | `0a37c9c53649f5458d6daf5171f9da52a6c450e5e383939dfa6dc72c77d1e6b8` | `2fddad45df4430dc0a7f377a110bb9bc1ab0840829047de56530587c5cc0667d` |
| 3 | `453159f3e479e3c1aff614e6f1163435339a3825dbbaa7c8829fcd7e94fc94e7` | `38fb5f83d8ad564abf5bbb5e556cf62b08e194f199f14d5d7ef26f96aba7e2bf` |
| 4 | `b07f990b446aa9eba8ef45437f18181cd30a319431886bc3a0acca3b95ec1380` | `35212ee2bba447b46f05fa758d049a3aac911dc6e8f361401340925c551c2ee1` |
| 5 | `d52ddc6582f98cca0f0023eee783c8e23c7d0b8896b08d97b3417abd6d76d266` | `682c4e367bd285a32cf8681248df3cabb3489ea634ada057aec5b26bee98a22c` |
| 6 | `d99eadd2cdb366df5d352819bfa1fb81808400cbdb6a1c6d570edef8d7c0d9f6` | `8b0ccd834a8669020eb09c1b9e5f944b850ddaa91ae8ecffa3630c36933b56ca` |

The 142 mm text block is centered and naturally filled. Page 6 was reviewed
especially closely: the final Sylow proof, displayed product, bibliography,
DOI, and two-entry run-in term index are all legible, separated, and inside
the live area; no sparse seventh page is introduced. Across all pages there
is no clipping, collision, overflow, broken symbol, tofu, isolated
punctuation, ambiguous filled/unfilled progress block, or edge contact.

The artifact is unencrypted PDF 1.7 with `id-ID` language metadata, three
outline entries, 36 resolved named destinations, nine closed internal actions,
five HTTPS actions, 25 embedded font rows, and no form, JavaScript, embedded
file, or unsafe additional action. The final log contains 2,276 newline-split
records including its terminal empty record and zero fatal/error,
unresolved-reference/citation, missing-character, empty-target, or overfull
diagnostics.

## Modular backend and projections

Canonical backend JSON is 243,849 bytes / SHA-256
`918e1f3cbf30ec950bb83dc6427f63190dde41c766cbc38d5d349728ee92cced`.
It validates against the shared schema and contains 332 audited UUIDv5
entities, including 280 concept-compatible records, 21 prerequisite records,
17 QA events, and 61 binding occurrences over 39 live paths. The bindings
cover the exact source/target boundary, formulas and identifiers, terminology,
citation and indexes, sole localization, build and visual surfaces,
component rights, production provenance, and independent/non-endorsed status.
Backend validation evidence is 5,656 bytes / SHA-256
`ae882acd82b052780416cda0fcfb50a19d89ff1aca388560f665025c39541b8a`.

All six CSV projections parse and exactly reproduce the JSON:

| Projection | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `unit-029-bindings.csv` | 61 | 11,392 | `6b15e1dbad92acadf337972cf3834e0070ef466c35ee1c34233170e488871c79` |
| `unit-029-entities.csv` | 332 | 73,832 | `b8febf85975d8df7637d78d4999220b385949937f12f59ed037380d0749ea538` |
| `unit-029-qa.csv` | 17 | 6,631 | `07db3580987635b0f4be0ecf240ec51a2bca19ec262f6addc95cb4df28ce2466` |
| `unit-029-relations.csv` | 617 | 168,333 | `c71816b03512b4194f42a380676777a968d429134b8ed7cae8709d207c94e6a4` |
| `unit-029-rights.csv` | 4 | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
| `unit-029-surfaces.csv` | 4 | 924 | `93dc825f748f7af6e8c16842098ff346fe8b05de95fd05adfeb7d2702e3774ea` |

## Rights, provenance, privacy, and verdict

Rights remain non-flattened. Principal source text and Indonesian translation
are CC BY 4.0; the credited `AJbook.cls` fragment remains CC BY-SA 3.0;
bundled Noto fonts remain OFL 1.1. `Lanzhou.png` remains CC BY-SA 3.0 but is
not used by this reader. The cover and backend visibly retain author/source
attribution, identify the translation and typographic changes, give the exact
production-model provenance, and state that the edition is not endorsed by
the source author. No blanket closure license or endorsement is implied.

The exact standard Unit 029 publication inventory existing before this final
audit comprised 43 paths / 3,387,425 bytes: terminology and README, the
reader, one backend JSON and six CSVs, admission and supporting reports, the
sanitized log, three machine-readable evidence files, 12 artifact-page
renders, canonical source/cover/driver/cross-reference files, and seven
Unit 029 build/check/generation/validation/readback scripts. A bounded byte
scan found zero drive-rooted user-profile paths, zero local-profile-name
literals, zero token-shaped literals, and zero credential assignments. The
same checks cover binary PDF/PNG payloads as well as every intended text,
source, script, report, JSON, CSV, render-inventory, and log path. Contact
sheets, isolated candidate/delta, promotion tooling, and clean-build trees are
evidence or staging inputs and are deliberately outside the publication set.

Conclusion: Unit 029 satisfies the source-order, translation, mathematics,
terminology, topology, localization provenance, build, reader, dual-renderer
visual, privacy, modular-backend, deterministic-projection, component-rights,
production-provenance, and non-endorsement gates. It is fit for local
admission and narrow GitHub publication. Publication and anonymous byte
readback are the next gate. The next canonical Li cursor is
`chapter4.tex:796`, Section 4.6.
