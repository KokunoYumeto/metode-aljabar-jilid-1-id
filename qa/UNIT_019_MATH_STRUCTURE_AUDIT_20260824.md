# Unit 019 independent mathematics and structure audit — 2026-08-24

Status: **PASS**

Unit: Chapter 3 opening and complete Section 3.1, “Definisi Dasar”

Audit provenance: **OpenAI Codex gpt-5.6-sol, Ultra**

This audit independently compares the integrated Indonesian Unit 019 against
the exact frozen authority and the existing translation/source review. It does
not admit a reader, backend, glossary promotion, Git checkpoint, or public
release; those remain separate production gates.

## Frozen inputs and exact boundary

- Authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`
  - complete file: 911 LF-terminated physical lines, 75,571 bytes;
  - complete-file SHA-256:
    `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`;
  - Unit 019 span: physical lines 1–227 inclusive, 21,745 bytes;
  - span SHA-256:
    `4aecde3d61fb173087ae3e7ab64cc84f7bd4f3fbc0dcbfa8a2c3d6bab1201a8a`.
- Integrated target: `repo/source/chapter3.tex`
  - complete file: 910 LF-terminated physical lines, 79,694 bytes;
  - complete-file SHA-256:
    `bfe5d4745f9a3ac1062b79ee429356a17f3d5bff9be02ef0093eab6978f98e60`;
  - Unit 019 span: physical lines 1–226 inclusive, 25,868 bytes;
  - span SHA-256:
    `6b42291293a06d15b64034a26ed25aeac3cb41465bf9533e069bc9ac65d9b8ac`.
- Existing translation/source review:
  `qa/UNIT_019_TRANSLATION_SOURCE_REVIEW_20260824.md`, 9,617 bytes,
  SHA-256
  `4e79fffff9762ad8398a7c772eb8e9458931a82069fba390e25239169267d0ac`.

Authority line 227 is only the trailing blank separator. The target deliberately
ends the translated content at physical line 226 and does not duplicate that
blank. Authority line 228 and target line 227 are both exactly
`\section{严格性与融贯定理}\label{sec:coherence}`. Every byte after that
boundary in the target is identical to authority lines 228–911. Thus the unit
contains the chapter introduction and all of the basic-definitions section,
and no prose from the next section.

Both spans contain 196 nonblank records. Their blank-line topology agrees
through line 225; the sole record-count difference is the authority’s trailing
separator at line 227. Seven full-line source/rights/inclusion comments and the
two inherited inline `% 3D effects` comments occupy the same records in both
spans.

## Deterministic structure census

| Surface | Authority | Indonesian target | Verdict |
|---|---:|---:|---|
| Begin/end environment calls | 45 / 45 | 45 / 45 | balanced; exact ordered topology |
| Labels | 16 | 16 | exact arguments and records |
| Ordinary references | 15 | 15 | exact arguments, order, and records |
| Equation references | 13 | 13 | exact arguments, order, and records |
| Citations | 4 | 4 | exact keys and optional locators |
| `\item` calls | 13 | 13 | exact records and nesting |
| Inline-math occurrences | 167 | 167 | same-record multisets preserved |
| Bracket displays | 9 | 9 | byte-identical |
| `align` / `equation` / `equation*` | 1 / 6 / 1 | 1 / 6 / 1 | math exact after declared correction |
| `tikzpicture` / `tikzcd` | 3 / 15 | 3 / 15 | complete topology preserved |
| TikZ nodes / paths / pentagon edges | 11 / 1 / 5 | 11 / 1 / 5 | exact |
| `tikzcd` arrows | 75 | 75 | exact records and directions |
| Index entries | 11 | 11 | localized hierarchy preserved |
| Balanced unescaped braces | 334 / 334 | 334 / 334 | balanced, same census |
| TeX commands | 1,034 | 1,035 | sole addition is disclosed `\munit` repair |
| Han code points | 2,381 | 0 | no untranslated Chinese residue |

The 45 environment pairs comprise three `enumerate`, one `wenxintishi`, four
`definition`, three `center`, three `tikzpicture`, one `compactitem`, three
`example`, one `lemma`, one `align`, six `equation`, fifteen `tikzcd`, one
`proof`, one `equation*`, and two `remark` environments. Their serialized
line/event topology has SHA-256
`d999cb6056e31480514aef3809dbdb1d6db8b983c30bc7410f182d7c7de37759`.

All sixteen labels retain their exact identifiers, from `sec:monoidal-cat` and
`sec:monoidal-cat-def` through `def:monoidal-functor` and
`eqn:monoidal-functor-units`. The combined ordered `\ref`/`\eqref` topology
has SHA-256
`dc7167651cb39693f71b6335834841ebc195ebbd348840f5dda17e6ea198a08f`.
The four exact citation surfaces remain `EGNO15`, `EGNO15` with locator
`\S 2.1`, `ML98`, and `EGNO15` with locator `Proposition 2.4.3`.

## Formula and diagram audit

All 167 inline formulae remain on their corresponding physical records. Three
Indonesian sentences reorder complete formula occurrences on lines 81, 109,
and 174; their same-record multisets are unchanged. The only translated text
inside inline mathematics is the mathematically equivalent
`\text{终对象}` → `\text{objek terminal}` on line 214.

The nine bracket displays are byte-identical; their combined SHA-256 is
`2d75116b9bbe81339667ee375689c8dba449f4d20e7a715c944a09697c4fcb5b`.
After normalizing insignificant whitespace and only the disclosed correction
below, the combined hashes agree source-to-target as follows:

- three `tikzpicture` environments:
  `8976422c3806d90e7215f93bd6e9ab159044977d30985974aad7fa4df0c7426b`;
- fifteen `tikzcd` environments:
  `605fbc179c37d1ca2d9f67561a6cc71f8dea1949e9beadc18b70aca565eb0632`;
- one `align` environment:
  `325ee8f9ff522bec5076417fe81a8beddb58581acc5def1b3ddade8445a9ae06`;
- six `equation` environments:
  `02c93e6204ce8d9e5b8a419a7c78eec1181c8a39dd2506cc5e88a33cea918384`;
- one `equation*` environment:
  `c8d801f5e0289118001a246647487287a4cb6ec2f71283360938b6c3977f2e29`.

This verifies the pentagon, unit and triangle constraints; every source and
target of the 75 categorical arrows; associators and unit constraints; the two
large Kelly coherence diagrams; both standard-unit diagrams for a monoidal
functor; their versions at a general object `X`; and the monoidal-natural-
transformation square.

## Declared correction

`O013-LI-U019-COR-001` is necessary, minimal, and mathematically certain. At
authority line 155, the lower-right Kelly-diagram node is
`Z \otimes ((1 \otimes X) \otimes Y)`, while the lower-left node uses the
monoidal unit `\munit` and the connecting horizontal arrow is an associator.
The literal `1` is not the notation defined for the unit object and makes that
arrow’s source/target expression inconsistent. Target line 155 replaces only
that occurrence by `Z \otimes ((\munit \otimes X) \otimes Y)`. The source
signature occurs exactly once, is absent from the target, and the corrected
signature occurs exactly once. No other command, formula, node, or arrow is
added or removed.

## Semantic and index review

Continuous comparison confirms preservation of:

1. the motivating tensor-product, braid, enriched-category, and `2`-category
   route and its prerequisite guidance;
2. all monoidal-category data and the pentagon and unit definitions;
3. the product, coproduct, endofunctor, module, and cobordism examples;
4. Kelly’s lemma, all three displayed conclusions, and the complete proof;
5. monoidal, strong monoidal, right-lax, and left-lax functors;
6. standard unit comparison maps, monoidal natural transformations, the
   retained informal exercise, and monoidal equivalence.

No hypothesis, invertibility condition, naturality claim, object/morphism
type, proof dependency, example, or informal exercise is omitted, weakened,
or strengthened. This span contains no formal `Exercises` environment, no
formal hint, and no solution; the target introduces none.

All eleven index surfaces are deliberately localized rather than copied as
Chinese display text. The symbol entry for `\otimes` is unchanged. Subject
hierarchies are explicit, including `kategori monoidal!subkategori monoidal`,
`fungtor monoidal!longgar-kiri/longgar-kanan`, and the monoidal cases nested
under transformasi natural and ekuivalensi kategori. Latin sort keys and
English parenthetical index glosses are metadata, not untranslated prose.

## Executable gate and disposition

The fail-closed checker is
`scripts/check_unit_019_structure.py`, 24,362 bytes, SHA-256
`7cba44c81b5fd73d027bdde81338df4f68a41328fb95d8275b6e2a570cbe6100`.
It accepts no path overrides, pins both complete-file and exact-span
identities, verifies the shifted next boundary and untouched remainder, and
then enforces every census and correction described above. Its current run
exits `0` with `PASS Unit 019 structural checker`.

**PASS.** Unit 019 is mathematically faithful, structurally complete,
formula-safe, diagram-safe, reference-safe, index-safe, and exact at its source
boundary. No additional high-confidence mathematical or structural defect was
found. Any change to either pinned file identity invalidates this pass and
requires a fresh bounded audit.
