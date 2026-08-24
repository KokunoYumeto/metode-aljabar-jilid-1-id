# Unit 022 mathematical and protected-structure audit — 2026-08-24

## Verdict

**PASS.** Unit 022 is a complete source-order Indonesian translation of
Section 3.4, from enriched categories through additive categories. Every
mathematical surface in the frozen authority span has a deterministic target
counterpart. Two source defects are corrected explicitly; no other formula,
hypothesis, implication, universal property, reference target, citation key,
index occurrence, or diagram topology changes.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. This provenance is
separate from Wen-Wei Li's authorship and from all human source credits.

## Frozen byte and line boundary

- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`,
  75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Authority span: physical lines 513–722 inclusive, 210 LF records, 15,089
  bytes, SHA-256
  `85332852a2b9808a5a9e7ec240adffdd5b286d44d724be38833aed53e65bd53d`.
- Reviewed candidate:
  `build/unit-022-candidate/chapter3-enriched-categories-id.tex`, 210 LF
  records, 17,541 bytes, SHA-256
  `e1fa8da94c0c2431660f690aa9b2193e3c966e2d71b9d5a029da12a76bc0e255`.
- Canonical target: `repo/source/chapter3.tex`, 910 LF records, 86,033 bytes,
  SHA-256
  `b395e1014becb462dae95eda5fde37da9b4edd0b477df8f0b5cefef43edbefa2`.
- Canonical Unit 022 span: target lines 512–721, byte-identical to the reviewed
  candidate. Target lines 1–511 retain the admitted prior translation; target
  lines 722–910 are byte-identical to authority lines 723–911. The next section
  (`sec:2-cat`) is excluded.

The source and target have the same 210-record physical topology. Their blank
or whitespace-only records coincide at relative lines 14, 33, 47, 56, 58, 70,
81, 91, 95, 99, 109, 117, 119, 132, 152, 176, 190, 194, 196, 203, and 210.

## Formal-environment and navigation census

There are 41 balanced environment pairs. The exact counts are: six `tikzcd`;
five `definition`; four `proof`; three each of `tikzpicture`, `example`,
`align*`, and `cases`; two each of `compactitem`, `center`, `remark`,
`compactenum`, and `proposition`; and one each of `enumerate`, `gather*`,
`theorem`, and `lemma`.

The 11 labels are preserved in value and relative position:

1. `sec:enriched-cat`;
2. `def:enriched-cat`;
3. `def:enriched-functor`;
4. `rem:enriched-to-ordinary`;
5. `def:enriched-naturaltrans`;
6. `eg:Ab-cat`;
7. `def:biproduct`;
8. `prop:biproduct-criterion`;
9. `def:additive-cat`;
10. `prop:biproduct-preservation`;
11. `prop:additive-prod-coprod`.

All 15 cross-reference occurrences are ordinary `\ref` calls; there are no
`\eqref` calls. Their values and positions are unchanged, including the two
occurrences of `eg:categories` on relative line 97 and the two occurrences of
`prop:product-associativity` later in the section. Both citations are preserved:
`\cite{Ke05}` on relative line 13 and `\cite[Chapter 5]{May99}` on relative
line 97. All 17 `\item` occurrences remain at relative lines 4, 5, 18, 19, 20,
23, 103, 104, 105, 106, 136, 137, 138, 180, 181, 182, and 183.

## Formula and diagram audit

The source and target each contain 204 dollar-delimited inline formula
occurrences, 11 bracket-display occurrences, and four display-environment
occurrences (three `align*` and one `gather*`), for 219 indexed formula
surfaces. Formula order and relative line placement are preserved. Localized
`\text{...}` labels are excluded from symbolic comparison. The two declared
source corrections below are normalized only for the corresponding comparison;
all remaining symbolic contents compare equal.

The nine diagrams are preserved as three `tikzpicture` blocks and six `tikzcd`
blocks at the same relative line ranges. The protected primitive census is 14
`\node` occurrences, 21 `\arrow` occurrences, 13 `edge` tokens, and 11
`\draw` occurrences; there are no `\coordinate`, `\path`, or `\braid`
occurrences. The three prose node labels in the introductory replacement
diagram and the textual arrow labels are translated, while their geometry,
arrows, algebraic objects, and composition order remain intact.

The ten index occurrences are retained at the same lines: nine ordinary-index
records and one `sym1` symbol record. Their Indonesian display payloads cover
the enriched-category, enriched-functor, enriched-natural-transformation,
enriched-equivalence, topological-category, category-Ab, biproduct,
additive-category, and additive-functor surfaces while preserving stable sort
keys and the Hom-object symbol.

## Declared source corrections

### O013-LI-U022-COR-001 — product of ordinary Hom-sets

Authority line 588 uses `\otimes` between two ordinary sets
`\Hom_{\mathcal V}(\munit,-)` as the domain of a function induced by
fungtoriality of the monoidal product. No tensor product of these sets is part
of the hypotheses. The target changes only this set-level operator to the
Cartesian product `\times`; the enriched Hom-objects and all monoidal products
in the codomain remain unchanged.

### O013-LI-U022-COR-002 — biproduct injection domain

Authority line 665 prints `\iota_i:X_1\to Z` for both `i=1,2`, while the next
equations require `p_i\iota_i=\identity_{X_i}`. The target changes the domain
to `X_i`, restoring well-typedness for `i=2`. No other symbol or proof step is
changed.

The detailed reversible provenance is in
`qa/UNIT_022_SOURCE_CORRECTIONS_20260824.md`. Frozen authority bytes are
unchanged, and neither correction is represented as source-authored prose.

## Language, terminology, and rights boundary

The candidate contains zero Han characters. Eleven admitted glossary records
are applicable: the eight new Unit 022 records for enriched functor, enriched
natural transformation, enriched category equivalence, Hom-object,
topological category, Ab-enriched category, preadditive category, and additive
functor, together with the existing enriched category, additive category, and
biproduct records. Their evidentiary limits are preserved in
`qa/UNIT_022_TERMINOLOGY_AUDIT_20260824.md`.

Component rights remain separate: principal source text and Indonesian
translation under CC BY 4.0; the credited `AJbook.cls` fragment under CC
BY-SA 3.0; bundled Noto fonts under SIL OFL 1.1; and `Lanzhou.png` under CC
BY-SA 3.0 in the wider closure but unused by this unit reader. This audit does
not flatten those rights into a single license.

## Deterministic checks

- `python -B scripts/check_unit_022_candidate.py`: PASS.
- `python -B scripts/check_unit_022_structure.py`: PASS.
- Source/candidate/canonical line boundaries and SHA-256 identities: PASS.
- Environment, label, reference, citation, item, index, formula, and diagram
  occurrence mapping: PASS.
- Han residue in the Unit 022 target span: zero.

Reader-build, all-page visual, PDF-safety, backend-schema, UUID/reference, CSV,
and complete file/span-binding evidence are separate admission gates; this
mathematical audit does not pre-claim those results.
