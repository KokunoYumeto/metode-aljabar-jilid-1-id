# Unit 033 pre-promotion audit — 2026-08-26

Status: **PASS WITH WARNINGS; zero actionable defects.** This audit binds the
complete translation, canonical source integration, and reader evidence. The
modular backend and public release remain separate subsequent gates.

## Frozen boundary and target

The pinned authority is `chapter4.tex:1389-1608`: 220 normalized-LF records,
19,076 bytes, SHA-256
`c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a`.
Line 1608 is the blank boundary; Section 4.10 begins at authority line 1609.
The final candidate contains the 219 substantive records aligned to lines
1389–1607, 23,099 bytes, SHA-256
`1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76`.

Canonical `repo/source/chapter4.tex` is 185,920 bytes, SHA-256
`a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde`.
Target lines 1384–1602 are byte-identical to the candidate; line 1603 is the
preserved blank boundary and line 1604 is the untouched Section 4.10 sentinel.
The splice preserves the accepted Units 025–032 prefix and the entire
untranslated suffix.

The controlled glossary contains 478 data rows, 76,280 bytes, SHA-256
`9a999be8091cfb9429975d6dcf98aca3d6d3b432ab909891651c9c32e0c79f4c`.
Its exact thirteen-row Unit 033 tail is bound by the admitted delta
`build/unit-033-staging/terminology-delta.csv`, 1,987 bytes, SHA-256
`783f39a1d80f93613f1d60c53ab77c7ce0a4c5c799c8ea25248f427e4049437b`.
The distinct QA copy remains a proposed-state witness, 1,987 bytes, SHA-256
`48079d6ee3c7f57adb86e12b3d0cbbb7e10fbc286beacc373725c36e89b3df5f`.

## Semantic and structural gates

Repeated candidate and canonical checks preserve 43 paired environments / 86
ordered markers, ten labels, twenty references, zero citations, nine index
entries, 311 mathematical zones, twelve diagrams, four arrows, nine braid
commands, three drawing commands, and ten nodes. No exercise, hint, answer, or
solution is present or invented. Residue, placeholder, invisible-control, and
unbalanced-TeX checks pass.

Two source corrections are explicit: the braid-generator endpoint is repaired
from `\tilde{\tau}_n` to `\tilde{\tau}_{n-1}`, and the left side of a numeric
group-order bound receives the missing cardinality bars. Five protected
mathematical-text fragments are localized. Two uses of `unsur satuan` are
normalized to `unsur identitas`. One target-only reflow promotes the unchanged
Klein-four equality to display mathematics, removing an 11.9841 pt overflow.
Corrections, terminology normalizations, and reflow are distinct records.

The fail-closed candidate checker is 18,099 bytes, SHA-256
`643b1ccc5fe1f47aa185cbb8d2813e971c1381cbcc032fac8cc01c2c941c2a1d`;
the structure checker is 12,660 bytes, SHA-256
`d018a2966e46fe44045c2159a420769fa2f1a0bd5992ecceb454ab98ebfc4e65`.

## Reader gate

The ten-page reader
`artifacts/unit-033-bab-4-grup-simetris-id.pdf` is 118,964 bytes, SHA-256
`0af07d45c9aee57e28a6f27fe6162afda253e15c44779ccf07ac591516bd1f1d`.
The final clean builds are:

- `build/unit-033-final-m/unit-033-bab-4-grup-simetris.pdf`, 118,969 bytes,
  SHA-256
  `3705b36a3d0f7a1bf74214919229d9cfd6134b28dbd19832802f0ff8043d03e4`;
- `build/unit-033-final-n/unit-033-bab-4-grup-simetris.pdf`, 118,964 bytes,
  SHA-256
  `0af07d45c9aee57e28a6f27fe6162afda253e15c44779ccf07ac591516bd1f1d`.

The artifact is byte-identical to the latter build. All sixty final renders—
three PDFs, ten pages, two renderers—are decoded-pixel stable in the defined
same-renderer comparisons and edge-clear. All pages were inspected at full
readability in Poppler and MuPDF. The repaired labelled equality is visible,
centered, and unclipped in both renderers.

The sanitized final log is 75,964 bytes, SHA-256
`ecc90e94457ba8e47e08329ed38a342e58576546a0c2c1733756cf470be702e8`.
It records zero errors, unresolved references/citations, missing characters,
empty targets, and overfull boxes. Exactly one underfull hbox remains and is
visually non-actionable. The unencrypted PDF 1.7 has `/Lang id-ID`, exact
metadata, three outline entries, 35 resolving destinations, 22 `/GoTo`
actions, three safe `/URI` actions, and 27 embedded fonts. It is untagged, so
no tagged-accessibility claim is made.

The reader driver is 4,919 bytes, SHA-256
`0f95f282b9b49b5ef8df029b0b82d64842a9ae77a3fc9614f8bfb386c1fa5152`.
Its local robust `\xlongequal` definition compensates for Poppler dropping
dvipdfmx's extensible rule while retaining the same labelled equality
semantics with an embedded glyph. It changes no candidate or canonical-source
mathematics.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**, acting on the
user's instruction. Source-author and human-contributor credits remain
intact. Backend admission, publication, public-byte readback, and the cursor
transition are not claimed here.
