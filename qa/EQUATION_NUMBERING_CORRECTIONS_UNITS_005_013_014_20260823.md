# Standalone equation-number continuity corrections - Units 005, 013, and 014

Date: 2026-08-23

Status: admitted locally; ready for the existing GitHub lineage.

## Scope

The three standalone readers previously restarted the chapter equation counter
at zero. Their translated source spans, mathematics, labels, references,
citations, diagrams, indexes, terminology, attribution, and component rights
were already correct. Only the standalone driver state and the downstream
reader/backend/evidence bindings changed.

| Unit | Source-order correction | Corrected reader identity |
|---|---|---|
| 005 | Set Chapter 1's equation counter to 1 before the span; equations now print as (1.2) and (1.3). | 12 pages; 128,554 bytes; SHA-256 `205359b6c3b406a4f6595908381147e2bb3dba6aab8fdc9057436b11bec252de` |
| 013 | Set Chapter 2's equation counter to 2 before the span; equations now print as (2.3) and (2.4). | 7 pages; 106,162 bytes; SHA-256 `03ced2b80bf14814d01bc73cf378bfab820ec40ad0571eaa33cf514d79d760cf` |
| 014 | Set Chapter 2's equation counter to 4 before the span; equations now print as (2.5) and (2.6). | 9 pages; 121,761 bytes; SHA-256 `1241ca5ff345ff5315d5e3f4e6fcb1f37af2b0e948f458306c4b790035779d04` |

## Verification

- Unit 005: two clean builds; 12/12 Poppler and 12/12 MuPDF pages
  pixel-identical; every page inspected; backend validation passed.
- Unit 013: two clean builds; 7/7 Poppler and 7/7 MuPDF pages
  pixel-identical; every page inspected; backend validation passed.
- Unit 014: two clean builds; 9/9 Poppler and 9/9 MuPDF pages
  pixel-identical; every Poppler page and both changed MuPDF equation pages
  inspected; backend validation passed.
- The Unit 013 and Unit 014 translation-structure gates were rerun after the
  repairs and passed with their original source boundaries and declared source
  corrections unchanged.
- No content outside these three standalone reader packages was changed by the
  correction.

Detailed unit-level evidence is in:

- `qa/UNIT_005_EQUATION_NUMBER_REPAIR_20260823.md`;
- `qa/UNIT_013_EQUATION_NUMBER_CORRECTION_20260823.md`;
- `qa/UNIT_014_EQUATION_NUMBERING_CORRECTION_20260823.md`.

## Rights and provenance

Wen-Wei Li remains the source author. The principal source text and Indonesian
translation remain CC BY 4.0; the credited AJbook fragment remains CC BY-SA
3.0; bundled Noto fonts remain OFL 1.1. This is an independent, non-endorsed
derivative. Production provenance is recorded separately as OpenAI Codex
gpt-5.6-sol, Ultra.
