# Unit 034 local source-and-reader admission receipt - 2026-08-28

Status: **SOURCE, READER, AND MODULAR BACKEND LOCALLY ADMITTED; PUBLICATION IS
PENDING.** This receipt makes no Git, remote, DOI, or public-byte claim.

This boundary admits the complete Bahasa Indonesia rendering of Section 4.10,
"Limit dan Pelengkapan Grup," as the canonical Unit 034 source and reader.

## Exact authority and target boundary

- Upstream: <https://github.com/wenweili/AlJabr-1>, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority Chapter 4: 154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Unit slice: authority lines 1609-1744, 136 normalized-LF records, 15,005
  bytes, SHA-256
  `9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab`;
  its final record is blank and Section 4.11 begins at line 1745.
- Candidate: `build/unit-034-candidate/chapter4-group-limits-completions-id.tex`,
  135 records, 19,019 bytes, SHA-256
  `8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62`.
- Canonical Chapter 4: 189,935 bytes, SHA-256
  `37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569`;
  lines 1604-1738 are candidate-identical, line 1739 is blank, and line 1740
  is the untouched Section 4.11 sentinel.

The deterministic gates preserve 25 paired environments, 11 labels, 16
references, six citation occurrences over two bibliography keys, six index
entries, 276 protected mathematics zones, five list items, and one `tikzcd`
diagram with 12 arrows. The span contains no exercise, hint, answer, or
solution. The exact 37-row terminology delta produces a unique 513-row
glossary. One source correction, nine protected-text localizations, three
citation-locator localizations, six index localizations, and one target-only
display reflow are separately recorded.

## Reader and evidence

- Reader: `artifacts/unit-034-bab-4-limit-dan-kompletisasi-grup-id.pdf`, nine
  pages, 136,702 bytes, SHA-256
  `e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272`.
- Driver: 5,235 bytes, SHA-256
  `3451d8581e0fa92a993c378bec019b991b9a07b2638973a67131226fed550b8e`;
  build script: 10,343 bytes, SHA-256
  `2511bb4e0a936a96fb8519ff96977aa51400730e551083d354703d2e74e431f2`.
- Sanitized build log: 77,357 bytes, SHA-256
  `bb4b9b6d7de341239eb137173b7dc774f4774298cccf534645cb2561ca9a779d`.
- Structure/PDF evidence: 31,319 bytes, SHA-256
  `4c37064eaa05cfcb0b70718b27c2213a36e1dfa0eda6bf098fd92c06fd641e2d`.
- Render inventory: 41,802 bytes, SHA-256
  `c1e54d2d0d2527542b8b0f575614d8cc27d7c7238a3ea859074d271d9945c3ba`.

Two clean nine-page builds and the artifact pass all-page Poppler and MuPDF
rendering, decoded-pixel, edge, metadata, navigation, font, safe-action,
geometry, extraction, and full-resolution visual gates. The final artifact is
byte-identical to the second clean build. Logs have zero errors, unresolved
references/citations, missing characters, empty targets, overfull boxes, and
underfull boxes. All 39 named destinations resolve, all 31 font objects are
embedded, and the 20 internal plus five HTTPS actions are safe.

The build script extracts canonical target lines 1604-1738 into a build-local
span only after checking the complete target identity, and then requires those
bytes to equal the admitted candidate. The driver consumes that generated span;
it does not build directly from the isolated candidate path.

`O013-LI-U034-REFLOW-001` turns one overwide neighborhood-basis display into
three centered rows. The fail-closed checker removes exactly that declared
presentation wrapper before comparing protected mathematics, and therefore
proves that the formula, conditions, order, and mathematical tokens remain
unchanged. The measured 26.11896 pt overflow is absent from both final builds.
The PDF is untagged, so this receipt makes no tagged-accessibility claim.

## Modular backend admission

- Canonical backend:
  `backend/data/unit-034-bab-4-limit-dan-kompletisasi-grup.json`, 341,684
  bytes, SHA-256
  `c475108a1d6ed5d4c2084adc00c122e1a3294b5d44e6af3e302d39a06d7a6c35`.
- Validation receipt: `qa/unit-034-evidence/backend-validation.json`, 6,315
  bytes, SHA-256
  `41e019eaca9e2af1363b1ed573817e7d08ae2c895547fb57153ffb41c98a2eaf`.
- The record contains 419 concept-compatible records and 482 audited UUIDv5
  entities. It binds 82 occurrences across 44 exact paths and 18 line spans,
  with 22 ordered QA events and six deterministic CSV projections.
- Two generator passes produce byte-identical JSON/CSV outputs. The dedicated
  validator, shared schema validator, their exact tool identities,
  UUID/reference/order/hash gates, and
  JSON/CSV round-trip checks pass without mutating the admitted outputs.

The backend distinguishes the single source correction, nine protected-text
localizations, three citation-locator localizations, six index localizations,
one target-only digital reflow, and ten cross-unit reference isolations. It
records both bibliography keys and all six source citation occurrences without
inventing exercises, hints, answers, or solutions.

## Rights and decision

The principal source text and translation remain CC BY 4.0. The credited
AJbook fragment remains CC BY-SA 3.0, bundled Noto fonts remain OFL 1.1,
Fandol 0.3 remains GPLv3 with its document-embedding font exception, and
unused `Lanzhou.png` remains CC BY-SA 3.0. The aggregate is not relabelled
under one blanket license. Attribution, independent-derivative status,
non-endorsement, and production provenance (**OpenAI Codex gpt-5.6-sol,
Ultra**, acting on the user's instruction) remain explicit.

The Fandol record binds CTAN package 0.3 at 26,688,406 bytes / SHA-256
`9278f01b417ded5766d98c3937192a1a6a2c73a5e94a3493fdfc932b2a55005a`,
the unmodified 35,737-byte `COPYING` with SHA-256
`853b586f0d520493390e571431afaf36a5fbb27dcfd239338a7ee9b0505cb004`,
the package README, the font setup, the final reader, and the embedded-font
evidence without treating the font as CC BY or OFL material.

The source, reader, and backend surfaces pass and are locally admitted. This
receipt does not claim publication. The next source-order boundary is Section
4.11 plus the complete Chapter 4 exercise block at authority line 1745;
durable cursor advancement follows Git publication and anonymous public-byte
readback.
