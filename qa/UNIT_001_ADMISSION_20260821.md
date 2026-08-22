# Unit 001 admission receipt — Pendahuluan

Date: 2026-08-21  
Decision: admitted as the first independently buildable `id-ID` reader unit.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit: `c4f7a01f68f5f407906b4b970640cddbbad85f6b`
- Upstream tree: `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Source `prelude.tex`: 25,159 bytes; SHA-256 `eb854d4fa7bca307ee5290da41d642a9d64bfa0f7e919760cc21fd7fbb5cabbd`
- Target `repo/source/prelude.tex`: 35,393 bytes; SHA-256 `60076e51a9a2e739628f0e0ac5daa02ad117ce9ea558834ce154a24b9eee685c`

## Translation and mathematical audit

The complete prelude was reviewed against the frozen Chinese source in source order. All headings, paragraphs, displayed and inline mathematics, citation keys, cross-reference keys, diagrams, and the index entry are retained. The audit found no unresolved P1, P2, or P3 issue. Source-specific naming and index conventions are identified honestly rather than silently presented as Indonesian conventions. No exercise, hint, answer, or solution occurs in this unit.

## Exact admitted build

- Driver: `repo/source/unit-001-pendahuluan.tex`, 2,328 bytes, SHA-256 `bf680cdaed56b99dfdc91c259fd0bbf4d98bdc04008a3c715e72dfc91187038b`
- Build script: `scripts/build_unit_001.ps1`, 2,560 bytes, SHA-256 `12b4c5a731947a324f8c5cecd9ce886a8e8cdcd79a70c258102d573d44a755bc`
- Reader: `artifacts/unit-001-pendahuluan.pdf`, 199,926 bytes, SHA-256 `b3fca2af76b793a19877ffc822d6ec89c2494641f7e1dfa468b158c7bec30a3e`
- Portable build-log summary: `qa/unit-001-evidence/build-log-summary.txt`, 1,756 bytes, SHA-256 `e340549356454de27ece44adc231f0468fcfbf98b8ef56610c5525ab2e7ebedd`. The machine-specific raw final log is retained locally: 87,018 bytes, SHA-256 `923d8b61f5e47da1cfba3fc4167fa876128eb7417334eb6fc3e75b52aa88a292`.
- Toolchain witness: MiKTeX 26.5 XeLaTeX, Biber 2.21, MakeIndex, then three convergence passes; shell escape disabled.
- Result: 21 pages; zero TeX errors, undefined citations, undefined references, duplicate destinations, or missing-character warnings.
- Navigation: PDF language `id-ID`; 4 outline roots; 36 named destinations; 39 internal GoTo actions, 8 intentional URI actions, no GoToR action, and no unresolved named internal link.
- The 13 small overfull boxes are visually contained; the largest is 18.76993 pt in a bibliography entry. Five suppressed empty-target messages intentionally prevent the unit-only cross-references from creating false links to a nonexistent external PDF.

`SOURCE_DATE_EPOCH=1784878369` and a fixed PGF seed make dates and rendered content deterministic. Two clean terminology-QA builds in different output directories rendered to 21 pairwise identical 144-dpi PNG pages in both Poppler and MuPDF; extracted text is also pairwise identical. XeTeX nevertheless serialized the two PDF containers to different byte hashes, so this receipt does not claim bit-identical PDF reproduction across output directories.

## Visual and portability audit

The exact admitted PDF was rendered in full with MuPDF and Poppler: 21/21 pages from each renderer. MuPDF produced no stderr and was the authoritative visual witness for embedded CJK text. The installed Poppler lacks the Adobe-GB1 CMap and emitted a 4,601-byte environment warning stream; this does not indicate a missing embedded glyph in the PDF. All six MuPDF contact sheets and the full-resolution dense algebra-structure table were inspected. No clipping, collision, blank content, broken diagram, unreadable table, or pagination defect was found.

Compact portable evidence is under `qa/unit-001-evidence/`.

## Post-admission Indonesian terminology QA

On 2026-08-22, the bounded primary-source terminology check recorded in
`qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md` changed the house
term `funktor` to the attested `fungtor` and changed the single inconsistent
chapter-overview phrase `transformasi alami` to `transformasi natural`. The
unit was rebuilt twice and all 21 pages were reinspected. Mathematics,
identifiers, source topology, and pagination are unchanged. Model: OpenAI Codex
gpt-5.6-sol, Ultra.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with Wen-Wei Li credited and the independent, non-endorsed derivative status stated. Component exceptions remain separately recorded: the source-map fragment in `AJbook.cls` is CC BY-SA 3.0, and bundled Noto fonts are OFL 1.1. The CC icon and bibliographic/source material retain their recorded provenance. Admission does not flatten these component rights.

## Cursor

Unit 001 is admitted. The next translation cursor is the beginning of `repo/source/chapter1.tex`; Chapters 1–10 remain in the source language until reviewed and admitted in later contiguous units.
