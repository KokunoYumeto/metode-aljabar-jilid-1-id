# Unit 034 source and translation review — 2026-08-25

Status: **PASS; the final 19,019-byte Indonesian candidate preserves the
complete semantics of Section 4.10.** The original review date and source
analysis are retained; the byte, topology, terminology, canonical-splice, and
digital-reflow bindings were refreshed against the live 2026-08-27 files.
This review is pre-admission evidence and does not claim backend, control,
Git, publication, or public-byte-readback completion.

## Scope and authority

- Corpus/unit: `O013-LI-U034`.
- Work: Wen-Wei Li, *Methods in Algebra*, Volume 1.
- Frozen upstream commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
- Authority identity: 154,744 bytes; SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`;
  1,898 LF-delimited records and no final LF.
- Selected exact contiguous boundary: authority lines **1609–1744**, all of
  Section 4.10, group limits and completions. Line 1744 is the blank
  section-boundary record.
- Exact normalized-LF authority slice: 136 records, 15,005 bytes; SHA-256
  `9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab`.
- Content coverage: the explicit construction of projective limits of groups;
  upward-directed index posets; topological groups and neighborhood bases;
  Hausdorff separation and closed-neighborhood bases; open-and-closed
  subgroups and finite index in compact groups; product topology and
  compactness of projective limits; profinite groups and their intrinsic
  characterization; total disconnectedness; algebraic and topological group
  completions; Cauchy sequences and the three completion axioms; realization
  of completion as a projective limit; the additive group of the p-adic
  integers; rational Tate modules and Tate modules; and the complex-torus and
  elliptic-curve interpretation of the Tate module.
- No exercise, hint, solution, or assessment environment occurs in this exact
  range. The section contains six active citation commands.
- Next source-order boundary: Section 4.11, groups in categories, begins at
  authority line **1745** and remains excluded.

## Final candidate and canonical binding

- Candidate:
  `build/unit-034-candidate/chapter4-group-limits-completions-id.tex`.
- Candidate identity: 19,019 bytes; SHA-256
  `8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62`.
- Encoding and boundary: strict UTF-8 without BOM, LF-only, 135 substantive
  records with exactly one final LF. Candidate records map one-for-one to
  authority lines 1609–1743; the boundary-only blank authority line 1744 is
  intentionally omitted.
- The Indonesian translation occupies the complete substantive candidate and
  exceeds the normalized source-slice byte extent by 4,014 bytes. It contains
  no Han source prose, Chinese punctuation, invisible Unicode control,
  placeholder, untranslated editorial block, or disabled source content.
- Canonical source: `repo/source/chapter4.tex`, 189,935 bytes; SHA-256
  `37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569`;
  1,893 records. Canonical lines **1604–1738** are byte-identical to the
  candidate, line 1739 is the preserved blank boundary, and line 1740 remains
  the untouched `\section{范畴中的群}\label{sec:group-in-cat}` sentinel.
- Live glossary: `00_control/TERMINOLOGY.id-ID.csv`, 82,586 bytes; SHA-256
  `59e66d5acf8f8e792327730c01a236d3bc7570b9f71a200b9a6d7b9a71fa3955`;
  exactly 513 unique data rows.

These are observed live identities. Updating this review changed none of the
candidate, canonical source, glossary, build, artifact, backend, control, Git,
or publication bytes.

## Translation, terminology, and semantic review

The candidate uses natural formal id-ID prose and reuses the edition's
controlled forms `kategori`, `fungtor`, `homomorfisme`, `produk`, `ekualiser`,
`limit`, `limit proyektif`, `poset terarah ke atas`, `kategori terarah ke
atas`, `topologi produk`, `topologi diskret`, `grup abelian`, and `teori
homologi`. Section-specific forms are applied consistently: `grup topologis`,
`basis lingkungan`, `ruang Hausdorff`, `kompak`, `grup profinit`, `tak
terhubung total`, `pelengkapan grup`, `barisan Cauchy`, `net`, `filter`,
`bilangan bulat p-adik`, `modul Tate rasional`, `modul Tate`, `torus
kompleks`, and `kurva eliptik`.

A complete source-to-target semantic pass followed structural parity, and a
separate prose-quality pass followed that. Together they checked:

- the contravariant diagram data, both functoriality conditions, the explicit
  compatible-family description of the projective limit, and every canonical
  projection;
- the upward-directed convention and construction of a group topology from a
  decreasing family of normal subgroups;
- continuity of multiplication and inversion, translation of neighborhood
  bases, the three Hausdorff criteria, and every step of the closure and
  diagonal arguments;
- both directions of the open-and-closed subgroup lemma and the compactness
  consequence for the subgroup index;
- the product-topology neighborhood basis, the reduction from finite index
  sets to one upper bound, Hausdorffness, Tychonoff compactness, and closedness
  of the projective limit;
- the definition and both directions of the profinite characterization,
  including injectivity, density, compact-Hausdorff surjectivity, and the
  total-disconnectedness reformulation;
- the algebraic completion map, Cauchy condition, all three topological
  completion axioms, their uniqueness claim, and each stage of the
  coordinatewise convergence proof;
- the complete p-adic example, including its index set, quotient system,
  compatibility maps, and forward reference to multiplication; and
- both Tate-module functors, the rational/integral distinction, all four rows
  and twelve arrows of the diagram, the natural completion isomorphism, and
  the final complex-torus/elliptic-curve interpretation.

No hypothesis, implication, quantifier, formula, reference, label, citation,
index, diagram, or active source environment was omitted.

## Declared source correction

Exactly one high-confidence mathematical source correction is applied openly.

### `O013-LI-U034-COR-001` — p-adic family index

- Authority location: line 1720.
- Authority expression:
  `$(a_i \in \Z/p^{i+1} \Z)_{i \geq 1}$`.
- Candidate repair:
  `$(a_i \in \Z/p^{i+1} \Z)_{i \geq 0}$`.
- Reason: the same sentence fixes `I = \Z_{\geq 0}`, defines `H_i` for every
  `i \geq 0`, and uses the quotient `\Z/p^{i+1}\Z`; the compatible family
  therefore begins at `i=0`, with its first component in `\Z/p\Z`. The frozen
  book source independently uses the corrected convention in
  `chapter5.tex:701` and `chapter5.tex:706`. Starting at `i=1` would omit the
  component indexed by the declared initial object.

No other mathematical source correction is required or claimed.

## Explicit order clarification

At authority line 1680, the source says that inclusion gives the neighborhood
basis its poset structure without repeating the orientation already fixed
earlier in the section. The translation writes `inklusi terbalik` explicitly.
This is forced by the established convention
`i \leq j \implies N_j \subset N_i`, makes intersections/refinements into
upper bounds, and is exactly the orientation used by the subsequent quotient
maps and density proof. No symbol, relation, hypothesis, or proof step is
changed.

## Protected text, indexes, and final TeX topology

Nine `\text{...}` fragments inside protected mathematics are localized
without changing their mathematical role: `himpunan bagian`, `terbuka`,
`himpunan bagian tertutup`, `lingkungan terbuka`, `semua lingkungan dari`,
`himpunan bagian berhingga`, `himpunan bagian terbuka`, `dikalikan dengan`,
and `hasil bagi`. Six index commands are localized while preserving their
stream, source sort-key role where present, symbol, and record order:
upward-directed poset, topological group, profinite group, completion, `Z_p`,
and Tate module.

The final candidate contains, before reflow normalization, 26 paired
environments / 52 ordered begin/end markers: one `align*`, two `aligned`, one
`compactitem`, four `definition`, one `enumerate`, one `equation`, one
`equation*`, two `example`, three `lemma`, five `proof`, two `remark`, two
`theorem`, and one `tikzcd`. The second `aligned` pair is solely the declared
target-only reflow. Exact inverse normalization removes that pair and yields
the authority-comparable census of 25 pairs / 50 markers, including the one
pre-existing `aligned` environment.

The final candidate also preserves:

- 11 labels, 16 ordered `ref`/`eqref` targets, six citations, and six indexes;
- 277 raw protected mathematical zones, of which 276 remain after the exact
  reflow normalization and compare identically with the normalized authority;
- one `tikzcd` diagram and twelve exact `\arrow` commands;
- 534 unescaped dollar delimiters; 259 opening / 259 closing raw braces before
  reflow normalization and 257 / 257 after it; and
- zero comments, exercises, hints, solutions, Han characters, Chinese
  punctuation residues, invisible controls, or translation placeholders.

## Target-only digital reflow

`O013-LI-U034-REFLOW-001` changes only candidate record 53, corresponding to
authority line 1661 and canonical line 1656. The single display record is
wrapped in `aligned`, receives two TeX row breaks and three alignment markers,
and remains one LF-delimited record. Removing that exact wrapper, row-break,
and alignment syntax from the live candidate produces the complete
pre-reflow normalized candidate: 18,982 bytes, SHA-256
`c5e91c2271ed44eb51ecaad442799c0312af243fd7ab27a79fa1ff1d0492cc94`.
The live reflow therefore adds exactly 37 bytes at one exact occurrence and
changes no other byte of that normalized candidate.

The reflow does not alter any operand, operator, subscript, inverse image,
membership or subset relation, punctuation-bearing TeX text, display
delimiter, label, reference, citation, index, or prose proposition. It repairs
the 26.11896 pt overfull hbox measured at candidate line 53 in both pre-reflow
build logs. The final E/F logs contain zero overfull and zero underfull hboxes;
Poppler and MuPDF render all nine pages with decoded-pixel identity across the
two builds, and the page-5 visual review confirms that the three-line display
is centered, legible, and within the text block. The complete before/after and
evidence binding is recorded in
`qa/UNIT_034_DIGITAL_REFLOW_20260827.md`.

## Deterministic admission checks

- Candidate checker: `scripts/check_unit_034_candidate.py`, 16,590 bytes;
  SHA-256
  `7b444643a1ccc1705690c64d099722844a30f40f0d97f04200095f0aaa40caf7`.
- Canonical/glossary checker: `scripts/check_unit_034_structure.py`, 3,703
  bytes; SHA-256
  `c80e22ed46a8920c36b07ba5543c447bb851d9c0681429ebffafaf270057da0d`.

The candidate checker is read-only and fails closed on the complete authority
identity, exact 1609–1744 slice identity, line-1745 next-boundary sentinel,
candidate byte identity, strict UTF-8/LF shape, exact 135-record mapping,
opening and closing boundaries, the exact one-occurrence reflow normalization,
environment sequence, labels, references, citations, index streams and
localizations, ordered per-record TeX commands, protected mathematics,
diagram topology, controlled terminology, semantic anchors, nine
protected-text localizations, the declared p-adic correction, dollar and brace
topology, source residue, invisible controls, placeholders, and absence of
exercise, hint, and solution topology.

Two current replays of each checker pass with byte-identical stdout. The
candidate checker reports 136 authority records / 15,005 bytes, 135 candidate
records / 19,019 bytes, 50 normalized environment markers, 11 labels, 16
references, six citations, six indexes, 276 normalized protected mathematical
zones, one diagram, twelve arrows, one declared source correction, and one
target-only digital reflow. The structure checker proves the candidate-identical
canonical span, preserved suffix boundary, 513-row glossary uniqueness, and
exact admission of all 37 staging-delta rows.

The final artifact is
`artifacts/unit-034-bab-4-limit-dan-kompletisasi-grup-id.pdf`, 136,702 bytes,
SHA-256
`e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272`.
Its final structure/PDF and render evidence are bound separately in
`qa/unit-034-evidence/structure-and-pdf-qa.json` and
`qa/unit-034-evidence/render-hash-inventory.json`.

This review proves the complete final Unit 034 translation candidate and its
canonical byte identity. The next source-order boundary remains authority line
**1745**; advancing any durable admission cursor is outside this review's
write boundary.
