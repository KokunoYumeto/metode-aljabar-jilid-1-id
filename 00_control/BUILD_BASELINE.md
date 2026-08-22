# Build baseline

Official upstream recipe:

    latexmk -pdf -pdflatex="xelatex -shell-escape -interaction=nonstopmode %O %S" Al-jabr-1

Upstream documents XeLaTeX/xeCJK, latexmk, xindy, biber, texlive-science,
Fandol, TeX Gyre Heros, and Noto Sans CJK SC. It does not lock the TeX
distribution, package versions, fonts, build date, or pgfplots version.
Therefore it is a functional recipe, not a byte-reproducible specification.

Windows replay on 2026-08-21 required a task-local portability shim:

- local Noto CJK font paths instead of unavailable system font names;
- makeindex in place of a failing MiKTeX xindy invocation;
- three build-only symbol-index normalization fixes for F_q and Z_p.

The replay completed successfully:

- Local witness: `build/upstream-functional-replay/Al-jabr-1.pdf`
- 446 pages; 3,646,137 bytes
- SHA-256 80ebb3bc2d8f9864fd0ff6cbfbbe0c3585c861d84cd81b1fe5f506c104ca1261
- Producer: MiKTeX-dvipdfmx (20260404)
- Untagged; unencrypted
- Log: 104,361 bytes, SHA-256
  2f1c38b3dc04069918e896e70f276120f07ec6dd4f2a67aaf2166470f9f0ebaa

This proves functional closure only. The one-page difference from the official
445-page PDF is a reflow/toolchain difference and remains an explicit adverse
condition. Before final publication, freeze a portable task-local build,
static edition date, font hashes, index procedure, and visual comparison.

## Admitted Unit 001 build

`scripts/build_unit_001.ps1` supplies the portable unit build: XeLaTeX with
shell escape disabled, Biber, MakeIndex, and three convergence passes. It pins
`SOURCE_DATE_EPOCH=1784878369`, uses the task-local Noto font closure, and the
cover uses PGF seed `20260821`.

The current terminology-corrected reader is
`artifacts/unit-001-pendahuluan.pdf`: 21 pages, 199,926 bytes, SHA-256
`b3fca2af76b793a19877ffc822d6ec89c2494641f7e1dfa468b158c7bec30a3e`.
It has no TeX error, undefined citation/reference, duplicate destination, or
missing-character warning. MuPDF and Poppler rendered all 21 pages; all pages
were inspected. The clean comparison build is 199,925 bytes, SHA-256
`20fbb6c3db8f66a176315bc47fcf48ff768169cc7a2fac91af2950a9d11eca0b`;
both engines produced 21/21 pairwise pixel-identical pages. The final log is
87,018 bytes, SHA-256
`923d8b61f5e47da1cfba3fc4167fa876128eb7417334eb6fc3e75b52aa88a292`.
Their PDF byte hashes differ slightly because of non-visible XeTeX
serialization, so bit-identical containers are not claimed.

## Admitted standalone digital-reader builds

Unit 002 was reflowed after admission so print-only blank verso pages no longer
appear in its standalone digital reader. The corrected artifact is 12 pages,
161,147 bytes, SHA-256
`ff2eb3fd1ec5abaa7989d0c29c419c04f99368dc3f278799be460e30042bfe58`.
Two clean builds produced 12/12 pixel-identical MuPDF pages.

Unit 003 uses the same pinned shell-escape-disabled procedure and target-only
interface layer. Its portability-corrected admitted artifact is 11 pages,
134,858 bytes, SHA-256
`031e231bc5d2ac74cada865700d8f76dda327941c7f442e6d47324b848103df8`.
The unit now uses the bundled Noto CJK closure for its intentional Chinese
bibliography metadata, standard Indonesian `Lema`, and Indonesian bibliography
back-reference strings. Two clean builds produced 11/11 pixel-identical MuPDF
pages. Neither unit claims byte-identical XeTeX PDF-container serialization
across output directories.

Unit 004 uses the same target-only digital reflow and a shell-escape-disabled
XeLaTeX/MakeIndex procedure. Its admitted artifact is 8 pages, 107,332 bytes,
SHA-256
`e48aa97d15ad9c192df5d744bfc8290fc816c4b681322295352517a02e267c13`.
Two clean builds produced 8/8 pixel-identical MuPDF pages at 144 dpi. MuPDF and
Poppler rendered every page without clipping, collision, blank pages, or
missing glyphs. The PDF container hashes differ across output directories, so
only deterministic rendered content is claimed.

Unit 005 uses the same target-only digital reflow, bundled Noto CJK closure,
and shell-escape-disabled XeLaTeX/MakeIndex procedure. Its admitted artifact is
12 pages, 128,556 bytes, SHA-256
`232d41f4e7f03123818ae14272958c8269242ebcbec68b832aaaf7ba295ebf3e`.
Two clean builds produced 12/12 pixel-identical MuPDF pages at 144 dpi. MuPDF
and Poppler rendered every page without clipping, collision, blank pages, or
missing glyphs. The PDF container hashes differ across output directories, so
only deterministic rendered content is claimed.

Unit 006 uses the same target-only digital reflow, bundled Noto CJK closure,
shell-escape-disabled XeLaTeX/Biber/MakeIndex procedure, and frozen external
reference numbers. Its admitted artifact is 9 pages, 120,808 bytes, SHA-256
`1fe15c59de6021b376643269423f2ef12e7b986f048ae39a31d8b1df9f7562c4`.
The target-only bibliography interface localizes the inherited Chinese `in`
label to Indonesian `Dalam:`. Two clean builds produced 9/9 pixel-identical
MuPDF and Poppler pages at 144 dpi. All pages were inspected without clipping,
collision, blank pages, missing glyphs, or Han residue. The PDF container hashes
differ across output directories, so only deterministic rendered content is
claimed. The reader remains untagged; correct `id-ID` catalog language does not
remove that inherited accessibility limitation.

Unit 007 uses the same pinned shell-escape-disabled XeLaTeX/Biber/MakeIndex
procedure and a frozen empty cross-reference witness because the Chapter 1
exercise set contains no symbolic cross-unit reference. Its admitted artifact
is 4 pages, 100,435 bytes, SHA-256
`e7d4d6745f88b56c7ef840499c8e1d759b2bbbc14a245e8fc477fb0a6504a2b1`.
For this two-page exercise body, the standalone digital driver omits a sparse
one-page print-style contents surface and empty bibliography/index surfaces;
the PDF outline still preserves chapter/exercise navigation. An independent
clean post-polish comparison build has PDF SHA-256
`0c4ab3f05d7e7f0be87e017e01dc72cada33c4a55eac855f3912a89939e72912`.
Both Poppler and MuPDF produced 4/4 pairwise byte-identical 144-dpi page PNGs,
and extracted text, metadata, outline, named destinations, and annotations are
equal. All pages were inspected without clipping, collision, blank pages,
missing glyphs, or Han residue. The PDF remains untagged; deterministic
rendered content, not byte-identical XeTeX PDF-container serialization, is
claimed.

Unit 008 uses the same pinned shell-escape-disabled XeLaTeX/Biber/MakeIndex
procedure and a frozen external-reference witness for Section 1.5, Section 2.7,
and Proposition 2.8.2. Its current terminology-corrected artifact is 5 pages,
100,805 bytes,
SHA-256
`0db18bfbae3ffd2194447781a77effb4f57f8bd8521baa3acb334b474f0773cd`.
The standalone driver reflows the source's four-row, five-column table into a
full-width text-native `tabularx`, reduces only the chapter-opening and reading-
box spacing, and localizes inherited bibliography role labels. Two clean builds
produced 5/5 pixel-identical Poppler and 5/5 pixel-identical MuPDF pages at 144
dpi; extracted text was also identical. The clean comparison PDF is 100,804
bytes, SHA-256
`61d0b2aff153a1893a9c02df7148eb3958f3d0a72fb15d485f65edd1e3889375`,
and the final log is 80,397 bytes, SHA-256
`d0f0da38335af5520cf7f74e37ddb9734242d7b1beaa24007f211259a4a7ab2d`.
All pages were inspected without
clipping, collision, blank pages, missing glyphs, or Han residue. The PDF
containers differ by one byte, so only deterministic rendered content and
semantic-text equality are claimed. The PDF remains untagged; the backend's
paired linear table semantics do not constitute tagged-PDF conformance.

## Admitted Unit 009 build

Unit 009 uses the pinned shell-escape-disabled XeLaTeX/Biber/MakeIndex
procedure, the task-local Noto font closure, and a frozen external-reference
witness for eight destinations outside complete Section 2.1. Its current
terminology-corrected artifact is
`artifacts/unit-009-bab-2-kategori-dan-morfisme.pdf`: 13 pages, 143,207 bytes,
SHA-256
`1a71610ba997348ce22db69944fec3529d9d6e6c2ef6ece48faa30df90ac5ce6`.
The clean comparison build is 143,192 bytes, SHA-256
`ea4f2845bdb0b3dc04aac01fe6fd1b15a2227e69b0ae0c7f69a1496d479e777b`.
All thirteen Poppler and all thirteen MuPDF page PNGs are pairwise identical,
and extracted text is identical. The final log is 85,064 bytes, SHA-256
`523242a89f71a31d03a3bd753e125a4dac4bb7e79b4a3e93fafb0cd122c689bf`,
with no TeX error, undefined citation/reference, duplicate destination,
missing-character warning, or overfull box. The standalone reader has four
outline entries, 49 named destinations, 42 internal GoTo annotations, and
three intentional URI annotations; it has no form, widget, embedded file,
JavaScript, GoToR, Launch action, or encryption. All 28 fonts are embedded and
subset, with only the inherited CMSY10 mathematics subset lacking a ToUnicode
map. Every page was inspected without clipping, collision, blank pages,
missing glyphs, or unreadable mathematics. The PDF remains untagged, and only
deterministic rendered content and semantic-text equality are claimed.

The 2026-08-22 terminology correction (`funktor` to `fungtor`, plus one
`transformasi alami` to `transformasi natural`) affected Units 001, 008, and
009. Each was rebuilt twice, compared in both renderers, visually checked on
all pages, and rebound to its current backend before translation resumed.

## Combined checkpoint reader 0.3.0

`scripts/build_checkpoint_reader_0_3_0.py` merges the current admitted Unit
001-009 readers behind one reader-first status/rights cover while namespacing
their named destinations and rebuilding their outline hierarchy. The final
artifact is
`output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-0.3.0-reader.pdf`: 96
pages, 1,517,117 bytes, SHA-256
`1752f4535ea2f564aa6931ea0c4ba1da0daa4e7e90ae0c2433bedbb3f22d0dda`.
Unit starts are physical pages 2, 23, 35, 46, 54, 66, 75, 79, and 84.

An independent deterministic replay produced the same PDF hash. All 95 merged
source-unit content streams are byte-identical to their admitted unit pages,
and separately rendered source pages are pixel-identical to checkpoint pages
2-96. Poppler and MuPDF each rendered all 96 pages; the cover, intentional
blank page 5, every unit boundary, the final page, and eight contact sheets
covering the entire reader passed visual inspection. The PDF is `id-ID`, has
299 named destinations, 194 internal GoTo and 40 intentional URI actions,
zero broken destinations or unsafe actions, and 234/234 embedded font objects.
It remains untagged. Exact machine and human-readable evidence is in
`qa/checkpoint-0.3.0-evidence/structure-and-render-qa.json` and
`qa/checkpoint-0.3.0-evidence/QA_SUMMARY.md`.
