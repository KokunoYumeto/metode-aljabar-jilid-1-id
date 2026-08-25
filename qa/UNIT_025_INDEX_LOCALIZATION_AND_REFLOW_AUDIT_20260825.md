# Unit 025 index localization and digital reflow audit — 2026-08-25

Status: **PASS.** Four target-only MakeIndex display repairs remove exposed
Pinyin parent headings from the Indonesian index, and the standalone reader is
reflowed as a centered ten-page digital edition. Neither intervention changes
the admitted mathematics or the source-order boundary.

## Frozen translation delta

The terminology-reviewed candidate before this final index pass was 20,409
bytes, SHA-256
`a1a60706d405f7f672b2cbcf99598911db93c1b4fa079779c7501ce4c00b7665`.
It already contained the complete translation of frozen authority
`chapter4.tex:1-176`, the thirty-row terminology promotion, and correction
`O013-LI-U025-COR-001`.

The final candidate is
`build/unit-025-candidate/chapter4-group-basics-id.tex`, 178 LF records,
20,464 bytes, SHA-256
`5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a`.
The only later source-text changes are four explicit Indonesian parent aliases
on descendant index records:

- `yaobanqun@monoid (monoid)!submonoid`;
- `qun@grup (group)!orde (order)` at the group definition;
- `qun@grup (group)!sederhana (simple)`;
- `qun@grup (group)!orde (order)` at the element-order definition.

The source romanization keys remain the sort keys. The aliases change only the
visible hierarchy, so the reader now shows `monoid` and `grup` rather than raw
`yaobanqun` and `qun`. Index count, order, options, and mathematical ownership
remain unchanged: 25 index commands in the canonical span. The final pinned
candidate checker passes with 280 mathematical spans, ten labels, eleven
references, three citations, 24 items, one declared mathematical correction,
and zero Han residue.

## Canonical integration

The final candidate is the exact prefix of `repo/source/chapter4.tex`. The
complete canonical target is 159,681 bytes, SHA-256
`b1b055416d392a66708047afb20a14175566c7839286979baac6289d3d125419`.
Its untouched authority suffix from source line 177 is 139,216 bytes,
SHA-256
`20e588a6d9f8361acad3deb3cdbfbb7e0d2a2495156c458bfe15897d21289b68`;
the only whole-file normalization is one disclosed terminal LF. Both the
candidate and canonical structure checkers pass.

## Reader reflow

The reader driver uses a 142 mm by 198 mm centered text block and 1.16 leading.
Its cover states the exact partial scope in prose rather than using ambiguous
filled and unfilled progress blocks. The reading-guidance box stays intact on
one page; the chapter and section openings have usable space; local references
remain live while unresolved references outside this bounded unit are rendered
as plain text; the final remark remains complete on the last content page; and
the bibliography plus localized term and symbol indexes share the final page
without clipping or a sparse extra page.

Two clean builds preserve extracted content and decoded page pixels while
differing only in ordinary PDF container bytes:

- build H: ten pages, 123,100 bytes, SHA-256
  `a1645230a6bb64d43f77a8608b1edff50769e819e337471673ac1ab4ece80d6a`;
- build I and the frozen artifact: ten pages, 123,117 bytes, SHA-256
  `511d1c0889c0882639be49d00580c0634de7e3074c757616ac10a3f2fa854615`.

The final build log is `qa/UNIT_025_BUILD_FINAL.log`, 85,827 bytes, SHA-256
`ee9a4e064edf0cf8cc4710e32c89eda7a8623bceb5ec5fbc75d8ef663826cd2a`.
It has zero overfull boxes, empty-target warnings, unresolved references or
citations, and missing-character warnings. Three underfull boxes are benign:
two occur in the imprint and one in a short matrix-example paragraph.

All ten final artifact pages were independently inspected at 144 dpi. The
centered cover, attribution, chapter opening, reading guidance, mathematical
prose, displays, proofs, final remark, bibliography, and both indexes are
legible and unclipped, with no overlap, tofu, stranded heading, or cross-page
hyphen fragment. The structured dual-render receipt records the complete
Poppler/MuPDF comparison separately.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra.** Wen-Wei Li remains
the source author; attribution, component rights, independent translation,
and non-endorsement remain distinct.
