# Unit 034 digital reflow audit — 2026-08-27

Status: **PASS.** `O013-LI-U034-REFLOW-001` is one exact target-only,
one-record display reflow. It removes the measured 26.11896 pt overflow,
changes no mathematics or terminology, preserves the 135-record splice, and
passes the final dual-build and all-page visual gates with zero actionable
defects.

## Bound source and target identities

| Object | Bytes | SHA-256 |
|---|---:|---|
| `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex` | 154,744 | `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3` |
| normalized-LF authority lines 1609–1744 | 15,005 | `9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab` |
| `build/unit-034-candidate/chapter4-group-limits-completions-id.tex` | 19,019 | `8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62` |
| `repo/source/chapter4.tex` | 189,935 | `37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569` |
| `00_control/TERMINOLOGY.id-ID.csv` | 82,586 | `59e66d5acf8f8e792327730c01a236d3bc7570b9f71a200b9a6d7b9a71fa3955` |

The authority slice contains 136 records, with authority line 1744 as the
blank boundary. The candidate contains the 135 substantive records
corresponding one-for-one to authority lines 1609–1743. Canonical lines
1604–1738 are byte-identical to the candidate; canonical line 1739 remains
blank and line 1740 remains the Section 4.11 sentinel.

## Defect observation

The pre-reflow A/B build logs are each 86,337 bytes and record the same single
layout defect at log line 2204:

```text
Overfull \hbox (26.11896pt too wide) detected at line 53
```

| Pre-reflow log | SHA-256 |
|---|---|
| `build/unit-034-final-a/unit-034-bab-4-limit-dan-kompletisasi-grup.log` | `3607ae709b87992c1ddeae70c83be1a7b6f4817359e76352474640f0b838b3d9` |
| `build/unit-034-final-b/unit-034-bab-4-limit-dan-kompletisasi-grup.log` | `534c2bdb95891408157cc0a31fb41331f1c9111ca016c214399d089c8e2b7429` |

The reported TeX line is candidate record 53, the neighborhood-basis display
inside Lema `prop:completion-compactness`. Its source/canonical mapping is:

- authority line 1661;
- candidate record 53; and
- canonical line 1656.

No other record is in the reflow scope.

## Exact before and after

The record's leading horizontal-tab byte and terminating LF are unchanged.
The exact pre-reflow payload after that tab was:

```tex
\[ \mathcal{U}_{I_0} = \bigcap_{i \in I_0} p_i^{-1}(U_i), \qquad I_0 \subset I: \; \text{himpunan bagian berhingga}, \quad U_i \ni 1: \; \text{himpunan bagian terbuka} \]
```

The exact live payload after that tab is:

```tex
\[ \begin{aligned} \mathcal{U}_{I_0} &= \bigcap_{i \in I_0} p_i^{-1}(U_i), \qquad\\ I_0 &\subset I: \; \text{himpunan bagian berhingga}, \quad\\ U_i &\ni 1: \; \text{himpunan bagian terbuka} \end{aligned} \]
```

The change adds only one `\begin{aligned}` / `\end{aligned}` pair, two `\\`
row breaks, and three `&` alignment markers. It inserts no LF-delimited record
and deletes none. The candidate therefore remains 135 records and the
canonical suffix remains at exactly the same line numbers.

The after payload occurs exactly once in the final candidate and the before
payload occurs zero times. Replacing that one exact after payload in memory
with the before payload removes exactly 37 bytes and produces 18,982 bytes,
SHA-256
`c5e91c2271ed44eb51ecaad442799c0312af243fd7ab27a79fa1ff1d0492cc94`.
That is the complete terminology-normalized pre-reflow candidate identity, so
all bytes outside this exact payload are unchanged.

## Mathematical and structural invariance

The displayed mathematics remains:

- the same neighborhood-basis symbol `\mathcal{U}_{I_0}`;
- the same equality with `\bigcap_{i \in I_0} p_i^{-1}(U_i)`;
- the same finite-subset condition `I_0 \subset I`;
- the same identity-neighborhood condition `U_i \ni 1`; and
- the same localized protected text, punctuation, display delimiters, and
  formula order.

No operand, operator, quantifier, subscript, inverse-image map, subset or
membership relation, hypothesis, conclusion, label, reference, citation,
index, diagram, source correction, or prose proposition changes. This is not
a second mathematical source correction; the sole source correction remains
`O013-LI-U034-COR-001` at authority line 1720.

Before checker normalization, the final candidate has 26 paired environments
/ 52 begin/end markers, 277 protected mathematical zones, and 259 opening /
259 closing raw braces. The reflow contributes exactly one environment pair,
one detected mathematical zone, and two brace pairs. Dollar-delimiter count
remains 534.

## Checker normalization

The read-only checker `scripts/check_unit_034_candidate.py` is 16,590 bytes,
SHA-256
`7b444643a1ccc1705690c64d099722844a30f40f0d97f04200095f0aaa40caf7`.
Its `remove_declared_digital_reflow()` function requires the exact live after
payload to occur once and replaces it with the exact before payload only in
memory. Structural and protected-mathematics comparisons then run on that
normalized text. Its `normalize_math()` function independently removes the
`aligned` wrapper, row breaks, alignment markers, and whitespace before
comparing mathematical-zone content.

After normalization, the candidate returns to 25 paired environments / 50
markers, 276 protected mathematical zones, and 257 / 257 raw braces, exactly
matching the authority topology after the nine declared protected-text
localizations and `O013-LI-U034-COR-001`. The checker also binds 11 labels, 16
references, six citations, six indexes, one diagram, twelve arrows, strict
UTF-8/LF shape, and the final 19,019-byte candidate identity.

The structure checker `scripts/check_unit_034_structure.py` is 3,703 bytes,
SHA-256
`c80e22ed46a8920c36b07ba5543c447bb851d9c0681429ebffafaf270057da0d`.
It requires the canonical 1604–1738 span to equal the final candidate bytes,
preserves the blank/sentinel suffix, and binds the 513-row live glossary. Two
current replays of each checker pass with byte-identical stdout.

## Final build and visual result

The final I/J logs are each 86,065 bytes. Both contain zero overfull hboxes,
zero underfull hboxes, and zero fatal, reference, citation, missing-character,
or empty-link-target diagnostics:

| Final build log | SHA-256 |
|---|---|
| `build/unit-034-final-i/unit-034-bab-4-limit-dan-kompletisasi-grup.log` | `d11b01866899dea4130f1617fd89c58df29cfa6bc566f8577bc0b6215b7b3dd7` |
| `build/unit-034-final-j/unit-034-bab-4-limit-dan-kompletisasi-grup.log` | `cf3973e129316205c5b0a6b73c13c481ca746a9f7cb3039e5ba005934ef5b6c2` |

The final I PDF is 136,700 bytes, SHA-256
`970402b3ab3e510c2f72c44723528616eb3456020433ed9cf7b7cce2d56ce83a`.
The final J PDF and released artifact are byte-identical at 136,702 bytes,
SHA-256
`e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272`.
All three contain nine pages.

Poppler and MuPDF rendered all nine pages of both final builds and the
artifact at 144 dpi. All nine decoded-RGB pages are identical between I and J
and between J and the artifact under each renderer; all 54 renders have zero
ink in the outer three-pixel band. Full-resolution review records page 5 as a
centered, readable three-line display with no overlap, clipping, missing
glyph, semantic divergence, or remaining overflow.

## Final evidence identities

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| `qa/UNIT_034_BUILD_FINAL.log` | 77,357 | `bb4b9b6d7de341239eb137173b7dc774f4774298cccf534645cb2561ca9a779d` |
| `qa/unit-034-evidence/structure-and-pdf-qa.json` | 31,319 | `4c37064eaa05cfcb0b70718b27c2213a36e1dfa0eda6bf098fd92c06fd641e2d` |
| `qa/unit-034-evidence/render-hash-inventory.json` | 41,802 | `c1e54d2d0d2527542b8b0f575614d8cc27d7c7238a3ea859074d271d9945c3ba` |

The sanitized final log reproduces build J, preserves all 2,274 line records,
and records zero forbidden diagnostics. The structure/PDF evidence reports
`PASS_WITH_WARNINGS`, cross-PDF semantic identity, artifact byte identity with
build J, and an empty actionable-defect list. The render inventory reports
`PASS_WITH_WARNINGS`; its manual all-page visual review is `PASS` with an
empty actionable-defect list. The disclosed untagged-PDF and fixed-toolchain
warnings are unrelated to the reflow and do not weaken the zero-overfull,
zero-clipping result.

Build I/J take their reader body from a generated build-local extraction of
canonical target lines 1604-1738. The build script hash-gates both the complete
canonical file and the extracted span, then requires the extracted bytes to
match the admitted candidate; the standalone driver no longer inputs the
isolated candidate path.

Verdict: **`O013-LI-U034-REFLOW-001` is admitted as a reversible,
mathematically invariant, one-record digital layout repair.**
