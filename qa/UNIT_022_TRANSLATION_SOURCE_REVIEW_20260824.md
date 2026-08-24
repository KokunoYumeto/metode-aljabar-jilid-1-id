# Unit 022 translation/source review — 2026-08-24

## Verdict

**PASS.** The isolated id-ID candidate is a complete, source-order translation
of frozen Section 3.4. Every prose claim, formula, diagram, environment, label,
reference, citation, item, index entry, and line position was compared against
the authority span. Two high-confidence mathematical source defects were
corrected provisionally and are pinned by exact source/candidate signatures.

Model provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.

No canonical integration, build, reader, backend, glossary, control, Git, web,
or publication operation was performed.

## Frozen boundary and identities

Authority:
`authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`

- Full authority: 911 LF records, 75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Prefix, lines 1–512: 43,092 bytes, SHA-256
  `6726e64e5924c3ca06d5ce68aa654e3e8ec00c01799164e5f959f6b485be09c9`.
- Included Unit 022 span, lines 513–722: 210 LF records, 15,089 bytes,
  SHA-256
  `85332852a2b9808a5a9e7ec240adffdd5b286d44d724be38833aed53e65bd53d`.
- Suffix, lines 723–911: 17,390 bytes, SHA-256
  `db85619a873a826c4a417252b5268b9c85d068f18f9467664599fb9b0575b6af`.
- Included line 513 (including LF): 47 bytes, SHA-256
  `c4fb914defd51476a7a9721c86e92cedeef7c29344722a029cf2dc46825ac541`;
  signature `\section{充实范畴}\label{sec:enriched-cat}`.
- Excluded line 723 (including LF): 64 bytes, SHA-256
  `26cf19a66c488255e23a0fa8774aca285f48b9049a6111bf2c6fe8d746bdced7`;
  signature
  `\section{\texorpdfstring{$2$}{2}-范畴一瞥}\label{sec:2-cat}`.

The included span begins with the enriched-categories section and contains its
complete progression through enriched categories, enriched functors and
transformations, categories enriched in `\cate{Ab}`, biproducts, and additive
categories. Authority line 722 is the blank separator after the final proof and
is included. Line 723 starts the distinct Section 3.5 on 2-categories and is
excluded.

Candidate:
`build/unit-022-candidate/chapter3-enriched-categories-id.tex`

- 210 LF records, 17,541 bytes, SHA-256
  `e1fa8da94c0c2431660f690aa9b2193e3c966e2d71b9d5a029da12a76bc0e255`.
- Opening line (including LF): 53 bytes, SHA-256
  `b78c271f491390406a7a662c60840619c688f3e225674d18f549c88170b2384e`;
  signature
  `\section{Kategori Diperkaya}\label{sec:enriched-cat}`.
- Candidate record 210 is the literal empty LF record corresponding to
  authority line 722. No `sec:2-cat` content is present.

Checker:
`scripts/check_unit_022_candidate.py`

- 23,938 bytes, SHA-256
  `2fc366f8af4439ca0667b0111d836348d0742c3e9cec8dd2dbaf08a7edb81613`.
- `python -B scripts/check_unit_022_candidate.py`: PASS.
- An unexpected positional argument is rejected with exit status 1; neither
  pinned input path can be overridden.

## Semantic review

The Indonesian candidate preserves the complete conceptual sequence:

1. the two viewpoints on enriched categories and replacement of Hom-sets by
   Hom-objects;
2. the data and associativity/unit diagrams for a category enriched over a
   monoidal category;
3. enriched functors, the underlying ordinary category, enriched natural
   transformations, and enriched equivalence;
4. the examples enriched over `\cate{Set}`, `\cate{CGHaus}`, and
   `\cate{Ab}`, including bilinearity and the forgetful functor;
5. binary and finite biproducts, equivalence with products and coproducts, and
   the universal-property proof;
6. zero objects in `\cate{Ab}`-categories, additive functors and categories,
   preservation of biproducts, and finite product/coproduct equivalence.

All quantifiers, hypotheses, implication directions, universal properties,
composition conventions, and duality arguments were retained. Formal
Indonesian is natural and consistent with the lane's established spellings,
including `fungtor`, `morfisme`, `koproduk`, `himpunan`, and
`terdefinisi dengan baik`. No semantic omission or unrecorded addition remains.

## Structure, mathematics, and topology audit

- Exact one-to-one physical topology: 210 source records and 210 candidate
  records. Blank or whitespace-only records coincide at relative lines
  `14, 33, 47, 56, 58, 70, 81, 91, 95, 99, 109, 117, 119, 132, 152, 176,
  190, 194, 196, 203, 210`. Record 47 preserves the authority's indentation;
  record 210 is empty in both.
- Environments: 41 balanced pairs / 82 position-identical ordered events:
  `tikzcd` 6, `definition` 5, `proof` 4, `tikzpicture` 3,
  `example` 3, `align*` 3, `cases` 3, `compactitem` 2,
  `center` 2, `remark` 2, `compactenum` 2, `proposition` 2,
  and one each of `enumerate`, `gather*`, `theorem`, and `lemma`.
- Labels: 11, position- and value-identical:
  `sec:enriched-cat`, `def:enriched-cat`, `def:enriched-functor`,
  `rem:enriched-to-ordinary`, `def:enriched-naturaltrans`,
  `eg:Ab-cat`, `def:biproduct`, `prop:biproduct-criterion`,
  `def:additive-cat`, `prop:biproduct-preservation`, and
  `prop:additive-prod-coprod`.
- Cross-references: 15 `\ref` calls and no `\eqref` calls. Commands,
  positions, and targets are identical. In source order the targets are
  `eg:categories`, `def:category`, `eg:monoidal-cat`,
  `con:U-small`, `eg:categories` twice on relative line 97,
  `rem:enriched-to-ordinary`, `sec:limits`,
  `prop:product-associativity`, `def:universal-objects`,
  `def:zero-morphism`, `def:enriched-functor`,
  `prop:Mod-cat-additive`, `prop:biproduct-criterion`, and
  `prop:product-associativity`.
- Citations: 2, exact and position-identical: relative line 13
  `\cite{Ke05}` and line 97 `\cite[Chapter 5]{May99}`.
- Items: 17 at identical relative lines
  `4, 5, 18, 19, 20, 23, 103, 104, 105, 106, 136, 137, 138, 180, 181,
  182, 183`.
- Index entries: 10 at identical lines. The localized payloads cover
  `kategori diperkaya` and its Hom-object symbol, enriched fungtors,
  enriched natural transformations, enriched category equivalence,
  `kategori topologis`, `kategori-$\cate{Ab}$`, `biproduk`,
  `kategori aditif`, and the additive case of fungtors.
- TeX commands: 668 in each file, with identical per-line command multisets
  after normalizing the declared `\otimes`-to-`\times` correction.
  Unescaped braces balance at 288 opening / 288 closing in each file.
- Inline mathematics: 204 occurrences, in identical sequence on identical
  lines after normalizing the declared injection-domain correction.
  Bracket displays: 11 and otherwise identical after the two declared
  corrections and localized `\text{...}` labels.
- Diagram topology is preserved: 3 `tikzpicture` and 6 `tikzcd` blocks;
  14 `\node`, 0 `\path`, 21 `\arrow`, 13 `edge`,
  11 `\draw`, and 0 `\coordinate` occurrences, all on identical lines.
  The TikZ blocks are identical after the three introductory node texts are
  localized; all algebraic diagram contents are otherwise exact after the two
  declared corrections.
- Han characters: 1,655 in the frozen authority span and 0 in the candidate.

## Explicit provisional source corrections

Both corrections are high-confidence, reversible, and pinned by exact
source/candidate signatures in the checker. They follow from internal typing
and the surrounding defining equations; no external source was consulted.

### O013-LI-U022-COR-001 — Cartesian product of ordinary Hom-sets

Authority line 588 (candidate-relative line 76) begins the composition map with

```tex
\Hom_{\mathcal{V}}(\munit,\iHom(Y,Z))
  \otimes
\Hom_{\mathcal{V}}(\munit,\iHom(X,Y)).
```

Each `\Hom_{\mathcal V}(\cdot,\cdot)` here is an ordinary set. For a general
monoidal category `\mathcal V`, no tensor product on those sets has been
specified. Functoriality of `\otimes` instead takes a *pair* of morphisms and
therefore has the Cartesian product of the two Hom-sets as its domain. The
candidate corrects the intervening `\otimes` to `\times` while retaining the
rest of the diagram exactly.

### O013-LI-U022-COR-002 — domain of the biproduct injections

Authority line 665 (candidate-relative line 153) defines, for `i=1,2`,

```tex
\iota_i: X_1 \to Z
```

but the immediately following equations require
`p_i\iota_i=\identity_{X_i}`. The formula is ill-typed for `i=2` unless the
domain is `X_i`. The candidate therefore uses

```tex
\iota_i: X_i \to Z.
```

No other formula or proof step changes.

## Terminology consistency

The only terminology evidence consulted was the frozen lane glossary and
existing lane corpus; no web source was used. At review time,
`00_control/TERMINOLOGY.id-ID.csv` was 39,866 bytes with SHA-256
`45e7b1500533e4fa8a8a257efe2982261704bd00a27f056030112141e5ed0efe`.
It directly admits:

- `enriched category` → `kategori diperkaya`;
- `additive category` → `kategori aditif`;
- `biproduct` → `biproduk`.

Existing corpus usage supports `kategori-$\mathcal U$`,
`himpunan-$\mathcal U$`, `kategori-$\cate{Ab}$`, `fungtor`,
`transformasi natural`, and `ekuivalensi kategori`. The candidate consistently
uses `kategori-$\mathcal V$`, `objek-$\Hom$`,
`kategori topologis`, `kategori praaditif`, and `fungtor aditif` for the
new specialized contexts. No glossary or control file was edited.
