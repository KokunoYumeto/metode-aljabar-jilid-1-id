# Unit 025 terminology audit — 2026-08-25

Status: **PASS; thirty controlled group-theory rows admitted before canonical
integration.**

## Exact boundary

- Unit: `O013-LI-U025`, Chapter 4 opening and complete Section 4.1.
- Frozen source: `chapter4.tex:1-176`, 15,528 bytes, SHA-256
  `d88ca03645fd4c781d16907e063b06cd072ad5fbe0e48ce2149d8fdecfb76a52`.
- Refined Indonesian candidate: 20,409 bytes, SHA-256
  `a1a60706d405f7f672b2cbcf99598911db93c1b4fa079779c7501ce4c00b7665`.
- Controlled glossary after promotion: 341 data rows, 51,472 bytes, SHA-256
  `3ed2a7a30aa06e9e574e36b237bf13ab6cec6779703ce91bc3238a107fe526b1`.
- Evidence authority retained locally:
  `authority/terminology-qa-20260822/pusat-bahasa-glosarium-matematika-2008.txt`.
  Its identity and PDF authority are bound by the existing terminology-QA
  manifest; this audit does not represent the OCR text as an upstream edition.

## Direct attestations and decisions

The official 2008 Indonesian mathematics glossary directly attests, among
others, `operasi biner`, `semigrup`, `monoid`, `subgrup`, `subgrup normal`,
`grup sederhana`, `grup siklik`, `koset`, `grup linear umum`, and
`grup selang-seling`. It also attests *cancellation law* as
`hukum pembatalan`. Those forms are admitted and applied consistently.

Two pre-admission repairs were required:

1. `grup alternasi` became `grup selang-seling` at candidate lines 26 and
   104. The selected form is directly attested and matches the independently
   reviewed Unit 033 candidate.
2. `hukum kanselasi` became `hukum pembatalan` four times across candidate
   lines 37, 59, and 144. The selected form is directly attested and already
   occurs in admitted Chapter 2.

The audit did not apply glossary entries mechanically where mathematical
context or corpus consistency points elsewhere:

- The target remains `unsur identitas`, with the directly attested synonym
  `unsur satuan` given at the definition.
- The target remains corpus-wide `grup simetris`; the glossary's
  `grup simetrik` is recorded as a variant.
- Group and element cardinality use `orde grup` and `orde unsur`. The global
  order-theory row `order -> urutan` must never leak into this sense, and the
  older glossary form `tingkat grup` is retained only as evidence, not used.
- OCR defects in the scanned glossary's left-coset and one permutation-group
  line are not propagated; the mathematically transparent forms are
  `koset kiri` and `grup permutasi`.

## Promoted surface

The thirty new rows cover binary operations; magma, semigroups, monoids and
submonoids; identity and left/right cancellation; unit groups; subgroup,
normal/trivial/generated/simple/cyclic subgroup families; group and element
order; cosets and subgroup index; Lagrange's theorem; group center,
centralizer and normalizer; and symmetric, alternating, permutation and
general-linear groups. Each row has a nonempty scope and decision note; the CSV
has 341 unique source terms and parses without duplicate keys.

The revised pinned candidate checker passes twice: 280 mathematical spans, 10
labels, 11 references, three citations, 25 indexes, 24 items, exact environment
topology, one disclosed mathematical correction, and zero Han residue. No
formula, identifier, citation, index stream, exercise, or hint changed during
terminology refinement.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra.** Source authorship,
terminology evidence, independent translation provenance, and non-endorsement
remain separate.
