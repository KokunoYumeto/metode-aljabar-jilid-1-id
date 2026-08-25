# Unit 027 source and translation review — 2026-08-24

Status: **superseded candidate review retained as historical evidence.** The
12,656-byte identity below predates the type-precision repair and terminology
normalizations recorded in
`UNIT_027_INDEPENDENT_REVIEW_20260825.md`. The current isolated candidate is
12,675 bytes, SHA-256
`aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563`.
At this historical review boundary it was not yet integrated; subsequent
canonical admission is governed by `UNIT_027_ADMISSION_20260825.md` and the
independent final audit, not by this superseded receipt.

## Scope and authority

- Corpus/unit: `O013-LI-U027`.
- Work: Wen-Wei Li, *Methods in Algebra*, Volume 1.
- Frozen upstream commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
- Authority file identity: 154,744 bytes; SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`;
  1,898 LF-delimited records and no final LF.
- Selected exact contiguous boundary: authority lines **365–517**, comprising
  all of Section 4.3, “direct products, semidirect products, and group
  extensions.” Line 517 is the blank section-boundary record.
- Exact normalized-LF authority slice: 153 records, 10,209 bytes; SHA-256
  `bb7cb2d385018971fe325c417bcafdccd9e92376c02e7cb72d3af038097f8db8`.
- Content coverage: direct products of monoids and their universal property;
  external and internal semidirect products; dihedral groups; internal direct
  products; exact sequences; group extensions, their equivalences, splittings,
  and the equivalence between split extensions and semidirect products.
- Next source-order boundary: Section 4.4, “group actions and the counting
  principle,” begins at authority line **518** with
  `\section{群作用和计数原理}\label{sec:group-action}` and remains excluded.

## Candidate identity and isolation

- Candidate:
  `build/unit-027-candidate/chapter4-products-group-extensions-id.tex`.
- Candidate identity: 12,656 bytes; SHA-256
  `71e71ebe04b027bbb5f3525317e7668d5f750d629410dc0b9d762fd94a4ad9c3`.
- Encoding and boundary: strict UTF-8 without BOM, LF-only, 152 substantive
  records with exactly one final LF. Candidate records map one-for-one to
  authority lines 365–516; the boundary-only blank authority line 517 is
  intentionally omitted.
- The Indonesian translation occupies the entire substantive candidate and
  exceeds the normalized source-slice byte extent by 2,447 bytes. It contains
  no Han source prose, Chinese punctuation, placeholder, or untranslated
  editorial block.
- No canonical source, backend, control file, README, Git state, public
  artifact, or publication state was modified.

## Translation and semantic review

The translation uses natural formal id-ID prose and retains the admitted
controlled terms `grup`, `homomorfisme`, `isomorfisme`, `automorfisme`,
`diagram komutatif`, `sifat universal`, `produk langsung`, and `barisan
eksak`. Local technical forms are used consistently: `monoid`, `produk
semilangsung`, `normalisator`, `grup dihedral`, `produk langsung internal`,
`ekstensi grup`, `ekuivalensi ekstensi grup`, `pemecahan`, and `ekstensi
terpecah`.

An independent source-to-target semantic pass was performed after the
structural checker had first passed. It re-read all 152 aligned substantive
records and separately checked:

- every hypothesis, quantifier, if-and-only-if direction, image/kernel
  equality, normalizer condition, normality claim, and uniqueness statement;
- the semidirect-product multiplication and inverse, the conjugation action,
  the normal-form calculation, and both internal product criteria;
- the dihedral action, rotation/reflection interpretation, diagram directions,
  and all three polygon drawings;
- exactness, injectivity/surjectivity examples, extension equivalence,
  splitting identities, and the map `(n,h) \mapsto n s(h)`;
- the order and identity of every label, reference, index stream/sort key,
  displayed equation, and protected mathematical expression.

The second pass found no omitted sentence, reversed implication, altered
quantifier, symbol substitution, diagram-direction error, or additional source
defect. No third correction is claimed.

## Declared source corrections

No mathematical change is silent. Exactly two high-confidence corrections are
applied in this isolated candidate.

### `O013-LI-U027-COR-001` — repair the universal-property codomain

- Authority location: line 384.
- Source form: `\varphi: M' \to M`.
- Candidate form: `\varphi: M' \to \prod_{i \in I} M_i`.
- Reason: no monoid `M` is introduced in the statement. The displayed diagram
  has codomain `\prod_{i \in I} M_i`, and the proof defines
  `\varphi(x)=(\varphi_i(x))_{i\in I}`, which is an element of precisely that
  product. The source codomain is therefore undefined and ill-typed.

### `O013-LI-U027-COR-002` — delimit the geometric dihedral model

- Authority location: line 442.
- Source scope: begins with `n \in \Z_{\geq 0}` and then states without
  qualification that `D_{2n}` is the rigid-motion group of a regular
  `n`-gon.
- Candidate scope: retains the algebraic range `n \in \Z_{\geq 0}` but adds
  `Untuk $n \geq 3$` to the geometric interpretation.
- Reason: the semidirect product `(\Z/n\Z) \rtimes (\Z/2\Z)` with inversion is
  algebraically meaningful for the original range, including the conventional
  `\Z/0\Z=\Z` case. A nondegenerate regular polygon and the stated collection
  of `n` reflection axes, however, require `n \geq 3`. Qualifying only the
  geometric portion repairs the false blanket claim without discarding the
  valid algebraic cases.

No other source correction is applied or claimed.

## Preserved TeX and mathematical topology

- 28 paired environments / 56 ordered begin/end markers:
  3 `align*`, 1 `center`, 1 `compactenum`, 3 `compactitem`, 3 `definition`,
  1 `enumerate`, 1 `example`, 1 `gather`, 1 `inparaenum`, 3 `lemma`, 3
  `proof`, 4 `tikzcd`, and 3 `tikzpicture`;
- 8 labels with exact identifiers and source order;
- 5 ordered `ref`/`eqref` targets;
- 0 citations;
- 6 index commands with preserved main/symbol streams and source sort keys;
- 171 protected inline, display, `align*`, `gather`, and `tikzcd`
  mathematical zones after the two exact correction normalizations;
- 30 TikZ `\arrow` commands, 6 `\foreach` commands, 6 `\draw` commands, and
  3 `\node` commands;
- 308 unescaped dollar delimiters;
- 155 opening and 155 closing braces;
- 0 Han characters, 0 Chinese punctuation residues, and 0 translation
  placeholders.

## Deterministic admission

- Checker: `scripts/check_unit_027_candidate.py`.
- Checker identity: 13,427 bytes; SHA-256
  `1477ba75527f3dfbfc4d642150093c73c8f68b75ba19284386ebc0dfa540c531`.
- The checker is read-only and fails closed on the complete authority identity,
  exact 365–517 slice identity, the line-518 next-boundary sentinel, candidate
  byte identity, strict UTF-8/LF shape, exact 152-record substantive mapping,
  opening and closing boundaries, environment sequence, labels, references,
  citations, index streams and sort keys, ordered per-record TeX commands,
  protected mathematics, exact TikZ drawing instructions, controlled
  terminology, semantic anchors, both correction sites, brace balance, source
  residue, and placeholders.
- Command: `python scripts/check_unit_027_candidate.py`.
- Result on 2026-08-24: **PASS**.
- Reported result: source slice 153 records / 10,209 bytes / SHA-256
  `bb7cb2d…8db8`; candidate 152 records / 12,656 bytes / SHA-256
  `71e71ebe…d9c3`; 56 environment markers, 8 labels, 5 references, 0
  citations, 6 indexes, 171 protected mathematical zones, zero Han residue,
  and exactly 2 declared source corrections.

This admission proves only the isolated Unit 027 translation candidate.
Canonical integration and all downstream build, reader, version-control, and
publication work remain outside this unit's write boundary.
