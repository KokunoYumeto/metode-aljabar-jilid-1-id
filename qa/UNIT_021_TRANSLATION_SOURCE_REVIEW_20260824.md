# Unit 021 translation/source review — 2026-08-24

## Verdict

**PASS.** The isolated id-ID candidate is a complete, source-order translation
of the frozen Section 3.3 boundary. Every prose claim, formula, diagram,
environment, label, reference, citation, index entry, and blank-line position
was compared against the authority span. The candidate is not canonically
integrated and no build, reader, backend, glossary, control, Git, or publication
operation was performed.

Model provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.

## Frozen boundary and identities

Authority:
`authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`

- Full authority: 911 LF records, 75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Prefix, lines 1–306: 27,816 bytes, SHA-256
  `ffce6a027b6d3ceacffd30548553b7539688ff552f075127dd769a9900bbfff5`.
- Included Unit 021 span, lines 307–512: 206 LF records, 15,276 bytes,
  SHA-256
  `cbbf8714c3e5a387e42e2653900a8f3911e41df530b39a86701261c89de64ff8`.
- Suffix, lines 513–911: 32,479 bytes, SHA-256
  `0184b127cecf8e973aa395e050385ed75280b898d5ea22293572d6513d7a6c83`.
- Included opening line 307 (including LF): 40 bytes, SHA-256
  `0f3481f923513a19091dc664cd63849cbceb4b3097c192d9ea5b1780c4f750e8`;
  signature `\section{辫结构}\label{sec:braiding}`.
- Excluded next line 513 (including LF): 47 bytes, SHA-256
  `c4fb914defd51476a7a9721c86e92cedeef7c29344722a029cf2dc46825ac541`;
  signature `\section{充实范畴}\label{sec:enriched-cat}`.

The included span begins with the braiding section and ends after its concluding
free-braided-monoidal-category/coherence paragraph. Authority line 512 is the
blank separator after that paragraph and is included. Line 513 opens the next
semantic unit, enriched categories, and is excluded. Thus 307–512 is the
smallest complete coherent section boundary beginning at line 307.

Candidate:
`build/unit-021-candidate/chapter3-braiding-id.tex`

- 206 LF records, 17,968 bytes, SHA-256
  `57f5bc8a211b6a9b76a096742fbfc94989c890f11d5140ad449d0e76e2c67085`.
- Opening line (including LF): 46 bytes, SHA-256
  `8acd960675d96dd70537f2cb73f61098075ac025b1b983fcc584dd66573605bd`;
  signature `\section{Struktur Kepang}\label{sec:braiding}`.
- Candidate line 206 is the preserved blank separator; no
  `sec:enriched-cat` content is present.

Checker:
`scripts/check_unit_021_candidate.py`

- 23,377 bytes, SHA-256
  `6448b0fa51ac8741bab5b29c7ed339f318c073388e79ba2705bd34b8413a9af6`.
- `python -B scripts/check_unit_021_candidate.py`: PASS.
- An unexpected positional argument is rejected with exit status 1, so source
  and candidate paths cannot be overridden.

## Semantic review

The translation preserves the section's full mathematical progression:

1. motivation and definition of a braiding, including the two hexagon diagrams
   and both unit diagrams;
2. the strict-monoidal form of the hexagon axioms, braided monoidal functors,
   symmetric monoidal categories, and the product/coproduct and module examples;
3. the Yang--Baxter proposition, its diagrammatic proof, and the strict form of
   the equation;
4. the unordered configuration space \(C_n\), topological braids, equivalence by
   endpoint-fixing deformation, composition, the Artin braid group
   \(\mathcal B_n=\pi_1(C_n,p)\), and its identity and inverse;
5. the strict monoidal category \(\cate{Braid}\), juxtaposition tensor product,
   its braiding, the hexagon and naturality interpretations, failure of
   symmetry, and the closing free-braided-monoidal-category statement.

The Indonesian is natural formal prose while retaining established local
spellings such as `fungtor`, `morfisme`, `naturalitas`, and `terdefinisi dengan
baik`. No semantic omission, addition, reversed implication, changed
quantifier, changed composition convention, or mistranslated diagram
interpretation remains.

## Structure, mathematics, and topology audit

- Exact one-to-one line topology: 206 source records and 206 candidate records.
  Blank records coincide at relative lines
  `3, 28, 37, 45, 49, 58, 74, 76, 87, 96, 101, 117, 129, 131, 141, 167, 176, 204, 206`.
- Environments: 43 balanced pairs / 86 ordered events, position-identical:
  `tikzpicture` 17, `tikzcd` 6, `center` 4, `definition` 3,
  `equation` 3, `remark` 2, `align*` 2, `example` 2,
  `proposition` 1, `proof` 1, `multline*` 1, and `array` 1.
- Labels: 9, position- and value-identical:
  line 1 `sec:braiding`; line 4 `def:braiding`; line 8
  `eqn:hexagon-axiom-1`; line 13 `eqn:hexagon-axiom-2`; line 30
  `rem:hexagon-axiom-strict`; line 46 `def:symm-monoidal-cat`; line 59
  `prop:YBE-cat-strict`; line 88 `rem:YBE-cat-strict`; line 97 `eg:braid`.
- Cross-references: 13, position-, command-, and value-identical. They are
  10 `\ref` calls at relative lines 2, 31, 51 (two), 56, 128, 130, 166,
  168, and 205, plus 3 `\eqref` calls at lines 29 (two) and 130.
  Their targets are respectively `eg:braid`, `def:strict-monoidal-cat`,
  `eg:monoidal-cat`, `prop:product-commutativity`,
  `sec:module-tensor-prod`, `eg:fundamental-groupoid`,
  `sec:symmetric-group`, `rem:hexagon-axiom-strict`,
  `rem:YBE-cat-strict`, `def:braiding`, `eqn:hexagon-axiom-1`,
  `eqn:hexagon-axiom-2`, and `eqn:braid-presentation`.
- Citations: 2, exact and position-identical: relative line 2
  `\cite{JS93}` and line 205 `\cite[Corollary 2.6]{JS93}`.
- Items: 0 in both source and candidate.
- Index entries: 8 at the same lines. Localized payloads are line 4
  `bianjiegou@struktur kepang (braiding)` and
  `liujiaoxinggongli@aksioma segienam (hexagon axiom)`; line 38
  `yaobanhanzi@fungtor monoidal (monoidal functor)!berkepang (braided)`;
  line 46 `yaobanfanchou@kategori monoidal (monoidal category)!kategori
  monoidal simetris (symmetric monoidal category)`; line 59
  `YBE@persamaan Yang--Baxter (Yang--Baxter equation)`; line 97 symbol
  entry `Braid@$\cate{Braid}$`; and line 130
  `bianqun@grup kepang (braid group)` plus symbol entry
  `B_n@$\mathcal{B}_n$`.
- TeX commands: 527 in each file, with an identical per-line command
  multiset. Unescaped braces are balanced at 276 opening / 276 closing in
  each file.
- Inline mathematics: 144 occurrences in each file on the same lines.
  Bracket displays: 6, equivalent after the three required
  `\text{...}` localizations. Natural prose reorders math tokens only on
  relative lines 100, 132, 144, and 146; the per-line math multisets remain
  identical.
- All 17 `tikzpicture` blocks are byte-identical. All 6 `tikzcd` blocks are
  identical after normalizing the declared naturality-square correction.
  The 3 `equation`, 2 `align*`, 1 `multline*`, and 1 `array` blocks are
  otherwise identical after localized `\text{...}` content.
- Diagram primitives are position-identical: 30 `\node`, 0 `\path`,
  26 `\arrow`, 15 `edge`, 32 `\draw`, 10 `\braid`, and 2
  `\coordinate` occurrences.
- Han characters: 1,446 in the frozen authority span and 0 in the candidate.

## Explicit provisional source adjudications

All three adjudications are high-confidence, reversible, and pinned by exact
source/candidate signatures in the checker. They were made from the frozen
source and internal mathematical consistency, without web research.

### O013-LI-U021-COR-001 — ill-typed naturality-square bottom row

Authority line 487 (candidate-relative line 181) repeats

```tex
X \otimes Y \arrow[r, "{c(X, Y)}"'] & Y \otimes X
```

under vertical arrows labelled \(f\otimes g\) and \(g\otimes f\). For the
naturality square with \(f:X\to X'\) and \(g:Y\to Y'\), that bottom row is
ill-typed. The candidate explicitly corrects it to

```tex
X' \otimes Y' \arrow[r, "{c(X', Y')}"'] & Y' \otimes X'
```

This restores the defined naturality square and changes no surrounding diagram
topology.

### O013-LI-U021-COR-002 — objects misnamed as braids

Authority lines 450 and 452 refer to “the braid \(X\)” and “the braid \(Y\)”
immediately after line 448 sets \(X=m\) and \(Y=n\), which are objects of
\(\cate{Braid}\); the braid is the morphism \(c(X,Y)\). Candidate-relative
lines 144 and 146 therefore use `objek $X$` and `objek $Y$`. This is a
type-consistent prose correction, not a change to any symbol or diagram.

### O013-LI-U021-ED-001 — duplicated word

Authority line 508 contains `无穷循环群群`, literally a duplicated final
“group.” Candidate-relative line 202 normalizes this once to
`grup siklik tak hingga` in the claim
\(\mathcal B_2\simeq\mathbb Z\). The mathematical claim is unchanged.

## Terminology consistency

The only terminology sources consulted were the frozen lane glossary and
existing lane corpus; no web source was used. The read-only glossary snapshot
`00_control/TERMINOLOGY.id-ID.csv` was 37,771 bytes with SHA-256
`3afc80895bec2d3710cbbd26de8451063ce53445c081b276670a0b3568f0c983`.
It directly supports `kendala komutativitas` (row 223), `kategori kepang`
(row 258), and `fungtor monoidal` (row 262). Existing corpus usage in
`repo/source/chapter3.tex` also supports `kategori kepang`, while the earlier
chapter corpus supports `kendala komutativitas`.

The coherent specialized choices used throughout this isolated candidate are
`struktur kepang`, `kategori monoidal berkepang`, `fungtor monoidal
berkepang`, `kategori monoidal simetris`, `aksioma segienam`, `persamaan
Yang--Baxter`, `kategori kepang`, `grup kepang Artin`, and `grup kepang`.
No glossary or control file was edited.
