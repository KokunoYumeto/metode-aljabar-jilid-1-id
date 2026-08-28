# O013-LI-U042 Translation Review — 2026-08-25

Status: **PASS**. This is an isolated candidate review. No canonical source, glossary, control, backend, reader, publication, or Git state was changed.

## Scope, identities, and durable cursor

- Frozen authority: `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex` — 1,382 records, 122,998 bytes, SHA-256 `e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143`.
- Inclusive source span: records 958–1182. The exact LF-normalized slice has 225 records, 22,981 bytes, SHA-256 `2e3758fa4b4175eeba5969159a89ccb40895c173c12699a8c2211e68a1e94b2a`.
- Boundary proof: record 957 is blank; record 958 opens `\section{唯一分解性}\label{sec:UFD}`; record 1182 closes the last proof; record 1183 is blank; record 1184 opens `\section{对称多项式入门}\label{sec:symmetric-poly}`.
- Candidate: `build/unit-042-candidate/chapter5-unique-factorization-id.tex` — 225 records, 29,674 bytes, SHA-256 `a76cf155134f6ae7a4a5e7a94cd9a5424ac83e277264f8d4228bdc5a2ed4b41a`.
- Checker: `scripts/check_unit_042_candidate.py` — 573 records, 21,414 bytes, SHA-256 `583bd404e4ff529c2231f287a3451a808d3f85144383d02fddfcecb65699e198`.
- Durable next source cursor: `chapter5.tex:1184`; Unit 043 must begin at that section heading, not at the blank separator.

## Fidelity and language review

The candidate translates the complete section into formal, natural id-ID: divisibility modulo units and greatest common divisors; irreducibles, prime elements, unique factorization, and ACCP; localization and principal ideal domains; Euclidean domains; Gaussian integers, quadratic integer rings, and Fermat's two-squares theorem; the strict Euclidean/PID/UFD inclusions; the rational-root test and integral closedness; coefficient valuations, polynomial content, and Gauss's lemma; polynomial and Laurent UFDs; a cyclotomic gcd identity; and Eisenstein's criterion. Every definition, proposition, lemma, theorem, example, remark, proof, list item, display, citation, inline comment, and connective argument in the source span is represented. No semantic omission or unauthorized addition remains beyond the seven declared corrections below.

Controlled admitted terminology is respected for `gelanggang`, `medan`, `grup`, `monoid`, `aljabar`, `homomorfisme`, `isomorfisme`, `gelanggang polinomial`, `monoid hasil bagi`, `himpunan terurut parsial (poset)`, `supremum`, `himpunan terurut baik`, and `grup siklik`. Section-specific terminology is consistent: `daerah faktorisasi unik`, `unsur tak tereduksi`, `unsur prima`, `pembagi persekutuan terbesar`, `relatif prima`, `syarat rantai menaik`, `daerah ideal utama`, `daerah Euklides`, `tertutup integral`, `konten`, `Lema Gauss`, and `Kriteria Eisenstein`.

The residue audit found zero Han characters, zero Chinese punctuation residue, zero placeholder markers, zero forbidden control characters, and no uncontrolled `cincin`, `lapangan`, `kelompok`, or `funktor`.

## TeX, identifiers, and topology

- Mathematical zones: 464/464 identical after 17 protected localization substitutions and seven declared corrections.
- Environment markers: 78, comprising 39 balanced begin/end pairs. Begin census: `definition` 2, `itemize` 1, `proposition` 3, `compactitem` 3, `proof` 10, `inparaenum` 2, `lemma` 3, `theorem` 4, `example` 4, `equation` 1, `cases` 1, `compactdesc` 1, `remark` 1, `compactenum` 2, `gather*` 1.
- Ordered labels (15): `sec:UFD`, `def:UFD`, `prop:UFD-localization`, `prop:ACC-PID`, `prop:PID-UFD`, `prop:Euclidean-ring`, `eg:polynomial-PID`, `eg:Gauss-integers`, `eqn:quadratic-integer`, `prop:sum-squares`, `prop:Gauss-lemma`, `rem:Gauss-lemma-monic`, `prop:polynomial-UFD`, `eg:gcd-cyclotomic`, `prop:Eisenstein-criterion`.
- Ordered references (16): `eg:Gauss-integers`, `def:max-sup`, `def:UFD`, `prop:localization-units`, `prop:localization-ideals`, `def:ACC-DCC-mod`, `prop:ACC-PID`, `prop:maximal-implies-prime`, `def:well-ordered`, `prop:Euclidean-ring`, `sec:integrality-finiteness`, `eg:polynomial-PID`, `prop:Gauss-lemma`, `prop:polynomial-UFD`, `prop:UFD-localization`, `prop:polynomial-UFD`.
- Ordered citations (2): `Go85`, `Wil73`.
- Index commands: 8 raw, comprising seven localized live entries and the localized disabled entry in the preserved inline comment at authority 1106 / candidate 149.
- Items: 25. Display-math delimiter pairs: 18. Inline comments: 1. Diagrams, arrows, and source asset pointers: 0. Exercise, problem, hint, answer, and solution environments: 0.
- The checker compares ordered command streams and per-record environment/identifier/brace/TeX-quote/comment signatures, in addition to exact protected mathematics and pinned byte identities.

## Declared source corrections

1. **O013-LI-U042-COR-001** — authority 1053 / candidate 96: squarefree `D` is restricted from `D\in\mathbb Z\setminus\{0\}` to `D\in\mathbb Z\setminus\{0,1\}`. Under the standard convention, `1` is squarefree, but `\mathbb Q(\sqrt1)=\mathbb Q` is not quadratic; moreover, authority 1056 would become the false direct-sum notation `\mathbb Z\oplus\mathbb Z\cdot1`.
2. **O013-LI-U042-COR-002** — authority 1074 / candidate 117: the dangling Gaussian unit `u` is completed by `\bar{\mathfrak p}=u\mathfrak p`. Equality of the two classes modulo `\mathbb Z[i]^\times` is exactly equivalent to this relation for some unit. Solving it for `u\in\{\pm1,\pm i\}` yields the axis and diagonal cases used immediately afterward.
3. **O013-LI-U042-COR-003** — authority 1114 / candidate 157: the unused phrase “for every irreducible `p`” is removed from the assertion about the global content `c`. The displayed conclusion is `c(fg)=c(f)c(g)`, while the proof checks every valuation `v_p` in order to prove multiplicativity of that single global function. If the quantifier were retained as written, it would have to govern `c_p`, not the displayed `c`.
4. **O013-LI-U042-COR-004** — authority 1117 / candidate 160: representatives of the content classes are explicitly chosen before writing `f=c(f)f^\flat` and `g=c(g)g^\flat`. Authorities 1109–1111 define `c(f)` and `c(g)` as cosets in `K^\times/R^\times`, which cannot literally multiply polynomials until representatives in `K^\times` have been selected.
5. **O013-LI-U042-COR-005** — authority 1127 / candidate 170: content is explicitly extended to multivariable polynomials by taking the minimum valuation over all coefficients. Authorities 1106–1111 define `c` only on `K[X]`, but authority 1130 applies `c(f)` to `K[X_1,\ldots,X_n]`; the stated extension makes that classification well-typed and is the one used by the induction.
6. **O013-LI-U042-COR-006** — authority 1151 / candidate 194: the gcd claim is qualified to the case in which `X^a-1` and `X^b-1` are nonzero; the ideal identity remains unconditional. This section defines gcds in `(R\setminus\{0\})/R^\times`. The allowed choice `X=1` makes both elements zero, so the unqualified source claim has no meaning under its own definition.
7. **O013-LI-U042-COR-007** — authority 1165 / candidate 208: `k\le n` is repaired to `1\le k\le n`. With `k=n=0`, `R=\mathbb Z`, `p=2`, and `f=1`, all three source bullets hold, but the unit polynomial has no irreducible factor and is not irreducible in `\mathbb Q[X]`. The proof at authorities 1172–1174 also requires `p\mid a_0`, which follows from the first bullet only when `k\ge1`.

No other high-confidence source correction was made.

## Rights, provenance, and deterministic result

The frozen Chapter 5 header attributes the source to Wen-Wei Li and licenses it under CC BY 4.0. This candidate is an AI-assisted Indonesian translation prepared with OpenAI Codex on instruction dated 2026-08-25; it is not an official or endorsed translation. The bounded section contains no external or diagram asset.

Final verification: `python scripts/check_unit_042_candidate.py` returned **PASS** twice consecutively with no intervening edit. Both runs reported the exact identities and counts above, 17 protected substitutions (eight index localizations plus nine mathematical-text localizations), seven proven corrections, the bound CC BY 4.0 header, and next cursor `chapter5.tex:1184`.
