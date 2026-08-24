# Unit 023 visual/PDF QA — 2026-08-24

**Verdict: PASS.** Unit 023 is a self-contained seven-page `id-ID` reader for
the complete Section 3.5, *Sekilas tentang 2-Kategori*. Two clean builds have
different PDF-container bytes but identical extracted content and
page-identical output within both Poppler and MuPDF. Every page was inspected
in both renderer families. This receipt performs no Git or publication action.

## Exact reader boundary

- Canonical `repo/source/chapter3.tex`: 88,491 bytes, SHA-256
  `8ade04d16a5b71d4d1ffdf3bcee6736bb199c631a8851336d692e7ebdced5e7f`,
  910 LF records.
- Canonical lines 722–871: 150 LF records, 14,894 bytes, SHA-256
  `c15e079bc551b30ad7cc6daf72bee58a90108dc7fa5f101f768275e99d1dad05`.
  The span is byte-identical to the reviewed candidate and contains all of
  Section 3.5. It translates authority lines 723–872. Target line 872 begins
  the excluded Chapter 3 exercise block. Editorial record
  `O013-LI-U023-ED-001` preserves the authority's romanized adjunction sort
  key while adding only the learner-visible Indonesian index display.
- Driver: 5,408 bytes, SHA-256
  `e3cd83f5ad24b69e676f8ac833d7796db15c7e28f890f71e0a46156a4d37a630`.
  It loads only `chapter3.tex` lines 722–871 and does not depend on the
  candidate directory.
- Cover: 3,620 bytes, SHA-256
  `3eb4c6fcdb5ad34d1aa2148f88b71dba87efca04bd275b2a57ede1a87530bd04`.
  Cross-reference AUX: 846 bytes, SHA-256
  `8074e688c018c89695c9fda35ffb18c4c585d1404c9fd652f5dfea22aabcc405`.
  Build script: 4,689 bytes, SHA-256
  `c390aedcc2cc9207094ac6d4b1e8175f3384815ed95e2f75a5cccd1ed7f7b37f`.

## Reflow and visual inspection

The initial reader was eight pages because the book class's print-oriented
`\backmatter` transition shipped content page 5 before either tiny index was
read. Physical page 8 then contained only two term-index entries and one
symbol-index entry. The standalone reader does not need a chapter-numbering
state transition at that point, so the driver now omits it. Both indexes use
the available lower portion of physical page 7, without changing Section 3.5
or any index entry.

Clean build A is 98,732 bytes, SHA-256
`f3f587cd584538612fc8aea440f44aaa2c6933b707688e011d097c7ace5eb5a0`.
Clean build B is 98,735 bytes, SHA-256
`5fb682094a829d8abd878aaf3f5e36cda7763323d1a8417d4e36595a7959add4`.
The fresh scripted replay is 98,741 bytes, SHA-256
`c7676a48134f18222cfa56c82d733db6ce9c06631faf39c222bfb3514cc486eb`.
The installed artifact is byte-identical to build B:
`artifacts/unit-023-bab-3-sekilas-tentang-2-kategori.pdf`, seven pages,
98,735 bytes, SHA-256
`5fb682094a829d8abd878aaf3f5e36cda7763323d1a8417d4e36595a7959add4`.

All seven pages were rendered at 144 dpi with Poppler and MuPDF for both clean
builds, the fresh replay, and the installed artifact, giving 56 checked page
rasters and eight contact sheets. The six clean-build/replay comparisons have
identical PNG files and decoded RGB pixels within each renderer on every page;
the artifact is byte-identical to build B. The admitted aggregate hashes are:

- Poppler PNG set
  `f3577ef81e2351e169c8020df15a5cbf7cc06ac2681d32f1db05527896043529`;
  raw RGB set
  `7ee0c2fd7123317c8f1f749e2e055c6b7d2d29acac22deeb5c6281fddd5b2b88`.
- MuPDF PNG set
  `778a25a1e188c9da5389952a25f31c1b19537e7a9540a735541e2a7fcff775d3`;
  raw RGB set
  `3d654eae42336bcf02456d0a7402d3c097b68b686c36fd8000fef946835e7734`.

The Poppler and MuPDF contact sheets were inspected, followed by a full-size
page-by-page Poppler inspection. Pages 1–2 have centered, balanced cover and
rights composition with explicit partial scope. Pages 3–7 preserve all
fourteen `tikzcd` diagrams and their 64 arrows, including vertical and
horizontal 2-cell composition, the interchange-law diagram, the enriched
category formulation, and the adjunction diagrams. Page 7 now closes with both
indexes below the final remark. No page has clipping, overlap, tofu or missing
glyphs, broken arrows, off-center composition, unintended blank space, or ink
in the outer three-pixel border.

## PDF structure, text, and build log

The artifact is unencrypted PDF 1.7, seven pages of 498.9 × 708.66 pt, with
catalog language `id-ID`. It has no form, JavaScript, embedded file, catalog
additional action, unsafe action, or out-of-bounds text. All 24 fonts are
embedded subsets. Four outline entries navigate to the chapter, Section 3.5,
term index, and symbol index; the file has 26 named destinations, four valid
`/GoTo` actions, and three HTTPS `/URI` actions. Every page has extractable
text. PyPDF, PyMuPDF, pdfplumber, and Poppler extraction have zero NUL,
replacement, unresolved-token, or Han characters. The PDF is not tagged; that
recorded limitation does not change its verified language, navigation,
extractability, or visual baseline.

The sanitized final log has zero overfull boxes, undefined references,
undefined citations, undefined control sequences, missing characters, fatal
errors, or emergency stops. It records five harmless underfull hboxes, one
underfull vbox, and fifteen expected suppressed-link warnings for external
printed-number-only references whose empty cross-document URL prevents false
links.

## Durable evidence and rights

- Structured PDF evidence: 34,048 bytes, SHA-256
  `4558664d48c7188dfdfac8ea9f02ec7dae7434b2d0377f027c870c92cb541c23`.
- Render inventory: 9,634 bytes, SHA-256
  `c53937157e0a66d6f607956d7969b778c64e23a8f1b0bfc69334f1750c277cf7`.
- Build summary: 1,246 bytes, SHA-256
  `644462a0708c11a10e618bd26971e4725da267b5874bcae4a3cf9ffa476c838f`.
- Sanitized final log: 83,880 bytes, SHA-256
  `1eba3cdbaa85de85e728daac9745f4dd6f7776e9d2315f15348ad23cd0b6c2ef`.
- Evidence generator: 31,038 bytes, SHA-256
  `1c18e16b9e004b2b4e4c1d93843aba10fe976280c19053b0a3c67238d7fb0783`.

Wen-Wei Li remains the source author. The principal source text and independent,
non-endorsed Indonesian translation are CC BY 4.0. The credited AJbook fragment
retains CC BY-SA 3.0, and bundled Noto fonts retain SIL OFL 1.1. Production
provenance is recorded separately from authorship as
`OpenAI Codex gpt-5.6-sol, Ultra`.
