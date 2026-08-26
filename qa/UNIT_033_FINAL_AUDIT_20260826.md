# Unit 033 independent source-and-reader final audit — 2026-08-26

Status: **PASS WITH WARNINGS; zero actionable source, reader, or backend
defects.** This final local audit binds the translation, reader, and modular
backend surfaces. It does not claim publication.

## Boundary, translation, and corrections

The frozen authority is `chapter4.tex:1389-1608`, 220 normalized-LF records,
19,076 bytes, SHA-256
`c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a`.
Line 1608 is blank and Section 4.10 begins at line 1609. The final candidate
contains 219 substantive records, 23,099 bytes, SHA-256
`1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76`.
Canonical `repo/source/chapter4.tex` is 185,920 bytes, SHA-256
`a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde`;
target lines 1384–1602 are byte-identical to the candidate, followed by the
blank boundary and untouched Section 4.10 sentinel.

Repeated checks preserve 43 paired TeX environments, ten labels, twenty
references, zero citations, nine index entries, 311 protected mathematics
zones, twelve diagrams, four arrows, nine braid commands, three drawings, and
ten nodes. The span contains no exercises, hints, answers, or solutions, and
none were invented. Thirteen terminology rows are admitted; the 478-row
glossary is 76,280 bytes, SHA-256
`9a999be8091cfb9429975d6dcf98aca3d6d3b432ab909891651c9c32e0c79f4c`.

`O013-LI-U033-COR-001` repairs the braid-generator endpoint from
`\tilde{\tau}_n` to `\tilde{\tau}_{n-1}`. `O013-LI-U033-COR-002` supplies
missing cardinality bars around `\mathfrak{S}'_n` in a numeric order bound.
Five protected mathematical-text fragments are localized. Two uses of `unsur
satuan` are normalized to `unsur identitas`. The one target-only reflow moves
an unchanged Klein-four equality into display mathematics and removes the
measured 11.9841 pt overflow. None of the normalizations or reflow is
misrepresented as a source correction.

## Reader, PDF, and visual evidence

The final reader has ten pages, 118,964 bytes, SHA-256
`0af07d45c9aee57e28a6f27fe6162afda253e15c44779ccf07ac591516bd1f1d`.
Clean build M is 118,969 bytes, SHA-256
`3705b36a3d0f7a1bf74214919229d9cfd6134b28dbd19832802f0ff8043d03e4`;
clean build N is byte-identical to the reader. All sixty Poppler/MuPDF renders
are edge-clear, and all defined same-renderer build/build/artifact comparisons
are decoded-pixel-identical. Every page was inspected at full readability.

No clipping, collision, missing glyph, tofu, broken formula, broken diagram,
edge contact, or unintended blank page remains. The final unencrypted PDF 1.7
has `/Lang id-ID`, exact metadata, three outline entries, 35 named
destinations, 22 internal actions, three safe URI actions, and 27 embedded
fonts. It contains no unsafe active payload. The sanitized log records zero
errors, unresolved references/citations, missing characters, empty targets,
and overfull boxes. Exactly one underfull hbox is visually non-actionable. The
PDF is untagged, so no tagged-accessibility claim is made.

The reader-surface-only robust `\xlongequal` definition compensates for
Poppler dropping dvipdfmx's extensible rule. It retains the same labelled
equality semantics with a standard embedded glyph. Both renderers show the
relation clearly; no candidate or canonical-source formula was changed by the
workaround.

Controlling evidence:

- `qa/UNIT_033_VISUAL_QA_20260826.md`, 5,285 bytes, SHA-256
  `c6380aa1402c7571242b21a08275e758ed7c189cf16b2e637e1220a01ec14e36`;
- `qa/unit-033-evidence/structure-and-pdf-qa.json`, 27,516 bytes, SHA-256
  `8edbcd847cedeb88f6f464d699e823864a77a8c4c077ec846228c51b177e707c`;
- `qa/unit-033-evidence/render-hash-inventory.json`, 46,048 bytes, SHA-256
  `7e0bc3fd33a0d1d8c44f6ec7bb43016eb9ea1b281139ae28b69ded144954b915`;
- `qa/UNIT_033_BUILD_FINAL.log`, 75,964 bytes, SHA-256
  `ecc90e94457ba8e47e08329ed38a342e58576546a0c2c1733756cf470be702e8`.

## Backend evidence

The canonical backend is 396,355 bytes, SHA-256
`edc5812ffd5d46d0fee21748dabbe1b75e71dd1226d3261c073db8930bebe4d7`.
Its 485 concepts and 561 audited UUIDv5 entities preserve 104 binding
occurrences over 41 live paths and 46 line spans. Twenty-two ordered QA/tool
events distinguish source corrections, protected-text and index
localizations, terminology normalizations, the source-target display reflow,
and the driver-only renderer workaround. Six CSV projections reproduce the
JSON exactly.

`qa/unit-033-evidence/backend-validation.json` is 5,827 bytes, SHA-256
`3a9d9d832d6ce69d5db364355cf38aceef7e4c8a68c9eeb0ba750203bd0a2fcb`.
Two repeated validator runs each performed two deterministic regenerations,
schema/UUID/reference/order/hash checks, JSON/CSV round-trip validation, and
candidate/structure replay without mutating the admitted outputs.

## Rights, provenance, and bounded verdict

Principal text and translation remain CC BY 4.0; the credited AJbook fragment
remains CC BY-SA 3.0; bundled Noto fonts remain OFL 1.1; unused `Lanzhou.png`
remains CC BY-SA 3.0. Source attribution, component rights,
independent-derivative status, and non-endorsement are preserved.

Production and review provenance is **OpenAI Codex gpt-5.6-sol, Ultra**,
acting on the user's instruction; it does not replace source-author or human
credits.

Verdict: Unit 033's source boundary, translation, mathematics, TeX topology,
terminology, canonical integration, reader, visual/PDF surfaces, modular
backend, provenance, and component-rights statements are mutually bound and
pass. Git publication, public-byte readback, and cursor transition remain
pending and are outside this local verdict. This does not claim that Chapter
4, Li Volume 1, or O013/D70 is complete.
