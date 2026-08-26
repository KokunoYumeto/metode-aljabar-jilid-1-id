# Unit 032 source and translation review — 2026-08-25

Status (independent re-review and integration 2026-08-26): **revised Indonesian
translation deterministically readmitted and integrated into the canonical
Chapter 4 source and controlled glossary; the two-build, dual-render reader
gate also passes. Backend, controls, README, Git history, and public release
remain pending at this review boundary.**

## Scope and authority

- Corpus/unit: `O013-LI-U032`.
- Work: Wen-Wei Li, *Methods in Algebra*, Volume 1.
- Frozen upstream commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
- Authority file identity: 154,744 bytes; SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`;
  1,898 LF-delimited records and no final LF.
- Selected exact contiguous boundary: authority lines **1108–1388**,
  comprising all of Section 4.8, free groups. Line 1388 is the blank
  section-boundary record.
- Exact normalized-LF authority slice: 281 records, 22,547 bytes; SHA-256
  `5a7083cd89d13e776bbf94189f7f96f5d976cd962cba7a8d4c6b2453bd59c8af`.
- Content coverage: the universal properties and constructions of free
  monoids and free groups; their adjunction to forgetful functors; uniqueness;
  words and word length; amalgamated products of monoids, their quotient
  construction and reduced normal form; the construction of free groups from
  copies of the additive group of integers; free products; free commutative
  monoids and groups as direct sums; generators, relations and finite group
  presentations; the word, conjugacy and isomorphism problems; and the
  Nielsen--Schreier theorem via graphs, maximal spanning trees, fundamental
  groups and covering spaces.
- No exercise, hint, solution or assessment environment occurs in this exact
  source range.
- Next source-order boundary: Section 4.9, symmetric groups, begins at
  authority line **1389** with
  `\section{对称群}\label{sec:symmetric-group}` and remains excluded.

## Candidate identity and isolation

- Candidate:
  `build/unit-032-candidate/chapter4-free-groups-id.tex`.
- Final candidate identity after independent re-review, protected-zone order
  normalization, and two exact display reflows: 27,910 bytes; SHA-256
  `28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc`.
- Encoding and boundary: strict UTF-8 without BOM, LF-only, 280 substantive
  records with exactly one final LF. Candidate records map one-for-one to
  authority lines 1108–1387; the boundary-only blank authority line 1388 is
  intentionally omitted.
- The Indonesian translation occupies the entire substantive candidate and
  exceeds the normalized source-slice byte extent by 5,363 bytes. It contains
  no Han source prose, Chinese punctuation, invisible Unicode control,
  placeholder, untranslated editorial block, or disabled source content.
- Canonical integration now binds this exact candidate at target lines
  1104--1383. The live glossary has admitted the exact 30-row delta; backend,
  control, artifact, README, Git, and publication state remain unmodified at
  this review boundary.

## Translation and semantic review

The candidate uses natural formal id-ID prose and preserves admitted corpus
forms including `grup`, `monoid`, `homomorfisme`, `morfisme`, `isomorfisme`,
`fungtor`, `fungtor pelupa`, `fungtor adjoin kiri`, `sifat universal`, `grup
bebas`, `produk bebas`, `jumlah langsung`, and `grup kepang`. Its internally
consistent local terminology includes `monoid bebas`, `kata`, `kata
tereduksi`, `panjang kata`, `produk teramalgamasi`, `representasi tereduksi`,
`monoid komutatif bebas`, `grup komutatif bebas`, `penutup normal`, `presentasi
grup`, `pembangkit`, `relasi`, `masalah kata`, `masalah konjugasi`, `masalah
isomorfisme`, `teori grup kombinatorial`, `teori rekursi`, `pohon rentang
maksimal`, `retraksi deformasi`, `ruang penutup`, and `sifat pengangkatan
lintasan`. These local forms are now admitted through the exact 30-row Unit 032
delta at the canonical terminology gate.

The 2026-08-26 re-review aligned the candidate with the already-admitted
`hasil bagi`, `ruang topologis bertitik dasar`, and `unsur identitas` forms;
corrected the typo `produk teramalgamasinya`; and made bounded same-record
clarity repairs without altering mathematical content or TeX topology. The
30-row proposal is recorded in
`qa/UNIT_032_TERMINOLOGY_DELTA_20260826.csv` and assessed in
`qa/UNIT_032_TERMINOLOGY_AUDIT_20260826.md`. Its admitted counterpart is
`build/unit-032-staging/terminology-delta.csv`; the live glossary now contains
all 30 rows exactly once.

A complete source-to-target semantic pass was performed after structural
parity first passed, followed by a separate prose-quality pass. They checked:

- both universal mapping properties, including source and target categories,
  existence, uniqueness, commutative triangles, functoriality and the
  left-adjoint interpretation;
- the uniqueness-up-to-unique-isomorphism argument and both inverse
  identities;
- the sequence-based construction of the free monoid, empty word,
  concatenation, identity, associativity and induced homomorphism;
- every datum and clause in the universal property of an amalgamated product,
  including the independence of the composite map from its family index;
- the disjoint-union/free-monoid quotient construction and all three families
  of generating relations;
- the factorization through the quotient and uniqueness forced by the images
  of the structural maps;
- invertibility of words and reversal of factor order under inversion;
- the transversal condition, reduction procedure, zero-length case, and the
  uniqueness proof using the induced action on the sequence set `\Sigma`;
- construction of the free group from copies of the additive group `\Z`, and
  verification of its universal property;
- the distinction between arbitrary words, reduced words and minimum word
  length;
- the group-valued specialization of amalgamated products and the definition
  and universal-property boundary of free products;
- the free commutative monoid and group constructions as finite-support direct
  sums and the exact universal map defined by a finite sum;
- realization of every group as a quotient of a free group, normal closure,
  finite generation, finite presentation, and the generators-plus-relations
  convention;
- both dihedral-group presentations and the Guralnick--Malle generation
  result with bibliography key `GM12`;
- Dehn's three decision problems, their general algorithmic undecidability,
  the stated braid-group exception class, and the distinction between
  combinatorial group theory and recursion theory; and
- every step of the Nielsen--Schreier proof: the bouquet of circles, van
  Kampen identification, geometric realization of a graph, contraction of a
  maximal spanning tree, graph fundamental groups, the subgroup-covering
  correspondence and path lifting.

No sentence, hypothesis, implication, quantifier, formula, reference,
citation, index, diagram, or active source environment was omitted.

## Declared source corrections

Exactly two high-confidence source corrections are applied openly.

### `O013-LI-U032-COR-001` — relation-list endpoint in a finite presentation

- Authority location: line 1335.
- Authority text first declares relations
  `w_1=1, \ldots, w_m=1`, but the next sentence writes the normal closure as
  `\lrangle{w_1, \ldots, w_n}_\text{nor}`.
- Candidate repair: the normal-closure endpoint is changed from `w_n` to
  `w_m`.
- Reason: `n` is already the number of generators `x_1, \ldots, x_n`, whereas
  `m` is the number of relations `w_1, \ldots, w_m`. The source's displayed
  presentation uniquely determines the intended endpoint.

### `O013-LI-U032-COR-002` — author-name spelling

- Authority location: line 1345.
- Authority spelling: `R.\ Guranlnick`.
- Candidate spelling: `R.\ Guralnick`.
- Reason: the cited result and bibliography key `GM12` identify the author as
  Robert Guralnick. The repair changes no mathematical claim or citation key.

No other source correction is required or claimed.

## Protected-text and citation-locator localizations

Thirteen `\text{...}` fragments inside protected mathematics are localized
without changing their surrounding formulas:

- authority line 1187: the two ambient-monoid annotations become `di dalam
  M_i` and `di dalam \mathbf{M}(S)`;
- authority line 1188: the two identity annotations become `unsur identitas
  M_i` and `unsur identitas \mathbf{M}(S)`;
- authority line 1221: `subhimpunan` and `sedemikian sehingga`;
- authority lines 1249 and 1250: both case annotations become `dengan`;
- authority line 1274: `pengulangan diperbolehkan`;
- authority line 1302: the finite-support qualifier becomes `untuk semua
  kecuali paling banyak berhingga banyak i`;
- authority line 1314: `jumlah formal` and `hanya berhingga banyak suku yang
  tak nol`; and
- authority line 1383: `adalah grup bebas`.

Four Chinese-language citation locators on the unchanged bibliography key
`You` are localized as `Bab IV \S 3.1`, `Lampiran B`, `Bab IV \S 4.3`, and
`Bab V \S 4`. No bibliography identity changes.

## Preserved TeX and mathematical topology

- 52 paired environments / 104 ordered begin/end markers: 2 `aligned`, 3
  `align*`, 1 `cases`, 3 `center`, 1 `compactenum`, 1 `compactitem`, 6 `definition`, 1
  `description`, 1 `equation`, 2 `example`, 1 `gather`, 1 `gather*`, 1
  `gathered`, 1 `inparaenum`, 3 `lemma`, 7 `proof`, 3 `proposition`, 1
  `remark`, 1 `scope`, 1 `theorem`, 9 `tikzcd`, and 2 `tikzpicture`
  environments;
- 10 labels with exact identifiers and source order;
- 20 ordered `ref`/`eqref` targets;
- 6 citations with exact bibliography keys and source order;
- 7 index commands with preserved main streams and source sort keys;
- 367 protected inline, display and mathematical-environment zones after the
  13 exact protected-text localizations and the declared relation-index
  correction;
- 9 TikZ-cd environments, 2 TikZ-picture environments, and 28 exact `\arrow`
  commands;
- 644 unescaped dollar delimiters, matching the authority, and 387 opening /
  387 closing raw braces. The six added balanced brace pairs belong solely to
  the two declared `aligned` display reflows (environment names and alignment
  spacers); normalized mathematical zones remain identical;
- 0 comments, 0 exercises, 0 hints, 0 solutions, 0 Han characters, 0 Chinese
  punctuation residues, 0 invisible Unicode controls, and 0 translation
  placeholders.

## Deterministic admission

- Checker: `scripts/check_unit_032_candidate.py`.
- Final checker identity: 18,668 bytes; SHA-256
  `318a57bf22d50baef5102ebc07bb9fd83943682b44d01dac4de5150e770a2cc0`.
- The checker is read-only and fails closed on the complete authority identity,
  exact 1108–1388 slice identity, line-1389 next-boundary sentinel, candidate
  byte identity, strict UTF-8/LF shape, exact 280-record substantive mapping,
  opening and closing boundaries, environment sequence, labels, references,
  citation keys, index streams and sort keys, ordered per-record TeX commands,
  all protected mathematical zones, diagram topology, controlled terminology,
  semantic anchors, all 13 protected-text localizations, all four localized
  citation locators, both declared source corrections, exact dollar topology,
  declared balanced brace additions, both exact digital reflows, source
  residue, invisible controls, placeholders, and absence of
  out-of-scope exercise, hint, and solution topology.
- Command: `python scripts/check_unit_032_candidate.py`.
- Final result on 2026-08-26: **PASS**, repeated twice with byte-identical
  output after rebinding the checker and restoring the authority order of the
  protected `$\Sigma$`, `$M$` zones in one Indonesian sentence.
- Final reported result: source slice 281 records / 22,547 bytes / SHA-256
  `5a7083cd…59c8af`; candidate 280 records / 27,910 bytes / SHA-256
  `28e8fd24…b4cfc`; 104 environment markers, 10 labels, 20 references, 6
  citations, 7 indexes, 367 protected mathematical zones, 11 diagrams / 28
  arrows, zero exercises and hints, zero Han residue, 13 protected-text
  localizations, four citation-locator localizations, two declared source
  corrections, and two target-only digital reflows.

The revised candidate is semantically, mathematically, structurally, and
terminologically admitted. The independent canonical structure checker passes
twice and binds target lines 1104--1383, canonical Chapter 4 SHA-256
`4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680`,
and the 465-row glossary SHA-256
`bb58d18ad5802c5c2159db092f0fc322761f8f9559ea7efd3789ab8d7317e582`.
The 13-page release reader is 149,624 bytes, SHA-256
`904330916e20f0782b6464cb85e07001851940f4adf153f6592cd34087dbadbf`.
Its two clean builds, all-page Poppler/MuPDF review, embedded-font, navigation,
diagnostic, and decoded-pixel gates pass; exactly three visually non-actionable
underfull hboxes remain disclosed. Backend, version-control, and publication
work remain downstream.
The next source-order cursor is authority line **1389**.
