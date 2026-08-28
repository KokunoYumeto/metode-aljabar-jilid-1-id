# O013-LI-U043 Translation Review — 2026-08-25

Status: **PASS**. This is an isolated candidate review. No canonical source, glossary, control, backend, reader, publication, or Git state was changed.

## Scope, identities, and durable cursor

- Frozen authority: `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex` — 1,382 records, 122,998 bytes, SHA-256 `e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143`.
- Inclusive source span: records 1184–1318. The exact LF-normalized slice has 135 records, 11,304 bytes, SHA-256 `2596fa0de36082ae7bc6800f25ad95d7bda419f84e2ab9aace686933227cbaf8`.
- Boundary proof: record 1183 is blank; record 1184 opens `\section{对称多项式入门}\label{sec:symmetric-poly}`; record 1318 ends the section with its `Mac95` reading reference; record 1319 is blank; records 1320–1321 are a decorative comment and blank separator; record 1322 opens `\begin{Exercises}`.
- Candidate: `build/unit-043-candidate/chapter5-symmetric-polynomials-id.tex` — 135 records, 13,664 bytes, SHA-256 `c2a2b1a1d86a22bf1474ecb82c021d746104502d5cf6f4cf25eecad992c20668`.
- Checker: `scripts/check_unit_043_candidate.py` — 521 records, 20,294 bytes, SHA-256 `d2bdf313dc7411c6af6dcf14dcee061bddfba026ef7d6698a7fdf4f9e65e57ac`.
- Durable next isolated source cursor: `chapter5.tex:1322`, the Chapter 5 exercise block. The separator at records 1319–1321 is outside Unit 043.

## Fidelity and language review

The candidate translates the complete symmetric-polynomials section into formal, natural id-ID. It covers the symmetric-group action and invariant subring; coefficient-orbit characterization; monomial symmetric polynomials indexed by integer partitions; Young diagrams and conjugation; dominance and lexicographic orders; elementary symmetric polynomials; the unitriangular transition between the monomial and elementary bases; the fundamental theorem of symmetric polynomials for rings and rational-function fields; the discriminant criterion for repeated roots; power sums; and Newton's formulas through their generating-series proof. Every definition, proposition, lemma, theorem, example, proof, list item, display, diagram/tableau command, citation, index entry, and disabled comment in the source span is represented.

Controlled admitted terminology is respected for `gelanggang polinomial`, `grup simetris`, `medan`, `modul bebas`, `sifat universal`, `isomorfisme`, `partisi`, `urutan leksikografis`, and `himpunan terurut parsial (poset)`. Section-specific terminology is internally consistent: `polinomial simetris`, `diagram Young`, `konjugat`, `urutan dominasi`, `polinomial simetris elementer`, `matriks segitiga unipoten`, `diskriminan`, `akar ganda`, `jumlah pangkat`, `Rumus Newton`, and `deret pembangkit`.

The residue audit found zero Han characters, zero Chinese punctuation residue, zero placeholder markers, zero forbidden control characters, and no uncontrolled `cincin`, `lapangan`, `kelompok`, `variabel`, or `funktor`. The Indonesian exposition preserves the distinction among a partition's length, a Young diagram's height, and the largest part; it also keeps the invariant-ring and rational-function-field assertions separate.

## Mathematics, identifiers, and TeX topology

- Mathematical zones: 190/190 identical after nine protected localization substitutions and two declared corrections.
- Environment markers: 40, comprising 20 balanced begin/end pairs. Begin census: `align*` 2, `equation*` 1, `definition` 2, `compactdesc` 1, `gather` 1, `proposition` 1, `proof` 4, `gather*` 1, `lemma` 1, `ytableau` 1, `theorem` 2, `example` 1, `cases` 1, and `compactitem` 1.
- Ordered labels (7): `sec:symmetric-poly`, `eqn:dominance-order`, `prop:dominance-lex-order`, `def:elementary-symm-poly`, `prop:m_lambda-e_lambda`, `prop:fund-thm-symmetric-poly`, and `eg:polynomial-discriminant`.
- Ordered references (5): `sec:polynomial-ring`, `def:free-module`, `eqn:dominance-order`, `prop:m_lambda-e_lambda`, and `prop:dominance-lex-order`.
- Citation: exactly one, `Mac95`, retained in source order.
- Index commands: seven, all live and localized without changing sort streams.
- Items: four. Display-math delimiter pairs: 14. Disabled inline comments: two, at authority/candidate records 1270 and 1307.
- Diagram topology: four `\ydiagram` commands, one balanced `ytableau`, and 12 `\none` placeholders. No external asset, `\input`, `\include`, URL, or TikZ arrow occurs.
- Exercise, problem, hint, answer, and solution environments: zero. Chapter 5 exercises begin at the next isolated cursor and are not silently absorbed into this section.
- The checker compares ordered environment, label, reference, citation, index, and TeX-command streams; per-record brace, math-delimiter, alignment, quote, and comment signatures; exact protected mathematics; terminology state; source/candidate byte identities; and both outer boundaries.

## Declared source corrections

1. **O013-LI-U043-COR-001** — authority 1199 / candidate 16: the source condition `1 \leq \lambda_i \leq n` is repaired to the index range `1 \leq i \leq r`. Authority 1195 already says that the `\lambda_i` are arbitrary positive integers and only the number of parts satisfies `r \leq n`. Retaining the source bound would make authority 1202 false: for `n=1`, the symmetric polynomial `X_1^2` could not be represented by any admitted `m_\lambda`, because the source would permit only the part `\lambda_1=1`. The correction preserves arbitrary positive parts while specifying the intended indexing range.
2. **O013-LI-U043-COR-002** — authority 1222 / candidate 39: the lexicographic-order condition `0 \leq i < k` is repaired to `1 \leq i < k`. Partitions in the section are indexed from 1, so the source condition invokes undefined entries `\mu_0` and `\lambda_0`; authority 1224's zero-padding convention applies only beyond the number of rows and does not define index 0. The repaired range is the standard preceding-coordinate condition and is exactly what the proof at authority 1231 uses.

No other high-confidence source correction was made. In particular, the non-strict symbol `\preceq` in the proposition is read as the reflexive closure of the strict lexicographic relation `\prec`, and the zero-padding convention, conjugate-partition length condition, unitriangular-basis argument, discriminant identity, and Newton signs are mathematically coherent as written.

## Rights, provenance, and deterministic result

The frozen Chapter 5 header attributes the source to Wen-Wei Li and licenses it under CC BY 4.0. This candidate is an AI-assisted Indonesian translation prepared with OpenAI Codex gpt-5.6-sol, Ultra, on instruction dated 2026-08-25; it is not an official or endorsed translation. The bounded section uses only source TeX diagram commands and contains no external media asset.

Final verification: `python scripts/check_unit_043_candidate.py` returned **PASS** twice consecutively with no intervening edit. Both runs reported the exact identities and counts above, nine protected substitutions (seven indexes plus two mathematical-text localizations), two proven corrections, the bound CC BY 4.0 header, and next isolated cursor `chapter5.tex:1322`.
