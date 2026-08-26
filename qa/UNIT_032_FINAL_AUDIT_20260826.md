# Unit 032 independent final audit — 2026-08-26

Status: **PASS.** Unit 032 is the complete Bahasa Indonesia rendering of
Section 4.8, “Grup Bebas,” from the pinned Li Volume 1 authority. This is a
local admission decision; it does not itself claim publication or public-byte
readback.

## Boundary and translation

- Authority: `chapter4.tex:1108-1388`, 281 normalized-LF records, 22,547
  bytes, SHA-256
  `5a7083cd89d13e776bbf94189f7f96f5d976cd962cba7a8d4c6b2453bd59c8af`.
  Line 1388 is blank; Section 4.9 begins at line 1389.
- Candidate: 280 substantive records, 27,910 bytes, SHA-256
  `28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc`.
- Canonical target: `repo/source/chapter4.tex`, 181,896 bytes, SHA-256
  `4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680`.
  Target lines 1104-1383 are byte-identical to the candidate; Section 4.9
  remains untouched at target line 1384.
- Repeated candidate and canonical gates preserve 52 paired TeX environments,
  ten labels, fourteen ordinary and six equation references, six citation
  occurrences over three bibliography keys, eleven list items, 367 protected
  mathematical zones, eleven diagrams with 28 arrows, eight drawing commands,
  and seven index entries. Han residue and placeholders are zero. This source
  span contains no exercises, hints, answers, or solutions, and none were
  invented.
- Thirty terminology rows are admitted. The 465-row glossary is 74,335 bytes,
  SHA-256
  `bb58d18ad5802c5c2159db092f0fc322761f8f9559ea7efd3789ab8d7317e582`.

Two source corrections are explicit: `O013-LI-U032-COR-001` changes the
normal-closure endpoint from the generator count `w_n` to the relation count
`w_m`; `O013-LI-U032-COR-002` repairs `Guranlnick` to `Guralnick`. Thirteen
protected mathematical-text fragments and four citation locators are
localized without changing formulas or bibliography keys. Two separate
target-only digital reflows split finite-support set-builder displays into
readable rows; set membership, quantifiers, finite-support conditions, and
term order remain unchanged. The reflows are not represented as source
corrections.

## Reader, PDF, and visual evidence

- Final reader: thirteen pages, 149,624 bytes, SHA-256
  `904330916e20f0782b6464cb85e07001851940f4adf153f6592cd34087dbadbf`.
- Clean build I: 149,636 bytes, SHA-256
  `c7f06f1579bfd0abfc70a8af7a2fdf6b39fc10ef37bc2a951b8f38f47373151f`;
  clean build J is byte-identical to the release artifact. All pages are
  decoded-pixel-identical between the builds within both Poppler and MuPDF.
- All 78 final build/artifact renders are edge-clear. Every page was inspected
  at full readability in both renderers. The two measured 22.16992 pt and
  27.03485 pt display overflows are gone. No clipping, collision, broken
  stroke, missing glyph, tofu, edge contact, ambiguous progress block, or
  unintended blank page remains.
- The final unencrypted PDF 1.7 has `/Lang id-ID`, exact metadata, three
  outline entries, resolving destinations, thirty internal actions, six safe
  URI actions, and 28 embedded fonts. It has no JavaScript, form, launch
  action, attachment, or out-of-bounds geometry.
- The sanitized final log has zero profile paths, errors, unresolved
  references/citations, missing characters, empty targets, or overfull boxes.
  Exactly three underfull hboxes were inspected at their rendered locations;
  none impairs reading. The fixed toolchain advisories and untagged-PDF
  limitation are disclosed.

Controlling evidence: `qa/UNIT_032_VISUAL_QA_20260826.md` (5,996 bytes,
SHA-256 `8f0e63c07a43e1c8e96415ccda97507c6a1e1a81b4cf2c344b9fb761a653a976`),
`qa/unit-032-evidence/structure-and-pdf-qa.json` (29,718 bytes, SHA-256
`c1a4b17ca7205f3ae76be812de61eb009ba6043c3e6d3090ee73e1b47add0184`),
and `qa/unit-032-evidence/render-hash-inventory.json` (58,936 bytes, SHA-256
`6fc75108fff42b86e040ec7b90cd2d05f98c75756bbcc35b0a66293e6bfd7e7b`).

## Backend and rights

The canonical backend JSON is 460,681 bytes, SHA-256
`a3f68cd45d5fc44720e769c7a12d745a4af78d7a361e6e8b81a1c5019be1a030`.
The generator and dedicated validator pass repeated byte-identical
regeneration plus the shared schema/UUIDv5/CSV gate. The backend contains 589
concept-compatible records, one section, eighteen QA events, and six exact
CSV projections; 660 UUIDv5 identities and 94 binding occurrences across 39
live paths are audited. It records the two corrections, two reflows, thirteen
protected-text localizations, four citation-locator localizations, and all six
citation occurrences as distinct evidence. Validation is 5,422 bytes,
SHA-256 `b66c40151489b4d162e63e9edef3da1d7c593362002bb8e0b9a6f5ba3410be6d`.

The principal text and translation remain CC BY 4.0. The credited AJbook
fragment remains CC BY-SA 3.0; bundled Noto fonts remain OFL 1.1; unused
`Lanzhou.png` remains CC BY-SA 3.0. The aggregate is not relabeled under one
blanket license. Source attribution, independent-derivative status,
non-endorsement, and production provenance (`OpenAI Codex gpt-5.6-sol,
Ultra`, acting on the user's instruction) are explicit.

Verdict: source, translation, mathematics, TeX topology, terminology, reader,
visual/PDF surfaces, backend, provenance, and component rights are mutually
bound and pass. Unit 032 is ready for local admission and authorized narrow
publication. This does not claim that Chapter 4, Li Volume 1, or O013/D70 is
complete.
