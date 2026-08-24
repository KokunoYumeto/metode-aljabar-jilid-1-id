# Unit 020 independent mathematics and structure audit — 2026-08-24

Status: **PASS**

Unit: Chapter 3, “Keketatan dan Teorema Koherensi”

Audit provenance: `OpenAI Codex gpt-5.6-sol, Ultra`

This audit independently compares the integrated Indonesian Unit 020 with the
exact frozen authority and reviewed isolated candidate. It does not operate on
a reader, build, backend, glossary, control, Git, or publication surface.

## Exact inputs and integration boundary

- Frozen authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`,
  911 LF records, 75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Authority Unit 020 span: physical lines 228–306 inclusive, 79 LF records,
  6,071 bytes, SHA-256
  `86f02abb667e1f03a99e89f34982527fbb715eb55496f9c76c576e041076d737`.
- Integrated target: `repo/source/chapter3.tex`, 910 LF records, 80,889 bytes,
  SHA-256
  `64d334af911539cbe844a250ab41c3e6d537e2c827919c21d41547e1f5782d7a`.
- Canonical Unit 020 span: target physical lines 227–305 inclusive, 79 LF
  records, 7,266 bytes, SHA-256
  `25f8aa41663253a28ac27c3cf635470ac2e20e69d48b168d98cb025a3a792270`.
- Reviewed candidate:
  `build/unit-020-candidate/chapter3-strictness-coherence-id.tex`, 7,266
  bytes, the same SHA-256. The canonical span is byte-identical to it.
- Translation/source review:
  `qa/UNIT_020_TRANSLATION_SOURCE_REVIEW_20260824.md`, 7,282 bytes,
  SHA-256
  `e3edf18ac72fc56ca13102f6bb1d469f6c7cc80e3898eb75727b0f96d6ef912c`.
- Correction provenance:
  `qa/UNIT_020_SOURCE_CORRECTION_20260824.md`, 3,406 bytes, SHA-256
  `1fd9438599ba395f4125e2b3b981ec13c142b3225377c29a0ace03cccbb7a62c`.

The canonical partition is independently closed:

- target lines 1–226: 25,868 bytes, SHA-256
  `6b42291293a06d15b64034a26ed25aeac3cb41465bf9533e069bc9ac65d9b8ac`;
- target lines 227–305: the exact Unit 020 candidate identity above;
- target lines 306–910: 47,755 bytes, SHA-256
  `2efcd829501d06686667549395cb4680ebeccce48ecb981f9b144890fcf4a1f2`,
  byte-identical to frozen authority lines 307–911.

The three target partitions sum to the exact target byte count. Authority line
306 and target line 305 are the included blank separator. Target line 306 is
exactly authority line 307,
`\section{辫结构}\label{sec:braiding}`, and is outside Unit 020.

## Deterministic topology and mathematics

| Surface | Authority | Canonical target | Verdict |
|---|---:|---:|---|
| Begin/end environment calls | 13 / 13 | 13 / 13 | balanced, identical order and records |
| Labels | 3 | 3 | exact identifiers and relative records |
| Ordinary references | 5 | 5 | exact arguments and order |
| Equation references | 0 | 0 | none introduced |
| Citations | 3 | 3 | exact keys and optional locators |
| `\item` calls | 10 | 10 | exact records and nesting |
| Inline-math surfaces | 64 | 64 | preserved after declared correction/reorder |
| Bracket displays | 5 | 5 | byte-identical |
| `tikzpicture` / `tikzcd` | 1 / 1 | 1 / 1 | byte-identical diagrams |
| TikZ nodes / paths / edges | 5 / 1 / 5 | 5 / 1 / 5 | exact topology |
| `tikzcd` arrows | 4 | 4 | exact directions and labels |
| Index entries | 2 | 2 | localized hierarchy and sort keys preserved |
| Unescaped braces | 95 / 95 | 95 / 95 | balanced, equal census |
| TeX commands | 228 | 229 | sole addition is declared `\rho` repair |
| Han code points | 811 | 0 | no untranslated Chinese residue |

The thirteen environment pairs comprise one `compactenum`, one `definition`,
one `theorem`, three `compactitem`, one `center`, one `tikzpicture`, one
`tikzcd`, two `lemma`, and two `proof` environments. Their ordered begin/end
events, all ten item positions, and the labels `sec:coherence`,
`def:strict-monoidal-cat`, and `prop:ML-coherence` agree exactly after the
one-line source/target offset.

The five ordered references remain `def:monoidal-cat`,
`sec:monoidal-cat-def`, `eg:monoidal-cat`, and two occurrences of
`prop:ML-coherence`. The exact citations remain
`\cite[VII.2]{ML98}`, `\cite[pp.26--27]{JS93}`, and
`\cite[\S 2.8]{EGNO15}`.

All five bracket displays are byte-identical, including the natural-family
definition, the four-arrow compatibility square, the tensor-product composite,
the definition of `$LX$`, and the Hom inverse. The five-node/five-edge
associativity pentagon and four-arrow naturality square are byte-identical to
the authority. Every object, functor, morphism, associator, identity, Hom type,
arrow direction, and quantifier is preserved.

Canonical line 270 trims a source-only leading space inside `$(F_2,\rho_2)$`.
Natural Indonesian word order also changes the sequence of the complete inline
surfaces `$\theta:F_1\to F_2$` and `$\rho$` on authority line 271 / canonical
line 270; their same-record multiset is exact. After that whitespace
normalization, this disclosed reorder, and the correction below, all 64 inline
formulas agree.

## Correction and index audit

`O013-LI-U020-COR-001` is necessary and minimal. Authority lines 254–255
define each object as `$(F,\rho)$` and define `\rho`; authority line 299 alone
uses the undefined `$(F,m)$`. Canonical line 298 replaces only that datum with
`$(F,\rho)$`. The source-defect signature occurs once, is absent from the
target, and the corrected essential-surjectivity signature occurs once. No
other command or formula delta exists. Full evidence is recorded in
`qa/UNIT_020_SOURCE_CORRECTION_20260824.md`.

The strict-category index is correctly nested under the established
`yaobanfanchou@kategori monoidal (monoidal category)` parent, and the theorem
uses the existing `MacLane` sort key with Indonesian display text. No Chinese
index display text remains; the Latin sort keys and English explanatory
parentheticals are metadata.

## Executable gate and disposition

The separate canonical checker is `scripts/check_unit_020_structure.py`,
21,048 bytes, SHA-256
`a4bdd19b4104d799cbb28a235898b8883aafecfbdb0bb5cca1e83d7e4f7b96b8`.
It accepts no arguments or path overrides, pins the complete source, complete
target, exact spans, inherited prefix, untouched remainder, and candidate,
then enforces all topology, formula, diagram, index, correction, and Han gates.
Its current run exits `0` with `PASS Unit 020 canonical structure checker`.

The isolated candidate checker `scripts/check_unit_020_candidate.py` also
passes independently against the same frozen source span.

**PASS.** Unit 020 is integrated exactly at the approved boundary and is
mathematically, structurally, formulaically, diagrammatically, referentially,
and index faithful. No unresolved mathematics or topology defect remains.
