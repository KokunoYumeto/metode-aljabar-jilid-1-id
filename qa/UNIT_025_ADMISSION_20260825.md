# Unit 025 admission — 2026-08-25

Status: **PASS — admitted locally; publication readback is the next gate.**
Unit 025 is the complete contiguous Indonesian translation of the Chapter 4
opening and Section 4.1 of Wen-Wei Li, *Methods in Algebra, Volume 1*. The
translation, protected mathematical topology, terminology, disclosed source
correction, target-only index localization, reader, component rights, modular
backend, deterministic CSV projections, clean build, and all-page visual QA
pass their admission gates.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. This provenance is
separate from Wen-Wei Li's authorship and all retained human/source credits.

## Frozen source and canonical translation

- Authority: `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`,
  154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Authority span: physical lines 1-176 inclusive, 15,528 bytes, SHA-256
  `d88ca03645fd4c781d16907e063b06cd072ad5fbe0e48ce2149d8fdecfb76a52`.
  Line 177 begins Section 4.2.
- Final reviewed candidate:
  `build/unit-025-candidate/chapter4-group-basics-id.tex`, 178 LF records,
  20,464 bytes, SHA-256
  `5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a`.
- Canonical target: `repo/source/chapter4.tex`, 159,681 bytes, SHA-256
  `b1b055416d392a66708047afb20a14175566c7839286979baac6289d3d125419`.
  Its lines 1-178 are byte-identical to the candidate. The 139,216-byte
  authority suffix from source line 177 remains byte-identical, SHA-256
  `20e588a6d9f8361acad3deb3cdbfbb7e0d2a2495156c458bfe15897d21289b68`,
  apart from one disclosed terminal whole-file LF normalization.
- Controlled terminology: `00_control/TERMINOLOGY.id-ID.csv`, 341 rows,
  51,472 bytes, SHA-256
  `3ed2a7a30aa06e9e574e36b237bf13ab6cec6779703ce91bc3238a107fe526b1`.

Both fail-closed checkers pass twice. The admitted span preserves 27 ordered
environment pairs, ten labels, eleven ordinary references, three citations,
25 index commands, 24 item markers, 280 mathematical surfaces, seven
definitions, four examples, one lemma, one proposition, one remark, two
proofs, and one convention. It contains no exercises, hints, solutions, or
diagrams and has zero Han residue.

## Mathematical and editorial closure

Correction `O013-LI-U025-COR-001` is explicit and uniquely scoped. In the
integer-subgroup example at authority line 115, the source writes
`H \subset G` even though the ambient group is `\mathbb Z` and no `G` is
introduced. The target uses `H \subset \mathbb Z`, matching the stated
classification `H=n\mathbb Z`. The checker permits exactly this mathematical
delta and no other.

Thirty controlled group-theory rows are admitted, including `semigrup`,
`monoid`, `subgrup`, `grup sederhana`, `grup siklik`, `koset`, `grup
selang-seling`, and `hukum pembatalan`. Group and element size use `orde`,
while `unsur identitas` retains `unsur satuan` as a defining synonym.

One collective target-only localization event adds explicit Indonesian display
aliases to four descendant MakeIndex records. It preserves the source
romanization sort keys and all index semantics while preventing exposed
`yaobanqun` and `qun` hierarchy heads. Exact identities and scope are recorded
in `qa/UNIT_025_INDEX_LOCALIZATION_AND_REFLOW_AUDIT_20260825.md`, 4,154
bytes, SHA-256
`3e836984f6c0468d2b491c8f786472fed5de2fb61aab6cdefe251f8ba4f68c25`.

## Reader, structure, and visual QA

- Driver: `repo/source/unit-025-bab-4-semigrup-monoid-dan-grup.tex`, 8,176
  bytes, SHA-256
  `8a9bed7ac738ab41b663951b0cdb18186f88b249622da1b5187df4f6c12fd30c`.
- Cover: `repo/source/coverpage-id-unit-025.tex`, 3,576 bytes, SHA-256
  `f0f9fb7f1232b92cb469678b7664113ea4c2a19b4e285306751c33604086c28d`.
- External-reference witness: `repo/source/unit-025-crossrefs.aux`, 351
  bytes, SHA-256
  `cbfc9fee8e501a1675a15ed8e763882f48523bfbe59fcf50523eda12d65342e9`.
- Reader: `artifacts/unit-025-bab-4-semigrup-monoid-dan-grup-id.pdf`, ten
  pages, 123,117 bytes, SHA-256
  `511d1c0889c0882639be49d00580c0634de7e3074c757616ac10a3f2fa854615`.
- Build log: `qa/UNIT_025_BUILD_FINAL.log`, 85,827 bytes, SHA-256
  `ee9a4e064edf0cf8cc4710e32c89eda7a8623bceb5ec5fbc75d8ef663826cd2a`.
- Structured PDF evidence:
  `qa/unit-025-evidence/structure-and-pdf-qa.json`, 38,927 bytes, SHA-256
  `235a69a3fbb0841707faef94f0c3d968c7d0c5a1833a4c98b1b4b2fc896ccab3`.
- Render inventory: `qa/unit-025-evidence/render-hash-inventory.json`,
  14,979 bytes, SHA-256
  `ec007cc1a58aeb14dcc413aa759c5b75cfda727a645e66c878095a94a2f4c080`.
- Visual receipt: `qa/UNIT_025_VISUAL_QA_20260825.md`, 6,502 bytes,
  SHA-256
  `e4b110846836f0690805030e920d7749d143e23eff3a6e8b31283b68b730ba43`.

All ten pages were inspected in Poppler and MuPDF. H, I, and the frozen
artifact produce 60 same-renderer page renders with zero decoded-pixel
mismatches and identical semantic text. The PDF has five outline entries, 50
named destinations, 32 resolved internal `GoTo` actions, six intended HTTPS
URI actions, 25 embedded/subset fonts, `id-ID` language metadata, no unsafe
actions, and no broken named target. The centered 142 mm digital reflow has no
clipping, overlap, tofu, edge contact, orphan heading/formula, split guidance
fragment, cross-page hyphen fragment, sparse final-content page, or exposed
Pinyin index head.

The file is not tagged; this is recorded as an accessibility limitation. One
pypdf-only extraction maps the displayed Unicode minus in `-x` to NUL, while
MuPDF/Fitz and Poppler recover U+2212 and the glyph is visually correct.
pdfplumber identifies the same CID. This is an explicitly adjudicated parser
limitation, not missing content or a rendering defect.

## Modular backend

Canonical JSON:
`backend/data/unit-025-bab-4-semigrup-monoid-dan-grup.json`, 328,559 bytes,
SHA-256
`478545e6f43f8557b3ea2da4dece92b9346886139cd3dea114336746aa9357a1`.
It contains 474 total entities: five root records, two sections, 404
concept-compatible entities, 19 prerequisites, four rights records, three
citations, 25 index records, one build surface, and eleven QA events.

The 404 concept-compatible entities include 27 environment records, ten
labels, eleven ordinary references, 24 item markers, 280 formulas, 30
terminology records, one source correction, and one collective target-only
index-localization record. No exercise, hint, solution, or diagram entity is
invented for this source span.

The six deterministic CSV projections are:

| File | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `backend/csv/unit-025-bindings.csv` | 101 | 23,457 | `f5c3dbee19ef73a22785687cb2cac7c0119416a668e756fc1861be463ada73ff` |
| `backend/csv/unit-025-entities.csv` | 474 | 93,457 | `c794d6687345542829d9de5bcdd3c7605e9cc40da1f844b0852ba46ea0d5a8e9` |
| `backend/csv/unit-025-qa.csv` | 11 | 4,481 | `628889d89573d3cc94a9f1be131c61f584de50ce9d9e6c09a4b33f10cc69f81f` |
| `backend/csv/unit-025-relations.csv` | 885 | 220,016 | `7da2909a2022d727ba61b60ce37c919ab31152e76c501f3cd7e0718dfd92655e` |
| `backend/csv/unit-025-rights.csv` | 4 | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
| `backend/csv/unit-025-surfaces.csv` | 29 | 6,961 | `b75ee120a430d832b696cc7bbfc063062c74f8e94ea863178f01721efd699b25` |

The dedicated validator passed four observed runs, including two independent
runs after generation; the shared validator passed twice. Each dedicated run
performs two additional deterministic regenerations. All 101 binding
occurrences across 34 unique live paths, including 56 line spans, match exact
bytes, ranges, hashes, ownership, rights, build, and QA records. No validation
run mutated the canonical JSON or CSV outputs.

Backend evidence:
`qa/unit-025-evidence/backend-validation.json`, 4,742 bytes, SHA-256
`6e07fdbf2b7e450eb6f22b0b680f924e1276db3eedcfd9a39bc630f244d7ba04`.

## Validation commands

```text
python -B scripts/check_unit_025_candidate.py
python -B scripts/check_unit_025_structure.py
pwsh -NoProfile -File scripts/build_unit_025.ps1 -OutputDirectory build/unit-025-replay
python -B scripts/generate_unit_025_backend.py
python -B scripts/validate_unit_025_backend.py
python -B scripts/validate_backend.py --lane-root . --data backend/data/unit-025-bab-4-semigrup-monoid-dan-grup.json --schema backend/schema/open-math-corpus-unit.schema.v1.json --csv-dir backend/csv
```

## Rights boundary and conclusion

The principal source text and Indonesian translation remain CC BY 4.0. The
credited `AJbook.cls` fragment remains CC BY-SA 3.0. Bundled Noto fonts remain
SIL OFL 1.1. `Lanzhou.png` remains CC BY-SA 3.0 in the wider closure and is
not used by this reader. The backend preserves these as separate components.

Unit 025 is admitted as a reproducible, visually checked, source-bound
Indonesian reader unit. It advances the canonical Li cursor to
`chapter4.tex:177`, the beginning of Section 4.2. It does not claim that
Chapter 4, Li Volume 1, or the complete O013 composite course is finished.
