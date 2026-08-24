# Unit 024 translation/source review — 2026-08-24

## Verdict

**PASS.** The isolated id-ID candidate is a complete, source-order translation
of the entire Chapter 3 exercise block and therefore of the exact physical
tail of frozen `chapter3.tex`. Every exercise, nested item, hint, formula,
diagram, environment, reference, and index entry was compared continuously
against authority lines 873–911. One high-confidence mathematical source
defect was repaired transparently and is pinned below.

Model provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.

No canonical integration, glossary, backend, control, build-reader, README,
Git, web, publication, or other-task operation was performed.

## Frozen boundary, EOF, and identities

Authority:
`authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`

- Full authority: 911 LF records, 75,571 bytes, SHA-256
  `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
- Prefix, lines 1–872: 70,617 bytes, SHA-256
  `8a0203bdb81b7384e7b84c9ccfbb37cdd57bc17f332061db707a9054fa7f58e9`.
- Included Unit 024 span, lines 873–911: 39 LF records, 4,954 bytes,
  SHA-256
  `2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857`.
- Suffix after line 911: exactly zero bytes, SHA-256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Included line 873 (including LF): 18 bytes, SHA-256
  `0f80848f05d5d2ea79e191700984eea0aec0f85dfcf13ac2ad2c23cb282ae699`;
  signature `\begin{Exercises}`.
- Included line 911 (including LF): 16 bytes, SHA-256
  `5737357e36540b3b9a76e967b17c118a49687b3fc513560a3231615ef0ef771a`;
  signature `\end{Exercises}`.

The authority is LF-terminated immediately after line 911. There is no line
912, hidden suffix, or subsequent Chapter 3 content. Unit 024 therefore closes
the physical authority file rather than stopping at a merely inferred section
boundary.

Candidate:
`build/unit-024-candidate/chapter3-exercises-id.tex`

- 39 LF records, 6,042 bytes, SHA-256
  `686dc8c4beb4d1073c4cc0238f42cd9955f4ca3d297850b2b3c7900376d97f56`.
- Its first and last records are byte-identical to the authority
  `\begin{Exercises}` and `\end{Exercises}` records above.
- It contains all eight top-level exercises, both hints, and all three nested
  items in the Drinfeld-center construction.

Checker:
`scripts/check_unit_024_candidate.py`

- 18,433 bytes, SHA-256
  `c5513be88ab4ee02f6a419a6921197da4a0ddb8474f07030c31df6f750fcc397`.
- `python -B scripts/check_unit_024_candidate.py`: PASS.
- An unexpected positional argument is rejected with exit status 1; neither
  pinned input path can be overridden.

## Continuous semantic review

The translated exercise sequence is complete:

1. Catalan-number enumeration of the parenthesizations of iterated tensor
   products;
2. commutativity of `\End(\munit)` under composition, with the Kelly-lemma
   hint intact;
3. the ordinal-sum monoidal structure on finite totally ordered sets and
   order-preserving maps;
4. the unique objectwise order isomorphism between the two ordinal sums and,
   after the correction below, the necessary naturality test;
5. the Yang--Baxter equation, its component form, its origin from a braiding,
   the quantum-integrable-systems remark, and the parameterized Hecke-type
   solution with all three cases;
6. the complete Drinfeld-center construction, including its objects,
   half-braiding diagram, morphism condition, tensor product, unit, induced
   braiding, and interpretation as a categorified center;
7. comparison of `\cate{Ab}`-enrichment with the general theory; and
8. the comma-category projections and the displayed 2-cell in `\cate{Cat}`.

All hypotheses, quantifiers, inequality directions, tensor-factor orders,
matrix-coefficient indices, summation indices, Hecke relation signs, diagram
orientations, and source/target types were retained. The Indonesian is formal
and consistent with the lane corpus. No exercise, subpart, hint, or displayed
condition was omitted.

## Structure, mathematics, and topology audit

- Exact one-to-one physical topology: 39 authority records and 39 candidate
  records. The only blank or whitespace-only records occur at relative lines
  11 and 19 in both files; relative line 11 retains the source indentation.
- Environments: seven balanced pairs / 14 position-identical ordered events:
  `hint` 2, `tikzcd` 2, and one each of `Exercises`, `cases`, and `itemize`.
- Exercise topology: eight top-level exercises and three `itemize` subitems,
  for 11 `\item` calls at identical relative lines
  `2, 3, 4, 5, 6, 20, 22, 27, 29, 32, 33`.
- Hints: two, both inline at relative lines 2 and 3; their environment
  boundaries and mathematical contents are preserved.
- Labels: none in either span.
- Cross-references: four `\ref` calls, position- and target-identical:
  `prop:Kelly` at relative line 3, `prop:YBE-cat-strict` at line 10,
  `eg:Ab-cat` at line 32, and `def:comma-category` at line 33. There are no
  `\eqref` calls or citations.
- Index entries: one, `YBE`, at identical relative line 18.
- TeX commands: 248 in each file, with identical per-line command multisets.
- Inline mathematics: 69 occurrences, value- and position-identical in the
  two spans.
- Bracket displays: six, byte-identical. They contain the operator
  Yang--Baxter equation, its coefficient equation, the three-case `R`, the
  Drinfeld-center coherence diagram, its morphism condition, and the comma
  category 2-cell.
- Diagram topology: two byte-identical `tikzcd` blocks and eight `\arrow`
  calls at identical lines. There are no TikZ nodes, paths, edges, draws, or
  coordinates.
- Unescaped braces balance at 83 opening / 83 closing in each file.
- Han characters: 575 in the frozen authority span and 0 in the candidate.
- Neither source nor candidate contains a TeX comment in this span.

## Explicit mathematical source correction

### O013-LI-U024-COR-001 — ordinal-sum symmetry is not natural

Authority line 877 (candidate-relative line 5) asks the learner first to show
that there is a unique order isomorphism

```tex
c(\sigma, \tau): \sigma \sqcup \tau \rightiso \tau \sqcup \sigma
```

and then to prove that these isomorphisms make
`(\cate{On}_f, \sqcup, c)` symmetric monoidal. The first statement is true:
the two finite total orders have the same cardinality and therefore a unique
order isomorphism. The second statement is false because the resulting family
is not natural for arbitrary order-preserving maps.

A minimal counterexample uses finite chains identified by their ranks. Take
`\sigma=\sigma'=\tau'=\mathbf 1`, `\tau=\mathbf 2`, let
`f:\mathbf 1\to\mathbf 1` be the unique map, and let
`g:\mathbf 2\to\mathbf 1` be constant. In the naturality equation

```tex
c_{\sigma',\tau'}(f\sqcup g)
  = (g\sqcup f)c_{\sigma,\tau},
```

the left composite sends source ranks `1,2,3` to target ranks `1,2,2`,
whereas the right composite sends them to `1,1,2`. Thus the composites differ.

The candidate preserves the objectwise-isomorphism task but replaces the
impossible proof demand with:

> Apakah keluarga isomorfisme ini membuat
> `(\cate{On}_f, \sqcup, c)` menjadi kategori monoidal simetris? Jika tidak,
> berikan contoh tandingan terhadap naturalitasnya.

This keeps the exercise mathematically meaningful and directly exposes the
failed axiom. The checker pins both the authority claim and the corrected
candidate sentence. No other source correction was made.

## Terminology consistency

The only terminology evidence consulted was the frozen lane glossary and
already translated lane corpus; no web or external source was used. At review
time, `00_control/TERMINOLOGY.id-ID.csv` was 39,866 bytes with SHA-256
`45e7b1500533e4fa8a8a257efe2982261704bd00a27f056030112141e5ed0efe`.
It directly admits:

- `totally ordered set` → `himpunan terurut total`;
- `order-preserving map` → `peta pelestari urutan`;
- `monoidal category` → `kategori monoidal`;
- `symmetric monoidal category` → `kategori monoidal simetris`;
- `braiding` → `struktur kepang`;
- `strict monoidal category` → `kategori monoidal ketat`;
- `Yang--Baxter equation` → `persamaan Yang--Baxter`;
- `enriched category` → `kategori diperkaya`;
- `comma category` → `kategori koma`;
- `2-cell` → `2-sel`.

The candidate additionally uses transparent established forms `bilangan
Catalan`, `sistem integrabel kuantum`, and `pusat Drinfeld`. No glossary or
control file was edited.

## Terminal Chapter 3 cursor

Unit 024 ends at authority line 911, the physical EOF of frozen
`chapter3.tex`. Consequently no untranslated Chapter 3 record remains after
this candidate. The next corpus-level source-order decision belongs to the
integrating task; this isolated unit did not inspect or modify another chapter.
