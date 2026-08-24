# Unit 020 translation and source review - 2026-08-24

Status: **PASS after three isolated candidate repairs**. The Indonesian candidate
was reviewed continuously and line by line against the exact frozen authority
span. The review found no omitted or added mathematical claim and no remaining
semantic, formula, diagram, reference, citation, index, environment, item, or
untranslated-Han defect. It does not integrate canonical source, generate a
build/backend/artifact, edit controls, run Git, or publish.

## Frozen boundary and identities

- Frozen authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`.
  The 911-line, 75,571-byte file has SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Exact included span: physical lines 228-306 inclusive, 79 LF records, 6,071
  UTF-8 bytes, SHA-256
  `86f02abb667e1f03a99e89f34982527fbb715eb55496f9c76c576e041076d737`.
  Line 228 is `\section{严格性与融贯定理}\label{sec:coherence}` and line
  306 is its included blank separator.
- Independent boundary partition: lines 1-227 are 21,745 bytes with SHA-256
  `4aecde3d61fb173087ae3e7ab64cc84f7bd4f3fbc0dcbfa8a2c3d6bab1201a8a`;
  lines 307-911 are 47,755 bytes with SHA-256
  `2efcd829501d06686667549395cb4680ebeccce48ecb981f9b144890fcf4a1f2`.
  The three byte counts sum exactly to the full authority byte count.
- Boundary-line hashes, including LF: authority line 228 is 56 bytes with
  SHA-256 `de95d42ef774ec462cf17acb4bfc80ad71f202f4d9b5c6caeabb4e6b513f0ca7`;
  authority line 307 is 40 bytes with SHA-256
  `0f3481f923513a19091dc664cd63849cbceb4b3097c192d9ea5b1780c4f750e8`.
  Line 307 is `\section{辫结构}\label{sec:braiding}` and is excluded.
- Reviewed candidate:
  `build/unit-020-candidate/chapter3-strictness-coherence-id.tex`, 79 LF
  records, 7,266 UTF-8 bytes, SHA-256
  `25f8aa41663253a28ac27c3cf635470ac2e20e69d48b168d98cb025a3a792270`.
  Its first record is the translated strictness/coherence section heading and
  its final record preserves authority line 306's blank separator.

## Claim, language, and structural review

The candidate faithfully preserves the two motivating questions, the
definition of a strict monoidal category, Mac Lane's coherence theorem, the
object/morphism/unit/tensor-product data defining
`$\mathbf{e}(\mathcal{V})$`, the strictness lemma, the construction and
properties of `$L$`, its proof sketch, and the deduction of the theorem from
the two lemmas. Quantifiers, arrow directions, compatibility conditions,
fullness, faithfulness, essential surjectivity, and the role of the pentagon
axiom are unchanged. The Indonesian is natural and formal after the repairs
recorded below.

The source and candidate have identical ordered topology: 13 matching
environment pairs (one `compactenum`, one `definition`, one `theorem`, three
`compactitem`, one `center`, one `tikzpicture`, one `tikzcd`, two `lemma`, and
two `proof`), ten `\item` commands, three labels, five ordered `\ref`
arguments, no `\eqref`, and three exact citations with their locators:
`\cite[VII.2]{ML98}`, `\cite[pp.26--27]{JS93}`, and
`\cite[\S 2.8]{EGNO15}`. Both localized index surfaces are present with the
intended hierarchy/sort keys.

There are 64 inline-math surfaces and five bracket displays in each text. The
inline surfaces are identical as line-local multisets after the declared
`(F,m)` correction; candidate line 44 naturally reorders `\theta` and `\rho`
in Indonesian prose without changing either formula. Both displayed diagrams
are byte-identical to the authority: one five-node/five-edge TikZ pentagon and
one four-arrow `tikzcd` square. All other displays, braces (95 opening and 95
closing), commands, objects, functors, morphisms, associators, unit constraints,
and Hom expressions are preserved. The authority span has 811 Han code points;
the candidate has zero.

## Repairs and declared source correction

Three candidate defects were repaired during this review:

1. Candidate line 9 had detached the strict-category index entry from the
   established Chapter 3 monoidal-category parent. It now preserves the source
   hierarchy and corpus display as
   `\index{yaobanfanchou@kategori monoidal (monoidal category)!kategori
   monoidal ketat (strict monoidal category)}`.
2. Candidate line 21 used the index sort key `Mac Lane`, inconsistent with the
   established Chapter 3 key `MacLane`. It now reads
   `\index{MacLane@Teorema koherensi Mac Lane (Mac Lane's Coherence Theorem)}`.
3. Candidate line 63 said that `$F$` was “`komutatif` dengan” right
   multiplication, which is unidiomatic and can suggest commutativity as an
   intrinsic property. It now says that `$F$` “`berkomutasi` dengan perkalian
   kanan” and that `$\rho$` witnesses that commutation, exactly preserving the
   source relation.

`O013-LI-U020-COR-001` - authority line 299 alone says
`$(F, m) \simeq L(F(\munit))$`. The frozen source defines every object of
`$\mathbf{e}(\mathcal{V})$` at line 254 as `$(F, \rho)$`, defines `\rho` at
line 255, and uses that same datum throughout lines 271-294; no datum `m` is
defined in the reviewed construction. A bounded exact search of the frozen
source finds the erroneous `$(F,m)$` only at line 299. Candidate line 72
therefore correctly and explicitly reads
`$(F, \rho) \simeq L(F(\munit))$`. No other mathematical source correction is
made.

## Terminology evidence and checker

Terminology checks were restricted to the lane glossary and existing lane
corpus; no web source was used. The reviewed glossary snapshot is
`00_control/TERMINOLOGY.id-ID.csv`, 36,785 bytes, SHA-256
`793d3cb4a80e493ff7b7ba5a81990e8bc965df5cb1932b3ff067af7073668dbc`.
Targeted corpus searches used `repo/source/chapter1.tex` (64,180 bytes,
SHA-256 `f40dcba1bc87d886f6b83bd6962e9cd044d0b39282c17e326e6afbedd4f6ceee`),
`repo/source/chapter2.tex` (166,465 bytes, SHA-256
`3ef0e0dd3a8a30f4e44d7f87d94a4a4343ac7097a1862180c8becaf3631cda16`),
and `repo/source/chapter3.tex` (79,694 bytes, SHA-256
`bfe5d4745f9a3ac1062b79ee429356a17f3d5bff9be02ef0093eab6978f98e60`).
The candidate consistently uses `kategori monoidal`, `fungtor`, `morfisme`,
`transformasi natural`, `kendala asosiativitas`, `kendala satuan`, `aksioma
segilima Mac Lane`, `fungtor penuh dan setia`, `surjektif secara esensial`,
and `fungtor monoidal` in the controlled/corpus register.

The fail-closed checker is `scripts/check_unit_020_candidate.py`, 20,005 bytes,
SHA-256 `8d091cd4a5db727770f09f01e43ebc8b510b48b09adaed5ed548247c545af1cc`.
Running `python scripts/check_unit_020_candidate.py` passes all identity,
boundary, structure, mathematics, diagram, terminology-signature, correction,
and Han-residue gates. It accepts no arguments or path overrides; an explicit
argument-rejection probe returned the required failure exit. Any authority or
candidate byte drift fails before semantic topology can be accepted.

## Disposition and provenance

**PASS - the isolated Unit 020 candidate is faithful and ready for the parent
workflow's later integration gates.** No review issue remains. This report is
the terminal record for the bounded review; canonical integration and all
downstream production remain outside its write authority.

Production provenance: `OpenAI Codex gpt-5.6-sol, Ultra`.
