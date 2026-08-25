# Unit 029 source and translation review — 2026-08-24

Status: **source/translation review complete; after a bounded prose refinement
on 2026-08-25, the candidate was integrated into canonical Chapter 4 and the
five approved terms were appended to the live glossary.** Reader, backend,
controls, README, Git, and publication remain outside this review; canonical
evidence is in `qa/UNIT_029_PREPROMOTION_AUDIT_20260825.md`.

## Scope and authority

- Corpus/unit: `O013-LI-U029`.
- Work: Wen-Wei Li, *Methods in Algebra*, Volume 1.
- Frozen upstream commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
- Authority file identity: 154,744 bytes; SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`;
  1,898 LF-delimited records and no final LF.
- Selected exact contiguous boundary: authority lines **666–795**, comprising
  all of Section 4.5, the Sylow theorems. Line 795 is the blank
  section-boundary record.
- Exact normalized-LF authority slice: 130 records, 8,043 bytes; SHA-256
  `760366ac81aff9bd6170c96996ae16c29a02a93034a77f7d4c7f01485bbf3163`.
- Content coverage: finite (p)-groups and the orbit-counting congruence; the
  nontrivial-center and proper-normalizer consequences; Cauchy's theorem and
  its cyclic-shift proof; the notation (p^a\mathrel\|n); Sylow subgroups;
  Wielandt's binomial-congruence lemma; the first, second, and third Sylow
  theorems; and the direct-product characterization of finite groups whose
  Sylow subgroups are all normal.
- No exercise, hint, solution, assessment, or diagram environment occurs in
  this exact source range.
- Next source-order boundary: Section 4.6, the composition series of groups,
  begins at authority line **796** with
  `\section{群的合成列}\label{sec:composition-series-grp}` and remains excluded.

## Candidate identity and isolation

- Candidate:
  `build/unit-029-candidate/chapter4-sylow-theorems-id.tex`.
- Candidate identity after the bounded prose refinement and the 2026-08-26
  rendered-punctuation repair: 10,028 bytes; SHA-256
  `234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d`.
- Encoding and boundary: strict UTF-8 without BOM, LF-only, 129 substantive
  records with exactly one final LF. Candidate records map one-for-one to
  authority lines 666–794; the boundary-only blank authority line 795 is
  intentionally omitted.
- The Indonesian translation occupies the entire substantive candidate and
  exceeds the normalized source-slice byte extent by 1,985 bytes. It contains
  no Han source prose, Chinese punctuation, invisible Unicode control,
  placeholder, untranslated editorial block, or disabled source content.
- At the original isolation boundary no canonical state was modified. The
  later two-file promotion changed only canonical Chapter 4 and the live
  glossary, as bound by the 2026-08-25 canonical-promotion audit.

## Translation and semantic review

The candidate uses natural formal id-ID prose and carries forward the admitted
forms `grup` and `produk langsung` as well as the Chapter 4 usage `orde`,
`subgrup`, `subgrup normal`, `grup hasil bagi`, `stabilisator`,
`normalisator`, `aksi konjugasi`, and `saling konjugat`. Its local new terms
are internally consistent: `$p$-grup`, `$p$-subgrup`, `subgrup Sylow $p$`,
`koefisien binomial`, and `saling koprima`. The later canonical terminology
gate admitted exactly those five forms without collision.

A complete source-to-target semantic pass was performed after the structural
checker first passed, followed by a separate prose-quality pass. They checked:

- the definition of a finite (p)-group and closure of its subgroups and
  quotient groups under the same property;
- both directions of the orbit-counting equivalences involving fixed points
  and stabilizers, and the deduction modulo (p) from orbit decomposition;
- the conjugation-action proof that a nontrivial finite (p)-group has
  nontrivial center, followed by the recursive quotient-by-the-center proof of
  the proper-normalizer result and its index-(p) consequence;
- the cyclic shift of (X_p), why it preserves the defining product, the
  description of the fixed points, the projection (X_p\to G^{p-1}), and the
  final congruence that proves Cauchy's theorem;
- the exact divisibility convention (p^a\mathrel\|n), the definition of a
  Sylow subgroup, every nonnegativity and divisibility hypothesis in
  Wielandt's lemma, and its coefficientwise polynomial proof;
- the subset action in the first Sylow theorem, the stabilizer index,
  divisibility of the stabilizer order, and the comparison with |E|;
- the normalizer lemma via (HP/P\simeq H/(H\cap P)), including the reason
  (HP) is again a (p)-group;
- both assertions of the second Sylow theorem and their proof using fixed
  points of a (p)-subgroup on the conjugacy orbit;
- the singleton fixed-point set in the third Sylow theorem and the resulting
  congruence; and
- both directions of the final characterization by the product of normal
  Sylow subgroups, including pairwise coprime orders, trivial intersections,
  the cited internal-direct-product criterion, and the concluding order
  comparison.

No sentence, hypothesis, implication, quantifier, formula, citation, or active
source environment was omitted. In particular, the somewhat compressed
authority wording at line 731 is rendered explicitly as requiring (m) to be
nonnegative, exactly as the Chinese grammatical list does; this is a semantic
clarification in Indonesian, not a change to the lemma.

## Source adjudication and protected-text localization

No mathematical source correction is required or claimed for this unit. The
source's formulas, hypotheses, references, and proof dependencies are
internally coherent across the selected boundary. The direct-product display
at line 788 and its isomorphism wording in the proof are preserved rather than
silently rewritten.

Exactly one `\text{...}` fragment inside protected display mathematics is
localized without changing the surrounding set expression:

- authority line 746: `\text{ 子集 }` becomes
  `\text{ subhimpunan }`.

This is language localization only. It does not alter a mathematical symbol,
operator, quantifier, or set boundary.

## Preserved TeX and mathematical topology

- 25 paired environments / 50 ordered begin/end markers: 1 `align*`, 1
  `compactenum`, 1 `convention`, 3 `corollary`, 2 `definition`, 2 `lemma`, 10
  `proof`, 2 `proposition`, and 3 `theorem` environments;
- 6 labels with exact identifiers and source order;
- 16 ordered `ref` targets;
- 1 citation with exact bibliography key `Lang02` and locator
  `Theorem 6.2`;
- 2 main index commands with no altered stream or sort-key topology;
- 211 protected inline, display, and `align*` mathematical zones after the
  exact protected-text localization normalization;
- 394 unescaped dollar delimiters;
- 153 opening and 153 closing braces;
- 0 comments, 0 diagrams, 0 exercises, 0 hints, 0 solutions, 0 Han
  characters, 0 Chinese punctuation residues, 0 invisible Unicode controls,
  and 0 translation placeholders.

The final rendered review removed one period placed after a display-closing
`\]` at the Sylow-II orbit definition. In the first build that punctuation
appeared alone at the left margin on the following line. The authority has no
period there; removing it restores both the source punctuation and readable
page flow without altering the displayed formula.

## Deterministic admission

- Checker: `scripts/check_unit_029_candidate.py`.
- Final checker identity is rebound after the rendered-punctuation repair and
  recorded in the canonical-promotion audit.
- The checker is read-only and fails closed on the complete authority identity,
  exact 666–795 slice identity, line-796 next-boundary sentinel, candidate byte
  identity, strict UTF-8/LF shape, exact 129-record substantive mapping,
  opening and closing boundaries, environment sequence, labels, references,
  citation, index streams and sort keys, ordered per-record TeX commands,
  protected mathematics, controlled terminology, semantic anchors, the sole
  protected-text localization, brace balance, source residue, invisible
  controls, placeholders, and the absence of out-of-scope exercise, hint,
  solution, and diagram topology.
- Command: `python scripts/check_unit_029_candidate.py`.
- Result on 2026-08-24: **PASS**.
- Reported final result: source slice 130 records / 8,043 bytes / SHA-256
  `760366ac…f3163`; candidate 129 records / 10,028 bytes / SHA-256
  `234c3a4d…c561d`; 50 environment markers, 6 labels, 16 references, 1
  citation, 2 indexes, 211 protected mathematical zones, zero diagrams,
  exercises, and hints, zero Han residue, zero declared source corrections,
  and one protected-text localization.

This review proves the translation candidate's source and semantic fidelity.
The separate 2026-08-25 terminology and canonical-promotion audits prove its
glossary and canonical integration; backend, build, reader, version-control,
and publication work remain downstream.
