# Unit 035 — Build and all-page visual QA — 2026-08-28

Status: **PASS**. This is the single bounded reader gate for Unit 035; do not
repeat it absent a concrete new defect.

## Frozen reader

- Artifact: `artifacts/unit-035-bab-4-grup-dalam-kategori-dan-latihan-id.pdf`
- Identity: 135,943 bytes; SHA-256
  `1cf97dd523ae1a8c5185c4b22a8e6b0dab6e7514ab5387c34959c417f4e35442`
- Build log: `qa/UNIT_035_BUILD_FINAL.log`, 87,586 bytes; SHA-256
  `1b87602c47d5b602a71b788ea14a18f10f4816ae1c0522bbd828dc51b02a2a7a`
- Pages: 9; 498.9 × 708.66 points; PDF 1.7; no encryption, forms,
  JavaScript, attachments, or missing embedded fonts.
- Extracted text: 19,744 bytes; SHA-256
  `ae8b43b6670ec87d7ab7f3b237b61e9fa769417916fe80ebfe300586fc3fc7dd`;
  no `??`, Han residue, replacement glyph, or missing-glyph marker.

The final log has no undefined control sequence, undefined reference or
citation, LaTeX/package error, fatal error, Biber rerun request, or
cross-reference rerun request. The one 32.49-point overfull diagnostic is the
wide categorical-equivalence diagram on reader page 5; the full-resolution
render proves that the diagram remains inside the page and is legible. The
single underfull paragraph is harmless line spacing in the opening definition.

## All-page inspection

All nine pages were rasterized at 120 dpi and inspected together and at full
resolution where the build log identified the wide diagram. The cover and
rights page are centered and readable; pages 3–5 preserve all eight diagrams
and arrow labels; pages 6–8 contain the complete 26-exercise / 36-item /
five-hint block without clipping or orphaned headings; page 9 contains the
term index. No page is blank, cropped, rotated, off-center, or missing content.

The contact sheet is
`qa/unit-035-evidence/all-pages-contact.png`, 1,688,795 bytes, SHA-256
`936d83afb23c5eb9cc9f25d964514977a016f0c53e17e3b6ace246e5ee9cb1bf`.
Per-page render identities are recorded in the adjacent JSON inventory.

Conclusion: the reader is fit for publication and completes Chapter 4 when
combined with Units 025–034. Next production cursor: `chapter5.tex:1`.
