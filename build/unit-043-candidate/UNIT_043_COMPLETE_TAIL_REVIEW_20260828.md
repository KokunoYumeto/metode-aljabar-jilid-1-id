# O013-LI-U043 Complete Chapter 5 Tail Review — 2026-08-28

Status: **PASS** as an isolated translation candidate. No canonical source,
shared glossary/control, backend, reader, Git, or publication state was changed.

## Scope and exact identities

- Frozen authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex`,
  1,382 records, 122,998 bytes, SHA-256
  `e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143`.
- Complete remaining span: authority records 1184–1382 inclusive, 199 records,
  18,389 normalized-LF bytes, SHA-256
  `755bb123580e5f50e0fff03175117190f1490e4e41ffaf2a6e0df2df9190565f`.
- Final candidate:
  `build/unit-043-candidate/chapter5-symmetric-polynomials-exercises-id.tex`,
  199 records, 22,558 bytes, SHA-256
  `5318c2433ca4784d1fbf64a86989bd3a3a007a10ed00cb6e0ae7f46a37122a2d`.
- The already checked section candidate for records 1184–1318 is preserved
  byte-for-byte as the first 135 records: 13,664 bytes, SHA-256
  `c2a2b1a1d86a22bf1474ecb82c021d746104502d5cf6f4cf25eecad992c20668`.
- The new records 1321–1382 exercise fragment is 62 records, 8,851 bytes,
  SHA-256
  `e642c19e0f7c79e55b3718a201ea7f25528c9cc4adbdf5b881180c2bb4c31475`.
  Candidate records 136–138 preserve authority 1319's blank, authority 1320's
  decorative comment, and authority 1321's blank before `Exercises`.
- Isolated checker:
  `build/unit-043-candidate/check_unit_043_candidate.py`, 12,793 bytes,
  SHA-256
  `85cacbd1857431cfa1ec7ba183366449d103cc858740940df9196c4ee7c5572a`.
- Candidate-only terminology delta: 22 CSV records, 2,978 bytes, SHA-256
  `442c80aeeb27bbbae9541a59f093d455f21bd98d15b8720926f489981966f767`.

The boundary begins with
`\section{对称多项式入门}\label{sec:symmetric-poly}` at authority 1184 and
ends with `\end{Exercises}` at authority 1382. The next source-order cursor is
`chapter6.tex:1`.

## Completeness and fidelity

The candidate contains the complete symmetric-polynomial section and the full
Chapter 5 exercise block. It preserves the symmetric-group action, invariant
ring, monomial and elementary bases, Young diagrams, dominance and
lexicographic orders, the fundamental theorem, discriminant, power sums,
Newton formulas, every proof and disabled comment, and all 22 top-level
exercises with their nested parts and 11 hints.

The deterministic topology census is 72 environment markers (36 balanced
pairs), seven labels, 14 ordered references, two citations, eight localized
index commands, 35 `item` tokens, one `Exercises` pair, and 11 balanced hint
pairs. The 35 items comprise four section list items and 31 exercise-block
items (22 top-level and nine nested). There are no answer or solution
environments. Mathematical content is preserved record by record after the two
declared corrections; display and mathematical-environment content is exact,
and inline mathematical zones are exact as per-record multisets so natural
Indonesian word order does not falsify the check.

The candidate has zero Han characters, Chinese punctuation, placeholders,
forbidden controls, or uncontrolled `cincin`, `lapangan`, `kelompok`,
`variabel`, `funktor`, or superseded `kompletisasi` residue.

## Declared source corrections

1. **O013-LI-U043-COR-001 — authority 1199 / candidate 16.** The source writes
   `1 \leq \lambda_i \leq n`, although authority 1195 already defines the
   parts as arbitrary positive integers and bounds only their count by
   `r \leq n`. The candidate uses `1 \leq i \leq r`, preserving the stated
   positivity while repairing the intended index range. Otherwise, for
   `n=1`, the valid symmetric monomial `X_1^2` would be excluded.
2. **O013-LI-U043-COR-002 — authority 1222 / candidate 39.** The source's
   lexicographic condition starts at index zero, invoking undefined partition
   entries. The candidate repairs `0 \leq i < k` to `1 \leq i < k`.

No other source correction was made. The exercise block required no
high-confidence mathematical correction.

## Terminology and provenance

`TERMINOLOGY_DELTA.id-ID.csv` records the candidate-only additions without
mutating the shared glossary. Existing `partisi` and `urutan leksikografis`
are retained; proposed additions include `polinomial simetris`, `diagram
Young`, `urutan dominasi`, `polinomial simetris elementer`, `jumlah pangkat`,
`Rumus Newton`, `diskriminan`, `polinomial bernilai bulat`, `polinomial
aditif`, and the exercise-specific algebraic-number-theory terms.

The frozen Chapter 5 header attributes the work to Wen-Wei Li and licenses it
under CC BY 4.0. This is an AI-assisted Indonesian translation prepared with
OpenAI Codex gpt-5.6-sol, Ultra, on instruction of the user; it is not official
or endorsed.

## Verification result

`python build/unit-043-candidate/check_unit_043_candidate.py` returned **PASS**
against the exact full-authority, tail-slice, and candidate identities above.
The pre-existing section checker also independently returned **PASS** against
the byte-identical 135-record section prefix. This candidate is ready for one
Chapter 5 batch admission together with Units 036–042; it does not require a
separate publication boundary.
