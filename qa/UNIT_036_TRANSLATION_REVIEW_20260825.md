# O013-LI-U036 Translation Review — 2026-08-25

Status: isolated candidate complete and checker-admissible; not promoted into
canonical source, glossary, backend, README, durable controls, Git, or any
publication lane.

## Exact authority and frozen boundary

- Frozen authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex`.
- Full authority identity: 122,998 bytes; 1,382 LF-delimited records; SHA-256
  `e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143`.
- Selected source records: absolute lines 1–172 inclusive, 172 records, 13,758
  bytes, SHA-256
  `84b70368ebdfa557fa76eb229166aa6851b3295f620b240cc080f419ef40c14f`.
- The span begins at the file's copyright header, contains the complete Chapter
  5 opening (`\chapter{环论初步}\label{sec:ring}`), the two-paragraph
  `wenxintishi` notice, and the complete first section
  (`\section{基本概念}\label{sec:ring-basics}`). It ends with the final prose
  record of that section at authority line 172.
- Authority line 173 is the blank separator. The next content record is line
  174, `\section{几类特殊的环}`. Excluding the separator makes lines 1–172 the
  smallest pedagogically complete chapter-opening-plus-first-section boundary.
- Next source-order cursor: `chapter5.tex`, line 174.

## Candidate identity and content census

- Candidate: `build/unit-036-candidate/chapter5-ring-basics-id.tex`.
- Identity: 18,181 bytes; 172 LF-delimited records; SHA-256
  `d93ad6adeccae67ace0035286e9a41ab1350dca875acdb349d529c7f180b991a`.
- Record correspondence is one-to-one: every selected authority record has
  exactly one candidate record, with no inserted or deleted blank record and
  exactly one LF terminator after record 172.
- TeX census: 54 begin/end environment markers (27 matched pairs), 11 labels,
  12 `ref`/`eqref` references, zero citations, 11 indexes, 230 protected
  mathematical zones, 420 unescaped dollar delimiters, and balanced raw braces
  (158 opening, 158 closing).
- Environment-begin census: `wenxintishi` 1; `definition` 5; `enumerate` 1;
  `compactitem` 1; `itemize` 2; `compactenum` 1; `example` 3; `pmatrix` 1;
  `smallmatrix` 1; `align*` 1; `array` 1; `gather*` 1; `proposition` 4;
  `equation` 1; `aligned` 1; and `tikzcd` 2.
- Diagram census: two `tikzcd` diagrams and six arrows. Their nodes, map labels,
  arrow directions, row-separation options, and the unique-existence marker are
  unchanged.
- Item census: 16 `\item` records across the ring axioms, distributive laws,
  homomorphism axioms, ideal variants, and ideal operations. This span contains
  no `Exercises`, `exercise`, `hint`, or `solution` environment in either
  authority or candidate, so exercise/hint/solution correspondence is exactly
  zero-to-zero.
- Comment-state census: seven source-disabled records, at records 1–6 and 8.
  No comment was activated or demoted into reader-visible prose.

## Source and translation review

- The chapter overview retains the commutative/noncommutative distinction, the
  algebraic-integer and matrix-ring examples, Hilbert's 1897 terminology,
  the nonzero-unital convention, smallness convention, all three forward
  references, Möbius inversion, and the Young-diagram motivation.
- The ring definition retains the additive abelian group, both distributive
  laws, multiplication associativity, the common multiplicative identity,
  nonunital-ring convention, subring convention, and ring-extension direction.
- The deductions `a0=0=0a`, `(-1)a=-a=a(-1)`, the zero ring, and the unit group
  `R^\times` are unchanged.
- The opposite-ring definition retains the reversed multiplication and exact
  commutativity criterion. The homomorphism definition retains addition,
  multiplication, and identity preservation, together with the nonunital
  variant.
- The matrix-ring example retains all dimensions, entry bounds, matrix layout,
  and diagonal identity. The endomorphism-ring example retains composition as
  multiplication, pointwise addition, and `\identity_A` as the unit.
- The quotient construction retains the congruence criterion, the computation
  `rs-r's'=r(s-s')+(r-r')s'`, left/right stability, all left/right/two-sided
  ideal distinctions, properness, arbitrary sums and nonempty intersections,
  generated ideals, ideal products, distributivity over sums, associativity,
  and ideal powers.
- The quotient-ring definition, the integer-ideal example, the quotient
  universal property, ideal-preimage correspondence, surjective correspondence,
  and subring-plus-ideal isomorphism retain their hypotheses and map directions.
- Ordered begin/end environments, label identifiers, reference identifiers,
  citation keys, index streams, TeX commands, and per-record structural
  signatures match the normalized authority exactly.
- All 230 inline, display, and mathematical-environment zones match after
  whitespace normalization, four enumerated Indonesian localizations inside
  protected `\text{...}` fields, and the two proven corrections below. No
  other mathematical symbol, bound, operation, quotient, arrow, or formula was
  changed.
- The four protected-text localizations are the two set descriptions at line
  148 (`ideal dua sisi di R_2` and `ideal dua sisi di R_1`) and the two
  `ideal dua sisi` descriptions at line 158. These are prose localizations
  inside mathematical mode, not mathematical corrections.
- All 11 index display strings are localized while the source sort keys and
  `sym1` stream assignments remain in their original positions.
- The only Han text retained is the exact source-author attribution `李文威
  (Wen-Wei Li)` in the copyright comment. No other Han characters, Chinese
  punctuation, placeholder markers, invalid UTF-8, BOM, CR/CRLF, zero-width
  characters, soft hyphens, or unauthorized controls occur.

## Proven source corrections

### O013-LI-U036-COR-001 — authority line 143

The source states the first isomorphism theorem for a homomorphism
`\varphi: R \to R'`, but writes the induced map as

`\bar{\varphi}: (R/I) \to \Image(\varphi)`.

No ideal `I` is introduced in that proposition; the `I` in the preceding,
separately closed proposition is not in scope. More decisively, the induced map
is defined by `[r] \mapsto \varphi(r)`. Two representatives have the same image
exactly when their difference lies in `\Ker(\varphi)`, so this map is
well-defined on `R/\Ker(\varphi)`, injective there, and surjective onto
`\Image(\varphi)`. The candidate therefore uses

`\bar{\varphi}: R/\Ker(\varphi) \to \Image(\varphi)`.

This is the unique quotient that makes the asserted induced isomorphism
well-typed and true.

### O013-LI-U036-COR-002 — authority line 168

The source hypotheses give a subring `S \subset R` and a two-sided ideal
`I \subset R`, then write the domain of the induced map as

`S/I \cap S`.

The hypotheses do not imply `I \subset S`, so `S/I` is generally undefined.
Even if it happened to be defined, ordinary precedence would read the source as
an intersection involving `S/I`, not as the needed quotient. The immediately
preceding source sentence correctly identifies the kernel of
`S \hookrightarrow R \twoheadrightarrow R/I` as `I \cap S`; its image is
`(S+I)/I`. Applying the first isomorphism theorem therefore gives precisely

`\theta: S/(I \cap S) \to (S+I)/I`.

The candidate inserts these necessary quotient parentheses. No other source
correction is asserted; all remaining differences are translations or the four
declared protected-text localizations.

## Terminology decisions

- `ring`, `commutative ring`, `opposite ring`, and `nonunital ring` are rendered
  as `gelanggang`, `gelanggang komutatif`, `gelanggang lawan`, and `gelanggang
  tanpa unsur satuan`, consistent with the admitted Chapters 2–4 vocabulary.
- `field` remains `medan`; `division ring` is `gelanggang pembagian`; `subring`
  is `subgelanggang`; and `ring extension` is `perluasan gelanggang`.
- `unit`, `zero ring`, `matrix ring`, and `endomorphism ring` are `unsur satuan`,
  `gelanggang nol`, `gelanggang matriks`, and `gelanggang endomorfisme`.
- `kernel`, `image`, `inverse image`, and `quotient homomorphism` are `kernel`,
  `citra`, `prabayangan`, and `homomorfisme hasil bagi`.
- `left ideal`, `right ideal`, `two-sided ideal`, `proper ideal`, and `quotient
  ring` are `ideal kiri`, `ideal kanan`, `ideal dua sisi`, `ideal sejati`, and
  `gelanggang hasil bagi`.
- `principal ideal domain` is provisionally rendered `daerah ideal utama` at
  its forward mention, matching the domain condition encoded by the referenced
  definition. This candidate-local choice does not mutate the terminology
  ledger.

## Rights, non-endorsement, and model provenance

- Candidate records 1–6 preserve the complete CC BY 4.0 permission notice,
  license URL, 2018 copyright year, and Wen-Wei Li attribution.
- This Indonesian translation is an independent derivative. It does not imply
  endorsement by the source author, the licensor, or any cited person or
  institution.
- Translation and review model provenance: OpenAI Codex gpt-5.6-sol, Ultra.

## Deterministic validation

- Checker: `scripts/check_unit_036_candidate.py`.
- The checker binds full-authority, source-slice, and candidate byte identities;
  enforces strict UTF-8/LF records and exact boundary sentinels; compares
  record-level TeX topology, ordered commands, identifiers, indexes, diagrams,
  comments, and all protected mathematical zones; enumerates the four
  protected-text localizations and both correction IDs; preserves the CC BY
  4.0 header and author attribution; and rejects residue, placeholders,
  invisible controls, malformed counts, and uncontrolled terminology.
- Final validation command: `python scripts/check_unit_036_candidate.py`.
- Required result on two consecutive executions:
  `PASS: O013-LI-U036 isolated Chapter 5 opening + complete Section 5.1`.

## Handoff

The parent may independently review and admit this candidate only at its own
admission boundary. On admission it should preserve both correction records,
splice exactly the 172 candidate records at Chapter 5 authority lines 1–172,
build and visually inspect the reader/backend surfaces, and then advance the Li
cursor to `chapter5.tex:174`. This receipt authorizes none of those parent-owned
actions.
