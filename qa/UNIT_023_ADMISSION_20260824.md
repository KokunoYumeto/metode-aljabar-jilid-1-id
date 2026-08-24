# Unit 023 admission — 2026-08-24

Status: **PASS — admitted.** Unit 023 is the complete, contiguous Indonesian
translation of Li Volume 1, Chapter 3, Section 3.5, from the definition of a
strict 2-category through adjunctions in a 2-category. The final reader,
protected mathematical topology, terminology, component rights, modular
backend, deterministic CSV projections, build replay, and all-page visual
inspection all pass their admission gates.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. This provenance is
separate from Wen-Wei Li's authorship and all human source credits.

## Frozen source and translation boundary

- Authority: `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`,
  75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Authority span: physical lines 723–872 inclusive, 150 LF records, 12,436
  bytes, SHA-256
  `2cb843048ffcb6378c3995e5b80c341000098187638e32af6aa918b87f5e5856`.
- Reviewed isolated candidate:
  `build/unit-023-candidate/chapter3-2-categories-id.tex`, 14,894 bytes,
  SHA-256
  `c15e079bc551b30ad7cc6daf72bee58a90108dc7fa5f101f768275e99d1dad05`.
- Canonical target: `repo/source/chapter3.tex`, 88,491 bytes, SHA-256
  `8ade04d16a5b71d4d1ffdf3bcee6736bb199c631a8851336d692e7ebdced5e7f`.
  Target lines 722–871 are byte-identical to the reviewed candidate. Target
  line 872 is the excluded `Exercises` boundary and the remaining authority
  continuation is unchanged.
- Controlled terminology: `00_control/TERMINOLOGY.id-ID.csv`, 45,230 bytes,
  SHA-256
  `9e2d946520a1c9f8984abd1b78935c2fe052e5bfdf79e9c9091d41a29b7cd68a`.

## Mathematical and editorial closure

The admitted span preserves 25 balanced environment pairs, two labels,
16 ordinary references, 19 active list items, 156 inline formulas, 11 bracket
displays, 14 `tikzcd` diagrams, 64 diagram arrows, and three index entries.
There are no equation references, citations, exercise, hint, answer, or
solution records in this source span. There is no Han residue in the target.

No mathematical source correction was needed. The sole editorial record,
`O013-LI-U023-ED-001`, preserves the authority's romanized adjunction index
sort key and adds the learner-visible Indonesian display payload
`pasangan adjoin`; it changes no prose or mathematics. Twenty applicable
terminology rows are bound: seventeen new higher-category rows and three
previously admitted category-theory rows.

## Final reader and reproducible evidence

- Reader driver:
  `repo/source/unit-023-bab-3-sekilas-tentang-2-kategori.tex`, 5,408 bytes,
  SHA-256
  `e3cd83f5ad24b69e676f8ac833d7796db15c7e28f890f71e0a46156a4d37a630`.
- Reader: `artifacts/unit-023-bab-3-sekilas-tentang-2-kategori.pdf`, seven
  pages, 98,735 bytes, SHA-256
  `5fb682094a829d8abd878aaf3f5e36cda7763323d1a8417d4e36595a7959add4`.
- Final build log: `qa/UNIT_023_BUILD_FINAL.log`, 83,880 bytes, SHA-256
  `1eba3cdbaa85de85e728daac9745f4dd6f7776e9d2315f15348ad23cd0b6c2ef`.
- Structured build/PDF evidence:
  `qa/unit-023-evidence/structure-and-pdf-qa.json`, 34,048 bytes, SHA-256
  `4558664d48c7188dfdfac8ea9f02ec7dae7434b2d0377f027c870c92cb541c23`.
- Render inventory: `qa/unit-023-evidence/render-hash-inventory.json`, 9,634
  bytes, SHA-256
  `c53937157e0a66d6f607956d7969b778c64e23a8f1b0bfc69334f1750c277cf7`.
- All-page visual receipt: `qa/UNIT_023_VISUAL_QA_20260824.md`, 6,108 bytes,
  SHA-256
  `4e8d267e796cb4440ad7e59d05b1cc16703dad7a5bd5ba9ae55ac9d1df04166d`.

The two clean builds are semantically and raster-identical within each
renderer. Poppler and MuPDF inventories cover all seven pages; 56 page renders
and eight contact sheets were checked, with zero same-renderer page mismatch,
zero outer-three-pixel ink, zero overfull boxes, zero undefined references or
citations, zero missing glyphs, and no fatal or emergency build event. PDF
safety, navigation, text extraction, embedded-font, and accessibility-baseline
checks pass. Every page was inspected in both renderer families.

## Modular backend

Canonical JSON:
`backend/data/unit-023-bab-3-sekilas-tentang-2-kategori.json`, 263,346 bytes,
SHA-256
`627bd414c5db75842f02d84ed87063c8bec2f3c3e60166f7a4227b2aa5937f8c`.
It contains 398 total entities, including 343 concept-compatible entities,
one section, 14 diagram records, three index records, 18 available prerequisite
records, one build surface, and nine QA events. The 343 concept-compatible
entities include every protected surface enumerated above, 20 terminology
bindings, 29 pedagogical concept records, and the one editorial normalization.

The six deterministic CSV projections are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `backend/csv/unit-023-bindings.csv` | 17,945 | `32ff0476cba96568337dfce5d93aa6c00af9ba3e20e1c7c25d01ccfa45da24cc` |
| `backend/csv/unit-023-entities.csv` | 72,821 | `48980a9118837239720ffddae0c70da40b46b806020172a2b062644639fee242` |
| `backend/csv/unit-023-qa.csv` | 4,390 | `0f3664948e1c019f847519d0dbc54887b4818453384d86b761827d4707c408ee` |
| `backend/csv/unit-023-relations.csv` | 200,165 | `52ae7f581e7c56b9572694afe3233db8c8fd41bf46e73e3ef533148ef46a30b0` |
| `backend/csv/unit-023-rights.csv` | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
| `backend/csv/unit-023-surfaces.csv` | 3,394 | `8710d4fd376843f0b5e5f728b8d38da54d41c3c282d2bbdf5cfd0bceaf455dc1` |

The dedicated recursive audit examined 80 binding occurrences across 35
unique live paths: 42 full-file bindings and 38 line-span bindings. Every
path exists; every byte count, full-file SHA-256, line boundary, span hashing
algorithm, and normalized span SHA-256 matches the live file. The authority
and integrated target are both in the audited binding set.

Backend validation evidence:
`qa/unit-023-evidence/backend-validation.json`, 5,878 bytes, SHA-256
`730cad441f495c71de26817047e99932ddeecf4dff00942380528fee6d6ba93e`.

## Validation commands and result

The following all returned PASS on the frozen bytes:

```text
python -B scripts/check_unit_023_candidate.py
python -B scripts/check_unit_023_structure.py
python -B scripts/generate_unit_023_evidence.py
python -B scripts/generate_unit_023_backend.py
python -B scripts/validate_unit_023_backend.py
python -B scripts/validate_backend.py --lane-root . --data backend/data/unit-023-bab-3-sekilas-tentang-2-kategori.json --schema backend/schema/open-math-corpus-unit.schema.v1.json --csv-dir backend/csv
```

The dedicated backend validator performed two consecutive deterministic
regenerations and proved that neither regeneration nor shared validation
changed the canonical JSON or any of the six CSV projections.

## Rights boundary

The principal source text and Indonesian translation remain CC BY 4.0. The
credited `AJbook.cls` fragment remains CC BY-SA 3.0. Bundled Noto fonts remain
SIL OFL 1.1. `Lanzhou.png` remains CC BY-SA 3.0 in the wider closure and is not
used by this reader. The backend records these components separately and does
not flatten the closure into a single unqualified license.

## Admission conclusion

Unit 023 is admitted as a reproducible, visually checked, source-bound
Indonesian reader unit. The next source-order boundary is the Chapter 3
exercise block beginning at authority line 873 / target line 872; it is not
part of this admission.
