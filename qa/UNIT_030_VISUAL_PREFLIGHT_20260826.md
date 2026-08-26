# Unit 030 visual preflight — 2026-08-26

Status: **PASS WITH WARNINGS**. Both independent clean builds and the canonical artifact were structurally inspected and rendered across all seven pages before admission. No actionable layout defect was found.

## Result

- Build I: 7 pages / 91,960 bytes / SHA-256 `cb5b2c5279e7c5574457846873a456cb644d2a1d54ace7ddc975378e036e00cd`.
- Build J: 7 pages / 91,961 bytes / SHA-256 `43ad2ffa2516f2f4394bcb82ad2e585f21c1e9e36a87870f4406a78597f18d74`.
- Canonical artifact: 7 pages / 91,961 bytes / SHA-256 `43ad2ffa2516f2f4394bcb82ad2e585f21c1e9e36a87870f4406a78597f18d74`; byte-identical to build J.
- Poppler and MuPDF each produced 21 full-page renders, for 42 total. Every I-to-J and J-to-artifact same-renderer decoded-pixel comparison passed, and all outer three-pixel bands were clear.
- All pages use a centered, readable text area and natural vertical reflow. The only framed cover element is a consistently filled prose scope panel; it does not encode progress and has no confusing filled/unfilled counterpart.
- Equations, theorem boxes, references, bibliography, term index, links, navigation, metadata, and embedded fonts passed deterministic checks.
- The final build log is reproducibly sanitized from build J while preserving all 2269 line records and diagnostics; it contains zero Windows user paths and zero local profile-name occurrences.

## Disclosed limitations

The PDF is untagged, so no tagged-accessibility claim is made. The local Poppler installation lacks optional Adobe-GB1 mapping data and emits dependent extraction diagnostics, but Poppler text has no replacement character or NUL and both renderers show all visible glyphs. The final log's one underfull hbox and four underfull vboxes are visually benign.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.
