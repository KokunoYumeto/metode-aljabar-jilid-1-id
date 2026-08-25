# Unit 026 terminology audit — 2026-08-25

Status: **PASS; all 33 reviewed Unit 026 rows are admitted in the controlled
glossary and the justified reader-facing refinements are present in the final
candidate.**

## Exact boundary

- Unit: `O013-LI-U026`, complete Section 4.2.
- Frozen source: `chapter4.tex:177-364`, 15,360 bytes, SHA-256
  `4377d6a31512cf3e2a56f4e8e1c3417b62ff1a6468eb85629c8d9867a4f975f8`.
- Final Indonesian candidate: 19,424 bytes, SHA-256
  `a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87`.
- Controlled baseline before this unit: 341 data rows, 51,472 bytes, SHA-256
  `3ed2a7a30aa06e9e574e36b237bf13ab6cec6779703ce91bc3238a107fe526b1`.
- Reviewed delta: `build/unit-026-staging/terminology-delta.csv`, 33 data rows,
  7,238 bytes, SHA-256
  `29da42f631cb8290e54335142e589c71939040e6f874a0e7f026b9d70caad408`.
- Controlled glossary after exact append: 374 data rows, 58,658 bytes,
  SHA-256
  `5ecccbbdbe99ce3dbe05baf42088c401e261663432d1116abcab66d2165abe17`.

The terminology evidence and candidate-locus review are preserved in
`qa/UNIT_026_TERMINOLOGY_RECOMMENDATION_20260825.md`. Its retained Pusat Bahasa
text is a bounded local extraction whose identity is recorded by its manifest;
neither that recommendation nor this audit claims that the extraction is a
byte-identical official-host download. Direct attestations, normalized older
forms/OCR, and transparent compositions remain distinguished in the delta's
notes.

## Exact admitted delta

The 33 source-to-target mappings are:

| Source term | Admitted target |
|---|---|
| semigroup homomorphism | homomorfisme semigrup |
| identity map | peta identitas |
| trivial homomorphism | homomorfisme trivial |
| inverse | invers |
| isomorphic | isomorfik |
| automorphism group | grup automorfisme |
| group homomorphism | homomorfisme grup |
| group isomorphism | isomorfisme grup |
| group automorphism | automorfisme grup |
| inner automorphism | automorfisme dalam |
| adjoint automorphism | automorfisme adjoin |
| image of a homomorphism | bayangan homomorfisme |
| kernel | kernel |
| quotient map | peta hasil bagi |
| well-defined | terdefinisi dengan baik |
| quotient structure | struktur hasil bagi |
| quotient monoid | monoid hasil bagi |
| induced homomorphism | homomorfisme terimbas |
| surjective | surjektif |
| quotient group | grup hasil bagi |
| quotient homomorphism | homomorfisme hasil bagi |
| coset space | ruang koset |
| surjectivity | surjektivitas |
| inclusion relation | relasi pencakupan |
| generator | pembangkit |
| cyclic subgroup | subgrup siklik |
| congruence | kongruensi |
| commutative monoid | monoid komutatif |
| monoid homomorphism | homomorfisme monoid |
| Grothendieck group | grup Grothendieck |
| cancellation law | hukum pembatalan |
| additive inverse | invers aditif |
| U-category | kategori-U |

Every row has status `admitted`, a nonempty scope, and a nonempty evidence or
decision note. The controlled glossary has 374 unique `source_term` keys. Its
bytes are exactly the 341-row baseline followed by the 33 delta data rows; no
pre-existing row was rewritten.

## Candidate refinements applied

The final candidate applies all twelve surface normalizations identified by
the bounded terminology review:

1. `peta yang melestarikan struktur` → `peta pelestari struktur` and
   `unsur satuan` → `unsur identitas` at candidate line 2;
2. `grup unsur invertibel` → `grup unit` at lines 19 and 20;
3. `unsur satuan` → `unsur identitas` at lines 55 and 90;
4. mixed `yang diinduksi` / `terinduksi` → `terimbas` at lines 64, 70, and
   124;
5. `Diagram yang komutatif` → `Diagram komutatif` at line 64;
6. `relasi inklusi` → `relasi pencakupan` at line 118; and
7. `generatornya` → `pembangkitnya` at line 140.

One additional type refinement was admitted after semantic review. Candidate
line 31 names `\Ad_x:G\to G` an `automorfisme adjoin`, not an `isomorfisme
adjoin`. The map is an automorphism of one group, so the narrower head noun is
mathematically more precise. The controlled row is consequently `adjoint
automorphism`, and this terminology remains distinct from the categorical
`pasangan adjoin` used at the end of the unit.

The contextual choice `bayangan` for `\Image(\varphi)` is retained because
`peta` already denotes a map in this corpus. `Invers aditif` preserves the
controlled inverse family while the older attested `balikan aditif` remains an
observed synonym. `Kongruensi` preserves the already controlled `kelas
kongruensi`; the older `kekongruenan` family is evidence, not the reader form.
The source's four `\text{ord}` operators are mathematical notation and remain
unchanged.

## Deterministic closure

`scripts/check_unit_026_structure.py` pins the baseline glossary, delta, and
final glossary byte identities; checks all 33 exact source/target mappings and
their complete metadata; proves unique keys and exact append topology; and
runs `scripts/check_unit_026_candidate.py` twice. Both candidate runs pass with
identical output: 187 candidate records, 72 environment markers, 12 labels, 24
references, one citation, ten indexes, four declared source corrections, and
zero Han residue.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra.** Source authorship,
terminology evidence, independent translation provenance, and non-endorsement
remain separate.
