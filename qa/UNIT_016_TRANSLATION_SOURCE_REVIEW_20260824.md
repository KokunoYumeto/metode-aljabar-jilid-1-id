# Unit 016 translation and source review - 2026-08-24

Status: translation/source integration reviewed. This record does **not** admit
the standalone reader, its build, its PDF, or its modular backend; those remain
subject to their separate deterministic build and QA gates.

## Frozen source and target

- Work: Wen-Wei Li, *Methods of Algebra*, Volume 1.
- Authority repository commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`; tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex`,
  139,983 bytes, SHA-256
  `56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840`.
- Exact Unit 016 boundary: authority `chapter2.tex:1111-1405`, inclusive,
  comprising all of Section 2.7 and no part of Section 2.8.
- Exact authority span: 295 line records, 24,790 UTF-8 bytes, SHA-256
  `48abd6c33ecdc32591a05ecfbdc7381637027963a61cb3015016909a8faacf82`.
- Integrated target file: `repo/source/chapter2.tex`, 162,316 bytes,
  SHA-256
  `644f98e065dae5761ae6cd41a334704ca890837537e4eb0d90fb2ed794536a0b`.
- Exact integrated target span: `repo/source/chapter2.tex:1111-1405`,
  295 line records, 28,854 UTF-8 bytes, SHA-256
  `fe5e54d56824e8f1a76f93e1732220813c654ab16eb2d7c8daa8dcdde17f5c81`.
  It is byte-identical to the independently prepared, reviewed candidate.

## Structural and mathematical preservation

The source and target have the same 295-line and blank-line topology. The
review counted 1,382 source and 1,384 target TeX command tokens; the only two
additions are the explicit `\in` binders declared in
`O013-LI-U016-COR-003`. The spans preserve 287 inline-math surfaces, twelve
display-math blocks, 66 environment starts and 66 corresponding ends,
seventeen labels, 21 ordinary references, seven equation references, one
citation, thirteen index entries, nine items, 23 `tikzcd` diagrams, and 98
diagram arrows. Label, reference, equation-reference, and citation argument
sequences are identical. Diagram command and arrow topology are unchanged;
only prose inside mathematical text surfaces is translated.

The normalized mathematical surfaces are equivalent after the three declared
repairs below. No formula, label, reference, environment, citation, index sort
key, diagram, or source identifier was omitted. The authority span contains
2,470 Han code points; the Indonesian target contains zero.

## Declared source corrections

1. `O013-LI-U016-COR-001` - **typographic**. Authority line 1177 writes a
   redundant leading `p_i:` immediately before the map already labelled
   `\xrightarrow{p_i}` in the projective-limit data. The target deletes only
   that duplicate prefix and preserves the map and its label.
2. `O013-LI-U016-COR-002` - **prose/order mathematical**. Authority lines
   1338-1343 construct the limit of `\alpha(i,\cdot)` first, which establishes
   the right iterated-limit expression, but the following prose names the left
   expression first. The Indonesian prose correctly says that the right side
   is defined and then the left side. No displayed formula or reduction to the
   `\varprojlim` case was changed.
3. `O013-LI-U016-COR-003` - **unbound-index notation**. Authority line 1348
   uses `\varinjlim \alpha(i)` and `\varprojlim \beta(i)` while defining the
   coproduct and product of an `I`-indexed family, leaving `i` free. The target
   supplies only the missing binders:
   `\varinjlim_{i \in I} \alpha(i)` and
   `\varprojlim_{i \in I} \beta(i)`.

These corrections are minimal, locally checkable, and recorded as target-side
repairs rather than silently attributed to the source author.

## Semantic and fluency review

The final Indonesian review made four prose-only refinements:

- the two defining clauses now use the grammatical construction
  `disebut ... dari` for the limit of `\alpha` or `\beta`;
- `morfisme natural` was normalized to the controlled mathematical term
  `transformasi natural`;
- the product hypothesis explicitly says that products are indexed by every
  `I_j`, removing a scope ambiguity; and
- the equalizer proof explicitly says that the composites of `\mu` and `\nu`
  with `\Ker(f,g) \to X` agree.

These edits improve Indonesian grammar or resolve prose scope only. They do
not change mathematical content, identifiers, formulas, environments,
references, diagrams, citations, or indexes.

## Errata adjudication

The live authority was checked against the source errata. The current errata
source is `Errata-Al-jabr-1.tex`, 6,129 bytes, SHA-256
`0a86bbbe172125984cfbd6da9c72664c3250a6082791264a630f4d329cd8097f`.
The archived `Errata-Al-jabr-1-v1.tex`, 10,435 bytes, SHA-256
`539b8c136adcc7f58abe022dbd4766d532d59b05ee7b4578ee10b869ff24e251`,
records two Section 2.7 corrections: the cone/cocone order below Definition
2.7.2 and two arrows from `x_j` after Equation (2.11), changed to `\mapsto`.
The frozen authority already contains the corrected cone/cocone order and both
`\mapsto` mappings. The Indonesian target preserves those authoritative forms;
they are therefore not counted again among the three Unit 016 repairs.

## Indonesian terminology evidence

The governing evidence and adjudication are recorded in
`qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md`. Its bounded
official arXiv search found no suitable Indonesian same-field TeX source, so
it honestly used the public UNDIP and UGM PDF fallbacks. Their frozen hashes
are respectively
`611b78c88407037489f22814bf054e00ff0f283c702a06082a3a583e9ab35fcb`
and
`4099c3d8aff59e723470f69b4d152b037261bc26d54ef74f1365377f05c25834`.
Those witnesses directly support the controlled family `fungtor`,
`transformasi natural`, `kategori`, and `gelanggang`; this record does not
misrepresent them as direct attestation for every Unit 016 term.

The reviewed target consistently applies the controlled corpus vocabulary and
the Section 2.7 choices `limit induktif`, `limit proyektif`, `ekualiser`,
`koekualiser`, `kategori terarah ke atas (filtered category)`, `topologi hasil
bagi`, and `topologi subruang`. Differences from observed variants were
decided by mathematical meaning, consistency with the admitted Indonesian
corpus, and the documented field-language evidence.

## Rights, authorship, and production provenance

Wen-Wei Li remains the source author. The source text and this Indonesian
translation are licensed CC BY 4.0, with attribution preserved. This is an
independent derivative and does not imply endorsement by the author, publisher,
terminology witnesses, or any human contributor.

Production provenance is recorded separately from authorship and human credit
with the exact model identification `OpenAI Codex gpt-5.6-sol, Ultra`.

