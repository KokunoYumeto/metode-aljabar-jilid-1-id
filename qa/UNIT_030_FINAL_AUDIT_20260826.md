# Unit 030 independent final audit — 2026-08-26

Status: **PASS for the isolated candidate only.** This audit does not integrate
the candidate into `repo/source/chapter4.tex`, alter the live glossary or
backend, change controls or README, or perform any Git/publication operation.

## Frozen source and candidate

- Corpus/unit: `O013-LI-U030`, Wen-Wei Li, *Methods of Algebra*, Volume 1.
- Authority: `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
  The complete authority file is 154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Exact contiguous source boundary: lines 796–935 (Section 4.6,
  composition series), 140 normalized-LF records, 7,981 bytes, SHA-256
  `7803452c4285c57e419a2cb2a288b3733975555fafd6b7a88c5732da369220c1`.
  Line 935 is the boundary blank; Section 4.7 starts at line 936 and is not
  included.
- Candidate: `build/unit-030-candidate/chapter4-group-composition-series-id.tex`;
  10,044 bytes, SHA-256
  `7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b`.
  It has 139 substantive LF records (lines 796–934) and one final LF.

## Independent deterministic and semantic checks

`python scripts/check_unit_030_candidate.py` was rerun independently and
passed. Checker identity: 14,417 bytes, SHA-256
`e8cf6de679203e4cf1173310c88767248463f9961b0dd556286cf863075f0b2e`.
The pass reports 52 environment markers, 10 labels, 9 refs/eqrefs, 6 index
commands, 88 protected mathematical zones, 6 TikZ-cd environments with 23
arrows, no citations, exercises, hints, Han residue, invisible controls, or
placeholders, and exactly one declared source correction.

I independently compared every source statement and formula with the target,
including all six diagrams, subgroup normality claims, Schreier endpoint and
matching identities, Jordan–Hölder multiplicities, the short-exact-sequence
splice, and the finite-abelian induction. No omitted or mistranslated
mathematical assertion was found. The candidate's one openly declared repair,
`O013-LI-U030-COR-001`, restores the missing `\\supset` at source line 895;
the indexed construction and neighboring relations determine it uniquely.
The two protected diagram labels are localized only from `子群` to `subgrup`
and from `正规子群` to `subgrup normal`. New local terms remain subject to the
later canonical glossary gate; the live glossary was not edited.

## Independent build and visual audit

A clean bounded XeLaTeX replay was run from the candidate with the lane's
portable AJbook/font/package closure, a merged cross-unit label witness, three
XeLaTeX passes, Biber, and both makeindex streams. The scratch driver is
`tmp/unit-030-audit/unit-030-audit.tex` (3,960 bytes, SHA-256
`824d74dde047ec4cf5f17ce1c1ccd1be5ddebb2b6bb4bee1e8f952ca0fb499a8`); the
cross-unit label witness is 276 bytes, SHA-256
`e11ad9122485f60662a9e92fddec310801f6dcaf86a4607156004f1ba3b8e840`.

The resulting five-page PDF is only an audit artifact (not a release):
`tmp/unit-030-audit/out2/unit-030-audit.pdf`, 56,151 bytes, SHA-256
`7dc93cff5d26941ded29800c0f124c263d51be081af77606524b7c681ba09ecb`.
The build completed without fatal errors, unresolved references, overfull
boxes, or missing fonts. All five pages were rendered and visually inspected;
the section heading, prose, formulas, six diagrams, theorem labels, index
entry, and page boundaries are readable with no clipping or overlap. Render
hashes (PNG, 120 dpi) are:

| page | bytes | SHA-256 |
|---:|---:|---|
| 1 | 150,707 | `b3388a24b123c4552e891b93568432dd1af5df778d16a1355b97dfb3cfd7faf1` |
| 2 | 94,055 | `9c76a77099ae0112fb50e76c589e0af3ea8e5f887b339d5201b6deedb0953bbe` |
| 3 | 150,448 | `7fa4bc691513fa3f268ff85b0bede9432be3fdf3a843177fecfd4da7f21bb03e` |
| 4 | 177,667 | `dc6c07ef1bb5cee8aeb75219c7cbabcf2f3a16fa9ef493d940afadac95aefd5c` |
| 5 | 103,494 | `29590fb13c89f6022015262259e75cf9945f70925ee324df973ece17172b336d` |

Non-fatal reproducibility warnings are the expected local LaTeX-release and
xeCJK/braids notices, four underfull vertical boxes, five suppressed empty
hyperref targets for isolated/external anchors, an untagged PDF, and an empty
bibliography because this span has no citations. None indicates a candidate
content or layout defect; the final canonical driver must retain its normal
metadata/accessibility QA.

## Boundary disposition

Unit 030 is independently audited and ready for the owner's later sequential
integration after the cursor has advanced. No canonical, backend, control,
README, Git, or public-release state was changed by this audit.
