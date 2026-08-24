# Unit 017 translation and source review - 2026-08-24

Status: **PASS**. The exact Section 2.8 authority and integrated Indonesian
target were independently compared line by line. The translation is faithful,
mathematically coherent, structurally complete, and written in natural formal
Bahasa Indonesia. This record reviews source/translation integration only; it
does not admit a reader build, PDF, modular backend, release, or publication.

## Frozen source, target, and boundary

- Work: Wen-Wei Li, *Methods of Algebra*, Volume 1.
- Authority repository commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`; tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex`,
  139,983 bytes, SHA-256
  `56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840`.
- Exact Unit 017 authority boundary: `chapter2.tex:1406-1602`, inclusive,
  comprising all of Section 2.8 and its trailing blank separator, but no part
  of the exercises.
- Exact authority span: 197 line records, 15,810 UTF-8 bytes, SHA-256
  `ccc5a17cbf856e59e7b8abbff8fd542c5deb399e58b6fc7a5a0f448c7c019e92`.
- Integrated target file: `repo/source/chapter2.tex`, 165,139 bytes, SHA-256
  `be7c571d574e7c8608f535f59627c47118cdb7f00a44aaf1e7d85eb11ea60e35`.
- Exact integrated target span: `repo/source/chapter2.tex:1406-1602`, 197 line
  records, 18,633 UTF-8 bytes, SHA-256
  `e27dba97355122446714b8e58f71f80edbb1d74e6160f99ba0b8160e7c3ec30b`.

The boundary was checked directly: authority line 1406 is
`\section{完备性}`, target line 1406 is `\section{Kelengkapan}`, line 1602 is
blank in both files, and line 1603 remains exactly `\begin{Exercises}` in
both. Authority and target line 1604 are also identical, proving that the
exercise block was not entered or modified by Unit 017.

## Structural and mathematical preservation

Both spans contain exactly 197 line records, twenty blank lines, eight
commented lines, and 764 TeX command tokens. The protected topology is
preserved as follows:

- forty environment starts and forty matching ends, with identical ordered
  environment sequences;
- eleven labels, 35 ordinary references, five equation references, and no
  citations, with their argument sequences byte-identical;
- nine index-command positions, all retained, with Indonesian display terms
  and the English `pullback`, `pushout`, `fibered product`, and
  `fibered coproduct` glosses retained where needed for discoverability;
- 199 inline-math surfaces, four bracket-display pairs, three `equation`
  environments, and three `align*` environments;
- nine `tikzcd` diagrams, 47 diagram-arrow commands, and 21 item commands;
- identical mathematical-command censuses: nineteen `\varinjlim`, 39
  `\varprojlim`, 26 `\Hom`, ten `\Obj`, seven `\Mor`, thirteen `\prod`, one
  `\coprod`, ten `\Ker`, four `\Coker`, and five `\rightiso` occurrences.

Every formula, diagram, environment, stable label, reference, and index entry
was inspected against the authority. Mathematical differences are limited to
the six declared, justified repairs below. The source span contains 1,642 Han
code points; the Indonesian target contains zero. There is no untranslated
Chinese residue in the admitted span.

## Declared source corrections

1. `O013-LI-U017-COR-001` - **wrong diagram index at authority line 1525**.
   The leg whose domain is `F\alpha(i)` is labelled upstream as
   `F(\alpha(j) \to \varinjlim \alpha)`, which is incompatible with that
   domain. The exact target form is
   `F(\alpha(i) \to \varinjlim \alpha)`; the separate leg from
   `F\alpha(j)` correctly retains index `j`.
2. `O013-LI-U017-COR-002` - **wrong coproduct description at authority line
   1554**. In `\cate{Ab}`, an arbitrary small coproduct is the direct sum,
   not the direct product; authority line 1513 and
   `\ref{prop:monoid-direct-sum}` already give the correct construction. The
   exact target statement is
   `koproduk dalam $\cate{Ab}$ adalah jumlah langsung grup abelian`.
3. `O013-LI-U017-COR-003` - **invalid object-set variable at authority line
   1585**. Here `i` is not a category, whereas the entire diagram is indexed
   by category `I`. The target therefore uses the exact form
   `j \in \Obj(I)` instead of `j \in \Obj(i)`.
4. `O013-LI-U017-COR-004` - **ill-typed Hom categories at authority lines
   1588-1589**. Both `F(\cdot)` and `\beta(j)` are objects of
   `\mathcal{C}_2`; the two upstream subscripts `\mathcal{C}_1` cannot type
   these Hom-sets. Both target occurrences are exactly
   `\Hom_{\mathcal{C}_2}(F(\cdot), \beta(j))`.
5. `O013-LI-U017-COR-005` - **false surjectivity styling at authority lines
   1589-1590**. A projection from a limit to a component need not be
   surjective because an arbitrary component morphism need not extend to a
   compatible cone. The two target projections therefore use ordinary
   `\arrow[r]`, not `\arrow[twoheadrightarrow,r]`; their endpoints and
   commutative-diagram positions are otherwise unchanged.
6. `O013-LI-U017-COR-006` - **wrong target-category limit at authority line
   1547**. Since `\beta: I^\text{op} \to \mathcal{C}_1`, the expression
   `\varprojlim \beta` is not the limit whose existence is asserted in
   `\mathcal{C}_2`. Preservation supplies the limit of the image diagram. The
   exact target form is `\varprojlim (F\beta)`.

All six repairs are minimal, locally checkable, mathematically necessary, and
recorded as target-side corrections rather than silently attributed to the
source author.

## Semantic and fluency review

The Indonesian span was read continuously rather than assessed only through
token counts. It maintains a formal graduate-mathematics register, clear
antecedents, correct quantifier scope, and stable terminology across the
definitions, Freyd argument, construction theorem, pullback/pushout material,
examples, limit-preservation discussion, and adjoint-functor proof.

Four final clarity refinements were verified in the integrated target:

- both halves of the completeness definition explicitly repeat
  `untuk setiap kategori kecil $I$`, so the complete and cocomplete
  quantifiers cannot be read with different scope;
- the Freyd proof calls `\mathcal{C}` a `kategori praterurut`, while retaining
  `himpunan praterurut` for the underlying `(P, \leq)`;
- the group coequalizer description supplies the required copula,
  `dengan $N$ adalah subgrup normal ...`; and
- `keberadaan ... dapat direduksi menjadi masalah representabilitas` replaces
  an unnatural literal calque without changing the mathematical reduction.

These are prose and scope improvements only. They do not alter protected
identifiers, formulas, diagrams, environments, references, or exercise
boundaries.

## Indonesian terminology evidence

The governing terminology record is
`qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md`, 16,797 bytes,
SHA-256
`ec6fdf9bee950fd7ba7ce48a779b5da0475f8cb6cd29489c963c0b01c1f03333`.
Its bounded official arXiv search found no suitable Indonesian same-field TeX
source and therefore used the disclosed Indonesian PDF fallback rather than
inventing evidence. The official UNDIP and UGM witnesses have frozen SHA-256
identities
`611b78c88407037489f22814bf054e00ff0f283c702a06082a3a583e9ab35fcb`
and
`4099c3d8aff59e723470f69b4d152b037261bc26d54ef74f1365377f05c25834`.
They directly support the core register `kategori`, `fungtor`, and the
product/koproduct context; they are not represented as direct attestation for
every specialized limit-theory term.

The Unit 017 adjudication adds and consistently applies sixteen controlled
rows: `kelengkapan`, `kategori lengkap`, `kategori kolengkap`, `produk kecil`,
`koproduk kecil`, `produk serat`, `fibered product`, `tarik balik (pullback)`,
`koproduk serat`, `dorong keluar (pushout)`, `diagram Kartesius`,
`mempertahankan limit`, `produk langsung`, `jumlah langsung`, `produk bebas`,
and `kernel selisih`. Their controlling glossary is
`00_control/TERMINOLOGY.id-ID.csv`, 31,697 bytes, SHA-256
`4cdef514de666a002681f593cb5578322dc19c3e9101da20f2caabc415d4cd08`.
The target uses these forms consistently and does not overstate the scope of
the external terminology witnesses.

## Rights, authorship, and production provenance

Wen-Wei Li remains the source author, and all source and human-contributor
credits remain separate and intact. The source and Indonesian derivative are
under CC BY 4.0 with attribution preserved. This independent translation and
its corrections do not imply endorsement by Wen-Wei Li, UNDIP, UGM, Pusat
Bahasa, ITB, or any cited human contributor.

Production provenance is recorded separately from authorship and human credit
with the exact model identification `OpenAI Codex gpt-5.6-sol, Ultra`.

## Review disposition

**PASS - Unit 017 source/translation integration is admitted for the next
deterministic build and backend gates.** No substantive mismatch, missing
mathematics, untranslated residue, boundary intrusion, or undisclosed source
repair was found. Any future mismatch in the frozen identities or protected
topology above invalidates this pass and must fail closed pending a fresh
bounded comparison.
