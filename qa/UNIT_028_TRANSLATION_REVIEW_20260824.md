# Unit 028 source and translation review — 2026-08-24

Status: **isolated Indonesian translation candidate admitted by its bounded
checker; not integrated into the canonical Chapter 4 source, live glossary,
backend, controls, reader, README, Git history, or any public release.**

## Scope and authority

- Corpus/unit: `O013-LI-U028`.
- Work: Wen-Wei Li, *Methods in Algebra*, Volume 1.
- Frozen upstream commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
- Authority file identity: 154,744 bytes; SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`;
  1,898 LF-delimited records and no final LF.
- Selected exact contiguous boundary: authority lines **518–665**, comprising
  all of Section 4.4, “group actions and the counting principle.” Line 665 is
  the blank section-boundary record.
- Exact normalized-LF authority slice: 148 records, 10,550 bytes; SHA-256
  `af7b91d4650e637505555cc188056656cd02f400bc6e1dd1ded0f619040a80db`.
- Content coverage: monoid and group actions; equivariant maps and
  isomorphisms; left and right actions; permutation, linear, function-space,
  and heat-semigroup examples; fixed points, orbits, and stabilizers; orbit
  decomposition and the orbit--stabilizer cardinal formula; faithful, free,
  transitive, and multiply transitive actions; homogeneous spaces, torsors,
  translation and conjugation actions, double cosets, bitorsors, and the
  bijective torsor criterion.
- No exercise, hint, solution, or assessment environment occurs in this exact
  source range.
- Next source-order boundary: Section 4.5, the Sylow theorems, begins at
  authority line **666** with
  `\section{Sylow 定理}\label{sec:Sylow}` and remains excluded.

## Candidate identity and isolation

- Candidate:
  `build/unit-028-candidate/chapter4-group-actions-counting-id.tex`.
- Candidate identity: 13,017 bytes; SHA-256
  `027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd`.
- Encoding and boundary: strict UTF-8 without BOM, LF-only, 147 substantive
  records with exactly one final LF. Candidate records map one-for-one to
  authority lines 518–664; the boundary-only blank authority line 665 is
  intentionally omitted.
- The Indonesian translation occupies the entire substantive candidate and
  exceeds the normalized source-slice byte extent by 2,467 bytes. It contains
  no Han source prose, Chinese punctuation, invisible Unicode control,
  placeholder, or untranslated editorial block.
- No canonical source, glossary, backend, control, artifact, README, Git, or
  publication state was modified.

## Translation and semantic review

The translation uses natural formal id-ID prose and retains the already
admitted controlled forms `grup`, `kategori`, `homomorfisme`, `isomorfisme`,
and `kardinal`. The local technical vocabulary is internally consistent:
`aksi`, `pemetaan aksi`, `aksi trivial`, `ekuivarian`, `himpunan-$M$`,
`titik tetap`, `orbit`, `stabilisator`, `setia`, `bebas`, `semireguler`,
`transitif`, `ruang homogen`, `torsor`, `aksi translasi`, `aksi konjugasi`,
`kelas konjugasi`, `sentralisator`, `pusat`, and `bitorsor`. Admission of new
rows into the live cross-unit glossary is deliberately left to the later
canonical terminology gate.

A complete source-to-target semantic pass was performed after the structural
checker first passed, followed by a second prose-quality pass. They separately
checked:

- both monoid-action axioms, equivariance, inverse-isomorphism conditions, and
  the left/right/opposite-monoid correspondence;
- the permutation, matrix, pullback-on-functions, and heat-kernel examples,
  including both cited locations, convolution, initial-value problem, and the
  nonextendability claim;
- definitions of fixed points, orbits, stabilizers, faithful/free/transitive
  actions, homogeneous spaces, principal homogeneous spaces, and torsors;
- every quantifier and direction in orbit decomposition, the coset-to-orbit
  isomorphism, cardinal formula, conjugacy of stabilizers, and the proof;
- left and right translation, the `H \times K^\text{op}` double-coset action,
  conjugation orbits, normalizers, centralizers, and the center;
- the two commuting automorphism actions on `\Isom(G_1,G_2)`, their combined
  bitorsor action, and both directions of the final bijective torsor criterion;
- the order and identity of every environment, label, reference, citation,
  index stream/sort key, mathematical zone, and diagram arrow.

No sentence, hypothesis, implication, quantifier, formula, citation, or active
source environment was omitted. The source's line-542 statement about monoid
actions and `\Aut(X)` is already disabled by an upstream TeX comment. The
candidate translates and preserves that record as a disabled comment; it does
not reactivate it or present it as reader content. No correction is claimed
for inactive commentary.

## Declared source correction

Exactly one high-confidence logical correction spans two authority records and
is applied openly as `O013-LI-U028-COR-001`.

### `O013-LI-U028-COR-001` — restore the declared source and target of the inverse maps

- Authority locations: lines 533 and 535.
- Source form: the equivariant-map diagram suddenly uses undefined objects
  `M_1` and `M_2`, followed by identities `\identity_{M_2}` and
  `\identity_{M_1}`.
- Candidate form: the diagram uses `X` and `Y`, followed by
  `fg=\identity_Y` and `gf=\identity_X`.
- Reason: the immediately preceding active sentence declares
  `f:X\to Y`, and no `M_1` or `M_2` is introduced. The inverse maps must
  therefore run between the already-defined $M$-sets `X` and `Y`; the
  candidate repairs the two labels and their identity subscripts together.

Three `\text{...}` fragments inside protected math are translated rather than
left in Chinese: `pemetaan` at line 557, `unsur-unsur berbeda` at line 610,
and `isomorfisme` at line 646. These are exact language localizations and do
not alter mathematical symbols or structure. No other source correction is
applied or claimed.

## Preserved TeX and mathematical topology

- 24 paired environments / 48 ordered begin/end markers: 2 `align*`, 1
  `cases`, 2 `compactenum`, 2 `compactitem`, 3 `definition`, 6 `example`, 1
  `gather*`, 1 `inparaenum`, 2 `lemma`, 2 `proof`, 1 `remark`, and 1
  `tikzcd`;
- 5 labels with exact identifiers and source order;
- 8 ordered `ref`/`eqref` targets;
- 2 citations with exact bibliography keys `Zh2`, `Zh1`;
- 9 index commands with preserved main/symbol streams and source sort keys;
- 213 protected inline, display, `align*`, `gather*`, and `tikzcd`
  mathematical zones after the exact correction/localization normalization;
- 2 exact TikZ-cd `\arrow` commands;
- 400 unescaped dollar delimiters;
- 122 opening and 122 closing braces;
- 1 translated but still-disabled source comment;
- 0 Han characters, 0 Chinese punctuation residues, 0 invisible Unicode
  controls, and 0 translation placeholders.

## Deterministic admission

- Checker: `scripts/check_unit_028_candidate.py`.
- Checker identity: 14,671 bytes; SHA-256
  `be2674c75fb17bf8dd8de43d4dd0230fd049f2b5640c72aa372aecc1742d1527`.
- The checker is read-only and fails closed on the complete authority identity,
  exact 518–665 slice identity, line-666 next-boundary sentinel, candidate byte
  identity, strict UTF-8/LF shape, exact 147-record substantive mapping,
  opening and closing boundaries, environment sequence, labels, references,
  citations, index streams and sort keys, ordered per-record TeX commands,
  protected mathematics, two diagram arrows, controlled terminology,
  semantic anchors, the one two-record correction, three protected-text
  localizations, brace balance, source residue, invisible controls, and
  placeholders.
- Command: `python scripts/check_unit_028_candidate.py`.
- Result on 2026-08-24: **PASS**.
- Reported result: source slice 148 records / 10,550 bytes / SHA-256
  `af7b91d4…a80db`; candidate 147 records / 13,017 bytes / SHA-256
  `027201c4…dcdd`; 48 environment markers, 5 labels, 8 references, 2
  citations, 9 indexes, 213 protected mathematical zones, 2 diagram arrows,
  zero exercises/hints, zero Han residue, and exactly one declared logical
  correction.

This admission proves only the isolated Unit 028 translation candidate.
Canonical integration and all downstream glossary, backend, build, reader,
version-control, and publication work remain outside this unit's write
boundary.
