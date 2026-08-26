# Unit 032 local admission receipt — 2026-08-26

Status: **LOCALLY ADMITTED; PUBLICATION AND PUBLIC-BYTE READBACK ARE NEXT.**

This receipt admits `O013-LI-U032`, the complete Bahasa Indonesia rendering
of Section 4.8, “Grup Bebas.” It records a deterministic local boundary only
and makes no Git or public-state claim.

## Exact authority and target boundary

- Upstream: <https://github.com/wenweili/AlJabr-1>, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority Chapter 4: 154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Unit slice: `chapter4.tex:1108-1388`, 281 normalized-LF records, 22,547
  bytes, SHA-256
  `5a7083cd89d13e776bbf94189f7f96f5d976cd962cba7a8d4c6b2453bd59c8af`;
  the final record is blank and Section 4.9 begins at line 1389.
- Candidate: `build/unit-032-candidate/chapter4-free-groups-id.tex`, 280
  records, 27,910 bytes, SHA-256
  `28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc`.
- Canonical Chapter 4: 181,896 bytes, SHA-256
  `4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680`;
  lines 1104-1383 are candidate-identical and line 1384 is the untouched
  Section 4.9 sentinel.

The repeated candidate and structure gates preserve 52 paired environments,
ten labels, twenty references, six citation occurrences, eleven list items,
367 math zones, eleven diagrams/28 arrows, eight drawing commands, and seven
index entries. The span has no exercise, hint, answer, or solution surface.
Thirty controlled terms were appended to produce the exact 465-row glossary.
Two disclosed source corrections, thirteen protected-text localizations, four
citation-locator localizations, and two target-only display reflows are
recorded separately.

## Reader and evidence

- Reader: `artifacts/unit-032-bab-4-grup-bebas-id.pdf`, thirteen pages,
  149,624 bytes, SHA-256
  `904330916e20f0782b6464cb85e07001851940f4adf153f6592cd34087dbadbf`.
- Build driver: 4,942 bytes, SHA-256
  `666bc58d188c95472e9f9feac2ae5bddc16cca53de168aef31781d9523978c0d`;
  build script: 4,767 bytes, SHA-256
  `33287d95b2f0a89f35ed0a24119739cd50f5a047a5e1a417bc23236b6e225dd5`.
- Sanitized build log: 78,679 bytes, SHA-256
  `3da283cc2d95f15148c6a5c5392951134235c104b7bd8fdee7844ea4217d2a31`;
  zero errors, unresolved references/citations, missing characters, empty
  targets, overfull boxes, or profile paths. Three underfull hboxes are
  visually non-actionable and remain disclosed.
- Visual QA: all thirteen pages inspected with Poppler and MuPDF; 78 final
  renders are edge-clear and every same-renderer build-I/build-J/artifact
  comparison is decoded-pixel-identical. Navigation, safe actions, metadata,
  geometry, and all 28 embedded fonts pass. Untagged-PDF and math-font
  extraction limitations are disclosed without an unsupported accessibility
  claim.

## Modular backend

- JSON: `backend/data/unit-032-bab-4-grup-bebas.json`, 460,681 bytes,
  SHA-256
  `a3f68cd45d5fc44720e769c7a12d745a4af78d7a361e6e8b81a1c5019be1a030`.
- Validation: `qa/unit-032-evidence/backend-validation.json`, 5,422 bytes,
  SHA-256
  `b66c40151489b4d162e63e9edef3da1d7c593362002bb8e0b9a6f5ba3410be6d`.
- Census: 589 concept-compatible records; 660 UUIDv5 identities audited;
  one section; eighteen QA events; six deterministic CSV projections; 94
  binding occurrences across 39 live paths. Repeated generation and
  validation are byte-identical and validation does not mutate outputs.

## Rights and decision

Principal text and translation are CC BY 4.0; the credited AJbook fragment is
CC BY-SA 3.0; Noto fonts are OFL 1.1; unused `Lanzhou.png` is CC BY-SA 3.0.
The closure is not described as unqualified CC BY 4.0. Attribution,
independent-derivative status, non-endorsement, and production provenance
(`OpenAI Codex gpt-5.6-sol, Ultra`, acting on the user's instruction) remain
explicit.

The independent audit `qa/UNIT_032_FINAL_AUDIT_20260826.md` passes. Unit 032
is locally admitted. Next transaction: commit and push this exact bounded
content set, anonymously read back every changed blob, record the public
receipt, and only then advance the durable cursor to Unit 033 at
`chapter4.tex:1389`. The broader O013 goal remains active.
