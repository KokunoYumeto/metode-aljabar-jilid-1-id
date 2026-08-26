# Unit 031 visual preflight — 2026-08-26

Status: **PASS WITH WARNINGS**. Two independent clean builds and the release
artifact were structurally inspected and rendered across all 9 pages.
No actionable defect remains.

- Build I: 9 pages / 126,051 bytes / SHA-256
  `9802661e5558d1879616703538f848a3091b668383fa2b0679c8913337566a43`.
- Build J: 9 pages / 126,053 bytes / SHA-256
  `313667c3f87439ccaac3f8708653bb352af0ba7a16c9d09b159ad1b836cc32fb`.
- Artifact: 9 pages / 126,053 bytes / SHA-256
  `313667c3f87439ccaac3f8708653bb352af0ba7a16c9d09b159ad1b836cc32fb`; byte-identical to build J.
- Poppler and MuPDF produced 54 full-page renders. Every
  same-renderer decoded-pixel comparison passed and every outer edge was clear.
- Metadata, outline, destinations, links, safe actions, embedded fonts, three
  extraction surfaces, page geometry, and all-page visual review passed.
- Final diagnostics contain zero errors, unresolved references/citations,
  missing characters, empty targets, overfull boxes, or underfull boxes.

The PDF is untagged, so no tagged-accessibility claim is made. pypdf's exact
17-NUL mathematics-font extraction limitation is disclosed; Poppler and MuPDF
contain no NUL or replacement characters. Fixed toolchain advisories are
retained in the evidence log.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.
