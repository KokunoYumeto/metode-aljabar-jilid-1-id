# Unit 044 — Complete Chapter 6 admission — 2026-08-28

Result: **PASS / admitted locally for publication**.

## Exact source and target closure

- Authority: `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter6.tex`; 1,994 records; 160,950 bytes; SHA-256 `c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49`.
- Complete checked candidate and canonical target: `repo/source/chapter6.tex`; 1,994 records; 193,563 bytes; SHA-256 `15c09af18eeab6ce1a4c5a4cb69b1b3a42bc2422b015f21f77ccfbb3c94f7e14`.
- Whole-chapter checker: `build/chapter6-batch-candidate/check_chapter6_complete.py`; 4,866 bytes; SHA-256 `d19acd54cd5bb96abe66fe678c8d5a8070fb6de5d681b8a81d6bc0c9c5001a86`; four segment checks plus whole-chapter closure all passed.
- Preserved topology: 12 sections, 98 labels, 224 references, 6 citation occurrences, 70 index entries, 132 list items, 14 top-level exercises, 22 exercise items including subitems, 8 hints, 37 `tikzcd` diagrams, and 7 `tikzpicture` diagrams. There are no answers or source solutions.
- Terminology registry after the one-time Chapter 6 merge: `00_control/TERMINOLOGY.id-ID.csv`; 93,793 bytes; SHA-256 `92b6aa981d5631ecb4b57379b7f38b7f3ed8f63c70bc12d05ed206550823c342`.

## Reader and layout gate

- Canonical translated TeX was not altered for typography. Three reader-only line-breaking changes are generated fail-closed from the canonical hash by `scripts/prepare_chapter6_reader_source.py`.
- Generated reader source: `build/chapter6-reader-source/chapter6-reader-reflow.tex`; 1,994 records; 193,613 bytes; SHA-256 `e83fc702c2a2839c1e3941b9ab0a83c67b474bd72c2846433dac854c959f8f28`.
- Complete Chapter 6 PDF: `artifacts/unit-044-bab-6-modul-id.pdf`; 75 pages; 465,036 bytes; SHA-256 `2c493005920fdd757e5786477fdf99b20aced1653348be7a076fa7a829a5c1d3`.
- Final build log: `qa/CHAPTER_6_BUILD_FINAL.log`; 89,084 bytes; SHA-256 `9640c9a29997b6d758368dda9d9355a11c139de3a08d871dde3451b2a908e064`; zero overfull boxes and zero unresolved references/citations or fatal diagnostics.
- PDF structural and all-page visual receipt: `qa/CHAPTER_6_PDF_STRUCTURAL_QA.json`; 2,174 bytes; SHA-256 `5e0297d266445ed8eb83e0bcabf796039e9450f2225ba347c79f94bae83ed6b0`. All 75 pages were rendered at 96 dpi and inspected across five ordered contact sheets; no clipping, overlap, missing/blank page, or off-page diagram was observed.

## Combined reader and backend

- Reader-first checkpoint through complete Chapter 6: `output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-through-bab-6-reader.pdf`; 460 pages; 6,750,492 bytes; SHA-256 `ff8a1fdb65e36bfa8dbb47dd707c96e10daf2d6bf33363ecd2da6f73f6d2f4cd`.
- The combined-reader check compared all 384 inherited content pages against the prior Chapter 5 checkpoint and all 75 appended pages against the standalone Chapter 6 reader: zero identity mismatches. The new cover, transition pages 385/386, and final page 460 passed the bounded 120-dpi visual check. Receipt: `qa/unit-044-evidence/checkpoint-through-bab-6-structural-qa.json`; 1,085 bytes; SHA-256 `2c10dc4827626ee674107a25f7c0c21a16ce10242719d40874894d01d4d0c4de`.
- Canonical backend: `backend/data/unit-044-bab-6-teori-modul.json`; 225,398 bytes; SHA-256 `aaf3db8135914ca8ceaef457883666da8b2f814833147792b819f0f09c2a5eac`.
- Backend validation passed schema and semantic checks with 203 entities, 12 sections, 34 outcome/exercise/hint concepts, 20 prerequisites, 5 unique citations, 44 diagrams, 70 index entries, two PDF surfaces, six QA events, component-separated rights, and six deterministic CSV projections. Receipt: `qa/unit-044-evidence/backend-validation.json`; 2,539 bytes; SHA-256 `68656b8a7c6a4d6b8ad8ec9c70a113935dc00e02362d15268616239013d970d3`.

## Rights and status boundary

The principal text and independent Indonesian adaptation remain CC BY 4.0. The credited AJbook fragment and retained Lanzhou component remain CC BY-SA 3.0, Noto remains OFL 1.1, and Fandol remains GPLv3 with its font exception. Component notices control; the aggregate is not blanket-relicensed. The edition is independent and non-endorsed. Production provenance is recorded as OpenAI Codex gpt-5.6-sol, Ultra, while Wen-Wei Li remains credited as author of the source work.

Unit 044 is admitted. This receipt does not claim that the full book or O013 composite is complete. The next source-order production boundary is complete Chapter 7.
