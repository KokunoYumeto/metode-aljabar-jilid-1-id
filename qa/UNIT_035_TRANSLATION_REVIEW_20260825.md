# O013-LI-U035 Translation Review — 2026-08-25

Status: isolated candidate complete and checker-admissible; promoted into the
canonical source and terminology ledger on 2026-08-28, with reader/backend and
publication admission recorded separately.

## Exact authority and boundary

- Frozen authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`
- Full authority identity: 154,744 bytes; 1,898 LF-delimited records; SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Selected source records: absolute lines 1745–1898 inclusive, 154 records,
  14,398 bytes, SHA-256
  `f841860520d4ab35dc82354f288bc295c4681f9faffc8f5a645c92a3af1dd287`.
- The selected span starts at
  `\section{范畴中的群}\label{sec:group-in-cat}` immediately after the blank
  line 1744. It contains all of Section 4.11 and the complete Chapter 4
  `Exercises` environment, and ends at the authority file's final
  `\end{Exercises}`. It is therefore the complete coherent remainder of
  Chapter 4 and does not cross into Chapter 5.
- Next source-order cursor: `chapter5.tex`, line 1.

## Candidate identity and content census

- Candidate:
  `build/unit-035-candidate/chapter4-groups-in-categories-and-exercises-id.tex`
- Identity: 18,089 bytes; 154 LF-delimited records; SHA-256
  `5d9bf6e5c9c17c83821f1bba63078f4d28e3836428f4557e0727ee5b1046c2ca`.
- Scope: Section 4.11, “Grup dalam Kategori,” plus all 26 top-level Chapter 4
  exercises. The exercise environment contains 36 total exercise/subitem
  `\item` records, five source hints, and no source solutions.
- TeX census: 60 begin/end environment markers, three labels, 15 references,
  zero citations, two indexes, 247 protected mathematical zones, eight
  `tikzcd` diagrams, and 35 diagram arrows.
- Both source-disabled comments are retained in place and translated; neither
  has been promoted into reader-visible prose.

## Mathematics and structural review

- The candidate has exactly one target record for every selected authority
  record. Ordered begin/end environments, label identifiers, reference
  identifiers, citation keys, index streams, and TeX commands are identical
  to the normalized authority at every record.
- Every inline/display/environment mathematical zone matches the authority
  after whitespace normalization, eleven explicitly enumerated Indonesian
  localizations inside protected `\text{...}` fields, and the single declared
  correction below.
- All three group-object diagrams, the three homomorphism diagrams, the
  pointwise group-functor equivalence diagram, and the naturality square retain
  their nodes, arrows, labels, and directions.
- The group-object definition retains multiplication, inversion, identity,
  associativity, identity, inverse, homomorphism, commutativity, action, and
  representability data without mathematical contraction.
- The complete exercise set retains formulas, subgroup/index orientation,
  Sylow qualifiers, direct/semidirect/restricted constructions, orbit and
  double-coset quotients, transfer, the ping-pong hypothesis, and the
  profinite continuous-Hom limit formula.
- No Han characters, Chinese punctuation, placeholder markers, invalid UTF-8,
  BOM, CR/CRLF, zero-width characters, soft hyphens, or unauthorized control
  characters remain.

## Proven source correction

`O013-LI-U035-COR-001` applies only at authority line 1858, in the Neumann
lemma exercise. The source introduces subgroups `H_1, ..., H_n`, then writes
the representatives with bounds

`\substack{1 \leq i \leq m \\ 1 \leq j \leq n}`.

This cannot be well-typed as written because `H_i` is subsequently used in
the union while the subgroup index has only been defined through `n`. The
hint also removes `H_1` and recurses on `n-1`, proving that `i` indexes the
`n` subgroups; `j` indexes the finite collection of `m` cosets assigned to
each subgroup. The candidate therefore uses

`\substack{1 \leq i \leq n \\ 1 \leq j \leq m}`.

No other source correction is asserted. All other apparent stylistic or
terminological differences are translations, not claims of upstream error.

## Terminology decisions

- `group object` → `objek grup`; this preserves the established categorical
  head noun `objek` and avoids the uncontrolled calque `grup objek`.
- `group functor` → `fungtor grup`; `fungtor`, `fungtor representabel`,
  `pembenaman Yoneda`, and `fungtor penuh dan setia` match the admitted Chapter
  2 category-theory vocabulary.
- `finite product` → `produk berhingga`; `terminal object` → `objek terminal`;
  and `associativity constraint` → `kendala asosiativitas`, matching the
  existing categorical terminology.
- `identity element` remains `unsur identitas`; `inner/outer automorphism`
  become `automorfisme dalam/luar`.
- `semidirect product` and `split extension` remain `produk semilangsung` and
  `ekstensi terpecah`, matching Unit 027.
- `restricted product` → `produk terbatas`, explicitly defined by the source
  formula; `direct sum` → `jumlah langsung`, matching the admitted glossary.
- `torsor`, `profinit`, `Sylow`, `Wilson`, and `Ping-Pong` are retained as
  international mathematical names with Indonesian grammatical framing.
- `upper unitriangular matrices` is rendered descriptively as
  `matriks-matriks segitiga atas unipoten`.
- Index display text is localized as `objek grup (group object)` and
  `automorfisme luar (outer automorphism)` while preserving the source sort
  keys and index stream.

These terms are now admitted in the canonical terminology ledger; the final
promotion also records `equivariant morphism` and `transfer`.

## Deterministic validation

- Checker: `scripts/check_unit_035_candidate.py`.
- The checker binds authority, slice, and candidate byte identities; requires
  exact record and EOF boundaries; compares record-level TeX topology and
  ordered commands; verifies all protected mathematical zones; enumerates the
  eleven protected-text localizations and the single correction; audits the
  environment/identifier/diagram/exercise/hint/index counts; and rejects
  residue, placeholders, invisible controls, and uncontrolled terminology.
- Final validation command:
  `python scripts/check_unit_035_candidate.py`.
- Required result on one post-fix execution:
  `PASS: O013-LI-U035 isolated Section 4.11 + complete Chapter 4 exercises`.

## Current boundary

The 154-record candidate and eleven terminology rows are now present in the
canonical target and ledger at their pinned final identities. The next action
is one clean reader/backend build, publication in the existing lineage, and
then immediate source-order advancement to `chapter5.tex:1`.
