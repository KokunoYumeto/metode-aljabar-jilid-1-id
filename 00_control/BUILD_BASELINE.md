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

The admitted reader is `artifacts/unit-001-pendahuluan.pdf`: 21 pages, 199,917
bytes, SHA-256
`c74ce05494e07cb55e70186f391227d62d7f7da7c984788b9415cefb54083d5d`.
It has no TeX error, undefined citation/reference, duplicate destination, or
missing-character warning. MuPDF and Poppler rendered all 21 pages; all pages
were inspected. Two independent clean builds produced 21/21 pairwise
pixel-identical MuPDF pages. Their PDF byte hashes differed slightly because
of non-visible XeTeX serialization, so bit-identical containers are not claimed.

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
