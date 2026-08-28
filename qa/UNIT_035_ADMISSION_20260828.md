# Unit 035 local source, reader, and backend admission — 2026-08-28

Status: **LOCALLY ADMITTED; PUBLICATION PENDING.** This receipt makes no remote
or DOI claim. Unit 035 completes Chapter 4 with Section 4.11, “Grup dalam
Kategori,” and the complete Chapter 4 exercise block.

## Authority and canonical source

- Authority: Wen-Wei Li, *Methods of Algebra*, Volume 1, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Frozen `chapter4.tex`: 154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Exact authority boundary: lines 1745–1898, 154 LF records, 14,398 bytes,
  SHA-256
  `f841860520d4ab35dc82354f288bc295c4681f9faffc8f5a645c92a3af1dd287`.
- Indonesian candidate:
  `build/unit-035-candidate/chapter4-groups-in-categories-and-exercises-id.tex`,
  154 records, 18,089 bytes, SHA-256
  `5d9bf6e5c9c17c83821f1bba63078f4d28e3836428f4557e0727ee5b1046c2ca`.
- Canonical `repo/source/chapter4.tex`: 193,626 bytes, SHA-256
  `2b682d67292e4c439ccc9f6d46f72d3d0eb7cb5bf8b3a3a5999210c45ef547c5`;
  canonical lines 1740–1893 are byte-identical to the admitted candidate.

The single deterministic translation gate preserves 30 paired environments,
three labels, 15 references, two index entries, 247 protected mathematics
zones, eight diagrams with 35 arrows, all 26 top-level exercises / 36 exercise
and subitem records, five hints, and zero source solutions. There is no Han
residue, placeholder, malformed UTF-8, or uncontrolled structural change.

`O013-LI-U035-COR-001` corrects the swapped finite-family bounds in the Neumann
lemma exercise: the source defines subgroups through `H_n` and `m` cosets for
each subgroup, so the Indonesian edition uses `1 <= i <= n` and
`1 <= j <= m`. The correction is explicit and separately provenanced.

## Reader

- PDF: `artifacts/unit-035-bab-4-grup-dalam-kategori-dan-latihan-id.pdf`, nine
  pages, 135,943 bytes, SHA-256
  `1cf97dd523ae1a8c5185c4b22a8e6b0dab6e7514ab5387c34959c417f4e35442`.
- Final log: `qa/UNIT_035_BUILD_FINAL.log`, 87,586 bytes, SHA-256
  `1b87602c47d5b602a71b788ea14a18f10f4816ae1c0522bbd828dc51b02a2a7a`.
- All-page contact sheet: 1,688,795 bytes, SHA-256
  `936d83afb23c5eb9cc9f25d964514977a016f0c53e17e3b6ace246e5ee9cb1bf`.
- Visual receipt: `qa/UNIT_035_VISUAL_QA_20260828.md`, 2,128 bytes,
  SHA-256
  `66c8c9202730583a1b617b19f0177c68d241208b7316eab9efd966c44943ad2f`.

All nine pages were inspected. The extracted text contains no unresolved
reference marker, Han residue, or replacement glyph. All fonts are embedded;
the file has no encryption, forms, JavaScript, or attachments. The sole
32.49-point diagnostic belongs to a wide categorical-equivalence diagram on
page 5; the full-resolution render proves that it remains within the page and
is legible. No repeat visual gate is warranted absent a new concrete defect.

## Modular backend

- JSON: `backend/data/unit-035-bab-4-grup-dalam-kategori-dan-latihan.json`,
  239,379 bytes, SHA-256
  `372a7dfa2ffc919b7fe5859b020c87f4bd143669331aeed1c0c270c65e9f02a7`.
- Validation receipt: `qa/unit-035-evidence/backend-validation.json`, 2,495
  bytes, SHA-256
  `0b5699f7e7f7d576c80379781ec809f7d7f4a9cea008d3e999e0a87925922c88`.
- Generator: `scripts/generate_unit_035_backend.py`, 25,311 bytes, SHA-256
  `2051242d17e9f9366084754ada188c431433d6f840efe26865f00004f2311259`.

The schema-valid dataset contains 429 entities, 379 concepts, 20 prerequisite
links, two sections, eight diagrams, and two index entries. Two generator
passes agree byte-for-byte; the shared validator and all six deterministic CSV
projections pass.

## Rights, provenance, and cursor

The principal source and translation remain CC BY 4.0. The credited AJbook
fragment remains CC BY-SA 3.0; Noto fonts remain OFL 1.1; Fandol 0.3 remains
GPLv3 with its document-embedding font exception; unused `Lanzhou.png` remains
CC BY-SA 3.0. The aggregate is not blanket-relicensed. Attribution,
independent-derivative status, non-endorsement, and production provenance
(**OpenAI Codex gpt-5.6-sol, Ultra**, acting on the user's instruction) remain
explicit.

The complete Chapter 4 source, reader, and backend are locally admitted. The
next source-order cursor is `chapter5.tex:1`; remote publication and anonymous
byte readback are the only remaining operations for this boundary.
