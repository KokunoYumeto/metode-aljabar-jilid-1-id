# Unit 007 admission receipt - Bab 1: Latihan

Date: 2026-08-22

Decision: admitted as the seventh independently buildable `id-ID` reader unit.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit/tree: `c4f7a01f68f5f407906b4b970640cddbbad85f6b` / `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Complete frozen `chapter1.tex`: 49,874 bytes; SHA-256 `3405949f78c539e5e5c3c778e0460f2fde45ad3cb246d82a97e5a9492f95fe92`.
- Complete Chapter 1 exercise source boundary, lines 508-536: 2,962 bytes; SHA-256 `2a2dd555d54526fe8ccd88413210fc6d63b7365cd198cd623248a96014e2702e` under `sha256-utf8-lines-lf-v1`.
- Current target `repo/source/chapter1.tex`: 64,180 bytes; SHA-256 `f40dcba1bc87d886f6b83bd6962e9cd044d0b39282c17e326e6afbedd4f6ceee`.
- Indonesian target boundary, lines 508-536: 3,677 bytes; SHA-256 `314d78e029031e48b1549ee56a4cca331159a1c1cb4531f5ba6d3be2c9c18432` under `sha256-utf8-lines-lf-v1`.

## Translation and mathematical audit

The complete source-order exercise set was translated into natural formal Indonesian. The exact protected topology is preserved: six top-level exercises, six enumerated subparts, six source hints, twelve total `\item` tokens, one balanced `Exercises` environment, two balanced `compactenum` environments, and six balanced `hint` environments. The source and target each contain 64 inline mathematics fragments and three bracket displays. Their normalized 67-surface mathematical multisets are identical, with shared digest `d8fa1443f1e0d2d9d023d7a1c917d8539bdb3f61bed79324d6381097ae4a6540`; the few sequence differences are natural prose-driven reorderings only. The unit has no labels, references, citations, index entries, diagrams, answers, or solutions.

Independent structural, mathematical, semantic, and Indonesian-language reviews found no remaining P1 or P2 defect. Accepted copyedits clarified the strict-inequality contradiction in the König-lemma hint, restored natural Indonesian copular and restriction phrasing, and standardized lowercase `lema`. All protected checks were repeated afterward. The final translated span contains no Han-script residue, replacement character, or NUL.

### Disclosed source correction

`O013-LI-U007-COR-001`: the frozen hint at source line 519 says to take `\delta` to be the well-ordered tail set `\{\xi : \alpha \leq \xi < \beta\}`. Unless `\alpha=0`, that tail is not itself a von Neumann ordinal, so the source expression has the wrong mathematical type. The target correctly takes `\delta` to be the order type of that well-ordered tail. This preserves the intended proof of the unique identity `\beta=\alpha+\delta` and is recorded as an editorial correction rather than silently attributed to the source.

## Exact admitted build

- Driver: `repo/source/unit-007-bab-1-latihan.tex`, 4,259 bytes, SHA-256 `539a79f1f819b8236b4d1fc94608a8c16a4f83d9af05090f36cadd73382fddb5`
- Cover: `repo/source/coverpage-id-unit-007.tex`, 4,329 bytes, SHA-256 `f42a061f4d5b8d390b50ca4a11ccf16dd3979937ad38f9a026e04efa687126b4`
- Frozen empty cross-reference witness: `repo/source/unit-007-crossrefs.aux`, 233 bytes, SHA-256 `ffebaaea98b3088dc9445182d0a0ec0edaf12f4f40491d4b6ed5491b6fc0110e`
- Build script: `scripts/build_unit_007.ps1`, 2,837 bytes, SHA-256 `eb7a6deef2379e54064e654c42a586b3abed3b146d41da9a7b69a14c4a166441`
- Backend generator: `scripts/generate_unit_007_backend.py`, 22,984 bytes, SHA-256 `a2e4ca20481d6e2a2291dc6d71409671bb87dee6f55f97804e653230b57534f5`
- Reader: `artifacts/unit-007-bab-1-latihan.pdf`, 4 pages, 100,435 bytes, SHA-256 `e7d4d6745f88b56c7ef840499c8e1d759b2bbbc14a245e8fc477fb0a6504a2b1`
- Final log: `qa/UNIT_007_BUILD_FINAL.log`, 79,993 bytes, SHA-256 `853e06d6f385c61427f6c785ae6469f561dc9fd9fb1013fea0907aa3cbe6c554`
- Public build-log summary: `qa/unit-007-evidence/build-log-summary.txt`, 3,432 bytes, SHA-256 `3e7af15048ac2e999218c930d341663aad275eeb166b1b9e6e9aa3ff6738c236`
- Clean post-polish comparison PDF: 100,428 bytes, SHA-256 `0c4ab3f05d7e7f0be87e017e01dc72cada33c4a55eac855f3912a89939e72912`; all four Poppler and all four MuPDF page PNGs, extracted text, and reader metadata are pairwise identical to the admitted build. The sole post-audit polish was replacing ASCII `Koenig` with controlled `König` in the PDF keyword metadata; visible content and backend terminology were already correct.

The final log has zero TeX errors, undefined citations or references, duplicate destinations, missing characters, or overfull boxes. One inherited underfull cover-table alignment is visually acceptable. Deterministic rendered pages and semantic PDF equality are established; bit-identical XeTeX PDF containers across output directories are not claimed.

## PDF and all-page visual QA

The exact PDF has catalog language `id-ID`, four nonblank pages, two outline entries, seventeen named destinations, and three intentional URI link annotations. It has no form, widget, embedded file, JavaScript, GoToR, Launch action, encryption, replacement character, NUL, or Han-script residue. All 27 fonts are embedded and subset; only the CMMI9 mathematics subset lacks a ToUnicode map, while extracted mathematics remains coherent. MuPDF and Poppler rendered every page, and all pages were inspected without clipping, collision, missing glyph, unreadable formula, or blank page.

For this two-page exercise body, the standalone digital driver omits the sparse one-page print-style contents surface and empty bibliography/index surfaces while retaining chapter/exercise outline navigation. This is a target-only reader reflow, not a source-content deletion. The PDF remains untagged; that inherited accessibility limitation stays open and is not represented as tagged-PDF conformance.

## Backend and learner surfaces

Backend schema v1.1.0 has no first-class exercise, subpart, or hint arrays, and the shared validator currently requires the corresponding scalar counts to remain zero. Unit 007 therefore preserves all learner surfaces without a schema fork: the six exercises are ordered section entities, while every subpart and hint receives its own deterministic UUIDv5 concept-compatible entity linked to its parent exercise. The true `6/6/6` topology is independently gated against the live source and target and disclosed in the QA event. This compatibility encoding is not a claim that exercises or hints are ordinary exposition concepts.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with Wen-Wei Li credited and independent, non-endorsed derivative status stated. The attributed `AJbook.cls` fragment remains CC BY-SA 3.0 and bundled Noto fonts remain OFL 1.1. No component rights are flattened.

## Cursor and publication state

Unit 007 completes Chapter 1. The next contiguous source-order target is the beginning of frozen `chapter2.tex`; its first coherent unit boundary must be frozen before translation. The verified Unit 007 boundary may be committed locally now. GitHub publication and anonymous public-byte readback for Units 005-007 remain pending the already-recorded external account-access restoration; no repeated push is attempted while that authentication state is unchanged.
