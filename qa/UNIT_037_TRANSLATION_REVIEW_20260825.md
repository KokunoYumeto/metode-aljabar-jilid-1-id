# O013-LI-U037 Translation Review — 2026-08-25

Status: isolated candidate complete and checker-admissible; not promoted into
canonical source, glossary, backend, README, durable controls, Git, or any
publication lane.

## Exact authority and frozen boundary

- Frozen authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex`.
- Full authority identity: 122,998 bytes; 1,382 LF-delimited records; SHA-256
  `e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143`.
- Selected source records: absolute lines 174–290 inclusive, 117 records,
  10,243 bytes, SHA-256
  `8309a8125f04a87ab5fd9b1c04b197769e4ddcfbebe07d19523fbac4b3be1b05`.
- The span is exactly the complete section `\section{几类特殊的环}`. It begins
  with centralizers and the center; develops zero divisors, characteristic,
  integral domains, division rings, fields, and prime subfields; proves the
  finite no-zero-divisor proposition and Wedderburn's little theorem; and ends
  with the complete quaternion example.
- Authority line 173 is the blank separator following Unit 036. Authority line
  291 is the blank separator following this section. The next content record is
  line 292, `\section{交换环初探}\label{sec:comm-ring-intro}`. Lines 174–290
  are therefore the smallest coherent complete source-order boundary beginning
  at the supplied cursor.
- Next source-order cursor: `chapter5.tex`, line 292.

## Candidate identity and content census

- Candidate:
  `build/unit-037-candidate/chapter5-special-rings-id.tex`.
- Identity: 13,369 bytes; 117 LF-delimited records; SHA-256
  `9f6ea7b368133027c1a12efef74db48eed36c6db6662fe746b894a938a0825f5`.
- Record correspondence is one-to-one: every selected authority record has
  exactly one candidate record, with no inserted or deleted blank record and
  exactly one LF terminator after record 117.
- TeX census: 36 begin/end environment markers (18 matched pairs), seven
  labels, 14 `ref`/`eqref` references, one citation (`Feng17`), 15 indexes, 186
  protected mathematical zones, 340 unescaped dollar delimiters, and balanced
  raw braces (184 opening and 184 closing).
- Environment-begin census: `equation` 3; `aligned` 1; `definition` 3;
  `example` 2; `proposition` 1; `proof` 2; `theorem` 1; `gather*` 1; `align*`
  1; `cases` 1; `tikzpicture` 1; and `itemize` 1.
- Diagram census: one `tikzpicture`, five `\draw` commands, three
  `\coordinate` commands, and three `\node` commands. The circle, real axis,
  points, labels, joining segment, baseline anchor, radii, and inequality are
  unchanged.
- Item census: four `\item` records, exactly the four defining multiplication
  properties of the quaternion algebra. This span contains no `Exercises`,
  `exercise`, `hint`, or `solution` environment in either authority or
  candidate, so exercise/hint/solution correspondence is exactly zero-to-zero.
- Comment-state census: zero source-disabled records and zero candidate comment
  records. No comment was activated or introduced.

## Source and translation review

- The definitions of `Z_R(x)` and `Z_R` retain all quantifiers, products,
  equalities, and the intersection over every `x \in R`; the candidate renders
  the terms as `sentralisator` and `pusat` and retains the conclusion that the
  center is commutative.
- The unit group, left and right inverses, left and right zero divisors, their
  cancellation-law characterizations, and every nonzero hypothesis are
  retained without changing the source's left/right naming convention.
- The unique structural homomorphism from `\Z` to `R`, its central image, the
  `\Z/p\Z` description, exclusion of `p=1`, characteristic definition, and
  prime-characteristic binomial formula are all preserved.
- The definitions of integral domain, division ring, field, and prime subfield
  retain commutativity, invertibility, nonzero-ring, and characteristic
  hypotheses, including both characteristic-zero and positive-characteristic
  prime-subfield identifications.
- The finite-ring proposition retains the injective-to-bijective argument for
  both left and right multiplication. The sole corrected ambient-ring symbol is
  proved separately below.
- The E. Witt proof attribution is preserved. The Wedderburn proof retains the
  conjugation equivalence, both inverse-closure deductions, the center field
  `F`, the dimension `n`, the conjugacy-class equation, all centralizer indices,
  the divisibility argument `n(x) \mid n`, and the alternative left-vector-space
  argument with its exact forward reference.
- The cyclotomic-polynomial passage retains the monic integer-polynomial
  identities, Euler function, inclusion-exclusion formula, Möbius function,
  both cases in its definition, all divisibility relations, and all four
  supporting forward/back references.
- The complex-plane diagram and its use retain `|q-\zeta| > q-1 \geq 1`, the
  product expression for `|\Phi_n(q)|`, and the contradiction concluding the
  proof.
- The W. Hamilton attribution and year 1843 are preserved. The quaternion
  example retains its real basis, all four multiplication axioms, the derived
  identities, the `\R`-algebra and complex-field embeddings, conjugation,
  norm, explicit inverse, formally real condition, quadratic-form/model-theory
  context, and exact `Feng17` citation.
- Ordered begin/end environments, label identifiers, reference identifiers,
  citation keys, index streams, TeX commands, and per-record structural
  signatures match the normalized authority exactly.
- All 186 inline, display, and mathematical-environment zones match after
  whitespace normalization, the eight enumerated Indonesian localizations
  inside protected mathematical text, and the single proven correction below.
  No other mathematical symbol, exponent, bound, operation, quotient, arrow,
  coordinate, length, or formula was changed.
- The eight protected-text localizations are: `项` to `suku` at line 183;
  `Euler 函数` to `fungsi Euler` at line 243; both occurrences of `素数` to
  `prima` at line 247; the elementary-number-theory justification at line 250;
  both prose fields in the first Möbius-function case at line 254, including
  the word-order localization needed to express “the number of prime factors
  of `d`” naturally in Indonesian; and the square-factor phrase at line 255.
- Eleven index display strings are localized while all source sort keys and all
  four `sym1` stream assignments remain in their original record positions.
- The candidate contains no Han characters, Chinese punctuation, placeholder
  markers, invalid UTF-8, BOM, CR/CRLF, zero-width characters, soft hyphens, or
  unauthorized controls.

## Proven source correction

### O013-LI-U037-COR-001 — authority line 219

The proposition at authority lines 215–220 introduces only the finite ring
`D`. Its proof fixes `x \in D`, defines the left-multiplication self-map
`L_x: D \to D`, and uses finiteness to conclude that this map is surjective.
The authority then writes that there exists

`x' \in R` with `xx'=1`.

No ring `R` is introduced in the proposition or proof. More decisively,
surjectivity of the displayed self-map on `D` supplies a preimage of `1` in its
domain `D`; hence the witness necessarily satisfies `x' \in D`. This is also
the membership required by the final conclusion `x \in D^\times`. The
candidate therefore uses

`x' \in D`.

This is a one-symbol ambient-ring repair forced by the local typing and proof.
No other source correction is asserted; every remaining difference is prose
translation, an explicitly enumerated protected-text localization, or an index
display localization.

## Terminology decisions

- `centralizer`, `center`, and `subring` are rendered `sentralisator`, `pusat`,
  and `subgelanggang`.
- `left/right zero divisor`, `cancellation law`, and `unit group` are rendered
  `pembagi nol kiri/kanan`, `hukum pencoretan`, and `grup perkalian semua unsur
  invertibel`.
- `characteristic`, `integral domain`, `division ring`, `field`, and `prime
  subfield` are rendered `karakteristik`, `daerah integral`, `gelanggang
  pembagian`, `medan`, and `submedan prima`, continuing Unit 036's use of
  `gelanggang` rather than `cincin`.
- `conjugation action`, `cyclotomic polynomial`, `monic`, `Möbius function`,
  and `inclusion-exclusion principle` are rendered `aksi konjugasi`,
  `polinomial siklotomik`, `monik`, `fungsi Möbius`, and `prinsip
  inklusi-eksklusi`.
- `quaternion algebra`, `formally real field`, `quadratic form`, and `model
  theory` are rendered `aljabar kuaternion`, `medan real formal`, `bentuk
  kuadratik`, and `teori model`.

These decisions are candidate-local only. This isolated task did not mutate the
canonical terminology ledger; promotion belongs to the parent admission
boundary.

## Rights, non-endorsement, and model provenance

- The frozen Chapter 5 authority records 1–6 carry the complete 2018 Wen-Wei
  Li attribution and CC BY 4.0 permission notice with its license URL. Unit 037
  is an exact continuation fragment beginning at record 174 and therefore does
  not duplicate or replace that chapter-level header. The checker binds both
  the full authority identity and those six header records; any admission of
  this fragment must retain the already translated Chapter 5 header from Unit
  036 unchanged.
- This Indonesian translation is an independent derivative. It does not imply
  endorsement by the source author, the licensor, E. Witt, W. Hamilton, the
  cited author, or any institution.
- Translation and review model provenance: OpenAI Codex gpt-5.6-sol, Ultra.

## Deterministic validation

- Checker: `scripts/check_unit_037_candidate.py`.
- The checker binds full-authority, source-slice, and candidate byte identities;
  requires strict UTF-8/LF records and exact source/candidate boundary
  sentinels; binds the inherited chapter-level rights header; compares
  record-level TeX topology, ordered commands, identifiers, indexes, citation,
  diagram primitives, comments, and all protected mathematical zones;
  enumerates all eight protected-text localizations and the single correction
  ID; and rejects residue, placeholders, invisible controls, malformed counts,
  unexpected exercise material, and uncontrolled terminology.
- Final validation command: `python scripts/check_unit_037_candidate.py`.
- Required and obtained result on two consecutive executions:
  `PASS: O013-LI-U037 isolated complete Section 5.2 special rings`.

## Handoff

The parent may independently review and admit this candidate only after Unit
036 is canonical. On admission it should preserve the correction record, splice
exactly the 117 candidate records at Chapter 5 authority lines 174–290, retain
the chapter-level rights header, build and visually inspect the reader/backend
surfaces, and then advance the Li cursor to `chapter5.tex:292`. This receipt
authorizes none of those parent-owned actions.
