# Unit 033 local source-and-reader admission receipt — 2026-08-26

Status: **SOURCE, READER, AND MODULAR BACKEND LOCALLY ADMITTED; PUBLICATION IS
PENDING.** This receipt makes no Git, remote, DOI, or public-byte claim.

This boundary admits the complete Bahasa Indonesia rendering of Section 4.9,
“Grup Simetris,” as the canonical Unit 033 source and reader.

## Exact authority and target boundary

- Upstream: <https://github.com/wenweili/AlJabr-1>, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority Chapter 4: 154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Unit slice: authority lines 1389–1608, 220 normalized-LF records, 19,076
  bytes, SHA-256
  `c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a`;
  its final record is blank and Section 4.10 begins at line 1609.
- Candidate: `build/unit-033-candidate/chapter4-symmetric-groups-id.tex`, 219
  records, 23,099 bytes, SHA-256
  `1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76`.
- Canonical Chapter 4: 185,920 bytes, SHA-256
  `a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde`;
  lines 1384–1602 are candidate-identical, line 1603 is blank, and line 1604
  is the untouched Section 4.10 sentinel.

The deterministic gates preserve 43 paired environments, ten labels, twenty
references, zero citations, nine indexes, 311 mathematics zones, twelve
diagrams, four arrows, nine braid commands, three drawing commands, and ten
nodes. The span contains no exercise, hint, answer, or solution. The exact
thirteen-row terminology delta produces a 478-row glossary. Two source
corrections, five protected-text localizations, two target terminology
normalizations, and one target-only display reflow are recorded separately.

## Reader and evidence

- Reader: `artifacts/unit-033-bab-4-grup-simetris-id.pdf`, ten pages, 118,964
  bytes, SHA-256
  `0af07d45c9aee57e28a6f27fe6162afda253e15c44779ccf07ac591516bd1f1d`.
- Driver: 4,919 bytes, SHA-256
  `0f95f282b9b49b5ef8df029b0b82d64842a9ae77a3fc9614f8bfb386c1fa5152`;
  build script: 9,366 bytes, SHA-256
  `640892442816eee59b93b5a2980236901d9caae5aeee4a503cdb204d73896fba`.
- Sanitized build log: 75,964 bytes, SHA-256
  `ecc90e94457ba8e47e08329ed38a342e58576546a0c2c1733756cf470be702e8`.
- Structure/PDF evidence: 27,516 bytes, SHA-256
  `8edbcd847cedeb88f6f464d699e823864a77a8c4c077ec846228c51b177e707c`.
- Render inventory: 46,048 bytes, SHA-256
  `7e0bc3fd33a0d1d8c44f6ec7bb43016eb9ea1b281139ae28b69ded144954b915`.

Two clean ten-page builds and the artifact pass all-page Poppler and MuPDF
rendering, decoded-pixel, edge, metadata, navigation, font, safe-action,
geometry, extraction, and full-resolution visual gates. The final artifact is
byte-identical to the second clean build. Logs have zero errors, unresolved
references/citations, missing characters, empty targets, and overfull boxes.
One underfull hbox is visually accepted and nonfatal.

The driver-only robust `\xlongequal` definition repairs a renderer surface:
Poppler omitted dvipdfmx's extensible rule, while the standard embedded
equality glyph is visible in Poppler and MuPDF and preserves the same labelled
relation. Candidate and canonical-source mathematics are unchanged. The PDF
is untagged; the receipt therefore makes no tagged-accessibility claim.

## Modular backend admission

- Canonical backend: `backend/data/unit-033-bab-4-grup-simetris.json`,
  396,355 bytes, SHA-256
  `edc5812ffd5d46d0fee21748dabbe1b75e71dd1226d3261c073db8930bebe4d7`.
- Validation receipt: `qa/unit-033-evidence/backend-validation.json`, 5,827
  bytes, SHA-256
  `3a9d9d832d6ce69d5db364355cf38aceef7e4c8a68c9eeb0ba750203bd0a2fcb`.
- The record contains 485 concepts and 561 audited UUIDv5 entities. It binds
  104 occurrences across 41 exact paths and 46 line spans, with 22 ordered QA
  events and six deterministic CSV projections.
- Two independent validator runs each regenerated the JSON and all six CSVs
  twice, passed the shared schema and JSON/CSV round-trip gates, and confirmed
  that validation did not mutate the admitted outputs.

The backend keeps the two source corrections, five protected-text
localizations, two terminology normalizations, one source-target digital
reflow, and the reader-driver-only renderer workaround as distinct events.
It preserves the component-rights boundary and records zero invented
exercises, hints, answers, solutions, or citations.

## Rights and decision

The principal source text and translation remain CC BY 4.0. The credited
AJbook fragment remains CC BY-SA 3.0, bundled Noto fonts remain OFL 1.1, and
unused `Lanzhou.png` remains CC BY-SA 3.0. The aggregate is not relabelled
under one blanket license. Attribution, independent-derivative status,
non-endorsement, and production provenance (**OpenAI Codex gpt-5.6-sol,
Ultra**, acting on the user's instruction) remain explicit.

The source, reader, and backend surfaces pass and are locally admitted. This
receipt does not claim publication. The next source-order boundary is Section
4.10 at authority line 1609; durable cursor advancement follows the authorized
Git publication and anonymous public-byte readback.
