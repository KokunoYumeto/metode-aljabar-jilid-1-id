# Unit 026 visual and PDF QA — 2026-08-25

Status: **PASS WITH WARNINGS**. Required identity, replay, same-renderer decoded-pixel, structure, navigation, font, text, action/link, and clipping gates pass.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
| `build/unit-026-c-20260825/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.pdf` | 115,288 | `de415fed2c9aceafc41d5e22d2dd6d73e81c37f3a3463af18d73f59409b09dbf` |
| `build/unit-026-d-20260825/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.pdf` | 115,284 | `e3c0e0241901eb0f5f2477a1fe09f64eff34af325dc209b25aa8d71900deb089` |
| `artifacts/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi-id.pdf` | 115,284 | `e3c0e0241901eb0f5f2477a1fe09f64eff34af325dc209b25aa8d71900deb089` |
| `qa/UNIT_026_BUILD_FINAL.log` | 86,417 | `f26903ed598b9191005e00dd8f2d55b2de09eb0464722ed5bef24e9f9f93f8fd` |

Build D and the artifact are byte-identical. All PDFs have 9 pages.

## Rendering gate

Poppler and MuPDF rendered every PDF at 144 dpi (998 × 1418 pixels per page). Equality uses decoded RGB pixels, not PNG compression.

- poppler build-c vs build-d: all 9 decoded RGB pages identical.
- poppler build-d vs artifact: all 9 decoded RGB pages identical.
- mupdf build-c vs build-d: all 9 decoded RGB pages identical.
- mupdf build-d vs artifact: all 9 decoded RGB pages identical.

All 54 renders have zero ink pixels in their outer 3-pixel band. Per-page PNG/decoded-pixel hashes and six contact sheets are recorded in `qa/unit-026-evidence/render-hash-inventory.json`.

## PDF gate

- PDF `%PDF-1.7`; `/Lang id-ID`; 9 pages; unencrypted; no form, JavaScript, additional action, or embedded file.
- Exact four-entry outline passes; all 44 named destinations are inventoried. All 25 `/GoTo` links close over them; three `/URI` links are HTTPS; no unsafe action occurs.
- Link rectangles and MuPDF text blocks are in bounds. All 23 pypdf font objects and 22 `pdffonts` rows are embedded.
- pypdf, Poppler, and MuPDF text hashes match separately across C, D, and artifact. MuPDF recovers `代数学引论`; this Poppler installation and pypdf do not.

## Independent full-resolution review

All pages were reviewed independently in both renderers.

| Page | Finding |
|---:|---|
| 1 | Cover hierarchy, subtitle, scope box, metadata line, and footer are balanced and inside the trim box. |
| 2 | Edition, attribution, licence, provenance, and repository statements wrap cleanly without collision. |
| 3 | Section 4.2, Definition 4.2.1, Proposition 4.2.2, displayed algebra, and coloured rules are intact. |
| 4 | Proof, automorphisms, kernel, quotient structure, and equation (4.1) are aligned and unclipped. |
| 5 | Universal diagram, induced homomorphism, equation (4.2), and quotient-group definition are clean. |
| 6 | Quotient homomorphism, Propositions 4.2.7–4.2.8, and correspondence diagram are intact. |
| 7 | Proposition 4.2.9, cyclic groups, congruence, Proposition 4.2.11, and Grothendieck opening are clean. |
| 8 | Grothendieck continuation/proof, categorical remark, and following paragraph remain within bounds. |
| 9 | Conclusion, bibliography, and indexes are clean; white space is intentional. MuPDF renders 代数学引论; this Poppler installation omits it. |

No overlap, clipping, broken math/diagram stroke, tofu box, or unintended edge contact was found.

## Warnings

1. Poppler reports a missing `Adobe-GB1` language pack and omits the five bibliography-title glyphs `代数学引论` on page 9; its extractor also reports the mapping/font limitation. MuPDF renders and extracts the title correctly. Same-renderer C↔D and D↔artifact pixel identity still passes.
2. `/Lang id-ID` is correct, but the PDF is untagged; no tagged-accessibility claim is made.
3. The log has 3 LaTeX release warnings, 1 xeCJK warning, 1 frozen/deprecated `braids` warning, 6 fontspec CJK advisories, and 4 visually benign underfull hboxes (badness 1365, 3168, 2865, 10000). Fatal/error diagnostics and overfull boxes are zero.
4. The raw log contains an absolute profile path; generated evidence is sanitized and does not reproduce it.

Evidence: `structure-and-pdf-qa.json` holds exact structures, destinations, actions, fonts, text hashes, tool output, and checks; `render-hash-inventory.json` holds all image identities/comparisons. Verdict: **PASS WITH WARNINGS**.
