# Unit 033 target-only digital reflow — 2026-08-26

Status: **PASS; the overflow is removed without semantic change.**

The first complete clean reader build reported one actionable overfull box:
11.9841 pt at candidate lines 107–108, in the inline equality identifying
`\mathscr{D}^1\mathfrak A_4` with the Klein four subgroup. The equality, set
entries, order, delimiters, and surrounding conclusion were mathematically
correct.

An attempted `\allowbreak` before the set was ineffective because the large
delimiter group remained unbreakable; that rejected build is not the release
reader. `O013-LI-U033-REFLOW-001` instead promotes the exact equality and
unchanged set to display mathematics, moving only the sentence punctuation
needed for valid display flow. This is a target-only typography record, not a
source correction.

The final candidate is 23,099 bytes, SHA-256
`1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76`;
the canonical Chapter 4 source is 185,920 bytes, SHA-256
`a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde`.
The candidate checker normalizes the one declared source-to-target layout
change before comparing all 311 mathematical zones, so the reflow is both
explicit and fail-closed.

Two final clean builds contain ten pages each. Their sanitized final log has
zero errors, unresolved references/citations, missing characters, empty
targets, and overfull boxes; the remaining one underfull hbox is visually
non-actionable. The admitted artifact is 118,964 bytes, SHA-256
`0af07d45c9aee57e28a6f27fe6162afda253e15c44779ccf07ac591516bd1f1d`.
Every page passes Poppler and MuPDF rendering, decoded-pixel comparison, edge
inspection, and full-resolution visual review. The reflowed display is
centered, legible, unclipped, and semantically unchanged in both renderers.

Separately, the reader driver robustly redefines `\xlongequal` because Poppler
dropped dvipdfmx's extensible rule. That renderer-only repair retains the same
labelled equality with a standard embedded equality glyph and does not alter
the candidate or canonical source mathematics.
