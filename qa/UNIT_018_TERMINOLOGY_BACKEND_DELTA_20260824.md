# Unit 018 terminology/backend delta — 2026-08-24

Status: **PASS.** This bounded delta changes no source mathematics, Indonesian reader prose, PDF byte, exercise/hint topology, identifier, or rights record. It refines one machine-facing Indonesian label after a second representative field-usage check and adds five future-facing controlled terms.

## Evidence and decision

- Terminology QA: `qa/TERMINOLOGY_QA_INDONESIAN_GRADUATE_ALGEBRA_20260824.md`, 4,145 bytes, SHA-256 `968996b90af9d53423ee5dcb9b3129961f5b26d5a3c7daacf4e335b6ddbdd490`.
- Evidence manifest: `authority/terminology-qa-20260824/MANIFEST.json`, 1,845 bytes, SHA-256 `b70875379080f304b010c9ceb0374f6d62aa1efc7a8e7470c89d88cdbab5a9e1`.
- Primary PDF witness: 450,227 bytes, SHA-256 `767e89f16a31f952ad4a5c3df74f7422f49abf5a4a4af1e1d1506654b0ad02f6`; retained locally and excluded from public release because no redistribution grant is inferred.
- Controlled glossary: 36,785 bytes, SHA-256 `793d3cb4a80e493ff7b7ba5a81990e8bc965df5cb1932b3ff067af7073668dbc`.
- Refined label: `gelanggang tanpa syarat unsur satuan` → `gelanggang yang tidak disyaratkan memiliki unsur satuan`. The new wording preserves “identity not required” without incorrectly asserting “identity absent.”
- Added terms: `modul unital`, `modul non-unital`, `barisan eksak`, `barisan eksak kanan`, and `keeksakan kanan`.
- Bounded drift search found no admitted reader prose requiring propagation. The Unit 018 PDF remains exactly 83,578 bytes, SHA-256 `4fc2997e6eafc8f2e74d8a03e3351cb49d99a95ae96ff254a211fbf505f6e00c`.

## Deterministic backend result

Two consecutive generator passes and the fail-closed Unit 018 validator reproduced the same 172-entity backend and six CSV projections:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `backend/data/unit-018-bab-2-latihan.json` | 136,931 | `66dd0fe0c8a723b5a7745b8ccea8cb7657598cf027c3d2f50fb26df86a8811c9` |
| `backend/csv/unit-018-bindings.csv` | 14,549 | `cb4720677ce86eb16e75d6104acccfbd118142a01fd3ac3de76914efcb602111` |
| `backend/csv/unit-018-entities.csv` | 31,565 | `001c086a5394143680034e5c49a675f8a43ed447223592bc5a8d2d87f5b4ee3f` |
| `backend/csv/unit-018-qa.csv` | 2,001 | `19e62ccfe5dac6d03c65f59b9050a76a15d4bf0e9ab5ae2e2a34a168b0a67893` |
| `backend/csv/unit-018-relations.csv` | 103,647 | `411ef794b36ad87ed5a42fa41420dae0766e148e472c7a2ef9f1979f8a514993` |
| `backend/csv/unit-018-rights.csv` | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
| `backend/csv/unit-018-surfaces.csv` | 482 | `a25fcc3b922f7240fce820f0648563197a484d7706829aacd89d0237f99b05ce` |

Generator: `scripts/generate_unit_018_backend.py`, 43,295 bytes, SHA-256 `c1226db75877870352f3a29b2fa9481a29f413485efc6ac8cf1e0bd9f929ee42`. Schema, UUIDv5 identity, live bindings, exercise/subpart/hint relations, formula/reference/diagram topology, rights, terminology binding, and exact CSV projections all pass. No answer or solution was invented.

Production provenance: `OpenAI Codex gpt-5.6-sol, Ultra`. This remains separate from Wen-Wei Li’s authorship and every human source credit.
