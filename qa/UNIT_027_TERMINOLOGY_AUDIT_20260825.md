# Unit 027 terminology and style audit — 2026-08-25

Status: **PASS; two bounded controlled-style normalizations applied by the
parent lane and a 9-row additive glossary delta approved.** This audit is
limited to Unit 027 and does not itself admit the canonical source, controlled
glossary, backend, controls, reader, artifacts, Git history, or public release.

## Compared identities and boundary

- Authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`,
  154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Exact authority span: lines 365–517 inclusive. Lines 365–516 are the 152
  substantive records of Section 4.3; line 517 is the blank boundary record.
- Candidate:
  `build/unit-027-candidate/chapter4-products-group-extensions-id.tex`,
  12,675 bytes, SHA-256
  `aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563`.
- Controlled glossary: `00_control/TERMINOLOGY.id-ID.csv`, 374 data rows,
  58,658 bytes, SHA-256
  `5ecccbbdbe99ce3dbe05baf42088c401e261663432d1116abcab66d2165abe17`.
- Independent review: `qa/UNIT_027_INDEPENDENT_REVIEW_20260825.md`, 6,104
  bytes, SHA-256
  `28d0834da4d076a4926ccc10b956c32a3445453567abff9c449ee7eeeae843ef`.

I compared the complete authority span and candidate record by record, then
checked every reusable Unit 027 expression against the complete controlled
glossary. The independent review's type-precision repair at candidate record
146 is correct: `pembatasan automorfisme adjoin` accurately describes
`\Ad(s(h))|_N` without claiming that its restriction is inner on `N`.

## Required integration normalizations

The candidate uses the official-glossary synonym `unsur satuan` twice, but the
controlled row `identity element -> unsur identitas` requires `unsur identitas`
as the corpus form. The parent lane applied these two exact prose-only changes
before canonical promotion:

1. Candidate record 8 / authority line 372:
   `unsur satuannya adalah` -> `unsur identitasnya adalah`.
2. Candidate record 41 / authority line 405:
   `unsur satuannya adalah` -> `unsur identitasnya adalah`.

No mathematical notation, environment, label, reference, diagram, index key,
or source correction changes. If the official synonym is reintroduced at a
future defining occurrence, the controlled form should lead, for example
`unsur identitas (juga disebut unsur satuan)`; it need not be repeated here.

## Additive glossary delta

`build/unit-027-staging/terminology-delta.csv` contains exactly 9 admitted rows
in source order: 1,959 bytes, SHA-256
`5a661682e425f53ed0bd25a3f1badd6cdc83b396946901573bcb0c7d8e1a977e`.
None duplicates an existing `source_term`, and all five columns match the
controlled schema:

1. `projection homomorphism` -> `homomorfisme proyeksi`
2. `semidirect product` -> `produk semilangsung`
3. `internal semidirect product decomposition` ->
   `dekomposisi produk semilangsung internal`
4. `dihedral group` -> `grup dihedral`
5. `internal direct product` -> `produk langsung internal`
6. `group extension` -> `ekstensi grup`
7. `equivalence of group extensions` -> `ekuivalensi ekstensi grup`
8. `splitting (of an extension)` -> `pemecahan`
9. `split extension` -> `ekstensi terpecah`

These rows are additive vocabulary controls, not claims of direct external
same-field attestation. Their notes state the mathematical scope and preserve
the important distinctions: splitting as the map versus split as the extension
property, internal versus external product constructions, and the algebraic
dihedral construction versus its `n >= 3` geometric model. Generic
compositional terms and elementary geometry vocabulary are intentionally not
added.

## Terms already controlled and correctly used

The candidate correctly reuses `produk langsung`, `monoid`, `operasi biner`,
`invertibel`, `sifat universal`, `homomorfisme trivial`, `subgrup normal`,
`normalisator`, `grup siklik`, `barisan eksak`, `diagram komutatif`,
`surjektif`, `kernel`, and `automorfisme adjoin`. The wording
`pembatasan automorfisme adjoin` at record 146 should remain unchanged.

Conclusion: the two `unsur identitas` normalizations are present in the pinned
candidate. After merger of the 9 nonduplicative delta rows, Unit 027
terminology is internally consistent and ready for the separate promotion,
build, backend, reader, visual-QA, receipt, and publication gates.

Production provenance for this terminology decision: OpenAI Codex
gpt-5.6-sol, Ultra, acting on the user's instruction; this does not alter or
replace the source author's credit.
