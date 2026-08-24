# Unit 018 translation and source review - 2026-08-24

Status: **PASS**. The complete Chapter 2 Exercises block was translated into
natural formal Bahasa Indonesia in an isolated candidate and independently
compared against the exact frozen authority. This record does not integrate
the candidate into the canonical chapter, admit a reader or backend, or claim
publication.

## Frozen authority, candidate, and boundary

- Work: Wen-Wei Li, *Methods of Algebra*, Volume 1.
- Authority repository commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`; tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex`,
  139,983 bytes, SHA-256
  `56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840`.
- Exact authority boundary: `chapter2.tex:1603-1645`, inclusive. It begins
  with `\begin{Exercises}`, ends with `\end{Exercises}`, and is the complete
  final block and final line of the authority file. Authority line 1602 is the
  preceding blank separator and is outside Unit 018.
- Exact authority span: 43 line records, 5,197 UTF-8 bytes, SHA-256
  `24417872734a2dc72c1d52d0df30246a427c5bbb714faf5238679e19c8dd7cce`.
- Isolated Indonesian candidate:
  `build/unit-018-candidate/chapter2-exercises-id.tex`, 43 line records,
  6,523 UTF-8 bytes, SHA-256
  `d69667baae061a5d06a57dcc25033b6a971986ea704c72a0f53d687707837b55`.

No canonical source, control, backend, reader, Git, or publication file is
admitted or modified by this review.

## Structural and mathematical preservation

Source and candidate both contain exactly 43 line records, one blank line,
zero comment lines, and 236 TeX command tokens. Their ordered environment
topology is identical:

1. `Exercises`;
2. `align*`;
3. `cases`;
4. `compactitem`;
5. `inparaenum`;
6. `tikzcd`.

All six environment starts and six ends are paired. Both spans contain
eighteen `\item` commands: thirteen top-level exercises, three nested
universal-property conditions, and two parts of the adjunction exercise. Both
also contain one `\hint`, eighty inline-math surfaces, two bracket-display
surfaces, one diagram, and ten diagram-arrow commands.

The source has no labels, equation references, citations, or index commands;
the candidate introduces none. The three reference arguments are preserved in
their original order and exact form:
`eg:forgetful-adjunction`, `prop:Yoneda-lemma`, and
`def:diagonal-functor`. The mathematical-command census is unchanged,
including three `\varinjlim`, one `\varprojlim`, twelve `\Hom`, ten `\Obj`,
two `\rightiso`, five `\xrightarrow`, three `\identity`, six `\eta`, one
`\varepsilon`, and seven `\varphi` occurrences.

Every displayed formula, object and morphism type, Hom-set, adjunction map,
diagram arrow, exercise division, and hint boundary was checked against the
authority. Mathematical changes are restricted to the two disclosed source
repairs below. The authority span contains 626 Han code points; the candidate
contains zero. No Chinese residue remains.

## Declared source corrections

1. `O013-LI-U018-COR-001` - **duplicated field predicate at authority line
   1640**. The source expression `设域 $\Bbbk$ 为域` redundantly says to let
   the field `\Bbbk` be a field. The candidate removes only the duplication
   and uses the exact target sentence opening `Misalkan $\Bbbk$ medan.` The
   subsequent vector-space category, finite-dimensional subspaces,
   `\varinjlim`, and transfer to `\cate{Ab}` are unchanged.
2. `O013-LI-U018-COR-002` - **unbound fungtor name at authority line 1644**.
   The source introduces the forgetful fungtor
   `\cate{Set}_\bullet \to \cate{Set}` but then asks for the left adjoint of
   `U` and denies a right adjoint to `U` without assigning that name. The
   candidate binds it explicitly in the exact form
   `U: \cate{Set}_\bullet \to \cate{Set}`. No map, adjunction direction, or
   exercise demand is changed.

The punctuation split in authority line 1604 is normalized as ordinary
Indonesian sentence punctuation and is not counted as a mathematical source
repair. The phrase about composing quasi-inverses is rendered with `dalam
urutan yang sesuai` to make the necessary reverse compositional order clear;
this explicates rather than alters the upstream claim.

## Semantic and language review

The candidate was read as one continuous exercise set. Its imperatives are
concise and formal, quantifiers and antecedents are explicit, and nested
conditions remain attached to the correct exercise. The categorical join,
quotient universal property, composite equivalence, unit/counit criterion,
adjunction hint, diagonal-fungtor problem, filtered-limit examples,
full-subcategory Hom bijection, and pointed-category problems retain their
mathematical scope.

In particular, the adjunction hint preserves the naturality square and the
chain of equivalences
`\eta_Y` invertible, precomposition by `\eta_Y` bijective, the adjunction
isomorphism, and `F` full and faithful. The `\cate{Ring} \to \cate{Rng}`
exercise continues to distinguish unital rings and unit-preserving
homomorphisms from rings without a required unit. The final exercise now binds
`U` without supplying or prejudging its requested adjoints.

## Terminology decisions

The governing evidence remains
`qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md`, 18,608 bytes,
SHA-256
`cc6400d922951ab474cf1dee0df3d12dc93183267723df0119b2b93731bb16e5`.
Its bounded same-field search and disclosed Indonesian witnesses support the
core register `kategori`, `fungtor`, `objek`, and the corpus-wide mathematical
style; it is not represented as direct attestation for every specialized term
in these exercises. The controlled glossary is
`00_control/TERMINOLOGY.id-ID.csv`, 35,880 bytes, SHA-256
`8d1ee2c145a76b000f57264fa5e80abb3a9781ffd21b57f0b98d91b52c2c0bc9`.
Fifteen later monoidal-category rows are explicitly marked `candidate` for the
next source-order unit; they do not alter any Unit 018 target form or the eight
dedicated admitted rows listed below.

The candidate consistently applies existing controlled forms:

- `fungtor`, `transformasi natural`, `fungtor kuasi-invers`, `fungtor penuh
  dan setia`, `pasangan adjoin`, `unit`, and `kounit`;
- `semesta Grothendieck`, `himpunan terurut total`, `peta pelestari urutan`,
  `kerangka`, `kategori hasil bagi`, and `subkategori penuh`;
- `gelanggang`, `homomorfisme gelanggang`, `unsur satuan`, `medan`, `ruang
  vektor berdimensi hingga`, and `grup abelian`;
- `limit induktif`, `limit proyektif`, `kategori lengkap`, `kategori
  kolengkap`, `produk`, and `koproduk`; and
- the already established `himpunan bertitik dasar`, `ruang topologis
  bertitik dasar`, `fungtor inklusi`, and `komposisi horizontal`.

For the source-defined operation `\mathcal{C} \star \mathcal{C}'`, the
candidate uses transparent `gabungan`; the displayed definition prevents it
from being confused with an ordinary union or categorical coproduct.
`Himpunan tunggal` follows the already admitted set-theory prose, and
`dibangkitkan secara berhingga` transparently renders finitely generated
abelian groups without introducing an unsupported abbreviation.

Eight dedicated rows were added at this boundary for the star-construction
category union, quotient category, full subcategory, pointed set, pointed
topological space, unital ring, nonunital ring, and finitely generated abelian
group. These additions formalize the already reviewed candidate wording for
the modular backend; they do not change the candidate text or overstate direct
attestation by the fallback witnesses.

## Rights, authorship, and production provenance

Wen-Wei Li remains the source author. Source attribution, CC BY 4.0 rights,
and all human-contributor credits remain separate and intact. This independent
Indonesian derivative and its disclosed corrections do not imply endorsement
by the source author or any terminology witness.

Production provenance is recorded separately from authorship and human credit
with the exact model identification `OpenAI Codex gpt-5.6-sol, Ultra`.

## Review disposition

**PASS - the isolated Unit 018 candidate is faithful and suitable for a later
canonical-integration, build, and backend gate.** No substantive mismatch,
missing exercise or hint, damaged formula, altered reference, topology loss,
or untranslated residue was found. Any change to the frozen authority or
candidate identities above invalidates this pass and must fail closed pending
a fresh bounded comparison.
