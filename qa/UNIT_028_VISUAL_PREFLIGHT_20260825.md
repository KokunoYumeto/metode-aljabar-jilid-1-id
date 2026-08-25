# Unit 028 visual and PDF preflight — 2026-08-25

Status: **PASS WITH WARNINGS**. No actionable defect was found. Both clean builds and the final artifact pass bound-identity, same-renderer decoded-pixel, all-page visual, PDF-structure, navigation, font, text, safety, and final-log gates.

This review is bounded to Unit 028. It changes no source, candidate, glossary, backend, control, artifact, or Git state. Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.

## Bound inputs

| Surface | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `build/unit-028-c-20260825/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan.pdf` | 7 | 108,700 | `ea6f6dea8bab77faf52f05517ad094fbabfb5e6f5294285269e565ab6edc084a` |
| `build/unit-028-d-20260825/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan.pdf` | 7 | 108,689 | `50c40ddefa870866568f8d1621d5fc204a1fd0fd0a45bdfc74659197c585790a` |
| `artifacts/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan-id.pdf` | 7 | 108,689 | `50c40ddefa870866568f8d1621d5fc204a1fd0fd0a45bdfc74659197c585790a` |
| `qa/UNIT_028_BUILD_FINAL.log` | — | 78,086 | `e34377e726cef55c50ead5b7a5e056ca332d653b0603a3e214f7b56d44594120` |

Build D and the final artifact are byte-identical. C and D differ only in volatile dvipdfmx font-subset naming; normalized semantic projections and every same-renderer decoded page agree.

## Deterministic evidence generation

`scripts/generate_unit_028_evidence.py` was run repeatedly from the bound inputs. Two consecutive complete regenerations produced an exactly equal sorted identity manifest for all 51 designed outputs (42 full-resolution page PNGs, six contact sheets, two JSON records, and the Markdown QA report). The manifest covers 51 paths and its UTF-8 SHA-256 is `df1df562ac48e219c2be601eaebfd25887d91aafedc6e6bd27211944073bd4de`.

Key generated identities after both runs:

| Output | Bytes | SHA-256 |
|---|---:|---|
| `qa/unit-028-evidence/render-hash-inventory.json` | 35,181 | `c622cde057eff3a70e0301d60fc6b46d3b3924153d7c01c2d4b7a206427ac310` |
| `qa/unit-028-evidence/structure-and-pdf-qa.json` | 55,099 | `e3907e0035f514b44180c6796ab44b5980ddd58c7110e1f7f6e4c4217d4d3426` |
| `qa/UNIT_028_VISUAL_QA_20260825.md` | 6,209 | `5ef33e044cd6c4e0b7cde33432a238d00ad835804ec4edbd7fd2deb7623bde73` |

## Rendering and all-page review

Poppler 24.04.0 and MuPDF 1.23.0 independently rendered C, D, and artifact at 144 dpi, yielding 42 full-resolution 998 × 1418 PNGs. All 14 C-versus-D and all 14 D-versus-artifact same-renderer pairs are decoded-RGB identical. Every render has zero ink in its outer three-pixel band.

All seven artifact pages were inspected in both renderer contact sheets. The cover and attribution page are centered, balanced, readable, and unclipped. Section 4.4, action/orbit/stabilizer definitions, numbered statements, proofs, citations, counting displays, conjugation and torsor material all remain within the live area with legible symbols and consistent hierarchy. The bibliography and two-column indexes on page 7 are readable; the remaining whitespace is intentional. No clipping, overflow, collision, broken stroke, missing label, tofu box, unintended sparse page, or edge contact was found.

## PDF, navigation, text, and log gates

- Each file is PDF 1.7, 498.9 × 708.66 pt, seven pages, unencrypted, unrotated, `/Lang id-ID`, with exact metadata and no form, JavaScript, embedded file, or additional action.
- The four-entry outline resolves to Section 4.4 on page 3 and the bibliography plus both indexes on page 7. All 38 named destinations resolve.
- Both `/GoTo` annotations close over that destination inventory; all three `/URI` annotations are HTTPS. Link rectangles, MuPDF text blocks, and the safe direct-page `/OpenAction` are in bounds.
- All 25 unique pypdf font objects and all 24 Poppler font rows are embedded. pypdf, Poppler layout text, and MuPDF text hashes match independently across C, D, and artifact. No extractor emits a replacement character; Poppler and MuPDF emit no NULs, while pypdf emits five at known mathematics-font loci.
- The final log ends with a seven-page marker and has zero fatal/error, unresolved-reference/citation, missing-character, empty-link-target, and overfull diagnostics. Reviewed warnings are three LaTeX release notices, one xeCJK notice, one frozen `braids` notice, six fontspec CJK advisories, and two visually benign underfull hboxes (badness 2865 and 10000).

## Disclosures

1. The PDF is untagged; no tagged-accessibility claim is made.
2. Two embedded mathematics fonts lack Unicode maps; visible glyphs and the two independent renderers pass.
3. Poppler reports that its optional Adobe-GB1 language pack is absent, followed by two dependent F37/show-space messages during layout-text extraction. Extracted text contains no replacement characters or NULs, all visible glyphs render, and no source or build correction is indicated.

Verdict: **PASS WITH WARNINGS; zero actionable defects.**
