# Unit 014 admission - Dasar-Dasar Fungtor Adjoin

Status: admitted locally after independent source comparison, protected-topology
review, two clean builds, PDF checks, terminology QA, and all-page visual QA.

## Frozen content

- Authority: Wen-Wei Li, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Range: complete `chapter2.tex:766-909` (144 physical lines), ending
  immediately before the first further example at line 910.
- Source span: 10,365 bytes; SHA-256
  `930232390be4aed3aea2155ae1779e95eae621bb7b23ea9c6899828b46ce2960`.
- Indonesian span: 11,655 bytes; SHA-256
  `5526e8eb99dba9dc3e0eebbd1ddd278eb6343fd50a1d18cf0f6715f09f6e1ed2`.
- Full current target: 155,822 bytes; SHA-256
  `bcf19c8d261947fa619c0257351c29217f401bc1c9453ad91286ff96c1bd69a5`.
- Reader: `artifacts/unit-014-bab-2-fungtor-adjoin-dasar.pdf`, 9 pages,
  121,761 bytes; SHA-256
  `1241ca5ff345ff5315d5e3f4e6fcb1f37af2b0e948f458306c4b790035779d04`.
- Final log: `qa/UNIT_014_BUILD_FINAL.log`, 85,851 bytes; SHA-256
  `7045b0b1ede153a2dcaea05e03139028f95621b5b44b9ba0bdea2c1cc0fb97cb`.

## Content, terminology, and corrections

The span preserves all mathematical content, environment topology, labels,
references, citation, index entries, and 13 TikZ-CD diagrams. The checker sees
99 source mathematics surfaces and 100 target surfaces solely because one
source surface containing both `eta` and `epsilon` was deliberately segmented
into two Indonesian inline surfaces joined by Indonesian prose. The normalized
mathematics is equivalent after the four disclosed source corrections. All 30
environment starts, six labels, five ordinary references, nine equation
references, one citation, two index entries, and 82 TikZ-CD arrows pass exact
topology checks. Han residue is zero and line 910 remains the next source-order
boundary.

- `O013-LI-U014-COR-001`: source line 785 writes `\varphi_{VW}` although the
  indexed family consistently uses `\varphi_{V,W}`; the target restores the
  separating comma.
- `O013-LI-U014-COR-002`: source line 789 describes the finite-dimensional
  restriction as having domain `Vect_f(k)` rather than its opposite category;
  the target supplies the required `^{\mathrm{op}}`.
- `O013-LI-U014-COR-003`: the same display inconsistently writes `Vect(k)_f`;
  the target uses the book's established `Vect_f(k)` notation.
- `O013-LI-U014-COR-004`: source line 799 indexes counit components by objects
  `X` of the first category; the target indexes `(\varepsilon_Y)` by objects
  `Y` of the second category.

The bounded Indonesian field-usage recheck remains applicable and supports the
controlled forms `fungtor`, `fungtor adjoin`, `pasangan adjoin`, `transformasi
natural`, `unit`, `kounit`, and `identitas segitiga`. The translation does not
claim stronger attestation than the documented terminology evidence provides.

## Build and reader QA

Two clean correction builds (`build/unit-014-equation-fix-e` and
`build/unit-014-equation-fix-f`) produced 9 pages. All 9 MuPDF pages and all 9
Poppler pages are pixel-identical within each renderer at 144 dpi. Per-page and
concatenated render hashes are recorded under `qa/unit-014-evidence/`.

The standalone driver now sets the Chapter 2 equation counter to four before
this source span. Consequently `eqn:unit-adjunction` prints as (2.5) and
`eqn:unit-counit-relation` as (2.6), matching the identifiers in the complete
source book. The first public Unit 014 checkpoint incorrectly restarted these
labels at (2.1) and (2.2); that packaging defect did not alter the translated
mathematics and is superseded by this corrected reader.

The final log has zero blockers: no undefined reference or citation,
multiply-defined label, missing glyph, TeX/package error, fatal error, or
emergency stop. It contains two tiny non-blocking overfull hboxes of 1.01085 pt
and 3.69489 pt; both remain visually inside the safe text area. Five suppressed
empty external-document targets are intentional: the frozen cross-reference
witness supplies numbers without inventing external URLs. The remaining
underfull and package-compatibility notices are non-blocking.

All 9 pages were visually inspected in Poppler and MuPDF. The reflow keeps the
diagrammatic conclusion on a useful content page and the nonempty term index on
one final page. No clipping, overlap, missing content, blank page, or unreadable
content was found. The PDF declares `id-ID`, has 23 named destinations, three
outline entries, 13 GoTo and three URI actions, and no Launch, GoToR,
JavaScript, or Widget action. All fonts are embedded.

## Rights and provenance

The source author remains Wen-Wei Li. The principal source text and its
Indonesian translation are CC BY 4.0; the separately credited AJbook class
fragment retains CC BY-SA 3.0; bundled fonts retain OFL 1.1. These rights
remain component-specific. This is an independent, non-endorsed derivative.
Production provenance records the exact model identification
`OpenAI Codex gpt-5.6-sol, Ultra` separately from source authorship and every
human-contributor credit.
