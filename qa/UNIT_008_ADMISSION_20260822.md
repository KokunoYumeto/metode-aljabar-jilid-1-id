# Unit 008 admission receipt - Bab 2: Pengantar Teori Kategori

Date: 2026-08-22

Decision: admitted as the eighth independently buildable `id-ID` reader unit.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit/tree: `c4f7a01f68f5f407906b4b970640cddbbad85f6b` / `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Complete frozen `chapter2.tex`: 139,983 bytes; SHA-256 `56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840`.
- Complete Chapter 2 introduction and reading-guidance boundary, lines 1-37: 3,659 bytes; SHA-256 `30e31fc7ba682acb3291cfa37cc29ad0567b5f8b7955b974713fc565d62a9874` under `sha256-utf8-lines-lf-v1`.
- Current target `repo/source/chapter2.tex`: 141,271 bytes; SHA-256 `d809e0f60420f6c19194b45734d6c042f2315619803c58119f20f68f09b9538a`.
- Indonesian target boundary, lines 1-37: 4,947 bytes; SHA-256 `c48ee98fc25e1dab9c581b618b492a4d2e40930c066b69c686b2c13bef5a7471` under `sha256-utf8-lines-lf-v1`.

## Translation, mathematics, and topology

The complete source-order Chapter 2 introduction and reading guidance were translated into natural formal Indonesian. The protected source and target each retain label `sec:category`; references `sec:limits`, `sec:Grot-universe`, and `prop:preorder-complete`; and citations `EM45`, `Co11`, `ML98`, and `sep-category-theory` in the same order. Eight inline mathematics fragments and one bracket display have identical normalized TeX multisets. The unit contains no exercise, hint, answer, solution, diagram asset, or index entry.

The source's native four-row, five-column `tabular` content is preserved as text and reflowed into a target-only full-width `tabularx` surface with the same sixteen cell separators and four horizontal rules. This change improves the standalone digital reader without treating a layout representation as mathematical content. A linear reading order is recorded in the backend accessibility surface. The chapter-opening gap and guidance-box padding are also reduced only in the standalone driver so the unit uses five coherent pages instead of stranding a single line on an otherwise blank page. Bibliography role labels inherited from the Chinese class are localized to `penyunting` and `disunting oleh` in the driver.

Independent structural, mathematical, semantic, and Indonesian-language review found no remaining P1 or P2 defect. The final translated span and extracted PDF contain no Han-script residue, replacement character, or NUL.

## External-reference witness

`repo/source/unit-008-crossrefs.aux` freezes the official-book destinations used by this standalone unit: `sec:Grot-universe` as Section 1.5, `sec:limits` as Section 2.7, and `prop:preorder-complete` as Proposition 2.8.2. The numbers were checked against the named destinations in the frozen official 445-page PDF. The driver imports the numbers with an empty external URL so the references print correctly without advertising links to an absent companion PDF.

## Exact admitted build

- Driver: `repo/source/unit-008-bab-2-pengantar-teori-kategori.tex`, 5,110 bytes, SHA-256 `b433d175c2e6fec24fa8df7ab75067eb44c06983c3135d49b641db68eb54a60c`
- Cover: `repo/source/coverpage-id-unit-008.tex`, 4,340 bytes, SHA-256 `7e3dc485dee2e3fac9e6c8e2fb180369814dd9923e71c211c551ff4b6a0e88ba`
- Frozen cross-reference witness: `repo/source/unit-008-crossrefs.aux`, 371 bytes, SHA-256 `008786a603c7ab6e19af02e7632daf2ca2f310c1035c5f73616a510b5c66a541`
- Build script: `scripts/build_unit_008.ps1`, 2,854 bytes, SHA-256 `9d5f1f1de9424a240d7487c89b605809ce3c8f1e2bd5d6f9ed94c6c52d3a43bb`
- Backend generator: `scripts/generate_unit_008_backend.py`, 28,389 bytes, SHA-256 `7bc9a7e2a545f1ee898b2cfd3443a8bad7339b8f565dd4d1bb08dfba6709cc71`
- Reader: `artifacts/unit-008-bab-2-pengantar-teori-kategori.pdf`, 5 pages, 100,795 bytes, SHA-256 `d4234cb0080a60ad06fcb004d4d75e7daea85b3846bbbd05f0261b03e9f66258`
- Final log: `qa/UNIT_008_BUILD_FINAL.log`, 80,397 bytes, SHA-256 `8db2b6b52b77654f17527dd0f6d096cd70171df52605c085f49dd7ce8638aa47`
- Clean comparison PDF: 100,814 bytes, SHA-256 `458586404b5689e629d51fbb6bee937f2f953fbf5f4fd2907c84912dda0e399b`; all five Poppler and all five MuPDF page PNGs and extracted text are pairwise identical to the admitted build.

The final log has zero TeX errors, undefined citations or references, duplicate destinations, missing characters, or overfull boxes. One inherited underfull cover-table alignment is visually acceptable. Three hyperref warnings are the deliberate consequence of suppressing false external links while retaining frozen reference numbers. Deterministic rendered pages and semantic text equality are established; bit-identical XeTeX PDF containers across output directories are not claimed.

## PDF and all-page visual QA

The admitted PDF has catalog language `id-ID`, five nonblank pages, two outline entries, ten named destinations, eight internal GoTo annotations, and seven intentional URI annotations. It has no form, widget, embedded file, JavaScript, GoToR, Launch action, encryption, replacement character, NUL, or Han-script residue. All 21 fonts are embedded and subset; only the CMSY10 mathematics subset lacks a ToUnicode map, while extracted mathematics remains coherent. MuPDF and Poppler rendered every page, and all pages were inspected without clipping, collision, missing glyph, unreadable formula, or blank page.

The comparison table is text-native, full-width, and legible; the guidance box is not split; and the bibliography no longer exposes the class's Chinese role labels. The PDF remains untagged, so the paired linear table semantics in the modular backend improve machine access without being misrepresented as tagged-PDF conformance.

## Backend representation

Backend schema v1.1.0 has no first-class entities for TeX labels, standalone external references, native tables, or accessibility descriptions. Unit 008 therefore assigns deterministic UUIDv5 concept-compatible identities to those six protected surfaces, with stable keys that explicitly identify them as surfaces. The four-row table and its linear reading semantics remain paired; this compatibility encoding is not a claim that either is an ordinary mathematical concept. The generator fails closed on source-span, target-span, mathematics, topology, build, and admission-evidence drift before writing canonical JSON or CSV.

The build gate cross-checks the live artifact byte count and SHA-256, live final-log byte count and SHA-256, and page count reported independently by `pdfinfo`, the final TeX log, the public build summary, and this receipt. Negative tests confirm that a stale summary and an injected page-count disagreement are both refused. The Unit 008 principal-rights record binds the frozen `chapter2.tex` authority rather than inheriting Unit 007's Chapter 1 binding.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with Wen-Wei Li credited and independent, non-endorsed derivative status stated. The attributed `AJbook.cls` fragment remains CC BY-SA 3.0 and bundled Noto fonts remain OFL 1.1. No component rights are flattened.

## Cursor and publication state

Unit 008 starts Chapter 2. The next contiguous source-order target begins at `chapter2.tex:39`, Section 2.1. GitHub remains temporarily unavailable because the user-reported account suspension is under support review, so no push retry occurs. Zenodo version `0.1.0` already preserves Units 001-007 under concept DOI `10.5281/zenodo.22059759`; this admitted unit must be carried forward only through that concept's linked new-version workflow, never through a duplicate record lineage.
