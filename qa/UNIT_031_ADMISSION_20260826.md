# Unit 031 local admission receipt — 2026-08-26

Status: **LOCALLY ADMITTED; PUBLICATION AND PUBLIC-BYTE READBACK ARE NEXT.**

This receipt admits `O013-LI-U031`, the complete Bahasa Indonesia rendering
of Section 4.7, “Grup Solvabel dan Grup Nilpoten.” It records a deterministic
local boundary only and makes no Git or public-state claim.

## Exact authority and target boundary

- Upstream: <https://github.com/wenweili/AlJabr-1>, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority Chapter 4: 154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Unit slice: `chapter4.tex:936-1107`, 172 normalized-LF records, 16,048
  bytes, SHA-256
  `647d22446e75cde39b7b9f53d6658f39de78c5d773d51d6f446d651e1734967b`;
  the final record is blank and Section 4.8 begins at line 1108.
- Candidate: `build/unit-031-candidate/chapter4-solvable-nilpotent-groups-id.tex`,
  171 records, 19,855 bytes, SHA-256
  `6bc4b1f7dd6cde6673915eba75cdf96cca6e8312d060d1fda0da25cb7073ee81`.
- Canonical Chapter 4: 176,533 bytes, SHA-256
  `440ed304a808c687d2e431eff1dbdbe0fe01458d7f8c82b47f515659307cf28f`;
  lines 933-1103 are candidate-identical and line 1104 is the untouched
  Section 4.8 sentinel.

The candidate and canonical checkers repeatedly pass. They preserve 31 paired
environments, six labels, seven references, `FT63`, fourteen list items, 326
math zones, three diagrams/three arrows, two drawing commands, and nine index
entries. The span has no source exercise, hint, answer, or solution surface.

Fourteen controlled terms were appended to produce a 435-row glossary,
69,632 bytes, SHA-256
`6bc960138192243f9fd6e52a8dc60536362bc377946b49de06b49ee1d6e8298f`.
One disclosed proof repair (`O013-LI-U031-COR-001`), eight protected-text
localizations, and one separate target-only display reflow are recorded. The
reflow preserves the four-term equality exactly and is not an upstream
correction.

## Reader and evidence

- Reader: `artifacts/unit-031-bab-4-grup-solvabel-dan-nilpoten-id.pdf`, nine
  pages, 126,053 bytes, SHA-256
  `313667c3f87439ccaac3f8708653bb352af0ba7a16c9d09b159ad1b836cc32fb`.
- Build driver: 5,956 bytes, SHA-256
  `0f6fa939eb1a65e0305ade87af2269c9f0637aad392fdf365e2430fb332bab75`;
  build script: 5,021 bytes, SHA-256
  `98a2ef100255e4c9f206570f6fd6bc80987cdd5da98f7fd13c889b36de18db6f`.
- Sanitized build log: 77,142 bytes, SHA-256
  `47dd6cc5677888afeee4b7e0e7fb4800f16790125746b0f32c9a40216a79a548`;
  zero errors, unresolved references/citations, missing characters, empty
  targets, overfull/underfull boxes, or profile paths.
- Visual QA: all nine pages inspected with Poppler and MuPDF; 54 edge-clear
  renders and every same-renderer build-I/build-J/artifact comparison are
  decoded-pixel-identical. The bibliography and both short indexes reflow onto
  the readable final page. PDF navigation, safe actions, metadata, geometry,
  and all 29 embedded fonts pass. Untagged-PDF and math-font extraction
  limitations are disclosed without making an unsupported accessibility claim.

## Modular backend

- JSON: `backend/data/unit-031-bab-4-grup-solvabel-dan-nilpoten.json`,
  367,588 bytes, SHA-256
  `307828cd0dc47e8229a01fd08beaad3cb3c6fdd4aa09e4f973ba28d86f92f391`.
- Validation: `qa/unit-031-evidence/backend-validation.json`, 5,837 bytes,
  SHA-256
  `51fe7f83d5b2c6a192d322b3e96899affb52045e16d9958f285497fe6840f7ca`.
- Census: 497 audited UUIDv5 entities; 433 concept-compatible records; one
  section; eighteen QA events; six deterministic CSV projections; 82 binding
  occurrences across 39 live paths. Generation and validation pass twice with
  byte-identical outputs and no mutations during validation.

## Rights and decision

Principal text and translation are CC BY 4.0; the credited AJbook fragment is
CC BY-SA 3.0; Noto fonts are OFL 1.1; unused `Lanzhou.png` is CC BY-SA 3.0.
The closure is not described as unqualified CC BY 4.0. Attribution,
independent-derivative status, non-endorsement, and production provenance
(`OpenAI Codex gpt-5.6-sol, Ultra`, acting on the user's instruction) remain
explicit.

The independent audit `qa/UNIT_031_FINAL_AUDIT_20260826.md` passes. Unit 031
is therefore locally admitted. Next transaction: commit and push this exact
bounded content set to the existing public repository, anonymously read back
every changed blob, record the public receipt, and only then advance the
durable cursor to Unit 032 at `chapter4.tex:1108`. The broader O013 goal remains
active.
