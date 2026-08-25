# Unit 027 final independent admission audit — 2026-08-25

Status: **PASS — no admission defect found.** This audit was performed after
canonical source integration, reader construction, final dual-renderer visual
evidence, and the additive repair that binds the canonical visual evidence in
the modular backend. It does not claim that Chapter 4, Li Volume 1, or the
composite O013 course is complete.

Production provenance is **OpenAI Codex gpt-5.6-sol, Ultra**, acting on the
user's instruction. This is separate from Wen-Wei Li's authorship and all
retained human and component credits.

## Replayed gates

The following four commands were run against the final live files and all
returned exit code 0:

```text
python scripts/check_unit_027_candidate.py
python scripts/check_unit_027_structure.py
python scripts/validate_unit_027_backend.py
python scripts/validate_backend.py --data backend/data/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup.json
```

The candidate gate reports 153 authority records / 10,209 bytes / SHA-256
`bb7cb2d385018971fe325c417bcafdccd9e92376c02e7cb72d3af038097f8db8`,
152 target records / 12,675 bytes / SHA-256
`aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563`,
and next boundary `chapter4.tex:518`. The structure gate reports canonical
`repo/source/chapter4.tex` as 166,211 bytes / SHA-256
`5a4ec3ec5f420c694f7e1207f02a79c558da0f18c6c1f23969856c481f9a7420`.
Target lines 366–517 are byte-identical to the candidate. The following 1,381
records are line-identical to authority lines 518 onward; the only raw-byte
difference in that suffix comparison is terminal-newline serialization.

All final JSON files parse. All six CSV projections parse and reproduce the
canonical data exactly:

| Projection | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `unit-027-bindings.csv` | 80 | 17,194 | `4d31f0e9423d69690e86e61c598f8583b97df3863500e37c9537aff66d018c03` |
| `unit-027-entities.csv` | 364 | 75,869 | `45c8bf8f6ae3ff57bff24e007e6e29f99b0e67d375f827230ab666165938281a` |
| `unit-027-qa.csv` | 16 | 6,263 | `7bb6d80fe260cc3528d464fce4690b92a1c1af6c859a7a32587ae1a6b4875997` |
| `unit-027-relations.csv` | 683 | 206,505 | `c98d5e6a79d46171b806d3294b96b2afadc983d89edf99cd8a86dad3fa1915c4` |
| `unit-027-rights.csv` | 4 | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
| `unit-027-surfaces.csv` | 14 | 3,156 | `c340c91ea58623cf7d294139d687330c591fffb8af8ab1532e2aa21400b2f178` |

The canonical backend is 262,798 bytes / SHA-256
`c014e552acfa52db88c15784d4150708465faf9fe54a5fcd839d8742dec8abf4`.
The dedicated validator performs two regenerations, proves byte stability,
runs the shared schema/UUIDv5 validator, audits 364 UUIDv5 entities and 80 live
binding occurrences over 38 paths, and reports no mutation of generated
outputs. Backend evidence is 5,871 bytes / SHA-256
`5139e94b9cf6863d2c47887fddc51b657f04553ed7ba15e35fd082f4303e2c84`.

## Independent content reconciliation

The exact authority boundary is `chapter4.tex:365-517`; line 517 is the blank
separator and is omitted from the 152-record source-to-target mapping. Coverage
is complete and ordered: direct products and their universal property;
semidirect products; internal decompositions; the dihedral example; direct
products internal to a group; exact sequences; group extensions; splittings;
and the split-extension/semidirect-product correspondence.

The final topology census is exact: 28 environment pairs, eight labels, four
ordinary references plus one equation reference, 171 protected mathematics
zones, 15 list items, four `tikzcd` diagrams with 30 arrows, three polygon
drawings with 15 drawing commands, six index entries, nine admitted terminology
rows, and zero citations, exercises, hints, answers, or solutions. All nine
terminology-delta rows are admitted in the 383-row controlled glossary.

The only mathematical/source changes are the two disclosed repairs:

1. `O013-LI-U027-COR-001` restores the product
   `\prod_{i\in I}M_i` as the codomain in the universal property.
2. `O013-LI-U027-COR-002` restricts the regular-polygon interpretation of
   `D_{2n}` to `n\geq3` while leaving the wider algebraic construction intact.

`O013-LI-U027-TR-001` is separately typed as a translation-precision repair:
the action induced by a splitting is described as the restriction of an
adjoint automorphism, not necessarily an inner automorphism of `N`. The two
remaining normalizations only replace accepted synonyms by the controlled
phrase `unsur identitas`; they change no formula or topology.

## Reader, evidence, and rights

The final reader has seven pages, 97,427 bytes, and SHA-256
`8eeab2d34a745b0e5a12acc29c0c5474e9c84d1248686d743302c03859851dd7`.
The final visual gate binds 42 renders from two clean builds and the artifact in
Poppler and MuPDF. All C-to-D and D-to-artifact decoded-pixel comparisons are
identical within each renderer; outer three-pixel edge bands are clear. The PDF
has `id-ID` language metadata, three outline entries, 30 closed named
destinations, ten safe internal links, three HTTPS links, 22 embedded fonts,
and no form, JavaScript, embedded file, encryption, or unsafe action. The PDF
is untagged; that disclosed accessibility limitation is not an admission
failure. Canonical visual evidence, structure/PDF evidence, render inventory,
and the earlier independent preflight remain distinct bound witnesses.

Rights remain non-flattened: principal text and Indonesian translation are CC
BY 4.0; the credited `AJbook.cls` fragment is CC BY-SA 3.0; bundled Noto fonts
are OFL 1.1; `Lanzhou.png` is CC BY-SA 3.0 and is not used by this reader. The
backend preserves attribution, change disclosure, non-endorsement, and each
component treatment separately.

Conclusion: Unit 027 satisfies the source, translation, mathematical,
terminology, topology, build, reader, visual, accessibility-disclosure,
backend, deterministic-projection, provenance, and rights gates. It is fit for
local admission and narrow public publication. The next canonical source
boundary is `chapter4.tex:518`, Section 4.4.
