# Unit 024 admission — 2026-08-25

Status: **PASS — admitted.** Unit 024 is the complete, contiguous Indonesian
translation of the eight-exercise tail of Li Volume 1, Chapter 3. The final
reader, protected mathematical topology, disclosed correction, terminology,
component rights, modular backend, deterministic CSV projections, build replay,
and all-page visual inspection pass their admission gates.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. This provenance is
separate from Wen-Wei Li's authorship and all human source credits.

## Frozen source and translation boundary

- Authority: `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`,
  75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Authority span: physical lines 873–911 inclusive, 39 LF records, 4,954
  bytes, SHA-256
  `2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857`.
- Reviewed isolated candidate:
  `build/unit-024-candidate/chapter3-exercises-id.tex`, 6,071 bytes, SHA-256
  `576c39746534853cd5127298cf0c2ba7f6afb239e4d7b83f368b7a9969c5f43a`.
- Canonical target: `repo/source/chapter3.tex`, 89,608 bytes, SHA-256
  `443b71b515aef66c6ba8e259e65083604d227370c1ee7ca3ed49bdb5996f45fb`.
  Target lines 872–910 are byte-identical to the reviewed candidate and end at
  the canonical Chapter 3 EOF.
- Controlled terminology: `00_control/TERMINOLOGY.id-ID.csv`, 311 rows,
  46,585 bytes, SHA-256
  `4fa4c6d2720dd7ab9c4ebe570a1124794bc8282af1b4491201fb61b7b973ce1b`.

## Mathematical and editorial closure

The admitted span preserves eight top-level exercises, three nested items, two
hints, seven balanced environments, four ordinary references, eleven active
items, 69 inline formulas, six bracket displays, two `tikzcd` diagrams, eight
diagram arrows, and the `YBE` index entry. There are no labels, equation
references, citations, answers, or solutions, and there is no Han residue in
the target.

Correction `O013-LI-U024-COR-001` is explicit and separately provenanced. The
authority's unique objectwise ordinal-sum isomorphisms exist, but do not form a
natural family for arbitrary order-preserving maps. The target replaces the
impossible symmetry-proof demand with a naturality test and an explicit
counterexample task; no other mathematical correction was made.

Seven terminology rows are admitted and bound. Backend labels distinguish
English glossary/correction evidence from `id-ID` labels rather than
misidentifying English text as Chinese or Indonesian.

## Final reader and reproducible evidence

- Reader driver:
  `repo/source/unit-024-bab-3-latihan-kategori-monoidal.tex`, 5,067 bytes,
  SHA-256
  `9823e3a5a3f6850d257abd32259583a579920ef062cc84f51b2e515c57772891`.
- Reader: `artifacts/unit-024-bab-3-latihan-kategori-monoidal.pdf`, four pages,
  86,254 bytes, SHA-256
  `eb4ee13fffe6a54a50357a0043aa82e0958b2f30feb92c440b6ea10a5efdc6b4`.
- Final build log: `qa/UNIT_024_BUILD_FINAL.log`, 78,542 bytes, SHA-256
  `62b3dac51522a1bd33ec6bd62a25f6dbef06ccbfa349982bb51b18eabc9c22fe`.
- Structured build/PDF evidence:
  `qa/unit-024-evidence/structure-and-pdf-qa.json`, 33,299 bytes, SHA-256
  `12cf8ec6af6b51fee727e6554ae3f6a182b562f5349a726a6b81389885443c72`.
- Render inventory: `qa/unit-024-evidence/render-hash-inventory.json`, 7,110
  bytes, SHA-256
  `d60e5a81bdd248b659d6440b6d442a8e4f6ca6a15dc0632e9dd45d9139f0c892`.
- All-page visual receipt: `qa/UNIT_024_VISUAL_QA_20260825.md`, 4,536 bytes,
  SHA-256
  `2cb3fc9f74f52a35cabd0b6e0fb786b4d2b5c51528e5f68369b475b8b84a7dde`.

Every physical page was inspected in Poppler and MuPDF. The inventory covers
32 page renders and eight contact sheets. Same-renderer pixel mismatches are
zero for both renderers; extracted text, normalized font families, PDF
structure, and decoded page pixels are stable across clean builds after
adjudicating randomized embedded-font subset prefixes. The admitted reflow has
zero overfull boxes, zero empty-target link warnings, no clipping, and no lost
exercise, hint, formula, diagram, reference, or index entry.

## Modular backend

Canonical JSON: `backend/data/unit-024-bab-3-latihan.json`, 137,184 bytes,
SHA-256
`c07bd1335e1a2aac2e7b008ff61a66c67303709823081c7c5fb0f8b3566b5d39`.
It contains 187 total entities: five root records, eight exercise sections,
139 concept-compatible entities, 18 available prerequisite records, four
rights records, two diagram records, one index record, one build surface, and
nine QA events.

The 139 concept-compatible entities comprise 13 mathematical concepts, seven
environment records, four references, eleven items, eight exercises, three
nested items, two hints, 69 inline formulas, six bracket displays, eight arrow
primitives, seven terminology rows, and the correction record. Surface counts
therefore report eight exercises and two hints rather than zero. Each exercise
section owns its exact concepts and a scoped prerequisite set; the Yang--Baxter
exercise includes linear transformations, while unrelated exercises do not
inherit vector-space or comma-category prerequisites.

The six deterministic CSV projections are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `backend/csv/unit-024-bindings.csv` | 13,858 | `7e71cc79e1b9a2923ca10c1d89c9af48e2eaf0b943ea54d05527e6bfe57146dc` |
| `backend/csv/unit-024-entities.csv` | 34,263 | `b8423f867f06f25995c8eb62806de204264134979bcb0dc37a2f0f29807199e4` |
| `backend/csv/unit-024-qa.csv` | 3,681 | `e3938aae03acc4227285ec9f62661d171e9f99f14d62eae25cda9fbdf09cf119` |
| `backend/csv/unit-024-relations.csv` | 83,609 | `24b60df767c21f0efb83933465441d1f9144a09dbe6fce488023d167ce03290d` |
| `backend/csv/unit-024-rights.csv` | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
| `backend/csv/unit-024-surfaces.csv` | 863 | `8e139c1ea9ee40373487d7af02b7dab0afbfcd8e3e1424eae6c0f821978d83b5` |

The dedicated recursive audit examined 65 binding occurrences across 34
unique live paths: 41 full-file bindings and 24 line-span bindings. Every path,
byte count, full-file SHA-256, line boundary, normalized span hash, section
ownership, prerequisite edge, diagram/index ownership, and unit entity array
matches the live records.

Backend validation evidence:
`qa/unit-024-evidence/backend-validation.json`, 6,143 bytes, SHA-256
`545ddd7bec7730135e388d2da9e7328ef060e34e220472f021faaebdaecb70a4`.

Backend generator: `scripts/generate_unit_024_backend.py`, 47,968 bytes,
SHA-256
`321b02956076924b79d9475b7cee1a1842a20b4807d901f3a0e425edc55a2673`.
Dedicated validator: `scripts/validate_unit_024_backend.py`, 24,833 bytes,
SHA-256
`8057cca699be0f676e50da6be4f149bc2b3a6d2768c8fed9ffd84921b595f9eb`.
Shared validator: `scripts/validate_backend.py`, 40,768 bytes, SHA-256
`67cb86238b3ccdff028e4968d1808609968d971dcf29f849a29728801b616a2d`.

## Validation commands and result

The dedicated validator passed twice on the corrected contract. The shared
validator passed twice independently. Each dedicated pass performed two
additional consecutive regenerations and proved that generation and validation
did not mutate the canonical JSON or six CSV projections.

```text
python -B scripts/generate_unit_024_backend.py
python -B scripts/validate_unit_024_backend.py
python -B scripts/validate_backend.py --lane-root . --data backend/data/unit-024-bab-3-latihan.json --schema backend/schema/open-math-corpus-unit.schema.v1.json --csv-dir backend/csv
```

## Rights boundary

The principal source text and Indonesian translation remain CC BY 4.0. The
credited `AJbook.cls` fragment remains CC BY-SA 3.0. Bundled Noto fonts remain
SIL OFL 1.1. `Lanzhou.png` remains CC BY-SA 3.0 in the wider closure and is not
used by this reader. The backend records these components separately and does
not flatten them into one unqualified license.

## Admission conclusion

Unit 024 is admitted as a reproducible, visually checked, source-bound
Indonesian reader unit. It completes the Chapter 3 exercise tail through the
canonical Chapter 3 EOF.
