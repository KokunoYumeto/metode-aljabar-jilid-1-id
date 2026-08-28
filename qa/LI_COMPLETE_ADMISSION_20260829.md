# Complete Li Volume 1 admission — 2026-08-29

Result: **PASS; ready for immediate public preservation.** This receipt admits
the complete Bahasa Indonesia edition of Wen-Wei Li's *Methods in Algebra,
Volume 1*. It does not claim completion of the separate Duncan, CRing, or
edition-original O013 components.

## Authority and rights

- Authority commit: `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Authority tree: `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority archive SHA-256:
  `6c8c416baa8f5ffc8810bbad6470c780413bd7917af739e07340e4b07e7eaff6`.
- Official 445-page PDF SHA-256:
  `dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38`.
- Principal work and translation: CC BY 4.0. `AJbook.cls` and the retained
  Lanzhou asset remain CC BY-SA 3.0, Noto remains OFL 1.1, and Fandol 0.3
  remains GPLv3 with its font exception. Rights are not flattened.
- Independent derivative; no author or upstream endorsement is claimed.
- Production provenance: OpenAI Codex gpt-5.6-sol, Ultra, acting on the user's
  instructions. This does not replace the author's or contributors' credits.

## Complete source closure

`repo/source/prelude.tex` plus `chapter1.tex` through `chapter10.tex` contains
13,599 normalized-LF records / 1,459,865 bytes. The aggregate target preserves
2,437 active environment pairs, 684 labels, 1,403 references, 138 citations,
569 index entries, 1,146 list items, 161 active top-level exercises, 268 total
exercise items, and 51 hints. The commented-out upstream Chapter 10 item remains
commented and is neither restored nor counted. Exact per-file identities and
topology are frozen in `qa/LI_COMPLETE_TRANSLATION_FREEZE.json`.

Final chapter target identities:

- Chapter 7: 132,871 bytes, SHA-256
  `6647f499bbe7ea82711bb550004e8bcaa264f1e5ba9c742128acb7b764d039b3`.
- Chapter 8: 121,871 bytes, SHA-256
  `68474f1dc3234410550d576c8cf2ce2fcf7f3c65a6f7a3ae23ee554a5990eb3e`.
- Chapter 9: 136,866 bytes, SHA-256
  `cb753a347ac047dff772f08916cca940fab617440e2ea50c602e8ea4e29f762d`.
- Chapter 10: 169,341 bytes, SHA-256
  `7d9464e0fb680c67d107f8eb6d501c2b43e4a44f3696cd271c983ee75d3dda55`.

## Reader and visual boundary

`artifacts/metode-aljabar-jilid-1-id-lengkap.pdf` is 521 pages / 2,875,853
bytes / SHA-256
`c2994530e3da1711d44f8c36315c40874e87f1968d1a81c1432105de2251c2ee`.
The full driver needed two concrete preamble repairs—loading `tabularx` and
restoring the already established `Y` column type—then completed its clean
XeLaTeX/Biber/makeindex build. The final 113,458-byte log has SHA-256
`95cb040d490d7dcc91a296b2a254604fa557b16cb07d4130a6dbf8c2b7a447d1`
and contains no fatal or unresolved diagnostics.

All 521 pages were rendered in order and inspected through 21 contact sheets;
24 cover, transition, final, and largest-diagnostic pages were inspected again
at 110 dpi. The centered text block consistently fills the page and no clipping,
overlap, malformed page, or accidental blank page was found. Exact evidence is
in `qa/LI_COMPLETE_VISUAL_QA_20260829.json`.

## Modular backend

Four schema-valid units cover the final four chapters, with stable IDs and 24
deterministic CSV projections:

- Unit 045 / Chapter 7: 153,133 bytes, SHA-256
  `6f387c95573d90b9863b6b50e3650fb89cc57e1bc370624fababe8c02393f5e3`.
- Unit 046 / Chapter 8: 141,197 bytes, SHA-256
  `5d3c6f58457dd5e0b2109df08a41bf998223ae80fdf201da6bb82560cf5bd25e`.
- Unit 047 / Chapter 9: 138,221 bytes, SHA-256
  `d71575577e66b4aa2ce4963876522ca99d54fa6eb73ca3be081e53efb7d1d2de`.
- Unit 048 / Chapter 10: 163,887 bytes, SHA-256
  `33f14d20639e5023da43d7c318ae73e815ba74bcb8586133a04f676ef703ba05`.

`scripts/generate_li_final_chapters_backend.py --check` and the shared semantic
validator both pass for all four units. Validation receipts are in
`qa/li-complete-evidence/unit-045-backend-validation.json` through
`unit-048-backend-validation.json`.

## Next action

Commit and push this complete-Li boundary using only explicit pathspecs,
perform anonymous public-byte readback, then publish reader-first version
`1.0.0` in the existing Zenodo concept DOI `10.5281/zenodo.22059759` and read
back every public file. Continue Duncan and CRing production afterward; do not
rerun this passing Li admission boundary without a concrete defect.
