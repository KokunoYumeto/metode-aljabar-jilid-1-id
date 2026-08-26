# Unit 030 source and translation review — 2026-08-25

Status: **isolated Indonesian translation candidate admitted by its bounded
checker; not integrated into the canonical Chapter 4 source, live glossary,
backend, controls, reader, README, Git history, or any public release.**

## Scope and authority

- Corpus/unit: `O013-LI-U030`.
- Work: Wen-Wei Li, *Methods in Algebra*, Volume 1.
- Frozen upstream commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
- Authority file identity: 154,744 bytes; SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`;
  1,898 LF-delimited records and no final LF.
- Selected exact contiguous boundary: authority lines **796–935**, comprising
  all of Section 4.6, the composition series of groups. Line 935 is the blank
  section-boundary record.
- Exact normalized-LF authority slice: 140 records, 7,981 bytes; SHA-256
  `7803452c4285c57e419a2cb2a288b3733975555fafd6b7a88c5732da369220c1`.
- Content coverage: normal, central, and composition series; subquotients and
  refinements; the Zassenhaus lemma and its six diagrammatic components; the
  Schreier refinement theorem; the Jordan--Hölder theorem and composition
  factors; behavior of composition factors under a short exact sequence; and
  the prime-order composition factors of a finite abelian group.
- No exercise, hint, solution, assessment, or citation occurs in this exact
  source range.
- Next source-order boundary: Section 4.7, solvable and nilpotent groups,
  begins at authority line **936** with
  `\section{可解群与幂零群}\label{sec:solvable-groups}` and remains excluded.

## Candidate identity and isolation

- Candidate:
  `build/unit-030-candidate/chapter4-group-composition-series-id.tex`.
- Candidate identity: 10,044 bytes; SHA-256
  `7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b`.
- Encoding and boundary: strict UTF-8 without BOM, LF-only, 139 substantive
  records with exactly one final LF. Candidate records map one-for-one to
  authority lines 796–934; the boundary-only blank authority line 935 is
  intentionally omitted.
- The Indonesian translation occupies the entire substantive candidate and
  exceeds the normalized source-slice byte extent by 2,048 bytes. It contains
  no Han source prose, Chinese punctuation, invisible Unicode control,
  placeholder, untranslated editorial block, or disabled source content.
- No canonical source, live glossary, backend, control, artifact, README, Git,
  or publication state was modified.

## Translation and semantic review

The candidate uses natural formal id-ID prose and preserves the admitted
forms `grup`, `barisan eksak`, and `grup abelian`, together with established
Chapter 4 forms such as `subgrup`, `subgrup normal`, `grup sederhana`,
`isomorfisme`, `orde`, and `grup siklik`. Its internally consistent local
terms are `deret normal`, `deret sentral`, `deret komposisi`, `subkuosien`,
`penghalusan`, `penghalusan sejati`, `faktor komposisi`, and
`multiplikitas`. Admission of new local forms into the live cross-unit
glossary is deliberately reserved for the later canonical terminology gate.

A complete source-to-target semantic pass was performed after the structural
checker first passed, followed by a separate prose-quality pass. They checked:

- every condition in the definitions of normal, central, and composition
  series, including which subgroup is normal in which ambient group and the
  strictness and simplicity conditions for a composition series;
- the distinction between a trivial and proper refinement and the treatment
  of subquotients as an unordered collection with multiplicity;
- both normality assertions and the natural quotient isomorphism in the
  Zassenhaus lemma;
- all six TikZ-cd diagrams, their 23 arrows, the subgroup/normal-subgroup
  legend, every intersection and subgroup product, and the two quotient
  isomorphisms obtained from the cited homomorphism proposition;
- the two families in the Schreier construction, their endpoint identities,
  every normal-subgroup relation, the full refined chain, the substitution
  into the Zassenhaus lemma, and the one-to-one matching of subquotients;
- the exact notion of equivalence used in the Jordan--Hölder theorem and the
  independence of the composition-factor multiset from the selected series;
- the counterexample showing that the composition-factor multiset does not
  determine a group up to isomorphism;
- the splicing of composition series along the exact sequence
  (1\to N\to G\to Q\to1), including multiplicities in the union; and
- the recursive Cauchy-theorem proof for finite abelian groups, including the
  prime-order cyclic subgroup and the induction parameter |G|.

No sentence, hypothesis, implication, quantifier, formula, reference, index,
diagram, or active source environment was omitted.

## Declared source correction

Exactly one high-confidence source correction is applied openly as
`O013-LI-U030-COR-001`.

### `O013-LI-U030-COR-001` — restore a missing relation in the Schreier refinement chain

- Authority location: line 895.
- Source fragment:
  `\supset G_{i, 1} \supset \cdots G_{i, s} \supset G_{i, s+1}`.
- Candidate fragment:
  `\supset G_{i, 1} \supset \cdots \supset G_{i, s} \supset G_{i, s+1}`.
- Reason: the displayed object is explicitly the refinement chain built from
  the already-proved relations
  (G_{i,j+1}\mathrel\lhd G_{i,j}). Every adjacent pair therefore requires a
  containment relation. The authority omits only the `\supset` between the
  ellipsis and (G_{i,s}); the neighboring terms and the general indexed
  construction determine the repair uniquely.

No other mathematical source correction is required or claimed.

## Protected-text localizations

Two `\text{...}` fragments inside protected TikZ-cd displays are localized
without changing diagram topology:

- authority line 836: `\text{子群}` becomes `\text{subgrup}`;
- authority line 839: `\text{正规子群}` becomes
  `\text{subgrup normal}`.

These are language localizations only; neither changes a mathematical object,
relation, or arrow.

## Preserved TeX and mathematical topology

- 26 paired environments / 52 ordered begin/end markers: 3 `align*`, 5
  `definition`, 1 `equation*`, 1 `gather`, 2 `gather*`, 1 `lemma`, 4 `proof`,
  1 `proposition`, 2 `theorem`, and 6 `tikzcd` environments;
- 10 labels with exact identifiers and source order;
- 9 ordered `ref`/`eqref` targets;
- 0 citations;
- 6 main index commands with their original sort keys and stream topology;
- 88 protected inline, display, and mathematical-environment zones after the
  two exact protected-text localizations and the declared relation repair;
- 6 TikZ-cd environments and 23 exact `\arrow` commands;
- 130 unescaped dollar delimiters;
- 168 opening and 168 closing braces;
- 0 comments, 0 exercises, 0 hints, 0 solutions, 0 Han characters, 0 Chinese
  punctuation residues, 0 invisible Unicode controls, and 0 translation
  placeholders.

## Deterministic admission

- Checker: `scripts/check_unit_030_candidate.py`.
- Checker identity: 14,417 bytes; SHA-256
  `e8cf6de679203e4cf1173310c88767248463f9961b0dd556286cf863075f0b2e`.
- The checker is read-only and fails closed on the complete authority identity,
  exact 796–935 slice identity, line-936 next-boundary sentinel, candidate byte
  identity, strict UTF-8/LF shape, exact 139-record substantive mapping,
  opening and closing boundaries, environment sequence, labels, references,
  indexes and sort keys, ordered per-record TeX commands, protected
  mathematics, six diagrams and 23 arrows, controlled terminology, semantic
  anchors, both protected-text localizations, the declared line-895 repair,
  brace balance, source residue, invisible controls, placeholders, and the
  absence of out-of-scope exercise, hint, and solution topology.
- Command: `python scripts/check_unit_030_candidate.py`.
- Result on 2026-08-25: **PASS**.
- Reported result: source slice 140 records / 7,981 bytes / SHA-256
  `7803452c…220c1`; candidate 139 records / 10,044 bytes / SHA-256
  `7e39460c…74b4b`; 52 environment markers, 10 labels, 9 references, 6
  indexes, 88 protected mathematical zones, 6 diagrams / 23 arrows, zero
  citations, exercises, and hints, zero Han residue, one declared source
  correction, and two protected-text localizations.

This admission proves only the isolated Unit 030 translation candidate.
Canonical integration and all downstream glossary, backend, build, reader,
version-control, and publication work remain outside this unit's write
boundary.
