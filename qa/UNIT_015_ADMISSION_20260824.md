# Unit 015 admission - Contoh, Keunikan, dan Ekuivalensi Adjoin

Status: admitted locally after independent source comparison, protected-topology
review, semantic review, terminology QA, two clean final builds, PDF checks,
and all-page visual QA in two renderers.

## Frozen content

- Authority: Wen-Wei Li, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Range: complete `chapter2.tex:910-1110` (201 physical lines), corresponding
  to source printed pages 54-58 and physical pages 60-64 of the official PDF.
  Line 1111 begins Section 2.7 on limits and remains the next source-order
  boundary.
- Source span: 16,925 bytes; SHA-256
  `49c812f4cdb1929cf11e1bc3e5d916d21e82051d17a686f826c1b171a1f33062`.
- Indonesian span: 19,355 bytes; SHA-256
  `df3c65bfea7f7272a31809b96b5ae18fdf966afe22e9ab38a0d8f9d35680520f`.
- Full current target: 158,252 bytes; SHA-256
  `a106ec94b9c2b4a276371e6527b0c7c86dfd84538dde0be8e31848d59d2caf8c`.
- Reader: `artifacts/unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin.pdf`,
  10 pages, 120,466 bytes; SHA-256
  `6f2a9be12465300ac7af2ea086b643b6891b1f9e23af66241a40086ac476c8ef`.
- Final log: `qa/UNIT_015_BUILD_FINAL.log`, 84,703 bytes; SHA-256
  `6d7fa510890ee32c19b65b2b51046b771f8e93570f6d6f1a9f17f0745fcc5874`.
- Structural checker: `scripts/check_unit_015_structure.py`, 15,739 bytes;
  SHA-256
  `aac9b5b614976524369e57054044384a7e0ac4d10a72548de9f18d905c898f78`.

## Content, topology, and corrections

The span preserves all mathematical content and source topology. The live
checker passes all 232 source and target mathematical surfaces, all 35
environment starts, nine labels, eight ordinary references, twelve equation
references, the citation signature, three index entries, four TikZ-CD diagrams,
sixteen TikZ pictures, 75 nodes, 32 coordinates, four draw commands, thirteen
TikZ-CD arrows, and four item commands. The normalized mathematical multiset is
equivalent after the two declared corrections. Han residue is zero.

- `O013-LI-U015-COR-001`: source line 962 writes the second adjunction tuple as
  `(F', G,' ...)`, attaching the prime after the comma; the target restores
  `(F', G', ...)`.
- `O013-LI-U015-COR-002`: source line 997 uses midpoint node `A1` inside the
  second TikZ picture even though only local node `A2` is defined there; the
  target uses `A2`, preventing an accidental cross-picture reference.

The final semantic review also tightened three Indonesian sentences at lines
919, 923, and 1100. These are fluency refinements only: they restore the
controlled term `fungtor adjoin kiri`, make the reference to Contoh 2.4.6
grammatical, and retain the proof's authorial voice. No formula, identifier,
environment, reference, diagram, citation, or index surface changed.

## Terminology QA

The bounded official arXiv search found no suitable Indonesian same-field
source with downloadable TeX, so the documented fallback was used honestly.
The four-page UNDIP Chapter I PDF remains 163,251 bytes with SHA-256
`611b78c88407037489f22814bf054e00ff0f283c702a06082a3a583e9ab35fcb`;
the seven-page UGM article remains 382,376 bytes with SHA-256
`4099c3d8aff59e723470f69b4d152b037261bc26d54ef74f1365377f05c25834`.
Their live pages support the controlled category/algebra choices `fungtor`,
`transformasi natural`, `kategori`, and `gelanggang`; the record does not
misrepresent them as direct attestation for every new Unit 015 term.

The Unit 015 delta adds controlled rows for `topologi diskret`, `topologi
takdiskret`, `grup bebas`, `modul bebas`, `gelanggang polinomial`,
`abelianisasi`, `pengompakan`, and `diagram untai (string diagram)`. These
choices follow mathematical meaning, established Indonesian word families,
and corpus consistency. No earlier admitted reader required a terminology
correction at this gate. Full source identities and adjudication remain in
`qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md`.

## Build and reader QA

Two clean final builds (`build/unit-015-final-c2` and
`build/unit-015-final-d2`) produced 10 pages. Their PDF container bytes differ,
but this is explicitly treated as functional reproducibility rather than byte
identity: all ten Poppler pages and all ten MuPDF pages are pixel-identical
within each renderer at 144 dpi, and their 16,531-byte layout-preserving text
extractions are identical with SHA-256
`e8756d14d02e17cb605da0b5bdcf3806ea817490d9624679a55aeeb2836b8787`.
Per-page and concatenated hashes are recorded under `qa/unit-015-evidence/`.

The standalone driver sets the Chapter 2 equation counter to six before this
continuation. The final AUX therefore maps `eqn:adj-zigzag-1` to (2.7),
`eqn:adj-zigzag-2` to (2.8), and `eqn:adj-equiv-two-expression` to (2.9),
exactly matching the complete source book's equation sequence.

The initial 1.45-spaced A/B builds occupied 11 pages and left the proof's
closing sentences on an orphan content page. The restrained `1.30` digital
reflow produces 10 pages and keeps the proof conclusion and closing reference
together without altering content, mathematics, or identifiers. The final log
has zero blockers: no undefined reference or citation, multiply-defined label,
missing glyph, overfull hbox, TeX/package error, fatal error, or emergency
stop. One cover alignment underfull hbox, one underfull vbox, seven suppressed
empty external-document targets, package notices, and the final makeindex
reminder are non-blocking and were visually checked.

All ten final pages were personally inspected at original rendered resolution
in both Poppler and MuPDF. No clipping, collision, missing content, unintended
blank page, malformed formula or diagram, missing glyph, unreadable surface,
or index defect was found. The PDF declares `id-ID`, carries the correct title
and author metadata, has 30 named destinations, two outline entries, eighteen
GoTo actions and five URI actions, and has no Launch, GoToR, JavaScript,
Widget, or other action. All 23 fonts are embedded. Extracted text contains no
literal `??`, replacement character, NUL, English `Lemma`, or Han residue.
The PDF remains untagged; that inherited accessibility limitation is recorded
and is not represented as passing tagged-PDF conformance.

## Rights and provenance

The source author remains Wen-Wei Li. The principal source text and Indonesian
translation are CC BY 4.0. The credited `AJbook.cls` fragment retains CC BY-SA
3.0; `Lanzhou.png` in the repository closure also retains CC BY-SA 3.0 but is
not used by this Unit 015 reader; bundled fonts retain OFL 1.1. These rights are
component-specific and are not flattened into one blanket license. This is an
independent, non-endorsed derivative.

Production provenance records the exact model identification `OpenAI Codex gpt-5.6-sol, Ultra`
separately from source authorship and every human-contributor credit.
