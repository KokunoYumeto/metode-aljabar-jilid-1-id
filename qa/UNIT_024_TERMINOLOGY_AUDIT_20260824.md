# Unit 024 terminology promotion audit — 2026-08-24

Status: **PASS — all seven staged rows are justified and admitted.** This
operation changed only the live terminology glossary and this audit receipt.
It did not modify the Unit 024 candidate, canonical Chapter 3 source, backend,
controls other than the glossary, reader files, README, Git state, or any
public record.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.

## Frozen inputs

- Proposed delta:
  `build/unit-024-staging/qa/UNIT_024_TERMINOLOGY_DELTA_PROPOSED_20260824.csv`,
  seven data rows, 1,341 bytes, SHA-256
  `d7e4c6a54bef6573481a5e157bc9327bc392dc6c3ae1e9ad0ccc6f24caf4153d`.
- Pre-promotion review:
  `build/unit-024-staging/qa/UNIT_024_PREPROMOTION_AUDIT_20260824.md`, 6,762
  bytes, SHA-256
  `bc809190caf4d3074050665f68b863629ccd26f194a9832223678ec230a1f298`.
- Staged read-only verifier:
  `build/unit-024-staging/qa/check_unit_024_prepromotion.py`, 11,751 bytes,
  SHA-256
  `eb473d4fe3680a6b8eb6bb68d4bf1414704616008f33c0ded3ade444bc6216df`.
- Live glossary before promotion: 304 data rows, 45,230 bytes, SHA-256
  `9e2d946520a1c9f8984abd1b78935c2fe052e5bfdf79e9c9091d41a29b7cd68a`.
  Reconstructing the pre-promotion prefix from the promoted file reproduces
  those exact bytes and that exact hash.

The current Unit 024 candidate was inspected read-only at
`build/unit-024-candidate/chapter3-exercises-id.tex`, 6,071 bytes, SHA-256
`576c39746534853cd5127298cf0c2ba7f6afb239e4d7b83f368b7a9969c5f43a`.
It already contains the three prose refinements requested by the staged
pre-promotion review. This terminology operation did not edit it.

## Schema, uniqueness, and ordering checks

- Both CSV inputs parse strictly as UTF-8 with the same five columns, in this
  exact order: `source_term,target_term,status,scope,note`.
- The live glossary had 304 data rows and no duplicate `source_term`; the
  proposed delta had seven rows, no duplicate `source_term`, and no source-term
  overlap with the live glossary.
- The seven rows were appended as one contiguous Unit 024 block in the exact
  staged order. Every field is byte-for-byte the staged value after CSV parsing
  except the deliberate status transition from `proposed` to `admitted`.
- The 304-row prefix remains byte-identical to the pre-promotion glossary.
- The resulting glossary has 311 data rows and no duplicate `source_term`.
- One target-term reuse is deliberate rather than conflicting:
  `morphism between functors` and the already admitted `natural transformation`
  both map to `transformasi natural`. In the functor-category context, these
  name the same mathematical structure. No other proposed target duplicates a
  live target.

## Adjudicated rows

| Source term | Admitted Indonesian | Decision |
|---|---|---|
| `Catalan number` | `bilangan Catalan` | Admitted. It is the transparent mathematical noun plus the unchanged proper name and occurs once in the candidate hint. |
| `quantum integrable system` | `sistem integrabel kuantum` | Admitted. It preserves the controlled technical adjective `integrabel` and Indonesian modifier order; it occurs once in the Yang--Baxter exercise. |
| `Drinfeld center` | `pusat Drinfeld` | Admitted. It retains the proper name and uses `pusat` consistently for the center construction; it occurs once. |
| `categorification` | `kategorifikasi` | Admitted. The productive technical nominalization is concise and unambiguous in the sentence relating the Drinfeld and monoid centers; it occurs once. |
| `monoid center` | `pusat monoid` | Admitted. It forms a consistent center family with `pusat Drinfeld` and occurs once in the same defining sentence. |
| `functor isomorphism` | `isomorfisme natural antarfungtor` | Admitted. The displayed map is an isomorphism in a functor category, hence a natural isomorphism; the expanded Indonesian form prevents it from being mistaken for an arbitrary objectwise isomorphism. It occurs once. |
| `morphism between functors` | `transformasi natural` | Admitted as an intentional semantic alias. Morphisms in the relevant functor category are natural transformations, and the displayed 2-cell has exactly that type. The candidate uses the target phrase twice. |

Direct candidate occurrence census: `bilangan Catalan` 1, `sistem integrabel
kuantum` 1, `pusat Drinfeld` 1, `kategorifikasi` 1, `pusat monoid` 1,
`isomorfisme natural antarfungtor` 1, and `transformasi natural` 2.

## Promoted output

`00_control/TERMINOLOGY.id-ID.csv` now contains 311 data rows, 46,585 bytes,
SHA-256
`4fa4c6d2720dd7ab9c4ebe570a1124794bc8282af1b4491201fb61b7b973ce1b`.
All seven promoted rows have status `admitted`; the earlier 304 rows and their
order are unchanged.
