# Unit 022 admission receipt — 2026-08-24

Status: **ADMITTED**

Unit 022 is admitted as the complete independent Bahasa Indonesia reader and
machine-indexed backend for Section 3.4, “Kategori Diperkaya,” through the end
of the additive-category discussion. Section 3.5 is outside this unit.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. This is separate
from Wen-Wei Li's authorship and all human source credits. The edition is
independent and non-endorsed.

## Frozen authority and canonical target

- Authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`,
  75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Authority span: lines 513–722 inclusive, 210 LF records, 15,089 bytes,
  SHA-256
  `85332852a2b9808a5a9e7ec240adffdd5b286d44d724be38833aed53e65bd53d`.
- Canonical target: `repo/source/chapter3.tex`, 910 LF records, 86,033 bytes,
  SHA-256
  `b395e1014becb462dae95eda5fde37da9b4edd0b477df8f0b5cefef43edbefa2`.
- Canonical Unit 022 span: target lines 512–721, 210 LF records, 17,541
  bytes, SHA-256
  `e1fa8da94c0c2431660f690aa9b2193e3c966e2d71b9d5a029da12a76bc0e255`.
- The target span is byte-identical to the reviewed candidate. Target line 722
  begins `sec:2-cat`; its SHA-256 is
  `26cf19a66c488255e23a0fa8774aca285f48b9049a6111bf2c6fe8d746bdced7`.
- The public driver
  `repo/source/unit-022-bab-3-kategori-diperkaya-dan-aditif.tex` loads only
  the canonical target range with
  `\InputSourceLineRange{chapter3.tex}{512}{721}`. It contains no dependency
  on `build/unit-022-candidate`.

## Reader closure

The admitted reader is
`artifacts/unit-022-bab-3-kategori-diperkaya-dan-aditif.pdf`: 9 pages,
117,933 bytes, SHA-256
`a9144221d3a4d8d01e186d5f7a81714b0ec240590f23dd9ea1dbf06b5252a323`.

Two clean builds and a replay have identical extracted text and same-renderer
rasters. The final structured evidence has 16 exact PASS checks: canonical
full-file identity, canonical-span/candidate identity, next-section boundary,
candidate checker, artifact/final-build identity, page count, semantic replay,
render replay, PDF safety, navigation, accessibility baseline, fonts, text
tokens, build log, page edges, and protected structure. All nine pages were
inspected with Poppler and MuPDF-family renders. The PDF has 28 embedded subset
fonts, 47 named destinations, 17 internal GoTo actions, three URI actions, no
encryption, no unsafe action, and no form or embedded-file payload. It is not a
tagged PDF; that recorded limitation does not change the checked language,
text-extraction, navigation, or visual baseline.

Reader evidence:

- `qa/unit-022-evidence/structure-and-pdf-qa.json`: 17,953 bytes,
  `b461ee52823e8e919006750d0b69ba3b100b0f71d0551b21762945369c2f0bfd`;
- `qa/unit-022-evidence/render-hash-inventory.json`: 10,132 bytes,
  `0511d0f65e2e9e5d0cff76ea7285acfde7f9a31bf1cd9407913b38a410bb47ac`;
- `qa/unit-022-evidence/build-log-summary.txt`: 1,286 bytes,
  `874d78fbd04112da3a9579c5d12721ccc6e202059d2d9fe53d3fda126fa04408`;
- `qa/UNIT_022_BUILD_FINAL.log`: 85,480 bytes,
  `ddec6e07c0e42bf938346e3490252a0e6f3acba7a3a0bcdd1e9974b995cd66e3`;
- `qa/UNIT_022_VISUAL_QA_20260824.md`: 6,946 bytes,
  `d0d6484c5df9d61961bc7ce630b00d483175061192b97e3ebc122a851cc3388d`;
- `scripts/generate_unit_022_evidence.py`: 26,705 bytes,
  `c96804cd29dc26eae5f1d287ec8e2e6dd01a4724703ffc6994432f6d68ae249d`.

## Protected mathematical surfaces

The deterministic backend enumerates 41 balanced environment occurrences, 11
labels, 15 ordinary reference occurrences, two citation occurrences, 17 list
items, 204 inline formulas, 11 bracket displays, four display-environment
formulas, nine diagrams, ten index entries, and eleven applicable terminology
records. The diagram census is six `tikzcd` and three `tikzpicture` blocks,
with 21 arrows, 14 nodes, 11 draws, and 13 edge tokens. No exercise, hint,
answer, or solution is invented for this source span.

Two reversible corrections are admitted:

- `O013-LI-U022-COR-001` changes the ill-typed tensor sign between two
  ordinary Hom-sets to their Cartesian product;
- `O013-LI-U022-COR-002` changes the biproduct injection domain from `X_1` to
  `X_i`.

Their exact source/target signatures and mathematical justification are bound
in `qa/UNIT_022_SOURCE_CORRECTIONS_20260824.md`. The math audit is
`qa/UNIT_022_MATH_STRUCTURE_AUDIT_20260824.md`, 7,050 bytes, SHA-256
`28b72b44a016d953a5e984383919249510ed7a11d36bb861192ffdb4bea9aa1a`.

The terminology layer binds eight new admitted records—enriched functor,
enriched natural transformation, enriched category equivalence, Hom-object,
topological category, Ab-enriched category, preadditive category, and additive
functor—plus the applicable existing enriched category, additive category, and
biproduct records. The glossary is 41,824 bytes, SHA-256
`bbe7c8906aa94a96766bb1aacbf1425527593d514fbe83649eea96095ff0d882`.

## Deterministic backend and binding audit

The generator was run from absent Unit 022 outputs and then run again. The
JSON and all six CSV projections were byte-identical across the second
generation. The dedicated validator then performed two more byte-identical
regenerations, ran the shared schema/UUIDv5 validator, and proved that shared
validation did not mutate any output.

The dedicated recursive binding audit checked every binding in the canonical
JSON against live bytes: **84 binding occurrences**, comprising **42 full-file
bindings** and **42 line-span bindings** across **36 unique local paths**.
Every full-file byte count and SHA-256 matched; every line span matched the
declared `sha256-utf8-lines-lf-v1` digest. The canonical source and target are
both present. The reader build inputs bind `repo/source/chapter3.tex` and do
not bind the isolated candidate.

Canonical backend outputs:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `backend/data/unit-022-bab-3-kategori-diperkaya-dan-aditif.json` | 307,946 | `cf6b8e923bf5e6001166ada95aaf014a106dd9beb32b2788a97adb652ce32550` |
| `backend/csv/unit-022-bindings.csv` | 19,068 | `348e9524bd3408ec821317e981af6d7ff1b9754d3cea469dcb239d14612876ca` |
| `backend/csv/unit-022-entities.csv` | 87,049 | `2cceb2147872b30abd3e2e2222dcc2a185c9a8133de9b9e5ed98dbb6b2b3c625` |
| `backend/csv/unit-022-qa.csv` | 4,236 | `d8d58d26b4752b4afebf378d62bd40786914f720101d0aec8ba4a377ad72913b` |
| `backend/csv/unit-022-relations.csv` | 238,099 | `c86eab94476fba3072d1262a8061bd17b3a82b7f0735d5c97415fd0f9056ee10` |
| `backend/csv/unit-022-rights.csv` | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
| `backend/csv/unit-022-surfaces.csv` | 4,984 | `29466479ec998cb279b9f15357f0900fd49903feb4e7e5d045a8717a492d6500` |

The JSON contains 405 concept-compatible UUIDv5 entities: 28 reusable
mathematical concepts and 377 Unit 022 occurrence/correction/terminology
surfaces. Together with the unit, section, prerequisites, rights, citations,
diagrams, indexes, build surface, and QA events, the shared validator reports
464 entities.

Backend tools and validation evidence:

- `scripts/generate_unit_022_backend.py`: 64,571 bytes,
  `426578ae2441b04ddc67fb6ca9ab041768970bb29f27c0d1ec05f0cf70cb499b`;
- `scripts/validate_unit_022_backend.py`: 19,899 bytes,
  `95ca9bf3f4fcff6966bae3ac64af2ceb0812ad3b755ce807e76858f1745f6e1e`;
- `qa/unit-022-evidence/backend-validation.json`: 5,920 bytes,
  `3637ba1f7f36246b2140e07a6fbc4eecd873b4de746c345243e925f6f399d5dc`.

## Rights and terminal boundary

Rights remain component-specific: principal text and Indonesian translation
under CC BY 4.0; the credited `AJbook.cls` fragment under CC BY-SA 3.0; bundled
Noto fonts under SIL OFL 1.1; and `Lanzhou.png` under CC BY-SA 3.0 in the wider
closure but unused by this reader. No flattened whole-closure CC BY claim is
made.

All translation, mathematical, terminology, canonical-integration, reader,
build, visual, backend-schema, stable-ID, rights, and live-binding gates for
Unit 022 pass. The next source-order production boundary is Section 3.5,
authority line 723 onward; this receipt does not pre-admit it.
