# Unit 026 admission — 2026-08-25

Status: **PASS — admitted locally; publication readback is the next gate.**
Unit 026 is the complete contiguous Indonesian translation of Section 4.2 of
Wen-Wei Li, *Methods in Algebra, Volume 1*: homomorphisms, quotient groups,
the isomorphism theorems, cyclic groups, Grothendieck group completion, and the
resulting adjunction. Translation, mathematical topology, terminology,
correction provenance, canonical integration, reader, component rights,
modular backend, deterministic projections, clean build, and all-page visual
QA pass their admission gates.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. This provenance is
separate from Wen-Wei Li's authorship and every retained human/source credit.

## Frozen source and canonical translation

- Authority: `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`,
  154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Authority boundary: physical lines 177–364 inclusive, 188 records and
  15,360 bytes, SHA-256
  `4377d6a31512cf3e2a56f4e8e1c3417b62ff1a6468eb85629c8d9867a4f975f8`.
  Line 364 is only the blank section separator. The 187 substantive records at
  lines 177–363 map one-for-one to the candidate.
- Final reviewed candidate:
  `build/unit-026-candidate/chapter4-homomorphisms-quotients-id.tex`, 187 LF
  records, 19,424 bytes, SHA-256
  `a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87`.
- Canonical target: `repo/source/chapter4.tex`, 163,745 bytes, SHA-256
  `fc3fd6ef470d41f146456bfc889eb7c7ec84bb48890f1b23f18e51a195e7d463`.
  Target lines 179–365 are byte-identical to the candidate; target line 366
  resumes the untouched authority at source line 365. The admitted Unit 025
  prefix and the 123,856-byte authority suffix remain byte-bound by the
  structure checker.
- Controlled terminology: `00_control/TERMINOLOGY.id-ID.csv`, 374 unique data
  rows, 58,658 bytes, SHA-256
  `5ecccbbdbe99ce3dbe05baf42088c401e261663432d1116abcab66d2165abe17`.
  Unit 026 contributes exactly 33 admitted rows.

Both fail-closed translation and integration checkers pass repeatedly. The
admitted content retains 36 textual environment pairs (35 active plus one
translated commented-out `align*` pair), 12 labels, 18 ordinary references,
six equation references, one citation to `DN00`, 12 list items, 275 protected
mathematical zones, three `tikzcd` diagrams with 12 arrows, and ten index
entries. It has no exercises, hints, answers, or solutions and no Han residue
in the translated span.

## Mathematical and terminology closure

Four source corrections are explicit and uniquely scoped:

1. `O013-LI-U026-COR-001` parenthesizes `H/(N\cap H)` in the second
   isomorphism theorem, including the preserved commented proof.
2. `O013-LI-U026-COR-002` uses one symbol, `\varphi`, for the homomorphism
   introduced and then composed in the group-completion construction.
3. `O013-LI-U026-COR-003` restricts `[x]^{-1}=[x^{-1}]` to the group case;
   arbitrary quotient monoids need not have inverses.
4. `O013-LI-U026-COR-004` states the finite cyclic quotient order as
   `|n/m|` for `n\ne0` and handles the `n=0` infinite/trivial cases
   explicitly.

The controlled delta includes `homomorfisme semigrup`, `automorfisme dalam`,
`automorfisme adjoin`, `kernel`, `homomorfisme terimbas`, `grup hasil bagi`,
`relasi pencakupan`, `pembangkit`, `grup Grothendieck`, and `kategori-U`.
The final reader also consistently uses `peta pelestari struktur`, `unsur
identitas`, `grup unit`, and `diagram komutatif`. The narrower phrase
`automorfisme adjoin` correctly describes the displayed automorphism
`\operatorname{Ad}_x:G\to G` and remains distinct from categorical
`pasangan adjoin`.

## Reader, structure, and visual QA

- Driver: `repo/source/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.tex`,
  6,257 bytes, SHA-256
  `01e707bfc20170ebf732b8df8619db6aa00040251ba426831ab5648a47bcb6c5`.
- Cover: `repo/source/coverpage-id-unit-026.tex`, 3,664 bytes, SHA-256
  `2f0a415d54b36cfe99f7ed6c04c3493ff633c6c483aa843a12ce02931063b999`.
- External-reference witness: `repo/source/unit-026-crossrefs.aux`, 445 bytes,
  SHA-256
  `a5197d6e72d92b8c26749d924a545b3ced53f28648714b96c954d60a28cbe137`.
- Reader: `artifacts/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi-id.pdf`,
  nine pages, 115,284 bytes, SHA-256
  `e3c0e0241901eb0f5f2477a1fe09f64eff34af325dc209b25aa8d71900deb089`.
- Final build log: `qa/UNIT_026_BUILD_FINAL.log`, 86,417 bytes, SHA-256
  `f26903ed598b9191005e00dd8f2d55b2de09eb0464722ed5bef24e9f9f93f8fd`.
- Structure/PDF receipt:
  `qa/unit-026-evidence/structure-and-pdf-qa.json`, 48,059 bytes, SHA-256
  `37e5aefb3bcea6fe78e17cb5dd881107590384f835a8f4cbc0b27258f91922e0`.
- Render inventory: `qa/unit-026-evidence/render-hash-inventory.json`, 41,318
  bytes, SHA-256
  `74fd7daa416595c6adc0d8c541db22756df655bdcd067c5d4985d5dc482f5731`.
- Visual receipt: `qa/UNIT_026_VISUAL_QA_20260825.md`, 4,333 bytes,
  SHA-256
  `b601c16c0a391484064f269998567ab8cb4919a0301433d8a4d0deacd287ebfe`.

The centered 142 mm digital measure and prose scope panel remove the ambiguous
filled/unfilled progress-block convention. Two final clean builds and the
frozen artifact produce 54 page images. All C-to-D and D-to-artifact decoded
pixels are identical within both Poppler and MuPDF, and all 54 outer
three-pixel edge bands are clear. Every artifact page was inspected in both
engines: no clipping, overlap, tofu, edge contact, orphaned heading/formula, or
sparse terminal page is present. Bibliography and both indexes use the
available lower portion of page 9.

The PDF has four outline entries, 44 named destinations, 25 closed internal
`GoTo` actions, three intended HTTPS URI actions, `id-ID` language metadata,
embedded fonts, no forms, JavaScript, embedded files, encryption, or unsafe
actions. It is untagged, which remains a disclosed accessibility limitation.
The installed Poppler lacks its Adobe-GB1 mapping and consequently omits the
five-glyph Chinese bibliography title from its page-9 extraction/render;
MuPDF renders and extracts that embedded-font title correctly. This is a
recorded local Poppler limitation, not missing source or reader content.

## Modular backend

Canonical JSON:
`backend/data/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.json`, 352,612
bytes, SHA-256
`cceb010d8569c01e9fd7fb4149765da798a0c00409cadeb743a0326d192df29c`.
It contains 491 UUIDv5 entities overall and 432 concept-compatible entities.
The latter bind the complete environment, label, reference, item, formula,
terminology, and correction surfaces; the native citation, diagram, and index
records remain first-class. No exercise, hint, answer, or solution surface is
invented.

The six deterministic CSV projections are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `backend/csv/unit-026-bindings.csv` | 17,161 | `37e4fd60b495a19ec90fb62ef8be8f0aa95d670041fd266d5586564eacec598f` |
| `backend/csv/unit-026-entities.csv` | 107,430 | `9ccc9ae7290fda3fcce488345a585255b22cecbdd6475fb8c76001ecad23795f` |
| `backend/csv/unit-026-qa.csv` | 5,578 | `f5bd9a379402d2d005c0e01163d18deb357c4c011498657a144e90aea41148ea` |
| `backend/csv/unit-026-relations.csv` | 270,652 | `2940e1cf9f3ee2d96f1f14e9060da68213c1c1dc90861d237f1a32e5f1902327` |
| `backend/csv/unit-026-rights.csv` | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
| `backend/csv/unit-026-surfaces.csv` | 3,424 | `ab151d44b097203e4117e789a40763e2899efa4de49e040ffceebc7890b2d7a3` |

The dedicated validator passed two independent root runs after its own two
deterministic regenerations per run; shared schema/UUIDv5 validation also
passes. All 80 binding occurrences across 39 unique live paths, including 30
line spans, match exact bytes and hashes. Backend evidence is
`qa/unit-026-evidence/backend-validation.json`, 5,336 bytes, SHA-256
`adabebe72d4a2c277f72cc300bed63e8496e040d44218a5c89bc1381512735a8`.

The final independent read-only audit is recorded in
`qa/UNIT_026_FINAL_AUDIT_20260825.md`. It reruns all three gate families,
checks every JSON/CSV surface, UUIDv5 identity and relation, confirms numbering
and absence of invented exercise/solution records, and finds no admission
defect.

## Rights boundary and conclusion

Principal source text and Indonesian translation remain CC BY 4.0. The
credited `AJbook.cls` fragment remains CC BY-SA 3.0; bundled Noto fonts remain
SIL OFL 1.1. `Lanzhou.png` remains CC BY-SA 3.0 in the wider source closure
and is not used by this reader. The backend preserves these rights as separate
components. The derivative is independent and non-endorsed.

Unit 026 is a reproducible, reflowed, source-bound Indonesian reader unit. Its
local admission advances the canonical Li cursor to `chapter4.tex:365`, the
beginning of complete Section 4.3. It does not claim that Chapter 4, Li Volume
1, or the composite O013 course is finished. Zenodo checkpoint `0.6.0` remains
the latest chapter-complete preservation version through Unit 024; this single
partial Chapter 4 unit does not create a duplicate preservation record.
