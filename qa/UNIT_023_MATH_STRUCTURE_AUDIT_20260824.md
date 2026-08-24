# Unit 023 mathematical and protected-structure audit — 2026-08-24

## Verdict

**PASS.** Unit 023 is a complete source-order Indonesian translation of
Section 3.5, from the definition of a strict 2-category through adjunctions in
a 2-category. Every mathematical surface in the frozen authority span has a
deterministic target counterpart. No mathematical source correction was
required. One index-only editorial normalization is explicitly provenanced;
it changes neither mathematical content nor displayed prose.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. This provenance is
separate from Wen-Wei Li's authorship and from all human source credits.

## Frozen byte and line boundary

- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`,
  911 LF records, 75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Authority span: physical lines 723–872 inclusive, 150 LF records, 12,436
  bytes, SHA-256
  `2cb843048ffcb6378c3995e5b80c341000098187638e32af6aa918b87f5e5856`.
- Reviewed candidate:
  `build/unit-023-candidate/chapter3-2-categories-id.tex`, 150 LF records,
  14,894 bytes, SHA-256
  `c15e079bc551b30ad7cc6daf72bee58a90108dc7fa5f101f768275e99d1dad05`.
- Canonical target: `repo/source/chapter3.tex`, 910 LF records, 88,491 bytes,
  SHA-256
  `8ade04d16a5b71d4d1ffdf3bcee6736bb199c631a8851336d692e7ebdced5e7f`.
- Canonical Unit 023 span: target lines 722–871, byte-identical to the reviewed
  candidate. Target lines 1–721 retain the admitted prior translation; target
  lines 872–910 are byte-identical to authority lines 873–911. Authority line
  872 and target line 871 are the included separator after the final remark.
  The next record is the excluded `\begin{Exercises}` at authority line 873 /
  target line 872; its LF-record SHA-256 is
  `0f80848f05d5d2ea79e191700984eea0aec0f85dfcf13ac2ad2c23cb282ae699`.

The source and target have the same 150-record physical topology. Their blank
or whitespace-only records coincide at relative lines 3, 5, 83, 87, 98, 100,
103, 115, 118, 123, 142, and 150. The final target separator is a pinned
tab-plus-LF record and remains semantically blank.

## Formal-environment and navigation census

There are 25 balanced environment pairs. The exact counts are: 14 `tikzcd`;
three `remark`; two each of `definition` and `compactitem`; and one each of
`itemize`, `enumerate`, `example`, and `convention`.

The two labels are preserved in value and relative position:

1. `sec:2-cat` at relative line 1;
2. `eg:Cat` at relative line 88.

All 16 cross-reference occurrences are ordinary `\ref` calls; there are no
`\eqref` calls. Their commands, values, and relative positions are unchanged.
In source order the targets are `eg:Cat`, `rem:strict-or-not`,
`prop:ML-coherence`, `con:U-small`, `prop:naturaltrans-associativity`,
`eg:categories`, `eg:monoidal-cat`, `sec:functor-category`,
`def:enriched-cat`, `def:enriched-functor`, `def:enriched-naturaltrans`,
`sec:functors`, `rem:triangle-identity`, `sec:adjoint-functor`, a second
`rem:triangle-identity`, and `prop:adjoint-equivalence`. There are no citation
occurrences in this span.

All 19 `\item` occurrences remain at relative lines 9, 10, 11, 15, 17, 32,
45, 53, 54, 67, 91, 92, 93, 94, 106, 107, 108, 110, and 112. The commented
source alternative on relative line 16 stays commented and translated; it is
not counted as a list item or active mathematical statement.

## Formula and diagram audit

The source and target each contain 156 dollar-delimited inline formula
occurrences and 11 bracket-display occurrences, for 167 indexed formula
surfaces. There are no `equation`, `align`, `gather`, or `multline` display
environments in the selected span. Formula order and relative line placement
are preserved. Nine Indonesian `\text{...}` labels in the bracket displays are
the only localized formula text; their surrounding symbols and diagrammatic
composition order compare equal.

All 14 diagrams are `tikzcd` blocks at identical relative line ranges:
18–24, 26–31, 32, 32, 33–37, 39–44, 46–51, 55–59, 61–66, 68–78,
126–128, 130–133, 135–140, and 145–147. The protected primitive census is
64 `\arrow` occurrences. There are no `\node`, `\coordinate`, `\draw`,
`\path`, `edge`, `\braid`, or `\hline` occurrences. The diagrams retain all
objects, 1-morphisms, 2-morphisms, bends, named paths, arrow directions,
identity cells, unit/counit cells, and vertical/horizontal composition order.

The three index occurrences remain at relative lines 6, 88, and 143. The
ordinary 2-category entry and `sym1` entry for `\cate{Cat}` are localized or
preserved in the established form. The final adjunction entry is governed by
the explicit editorial record below.

## Declared editorial normalization

### O013-LI-U023-ED-001 — readable adjunction index display

Authority line 865 contains `\index{bansuidui}`. That raw romanized sort key
would otherwise become learner-visible index text. Target line 864 preserves
the source sorting key and adds only an Indonesian display payload:
`\index{bansuidui@pasangan adjoin}`. This is an index-localization record, not
a mathematical source correction, and it does not alter prose, formulas, or
navigation identity.

The reversible source/candidate comparison and rationale are recorded in
`qa/UNIT_023_TRANSLATION_SOURCE_REVIEW_20260824.md`. Frozen authority bytes are
unchanged, and the editorial normalization is not represented as
source-authored prose.

## Language, terminology, and rights boundary

The Unit 023 target span contains zero Han characters. Its terminology covers
the strict 2-category hierarchy, 2-cells, vertical and horizontal composition,
the interchange law, bicategories, vertical categories, enrichment over
`\cate{Cat}`, 2-functors, 2-natural transformations, and adjunctions. The live
glossary rows and Indonesian field-usage adjudication are bound by the separate
Unit 023 terminology audit; this mathematical audit does not pre-claim that
external evidence or its final file identity.

Component rights remain separate: principal source text and Indonesian
translation under CC BY 4.0; the credited `AJbook.cls` fragment under CC
BY-SA 3.0; bundled Noto fonts under SIL OFL 1.1; and `Lanzhou.png` under CC
BY-SA 3.0 in the wider closure but unused by this unit reader. This audit does
not flatten those rights into a single license.

## Deterministic checks

- `python -B scripts/check_unit_023_candidate.py`: PASS.
- `python -B scripts/check_unit_023_structure.py`: PASS.
- Source/candidate/canonical line boundaries and SHA-256 identities: PASS.
- Environment, label, reference, item, index, formula, and diagram occurrence
  mapping: PASS.
- `O013-LI-U023-ED-001` is the sole declared editorial normalization.
- Han residue in the Unit 023 target span: zero.

Reader-build, all-page visual, PDF-safety, terminology-evidence,
backend-schema, UUID/reference, CSV, and complete file/span-binding evidence
are separate admission gates; this mathematical audit does not pre-claim
those results.
