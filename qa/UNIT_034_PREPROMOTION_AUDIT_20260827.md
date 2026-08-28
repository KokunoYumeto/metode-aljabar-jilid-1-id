# Unit 034 pre-promotion audit — 2026-08-27

Status: **PASS; zero actionable candidate, canonical-splice, glossary,
digital-reflow, build, artifact, or visual defects.** Canonical promotion and
glossary application have passed; this record is the final deterministic
pre-admission audit. Backend/control admission, Git, publication, and
public-byte readback are not claimed here.

## Frozen boundary and exact target

The pinned authority is `chapter4.tex:1609-1744`: 136 normalized-LF records,
15,005 bytes, SHA-256
`9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab`.
Line 1744 is the blank boundary and Section 4.11 begins at authority line 1745.
The complete substantive Unit 034 candidate maps one-for-one to authority
lines 1609-1743 and contains 135 records, 19,019 bytes, SHA-256
`8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62`.

The full pinned authority file is 154,744 bytes, SHA-256
`63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
The promoted canonical `repo/source/chapter4.tex` is 189,935 bytes, SHA-256
`37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569`,
with 1,893 records. Canonical lines **1604–1738** are byte-identical to the
candidate; line 1739 is the preserved blank boundary and line 1740 is the
untouched `\section{范畴中的群}\label{sec:group-in-cat}` sentinel. The exact
135-record splice therefore does not shift the suffix.

The original semantic review remains
`qa/UNIT_034_TRANSLATION_REVIEW_20260825.md`. Its 2026-08-25 title is retained,
but its live prose now binds this final candidate, the declared source
correction, the candidate-identical canonical range, and the target-only
digital reflow.

## Semantic and structural gates

The final fail-closed candidate checker is 16,590 bytes, SHA-256
`7b444643a1ccc1705690c64d099722844a30f40f0d97f04200095f0aaa40caf7`.
The canonical/glossary structure checker is 3,703 bytes, SHA-256
`c80e22ed46a8920c36b07ba5543c447bb851d9c0681429ebffafaf270057da0d`.
Two current replays of each pass and bind:

- 26 raw paired environments / 52 raw begin/end markers, reducing to the
  authority-comparable 25 / 50 census after exact one-occurrence reflow
  normalization;
- 11 labels, 16 references, six citations, and six index entries;
- 277 raw protected mathematical zones and 276 after reflow normalization;
- one `tikzcd` diagram and twelve ordered arrow commands;
- nine protected-text localizations and six localized indexes;
- 534 unescaped dollar delimiters; 259 opening / 259 closing raw braces and
  257 / 257 after reflow normalization;
- zero exercises, hints, solutions, comments, Han residue, Chinese
  punctuation, invisible controls, or placeholders; and
- the one declared mathematical repair
  `O013-LI-U034-COR-001`, changing the p-adic family index from
  `i \geq 1` to `i \geq 0` while leaving the quotient system unchanged.

The terminology pass changed no formula, command sequence, environment,
label, reference, citation, diagram arrow, quantifier, hypothesis, or proof
step. It replaced eleven `kompletisasi` surfaces with `pelengkapan`, normalized
one closure term and one open-cover term, made the two compact/Hausdorff
predicates idiomatic, restored one locative, and named `\Z_p` precisely as the
p-adic integers. These are target-language normalizations, not new source
mathematics.

The sole post-terminology structural change is
`O013-LI-U034-REFLOW-001`: candidate record 53 / authority line 1661 /
canonical line 1656 wraps the existing neighborhood-basis display in
`aligned`, with two row breaks and three alignment markers. Exact inverse
normalization yields the complete 18,982-byte pre-reflow candidate, SHA-256
`c5e91c2271ed44eb51ecaad442799c0312af243fd7ab27a79fa1ff1d0492cc94`.
The 37-byte delta is confined to that one occurrence and changes no
mathematics, terminology, label, reference, citation, index, or prose claim.

## Glossary gate

The final live glossary `00_control/TERMINOLOGY.id-ID.csv` contains 513 data
rows with 513 unique source terms, 82,586 bytes, SHA-256
`59e66d5acf8f8e792327730c01a236d3bc7570b9f71a200b9a6d7b9a71fa3955`.
The admitted staging delta `build/unit-034-staging/terminology-delta.csv`
contains 37 unique rows, all with status `admitted`, 6,613 bytes, SHA-256
`077b2903a33cdcf2df893a9ef57926b3c5d5157fc4be670f5aad10bdfdccf659`.
Every staging row exactly equals its live-glossary row.

The `completion` replacement is the sole admitted
`completion -> pelengkapan` row with topology/algebra/Chapter-10 scope. The
`completeness` replacement keeps `kelengkapan` and broadens its scope to
category theory and topology. The other 35 rows were appended exactly once;
neither replacement was appended as a duplicate.

## Digital-build and visual gate

The pre-reflow A/B logs each contain exactly one diagnostic:
`Overfull \hbox (26.11896pt too wide) detected at line 53`. The final I/J logs
are each 86,065 bytes and contain zero overfull hboxes, zero underfull hboxes,
and zero fatal, reference, citation, character, or link-target diagnostics:

| Final build log | SHA-256 |
|---|---|
| `build/unit-034-final-i/unit-034-bab-4-limit-dan-kompletisasi-grup.log` | `d11b01866899dea4130f1617fd89c58df29cfa6bc566f8577bc0b6215b7b3dd7` |
| `build/unit-034-final-j/unit-034-bab-4-limit-dan-kompletisasi-grup.log` | `cf3973e129316205c5b0a6b73c13c481ca746a9f7cb3039e5ba005934ef5b6c2` |

The final I/J PDFs contain nine pages. They differ in container bytes but are
semantically identical and decode to identical RGB pixels on all nine pages
under both Poppler and MuPDF. The final J PDF is byte-identical to the
artifact. All 54 retained renders have zero ink in the outer three-pixel band,
and the full-resolution page-5 review records the reflowed three-line display
as centered, legible, semantically identical, and wholly inside the text
block.

## Final artifact and evidence

| Path | Bytes | SHA-256 |
|---|---:|---|
| `build/unit-034-final-i/unit-034-bab-4-limit-dan-kompletisasi-grup.pdf` | 136,700 | `970402b3ab3e510c2f72c44723528616eb3456020433ed9cf7b7cce2d56ce83a` |
| `build/unit-034-final-j/unit-034-bab-4-limit-dan-kompletisasi-grup.pdf` | 136,702 | `e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272` |
| `artifacts/unit-034-bab-4-limit-dan-kompletisasi-grup-id.pdf` | 136,702 | `e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272` |
| `qa/UNIT_034_BUILD_FINAL.log` | 77,357 | `bb4b9b6d7de341239eb137173b7dc774f4774298cccf534645cb2561ca9a779d` |
| `qa/unit-034-evidence/structure-and-pdf-qa.json` | 31,319 | `4c37064eaa05cfcb0b70718b27c2213a36e1dfa0eda6bf098fd92c06fd641e2d` |
| `qa/unit-034-evidence/render-hash-inventory.json` | 41,802 | `c1e54d2d0d2527542b8b0f575614d8cc27d7c7238a3ea859074d271d9945c3ba` |

The final build log is a reproducible sanitization of build J with all 2,274
line records preserved and no user path or profile name. The structure/PDF
evidence reports `PASS_WITH_WARNINGS`, an empty actionable-defect list,
cross-PDF semantic identity, artifact byte identity with build J, all fonts
embedded, and zero forbidden diagnostics. The render inventory reports
`PASS_WITH_WARNINGS`; its manual all-page review is `PASS` with an empty
actionable-defect list. The disclosed warnings are the untagged-PDF limitation
and fixed toolchain advisories, not reflow, mathematics, terminology, clipping,
or overflow defects.

Both final builds extract target lines 1604-1738 from the hash-gated canonical
`repo/source/chapter4.tex` into a generated build-local span. The reader driver
does not consume the isolated candidate directly; the generated span is
strictly rechecked against the admitted candidate identity before XeLaTeX runs.

## Admission boundary

Candidate, canonical, glossary, structure, dual-build, artifact, and visual
gates are complete. This pre-admission audit intentionally makes no claim that
the backend/control admission transaction, Git checkpoint, publication, public
readback, or durable cursor advance has occurred. Updating these QA prose files
changed none of those external states.

Production and review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**, acting
on the user's instruction. Source-author and human-contributor credits remain
intact.
