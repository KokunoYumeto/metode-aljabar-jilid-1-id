# O013-LI-U039 translation review — 2026-08-25

## Decision

PASS for the isolated translation candidate. The unit is the complete contiguous
section `\section{间奏: Möbius 反演}\label{sec:Mobius}` at frozen authority
`chapter5.tex` lines 463--608. Authority line 462 is blank, line 609 is the
closing blank boundary, and the next source cursor is line 610,
`\section{环的极限与完备化}\label{sec:ring-limits}`.

## Frozen identities

| Artifact | Records | Bytes | SHA-256 |
|---|---:|---:|---|
| `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex` | 1,382 | 122,998 | `e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143` |
| normalized-LF authority slice, lines 463--608 inclusive | 146 | 11,278 | `2978911692e6f99187ad4cb63bdce610a00eacf7267af11646a1ca2c014ecb53` |
| `build/unit-039-candidate/chapter5-mobius-inversion-id.tex` | 146 | 13,976 | `5ed878a2ac0261b613cab8d050adc5130cf880e829736b80b24d696ba1a4c8a7` |
| `scripts/check_unit_039_candidate.py` | 507 | 19,408 | `a70f37086a66e10fac2a08a0faa9083d07c163207d7db6c4da2101a30bc763b6` |

All byte counts are UTF-8 byte counts. The authority-slice identity is formed by
joining the 146 selected records with LF and one final LF. The candidate is
strict UTF-8, BOM-free, CR-free, and ends in exactly one LF.

## Semantic and language review

The candidate translates the whole section into formal, natural id-ID: locally
finite posets, incidence algebras, the Möbius function and inversion formula,
the chromatic-polynomial example, finite and restricted products, classical
number-theoretic Möbius inversion, and Euler's totient identities. No source
claim, proof step, example, diagram prose, citation, or terminal paragraph is
omitted. The controlled admitted forms used include `gelanggang`, `medan`,
`himpunan terurut parsial (poset)`, `grup abelian`, and `unsur identitas`.
Standard mathematical Indonesian forms used outside the controlled glossary
include `aljabar insidensi`, `fungsi Möbius`, `produk terbatas`, `bebas kuadrat`,
and `fungsi rasional`.

The candidate contains zero Han characters, zero Chinese punctuation marks,
zero forbidden control or invisible characters, and zero placeholder tokens.

## TeX, mathematical, and identifier topology

- 144 ordered mathematical zones agree exactly after 16 declared textual
  localizations, one declared index localization, and the two corrections
  below. No mathematical symbol, operator, delimiter, or relation is otherwise
  changed.
- There are 58 environment markers, forming 29 ordered begin/end pairs. Begin
  census: `align*` 4, `cases` 4, `center` 1, `compactitem` 2,
  `definition` 1, `equation` 1, `equation*` 1, `example` 3, `gather` 2,
  `gather*` 1, `gathered` 1, `inparaenum` 1, `lemma` 2, `proof` 3,
  `proposition` 1, and `tikzpicture` 1.
- The eight labels, in order, are `sec:Mobius`, `eqn:incidence-ring-op`,
  `prop:incidence-ring-inv`, `eqn:Mobius-eq`, `prop:Mobius-inversion`,
  `prop:Mobius-prod`, `eg:Mobius-classical`, and `eqn:Euler-phi-sum`.
- The 12 ordered references are `sec:algebra-def`,
  `eqn:incidence-ring-op`, `prop:incidence-ring-inv` twice,
  `eqn:Mobius-eq`, `prop:Mobius-inversion`, `eqn:Mobius-eq` three more
  times, `prop:Mobius-inversion`, `prop:Mobius-prod`, and
  `prop:Mobius-inversion`.
- Citation keys are exactly `Stan09`, then `Sok05`.
- Five indexes are preserved: four localized main-index entries
  (`pianxuji!lokal berhingga`, `Kronecker@delta Kronecker`,
  `Mobius@fungsi Möbius`, and
  `Mobius@inversi Möbius (Möbius inversion)`) plus the unchanged symbol-index
  entry `\index[sym1]{mu@$\mu$}`.
- Diagram/content census: one `tikzpicture`, three nodes, one exact
  `\includegraphics[width=185pt]{Lanzhou.png}`, one preserved Wikimedia Commons
  link, and eight `\item` commands. There are no exercises, hints, solutions,
  or comments in this source slice or candidate.

## Declared high-confidence source corrections

### O013-LI-U039-COR-001 — authority line 566

Authority wording places the condition
`$x_i, y_i \neq \mathring{x}_i$` on the finitely many relevant indices. Read
literally, that requires both coordinates to differ from the basepoint and
incorrectly omits an index at which exactly one coordinate differs. If
`S_x={i:x_i\neq\mathring{x}_i}` and
`S_y={i:y_i\neq\mathring{x}_i}`, restricted-product membership makes both
sets finite, and the proof reduces over their finite union. The exact condition
is therefore
`$(x_i,y_i) \neq (\mathring{x}_i,\mathring{x}_i)$`, which the candidate uses.
No surrounding formula or proof topology changes.

### O013-LI-U039-COR-002 — authority line 598

The authority prose calls `\Q(X)^\times` nonzero rational polynomials. The
notation `\Q(X)` denotes the rational-function field; the polynomial ring would
be `\Q[X]`. The candidate therefore renders this as `fungsi rasional tak nol
$\Q(X)^\times$`. The displayed notation and group structure remain unchanged.

## Rights and provenance

The frozen Chapter 5 authority begins with the six-line CC BY 4.0 notice for
the Chinese source. The candidate preserves the source's `Lanzhou.png`
inclusion, explicit Wikimedia Commons file URL, and in-diagram attribution; no
separate asset-license reclassification is made here. This is an AI-assisted
Indonesian translation prepared by OpenAI Codex on user instruction on
2026-08-25. It is not represented as an official or author-endorsed
translation.

## Deterministic validation

Final command, run twice consecutively after freezing all three Unit 039
artifacts:

```text
python scripts/check_unit_039_candidate.py
```

Recorded result: PASS / PASS. Each run binds the exact authority, slice, and
candidate identities above; checks section boundaries, per-record TeX topology,
ordered environments/labels/references/citations/indexes, all 144 protected
mathematical zones, the diagram and attribution, controlled terminology,
language residue, and both declared correction identities. The next source
cursor is `chapter5.tex:610`.
