# Unit 019 translation and source review - 2026-08-24

Status: **PASS**. The Chapter 3 opening and complete section on basic
definitions of monoidal categories were translated into natural formal Bahasa
Indonesia in an isolated candidate and independently compared line by line
against the exact frozen authority. This record does not integrate the
candidate into the canonical chapter, admit a reader or backend, promote its
candidate terminology, or claim publication.

## Frozen authority, candidate, and boundary

- Work: Wen-Wei Li, *Methods of Algebra*, Volume 1.
- Authority repository commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`; tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`,
  75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Exact authority boundary: `chapter3.tex:1-227`, inclusive. It begins with
  the source copyright comment, contains the Chapter 3 opening and all of
  `\section{基本定义}`, and ends with the blank separator at authority line
  227. Authority line 228 begins the next section and is outside Unit 019.
- Exact authority span: 227 LF line records, 21,745 UTF-8 bytes, SHA-256
  `4aecde3d61fb173087ae3e7ab64cc84f7bd4f3fbc0dcbfa8a2c3d6bab1201a8a`.
- Isolated Indonesian candidate:
  `build/unit-019-candidate/chapter3-intro-basic-definitions-id.tex`, 25,868
  UTF-8 bytes, SHA-256
  `6b42291293a06d15b64034a26ed25aeac3cb41465bf9533e069bc9ac65d9b8ac`.
  It has 226 LF-terminated lines and ends after the translated authority line
  226. The sole line-count difference is authority line 227's trailing blank
  separator: both spans contain exactly 196 nonblank lines and seven comment
  lines, so no substantive source line is omitted.

No canonical source, control, backend, reader, Git, artifact, or publication
file is admitted or modified by this review.

## Structural and mathematical preservation

The source and candidate have the same ordered environment topology: 45 starts
and 45 matching ends, comprising three `enumerate`, one `wenxintishi`, four
`definition`, one `compactitem`, three `example`, three `center`, three
`tikzpicture`, one `lemma`, one `align`, six `equation`, fifteen `tikzcd`, one
`proof`, one `equation*`, and two `remark` environments. Both contain thirteen
`\item` commands, nine bracket-display pairs, 167 inline-math surfaces, eleven
TikZ nodes, one TikZ path, and 75 `\arrow` commands.

All sixteen label arguments are present in the same order and exact form:
`sec:monoidal-cat`, `sec:monoidal-cat-def`, `def:monoidal-cat`,
`def:monoidal-constraints`, `eg:monoidal-cat`, `eg:cob-cat`, `prop:Kelly`,
`eqn:unit-coherence-2a`, `eqn:unit-coherence-2b`,
`eqn:unit-coherence-2c`, `eqn:monoidal-cat-unit`,
`eqn:unit-coherence-1`, `eqn:unit-coherence-3`, `eqn:coherence-aux0`,
`def:monoidal-functor`, and `eqn:monoidal-functor-units`. The 28 ordered
`\ref`/`\eqref` arguments are exact, as are the four ordered citation keys
`EGNO15`, `EGNO15`, `ML98`, and `EGNO15`, including the source's optional
citation locators.

The eleven index surfaces retain their subject and hierarchy. Indonesian
display text and useful sort forms replace Chinese display text; in
particular, the corrected line 74 entry is explicitly nested as
`kategori monoidal!subkategori monoidal`. The symbol-index entry for
`\otimes` is unchanged. This is target-index localization, not a correction to
the mathematical source.

The inline-math multisets are identical except for the necessary language
localization `\text{终对象}` to `\text{objek terminal}`. After accounting for
the one declared source correction below, the TeX-control-sequence census is
also identical: the authority has 992 command tokens and the candidate 993,
with the only count difference being the added `\munit` that replaces the
authority's erroneous literal `1`. Every associator, unit constraint,
functorial map, object and morphism type, equation, commutative-diagram node,
diagram edge, and proof dependency was checked against the authority.

The authority span contains 2,381 Han code points; the candidate contains
zero. No untranslated Chinese prose remains. Latin transliterated index sort
keys, bibliography keys, TikZ/TQFT style names, and the English parenthetical
index glosses are structural metadata, not untranslated residue.

## Declared mathematical source correction

`O013-LI-U019-COR-001` - **undefined literal `1` in the Kelly coherence
diagram at authority line 155**. The lower-right node of the source diagram is

```tex
Z \otimes ((1 \otimes X) \otimes Y)
```

whereas its lower-left node is
`(Z \otimes (\munit \otimes X)) \otimes Y`, the connecting horizontal
arrow is the associativity constraint, and the entire section consistently
denotes the monoidal unit by `\munit`. The candidate therefore repairs only
that node to

```tex
Z \otimes ((\munit \otimes X) \otimes Y).
```

This is a disclosed correction to the source diagram, not a translation
choice. It restores the required source and target of the associator without
changing the proof or adding a new claim. No other mathematical source
correction is made. The polished prose at candidate line 63 and the localized
hierarchical index at candidate line 74 are ordinary translation and index
normalization, respectively; neither is represented as upstream mathematics.

## Semantic and language review

The candidate was read continuously from the chapter introduction through the
end of the section. It preserves the motivation and prerequisite guidance;
the definition of the monoidal data; the pentagon, unit, and triangle
constraints; the product, coproduct, endofunctor, module, and cobordism
examples; Kelly's coherence lemma and proof; and the definitions and examples
of monoidal, strong monoidal, right-lax, and left-lax functors, monoidal natural
transformations, and monoidal equivalence.

The three large coherence arguments retain which subdiagrams commute, which
maps are invertible, where naturality and the pentagon axiom are used, and
which tensor functor is applied. The standard unit comparison
`\varphi_F`, both unit diagrams, their generalizations to `F(X)`, and every
arrow direction are intact. The informal exercise on `\varphi_F`,
`\varphi_G`, and `\theta_{\mathbf{1}_1}` remains an exercise and is neither
answered nor strengthened mathematically. This span contains no formal
`Exercises` environment or hint, and the candidate introduces none.

Indonesian prose is formal and readable. The corrected line 63 now has a
complete grammatical subject before its two-item construction; line 74
retains closure under `\otimes` and membership of `\munit` while using a
properly nested Indonesian index entry. Neither repair changes the source
meaning.

## Terminology decisions and admission boundary

The governing evidence remains
`qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md`, 18,608 bytes,
SHA-256
`cc6400d922951ab474cf1dee0df3d12dc93183267723df0119b2b93731bb16e5`.
Its bounded same-field search and disclosed Indonesian witnesses support the
core register `kategori`, `fungtor`, `objek`, and the corpus-wide formal style;
it is not represented as direct attestation for every specialized monoidal
term.

The controlled glossary at this review boundary is
`00_control/TERMINOLOGY.id-ID.csv`, 35,880 bytes, SHA-256
`8d1ee2c145a76b000f57264fa5e80abb3a9781ffd21b57f0b98d91b52c2c0bc9`.
The established forms `kategori monoidal`, `kobordisme`, and `kendala
asosiativitas` are already admitted. Fifteen Unit 019 rows remain explicitly
at status `candidate` pending canonical integration, build, and admission:
`objek satuan`, `kendala satuan`, `aksioma segilima Mac Lane`, `aksioma
segitiga kategori monoidal`, `subkategori monoidal`, `kategori kepang`,
`kategori diperkaya`, `kategori aditif`, `biproduk`, `fungtor monoidal`,
`fungtor monoidal kuat`, `fungtor monoidal longgar-kanan`, `fungtor monoidal
longgar-kiri`, `ekuivalensi monoidal`, and `kategori tensor`. This isolated
PASS validates their use in the candidate but does not itself promote those
rows or admit Unit 019.

The candidate also consistently reuses admitted corpus forms including
`hasil kali tensor`, `gabungan saling lepas`, `produk`, `koproduk`, `objek
awal`, `objek terminal`, `transformasi natural`, `komposisi horizontal`,
`gelanggang komutatif`, `modul`, and `grup abelian`. `Objek satuan` is kept
distinct from `objek terminal`: the latter appears only in the Cartesian
monoidal example, exactly as the mathematics requires.

## Rights, authorship, and production provenance

Wen-Wei Li remains the source author. Source attribution, CC BY 4.0 rights,
and all human-contributor credits remain separate and intact. This independent
Indonesian derivative and its disclosed diagram correction do not imply
endorsement by the source author or any terminology witness.

Production provenance is recorded separately from authorship and human credit
with the exact model identification `OpenAI Codex gpt-5.6-sol, Ultra`.

## Review disposition

**PASS - the isolated Unit 019 candidate is faithful and suitable for later
canonical integration, build, visual QA, backend generation, and admission.**
No substantive mismatch, missing definition, damaged formula, altered label,
reference or citation loss, diagram-topology loss, index-semantic loss, or
untranslated residue was found. Any change to the frozen authority, candidate,
or controlled terminology identities above invalidates this pass and must fail
closed pending a fresh bounded comparison.
