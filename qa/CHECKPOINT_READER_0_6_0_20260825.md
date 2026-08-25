# Checkpoint reader 0.6.0 - build and QA receipt - 2026-08-25

Status: **PASS; ready for the existing GitHub and Zenodo lineages.**

## Artifact and exact scope

- Reader: `output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-0.6.0-reader.pdf`.
- Identity: 3,658,991 bytes; SHA-256
  `a147c05617e61a5d22a0038f2b5b995d668f387f9531514261d273fe9b6618c5`.
- Pagination: 229 pages - one checkpoint cover followed by all 228 admitted
  source-reader pages in exact unit order.
- Coverage: complete Pendahuluan, Chapter 1, Chapter 2, and Chapter 3 in Units
  001-024. Li Chapters 4-10, the Duncan component, the six CRing spans, and the
  connective/mastery layer remain absent. This is a partial active checkpoint,
  not the complete O013 course.
- Unit starts: 2, 23, 35, 46, 54, 66, 75, 79, 84, 97, 112, 119, 129, 136,
  145, 155, 171, 180, 184, 196, 201, 210, 219, and 226.

## Deterministic construction and structure

The builder pins every one of the 24 admitted inputs by exact filename,
SHA-256, and page count. A separate temporary invocation reproduced the reader
byte-for-byte with the same SHA-256. The PDF has uniform 498.90 by 708.66 point
pages, zero rotation, document language `id-ID`, and outline mode enabled.

Navigation contains 766 named destinations across all 24 namespaced units and
503 link annotations: 414 internal `GoTo` actions and 89 intentional URI
actions. Every named destination maps to a valid page; every named internal
target resolves; no malformed or broken target, unsafe action, remote launch,
attachment, collection, open action, additional action, or AcroForm exists.
The top-level outline contains the checkpoint entry plus all 24 units in source
order. In particular, the repaired Unit 024 `page.1` index target survives the
merge and closes correctly.

## Render, text, font, and accessibility QA

MuPDF and Poppler each rendered all 229 pages at 120 dpi. All 228 inherited
unit pages are pixel-identical to their separately admitted readers; raster
mismatches are zero. Poppler emitted 149 legacy font warnings, but their
normalized classes and counts match the 24 admitted source PDFs exactly, so the
merge introduced no new warning. The only blank page is intentional inherited
checkpoint page 5. All 599 font objects are embedded. Every nonblank page
extracts text, the metadata and cover state the partial scope and component
rights, and no filled/unfilled status legend appears.

All 229 pages were inspected through 20 contact sheets, with the cover and
Chapter 3 transitions also inspected at full resolution. No clipping, overlap,
missing content, broken diagram, black square, unreadable page, or accidental
blank page was found. The cover is centered, page-filling, reader-first, and
lists all 24 unit starts legibly. The PDF remains untagged; tagged-PDF
accessibility is not claimed.

## Bound evidence

- deterministic builder: 14,849 bytes; SHA-256
  `caec7a2acc505fe8a17831c719a0c5a999ac34b6b1d471c2cea5bb5eeabaa9cd`;
- fail-closed QA runner: 38,484 bytes; SHA-256
  `bd17d43fa371371ae792433c4518f9e5d808599afb6b88f51223e00f61280c9c`;
- machine QA record: 132,747 bytes; SHA-256
  `eb7faad5b8d2fd7c17e4fac1c924d4f8d9320d0ec28b2823364c17d0ed991b03`;
- all-page visual receipt: 1,495 bytes; SHA-256
  `8fc59ba81a8064962072983c0e2e18a419e9b6998216716e96d40f141cfefe5d`.

Principal text and the Indonesian adaptation are CC BY 4.0. The credited
`Lanzhou.png` and `AJbook.cls` fragment retain CC BY-SA 3.0; bundled Noto fonts
retain OFL 1.1. This is an independent, non-endorsed derivative. Production
provenance: `OpenAI Codex gpt-5.6-sol, Ultra`.
