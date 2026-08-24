# Unit 021 visual/PDF QA — 2026-08-24

**Verdict: PASS.** The two clean builds are structurally and semantically equivalent and produce page-identical output within Poppler and within PyMuPDF. All nine pages pass visual inspection in both renderers. The installed artifact is byte-identical to final build B and is bound to the canonically integrated Section 3.3 span; this visual lane performed no publication action. The public driver now loads that span directly from `repo/source/chapter3.tex`, so no ignored staging fragment is required.

## Exact source and builds

- Canonical `repo/source/chapter3.tex` — 83,581 bytes; SHA-256 `ce310d940819f0fc51ee6459f73a8380b602edee42ef666720e225451adee9f9`.
- Canonical lines 306–511 — 206 LF records, 17,968 bytes; SHA-256 `57f5bc8a211b6a9b76a096742fbfc94989c890f11d5140ad449d0e76e2c67085`; byte-identical to `build/unit-021-candidate/chapter3-braiding-id.tex`. Line 512 begins the excluded `sec:enriched-cat` section and has SHA-256 `c4fb914defd51476a7a9721c86e92cedeef7c29344722a029cf2dc46825ac541`.
- `build/unit-021-final-a/unit-021-bab-3-struktur-kepang.pdf` — 115,400 bytes; SHA-256 `3307ea4ff631081e1e7e70ae9e7c4453bba8be0a2c861283e4ba96bd7ab042b0`.
- `build/unit-021-final-b/unit-021-bab-3-struktur-kepang.pdf` — 115,395 bytes; SHA-256 `ff12bd0dbff7ba40d16050aef9f51b2b676dcfbeaa2e5808407373936fc37371`.
- `artifacts/unit-021-bab-3-struktur-kepang.pdf` — 115,395 bytes; SHA-256 `ff12bd0dbff7ba40d16050aef9f51b2b676dcfbeaa2e5808407373936fc37371`.

The driver is 6,293 bytes (`87b385c60bda370c246344f1e3013e31ee86a64ad595677746ff82a224bdd5d9`); cover 3,482 bytes (`b04cbf04808bef4e3dc528e61b26f15126c366b7daadb1c0de7cc41032d4517f`); cross-reference witness 561 bytes (`dd0ea3d3d5ffbb01843cc0e195c3a60b1015d01f59eac1f4516f3a5ca30559a4`); build script 4,775 bytes (`4a731d840469647b9070133d8667b2e1c2bfe81b53a13d595939996b386c4639`). The script requires strict UTF-8, 910 LF records, and the exact 17,968-byte Section 3.3 span, while deliberately recording rather than freezing the whole-file hash so later translations elsewhere in Chapter 3 do not break this reader.

## Rendering and visual inspection

- Every page was rendered at 144 dpi with Poppler 24.04.0 and PyMuPDF 1.27.2.3, twice per clean build and renderer: 72 page PNGs total. Eight contact sheets cover every renderer/build/replay combination.
- Both replay comparisons per renderer and both cross-build comparisons are decoded-pixel-identical and PNG-byte-identical on all pages. Final-B Poppler aggregate raw-RGB/PNG-set hashes are `fa54d88b634d0d10c59eb651a14ae474ab95018d504588e795b767bdff91f35a` / `5f3ad58070005698e6c68592ea73d504b7802f245f5f99b1b1ab2b1f1868e0a`; PyMuPDF hashes are `4b97fccf4e388aaeab79bf905a418f2a0aa81469fbb80063e31c013941fcddaf` / `fc91e67ec845d71da60880d3dc57426fdadb71a0f42d5457e4c2dc848b740032`.
- All pages were inspected for clipping, overlap, missing/tofu glyphs, broken arrows or diagrams, sparse/off-center composition, bad pagination, and blank print versos. No defect was found. No render has ink in the outer three-pixel border; PyMuPDF and pdfplumber report no text box outside a page.
- The centered cover accurately says `Cakupan parsial Bab 3`, contains no ambiguous progress blocks, and records the independent/non-endorsed translation status. The full-width content begins with `3.3 Struktur Kepang` and preserves all hexagons, unit triangles, the braided-functor square, the twelve-node Yang–Baxter cycle, braid sequences, strand diagrams, and the final naturality comparison.
- Nine pages were retained deliberately. An attempted same-page merge of the back matter with page 8 produced a 21.58 pt overfull vertical box and still spilled to page 9. The restored layout has zero overfull boxes; page 9 legibly combines the one-entry bibliography, six-entry term index, and two-entry symbol index.

## PDF structure, text, and safety

- Both PDFs are PDF 1.7, unencrypted, nine pages of 498.9 × 708.66 pt, with page labels `1, 2, 1, 2, 3, 4, 5, 6, 7` and identical metadata. The subject is `Terjemahan Bahasa Indonesia independen; Bagian 3.3 lengkap`, the keywords contain clean ASCII `Yang-Baxter`, and the catalog language is `id-ID`.
- Five valid outline entries navigate to Chapter 3, §3.3, bibliography, term index, and symbol index. There are 29 named destinations and 22 valid links: 18 `/GoTo` and four `/URI`. There are no unsafe/additional actions, JavaScript name trees, embedded files, forms, encryption, or strict-reader warnings.
- All 30 fonts are embedded and subset. Every page has extractable text. PyPDF, PyMuPDF, pdfplumber-layout, and Poppler-layout extraction are identical across clean builds, with SHA-256 `4d647c93cc800490aef058637cbdfdfc51731055634799211ca2c2082c01fd0f`, `696ed692cb11ec952eb3aca310d0746288bdcf77984d7d13459b047c9d6df982`, `35d5acff454e9e6c2505fc0eb4f8e9fa55719aeae433e4e4d4bcedaf49972e86`, and `9b68de54937294634bd925adcfaed5cc976ca10ce75774a4b1bede9ac986e161` respectively. There are zero unresolved references, template/editor tokens, or replacement characters.
- PyPDF alone maps two visibly rendered long-arrow glyphs to NUL. Poppler extracts them as arrows, while PyMuPDF and pdfplumber have zero NUL/replacement/control characters; this parser-specific ToUnicode limitation is recorded rather than hidden. The PDF is untagged, reported honestly as the current accessibility baseline.
- The final log has zero overfull boxes, undefined references/citations/control sequences, missing characters, fatal errors, or emergency stops. It records four harmless underfull hboxes, three underfull vboxes, and seven expected suppressed empty targets for frozen external-number witnesses.

## Evidence and provenance

- Visual manifest: `build/unit-021-visual-qa/qa-manifest.json` — 59,332 bytes; SHA-256 `2d1eded94b59f2047d547956199e67605bcb76d19ca745f9f832ad7a03a79810`.
- Structure/PDF evidence: `qa/unit-021-evidence/structure-and-pdf-qa.json` — 13,834 bytes; SHA-256 `110959bf80801379ec2d1cee26aaa969fd4b288cd752adc8fa9d891f1e3e697e`.
- Render inventory: `qa/unit-021-evidence/render-hash-inventory.json` — 9,043 bytes; SHA-256 `8531a5ee7c15bf935970ccafc6f1b2c1593a3bf5ec4bd50b723b16185eebe39f`. It hash-binds nine admitted Poppler PNGs and nine admitted PyMuPDF PNGs stored under `qa/unit-021-evidence/{poppler,mupdf}-final-b/`.
- Sanitized final build log: `qa/UNIT_021_BUILD_FINAL.log` — 85,345 bytes; SHA-256 `5495764755137cd39cac890bba5f0779b9f96c378330c8e46f7ea3c02bc11f08`.

Language/provenance are `id-ID` and `OpenAI Codex gpt-5.6-sol, Ultra`. Wen-Wei Li remains the source author. The principal text and independent translation are CC BY 4.0; the AJbook fragment is CC BY-SA 3.0; bundled Noto fonts are SIL OFL 1.1; the wider-closure Lanzhou PNG is not used by this reader.
