# Unit 014 equation-numbering correction

Status: corrected locally; publication update required.

The first standalone Unit 014 checkpoint omitted the four numbered Chapter 2
displays that precede `chapter2.tex:766-909`. Its reader therefore printed
`eqn:unit-adjunction` and `eqn:unit-counit-relation` as (2.1) and (2.2), while
the complete source book identifies them as (2.5) and (2.6). This was a
standalone packaging defect, not a change to the translated mathematics.

The driver `repo/source/unit-014-bab-2-fungtor-adjoin-dasar.tex` now executes
`\setcounter{equation}{4}` before importing the frozen span. Clean builds E and
F both record:

- `eqn:unit-adjunction` = (2.5), reader page 2;
- `eqn:unit-counit-relation` = (2.6), reader page 3.

The corrected nine-page reader is 121,761 bytes, SHA-256
`1241ca5ff345ff5315d5e3f4e6fcb1f37af2b0e948f458306c4b790035779d04`.
The final 85,851-byte log has SHA-256
`7045b0b1ede153a2dcaea05e03139028f95621b5b44b9ba0bdea2c1cc0fb97cb`.
Poppler and MuPDF replays are pixel-identical on 9/9 pages between the two
clean builds. All nine Poppler pages and the two changed equation-bearing
MuPDF pages were inspected at original render resolution; no new clipping,
overlap, missing content, blank page, or unreadable surface was found.

The source author, translation text, terminology, diagrams, formulas, labels,
references, component rights, and production provenance remain unchanged.
Production provenance: OpenAI Codex gpt-5.6-sol, Ultra.
