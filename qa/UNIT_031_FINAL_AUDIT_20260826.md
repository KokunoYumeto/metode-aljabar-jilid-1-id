# Unit 031 independent final audit — 2026-08-26

Status: **PASS.** Unit 031 is the complete Bahasa Indonesia rendering of
Section 4.7, “Grup Solvabel dan Grup Nilpoten,” from the pinned Li Volume 1
authority. This audit is a local admission decision; it does not itself claim
publication or public-byte readback.

## Boundary and translation

- Authority: `chapter4.tex:936-1107`, 172 normalized-LF records, 16,048
  bytes, SHA-256
  `647d22446e75cde39b7b9f53d6658f39de78c5d773d51d6f446d651e1734967b`.
  Line 1107 is the blank boundary; Section 4.8 begins at line 1108.
- Candidate: 171 substantive records, 19,855 bytes, SHA-256
  `6bc4b1f7dd6cde6673915eba75cdf96cca6e8312d060d1fda0da25cb7073ee81`.
- Canonical target: `repo/source/chapter4.tex`, 176,533 bytes, SHA-256
  `440ed304a808c687d2e431eff1dbdbe0fe01458d7f8c82b47f515659307cf28f`.
  Target lines 933-1103 are byte-identical to the candidate; Section 4.8
  remains untouched at target line 1104.
- Candidate and canonical gates pass repeatedly. They preserve 31 paired TeX
  environments, six labels, seven references, citation `FT63`, fourteen list
  items, 326 protected mathematical zones, three diagrams with three arrows,
  two drawing commands, and nine index entries. The source has no exercises,
  hints, answers, or solutions in this span, and none were invented. Han
  residue and placeholders are zero.
- Fourteen terminology rows were admitted. The resulting 435-row glossary is
  69,632 bytes, SHA-256
  `6bc960138192243f9fd6e52a8dc60536362bc377946b49de06b49ee1d6e8298f`.

One proof repair, `O013-LI-U031-COR-001`, makes explicit that induced factors
in the supersolvability argument may be trivial and that repeated terms are
removed. Eight mathematical-text fragments are localized without altering
their enclosing formulas. A separate target-only digital reflow splits the
four-term equality at authority line 1061 after the term containing only
`q`; equality, signs, term order, and mathematics remain unchanged. The
reflow is not represented as an upstream correction.

## Reader, PDF, and visual evidence

- Final reader: nine pages, 126,053 bytes, SHA-256
  `313667c3f87439ccaac3f8708653bb352af0ba7a16c9d09b159ad1b836cc32fb`.
- Two independent clean builds produce decoded-pixel-identical pages within
  both Poppler and MuPDF. Build I is 126,051 bytes, SHA-256
  `9802661e5558d1879616703538f848a3091b668383fa2b0679c8913337566a43`;
  build J is byte-identical to the final artifact.
- All 54 page renders are edge-clear. All nine pages were inspected in both
  renderers. The original 42.13312 pt display overflow is gone, and the
  avoidably sparse tenth page was removed by reflowing the short term and
  symbol indexes after the bibliography on page nine. Body typography was
  not reduced. No clipping, collision, broken stroke, missing glyph, tofu,
  edge contact, ambiguous progress block, or unintended blank/sparse page
  remains.
- The final PDF is unencrypted PDF 1.7 with `/Lang id-ID`, exact metadata,
  four outline entries, 37 resolving destinations, fourteen closed internal
  actions, three HTTPS URI actions, and 29 embedded fonts. It contains no
  JavaScript, form, launch action, embedded file, or out-of-bounds geometry.
- The sanitized final log retains all 2,265 records and has zero profile paths,
  errors, unresolved references/citations, missing characters, empty targets,
  overfull boxes, or underfull boxes. The fixed toolchain advisories and the
  untagged-PDF limitation are disclosed. Seventeen stable pypdf NUL
  placeholders arise from unmapped math-font extraction; Poppler/MuPDF text
  extraction has zero NULs and both renderers show the mathematics correctly.

The controlling evidence is `qa/UNIT_031_VISUAL_QA_20260826.md` (6,392 bytes,
SHA-256 `1c30ff4dfc36b7e7647b8712cce795703915bc98745cf6199e7306393287b0be`),
`qa/unit-031-evidence/structure-and-pdf-qa.json` (70,700 bytes, SHA-256
`7ad6a8ef294147fd6b14dfac88f4982da768606eec48d45c0b30be6162021167`),
and `qa/unit-031-evidence/render-hash-inventory.json` (42,967 bytes, SHA-256
`a7d7bb3cd8aa8e660de56a3a6c9e5f29e37840e2a56eafbcf89bf65f4c5e28e3`).

## Backend and rights

The canonical backend JSON is 367,588 bytes, SHA-256
`307828cd0dc47e8229a01fd08beaad3cb3c6fdd4aa09e4f973ba28d86f92f391`.
The generator and validator each pass twice with byte-identical outputs. The
backend contains 497 audited UUIDv5 entities, including 433 concept-compatible
records, eighteen QA events, and six deterministic CSV projections. All 82
full-file or line-span binding occurrences over 39 paths resolve. It records
the proof repair, digital reflow, and eight localizations as distinct events.
Validation evidence is 5,837 bytes, SHA-256
`51fe7f83d5b2c6a192d322b3e96899affb52045e16d9958f285497fe6840f7ca`.

The principal text and translation remain CC BY 4.0. The credited AJbook
fragment remains CC BY-SA 3.0; bundled Noto fonts remain OFL 1.1; unused
`Lanzhou.png` remains CC BY-SA 3.0. The aggregate is not relabeled under a
single blanket license. Source attribution, independent-derivative status,
non-endorsement, and production provenance (`OpenAI Codex gpt-5.6-sol,
Ultra`, acting on the user's instruction) are explicit.

Verdict: the source, translation, mathematics, TeX topology, terminology,
reader, visual/PDF surfaces, modular backend, provenance, and component rights
are mutually bound and pass. Unit 031 is ready for local admission and the
authorized narrow publication transaction. This does not claim that Chapter 4,
Li Volume 1, or O013/D70 is complete.
