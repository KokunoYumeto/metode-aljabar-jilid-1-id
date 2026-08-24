# Unit 023 translation/source review — 2026-08-24

## Verdict

**PASS.** The isolated id-ID candidate is a complete, source-order translation
of frozen Section 3.5. Every prose claim, formula, diagram, environment, label,
reference, item, index entry, and line position was compared continuously
against the authority span. No mathematical source correction was required.
One index-only editorial normalization is isolated below; it changes neither
the source mathematics nor the displayed prose.

Model provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.

No canonical integration, glossary, backend, control, build-reader, Git, web,
or publication operation was performed.

## Frozen boundary and identities

Authority:
`authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`

- Full authority: 911 LF records, 75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Prefix, lines 1–722: 58,181 bytes, SHA-256
  `d140ee3d1cb53d03b8939223e412bfa974e10c0ab2b5b51a8a99400fd93353ad`.
- Included Unit 023 span, lines 723–872: 150 LF records, 12,436 bytes,
  SHA-256
  `2cb843048ffcb6378c3995e5b80c341000098187638e32af6aa918b87f5e5856`.
- Suffix, lines 873–911: 4,954 bytes, SHA-256
  `2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857`.
- Included line 723 (including LF): 64 bytes, SHA-256
  `26cf19a66c488255e23a0fa8774aca285f48b9049a6111bf2c6fe8d746bdced7`;
  signature
  `\section{\texorpdfstring{$2$}{2}-范畴一瞥}\label{sec:2-cat}`.
- Included authority line 872 is the one-byte LF separator after the final
  remark, SHA-256
  `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b`.
- Excluded line 873 (including LF): 18 bytes, SHA-256
  `0f80848f05d5d2ea79e191700984eea0aec0f85dfcf13ac2ad2c23cb282ae699`;
  signature `\begin{Exercises}`.

The included span begins with the section on strict 2-categories, contains the
entire definition and examples, the reformulation as categories enriched over
`\cate{Cat}`, 2-functors and 2-natural transformations, the diagrammatic
convention, and adjunctions in a 2-category. Authority line 872 is the blank
separator after the final remark and is included. Line 873 begins the distinct
chapter exercise block and is excluded.

Candidate:
`build/unit-023-candidate/chapter3-2-categories-id.tex`

- 150 LF records, 14,894 bytes, SHA-256
  `c15e079bc551b30ad7cc6daf72bee58a90108dc7fa5f101f768275e99d1dad05`.
- Opening line (including LF): 76 bytes, SHA-256
  `d383b0253bea36216351c071a8e8ba5a441658261e213bf2e03afb4bf7f0ecbe`;
  signature
  `\section{Sekilas tentang \texorpdfstring{$2$}{2}-Kategori}\label{sec:2-cat}`.
- Candidate record 150 is a whitespace-only tab-plus-LF separator, two bytes,
  SHA-256
  `34a6225b83a638ed08f01ecdbf30cf0be3478ffdd36be92295fee92c5585d57c`.
  It corresponds to authority line 872 and does not contain exercise content.

Checker:
`scripts/check_unit_023_candidate.py`

- 20,526 bytes, SHA-256
  `9ba3a0b4dce48e31cdfe3a796028c416148da6c863bdb7e32a8444eee4763839`.
- `python -B scripts/check_unit_023_candidate.py`: PASS.
- An unexpected positional argument is rejected with exit status 1; neither
  pinned input path can be overridden.

## Continuous semantic review

The Indonesian candidate preserves the complete conceptual sequence:

1. the dimensional motivation from sets as 0-categories and ordinary
   categories as 1-categories, together with topological spaces, continuous
   maps, and homotopies as motivation for 2-cells;
2. the complete data of a strict 2-category: 0-, 1-, and 2-morphisms,
   vertical and horizontal composition, strict associativity, horizontal and
   vertical identities, and the interchange law;
3. the strictification remark for bicategories and the stated limit of that
   coherence phenomenon beyond dimension 2;
4. `\cate{Cat}` as the canonical example, with small categories, functors,
   natural transformations, and their two compositions, followed by its
   Cartesian monoidal structure;
5. the equivalent presentation of a strict 2-category as a category enriched
   over `\cate{Cat}`, including the vertical categories
   `\mathcal V(X,Y)`, composition functors, and unit functors;
6. 2-functors, 2-natural transformations, the diagram-shorthand convention,
   and adjunction data in an arbitrary 2-category.

All quantifiers, source/target orientations, composition orders, identity
types, implication directions, and strictness qualifications were retained.
The interchange equation retains the source order of all four 2-cells and
labels each composition direction in Indonesian. Formal Indonesian is natural
and consistent with the lane's established spellings, including `fungtor`,
`morfisme`, `transformasi natural`, `kategori diperkaya`, and `pasangan
adjoin`. No semantic omission or unrecorded addition remains.

## Structure, mathematics, and topology audit

- Exact one-to-one physical topology: 150 authority records and 150 candidate
  records. Blank or whitespace-only records coincide at relative lines
  `3, 5, 83, 87, 98, 100, 103, 115, 118, 123, 142, 150`. The final candidate
  separator is tab-plus-LF rather than bare LF, but is semantically blank and
  is pinned exactly by the checker.
- Environments: 25 balanced pairs / 50 position-identical ordered events:
  `tikzcd` 14, `remark` 3, `definition` 2, `compactitem` 2, and one each of
  `itemize`, `enumerate`, `example`, and `convention`.
- Labels: two, position- and value-identical: relative line 1 `sec:2-cat` and
  line 88 `eg:Cat`.
- Cross-references: 16 `\ref` calls and no `\eqref` calls. Commands,
  positions, and targets are identical. In source order the targets are
  `eg:Cat`, `rem:strict-or-not`, `prop:ML-coherence`, `con:U-small`,
  `prop:naturaltrans-associativity`, `eg:categories`, `eg:monoidal-cat`,
  `sec:functor-category`, `def:enriched-cat`, `def:enriched-functor`,
  `def:enriched-naturaltrans`, `sec:functors`, `rem:triangle-identity`,
  `sec:adjoint-functor`, `rem:triangle-identity`, and
  `prop:adjoint-equivalence`.
- Citations: none in either span.
- Items: 19 at identical relative lines
  `9, 10, 11, 15, 17, 32, 45, 53, 54, 67, 91, 92, 93, 94, 106, 107,
  108, 110, 112`.
- Index entries: three at identical lines. The target localizes the general
  2-category entry, preserves the symbolic `\cate{Cat}` entry, and supplies a
  readable display term for the adjunction key as recorded below.
- TeX commands: 446 in each file, with identical per-line command multisets.
  The sole commented-out source line, relative line 16, remains commented and
  is translated without changing any embedded command or formula.
- Inline mathematics: 156 occurrences, value- and position-identical in the
  two spans.
- Bracket displays: 11. They are byte-identical after normalizing only nine
  text-label occurrences: `dikomposisikan menjadi` twice,
  `komposisi horizontalnya adalah` once, `vertikal` three times, and
  `horizontal` three times.
- Diagram topology: 14 `tikzcd` blocks are byte-identical; all 64 `\arrow`
  calls remain at identical lines. There are no TikZ nodes, paths, edges,
  draws, or coordinates in the span.
- Unescaped braces balance at 186 opening / 186 closing in each file.
- Han characters: 1,519 in the frozen authority span and 0 in the candidate.
- The excluded `Exercises` environment does not occur in the candidate.

## Explicit editorial normalization

### O013-LI-U023-ED-001 — readable adjunction index display

Authority line 865 (candidate-relative line 143) contains only

```tex
\index{bansuidui}
```

Unlike the structured adjunction entries elsewhere in the book, that form
would print the internal romanized sorting key `bansuidui` as learner-visible
index text. The candidate retains the same sorting key and localizes only its
display payload:

```tex
\index{bansuidui@pasangan adjoin}
```

This is an index-localization repair, not a mathematical source emendation. No
other source correction or editorial intervention was made.

## Terminology consistency

The only terminology evidence consulted was the frozen lane glossary and the
already translated lane corpus; no web or external source was used. At review
time, `00_control/TERMINOLOGY.id-ID.csv` was 39,866 bytes with SHA-256
`45e7b1500533e4fa8a8a257efe2982261704bd00a27f056030112141e5ed0efe`.
It directly admits:

- `2-cell` → `2-sel`;
- `vertical composition` → `komposisi vertikal`;
- `horizontal composition` → `komposisi horizontal`;
- `natural transformation` → `transformasi natural`;
- `enriched category` → `kategori diperkaya`;
- `adjunction` and `adjunction pair` → `pasangan adjoin`;
- `triangle identities` → `identitas segitiga`;
- categorical `coherence` → `koherensi`.

The candidate extends those admitted families transparently as `2-kategori`,
`0/1/2-morfisme`, `2-fungtor`, `2-transformasi natural`, `kategori vertikal`,
and `bikategori`. It uses `ketat` consistently with the admitted strictness
family. No glossary or control file was edited.

## Next source-order cursor

Unit 023 ends with authority line 872. The next untranslated record is exact
authority line 873, `\begin{Exercises}`. Thus the next coherent unit is the
complete Chapter 3 exercise block, authority lines 873–911; no Section 3.5
prose remains outside this candidate.
