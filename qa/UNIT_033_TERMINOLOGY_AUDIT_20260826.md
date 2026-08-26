# Unit 033 terminology audit — 2026-08-26

Status: **PASS; the bounded terminology delta and two target normalizations are
admitted.**

The live glossary before this boundary contained 465 data rows, 74,335 bytes,
SHA-256 `bb58d18ad5802c5c2159db092f0fc322761f8f9559ea7efd3789ab8d7317e582`.
The admitted delta `build/unit-033-staging/terminology-delta.csv` contains 13
data rows, 1,987 bytes, SHA-256
`783f39a1d80f93613f1d60c53ab77c7ce0a4c5c799c8ea25248f427e4049437b`.
The resulting live glossary contains 478 data rows, 76,280 bytes, SHA-256
`9a999be8091cfb9429975d6dcf98aca3d6d3b432ab909891651c9c32e0c79f4c`.
The exact thirteen rows are the live glossary tail; every source term is
unique, every row has status `admitted`, and every target surface is supported
by the final Unit 033 translation.

The preserved pre-admission audit copy
`qa/UNIT_033_TERMINOLOGY_DELTA_20260826.csv` retains the same thirteen term
decisions with status `proposed`; it is 1,987 bytes, SHA-256
`48079d6ee3c7f57adb86e12b3d0cbbb7e10fbc286beacc373725c36e89b3df5f`.
It is evidence of the proposal state, not the admitted control delta.

## Decisions

The admitted rows cover `permutasi`, `siklus`, `permutasi siklik`, `panjang
siklus`, `transposisi`, disjoint-cycle terminology, `dekomposisi siklus`, `tipe
siklus`, `kelipatan persekutuan terkecil`, `permutasi genap`, `permutasi
ganjil`, braid `untai`, and `grup Coxeter`. Existing admitted rows continue to
govern `grup simetris`, `grup selang-seling`, `partisi`, `titik tetap`, `grup
sederhana`, `grup kepang`, `kepang`, `persamaan Yang--Baxter`, `presentasi
grup`, `subgrup turunan`, and `kelas konjugasi`.

Two proposed rows were deliberately rejected: `adjacent transposition` and
`sign homomorphism` are mathematically relevant English aliases, but neither
label is actually named in this source span. The edition does not add absent
labels merely to populate the backend.

The audit found two occurrences of the older target synonym `unsur satuan`,
aligned to authority lines 1407 and 1516. Both now use the established corpus
form `unsur identitas`. The first sentence was also clarified to say that all
cycles of length one may be omitted, resolving an ambiguous plural antecedent
while preserving the exact mathematical claim. These are two separately
counted terminology normalizations, not source corrections.

The terminology pass itself changed no formula, command, environment, label,
reference, index, diagram, quantifier, hypothesis, or source-correction state.
A later, separately documented typography pass promoted one unchanged inline
equality to display mathematics; that one target-only reflow is not attributed
to the terminology audit.

## Final binding

- Candidate: 219 records, 23,099 bytes, SHA-256
  `1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76`.
- Canonical `repo/source/chapter4.tex`: 185,920 bytes, SHA-256
  `a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde`;
  target lines 1384–1602 are candidate-identical.
- Candidate checker: 18,099 bytes, SHA-256
  `643b1ccc5fe1f47aa185cbb8d2813e971c1381cbcc032fac8cc01c2c941c2a1d`.

Repeated checks pass with 43 environment pairs, ten labels, twenty references,
nine indexes, 311 protected mathematics zones, twelve diagrams, four arrows,
nine braid commands, five protected-text localizations, two declared source
corrections, two terminology normalizations, one target-only digital reflow,
and no citations, exercises, hints, answers, solutions, Han residue,
placeholders, or invisible controls.

Production and review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**, acting
on the user's instruction. Source and human-contributor credits remain intact.
