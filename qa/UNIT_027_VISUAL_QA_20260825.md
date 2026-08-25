# Unit 027 visual and PDF QA — 2026-08-25

Status: **PASS WITH WARNINGS**. No actionable defect was found. Exact identity, same-renderer decoded-pixel, structure, metadata, navigation, font, text, action/link, clipping, and final-build-log gates pass.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
| `build/unit-027-c-20260825/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup.pdf` | 97,436 | `c8ec8a08e94c9f762b94029bc9b2fe68d4bf1e2242511f2464958c0548b817c3` |
| `build/unit-027-d-20260825/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup.pdf` | 97,427 | `8eeab2d34a745b0e5a12acc29c0c5474e9c84d1248686d743302c03859851dd7` |
| `artifacts/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup-id.pdf` | 97,427 | `8eeab2d34a745b0e5a12acc29c0c5474e9c84d1248686d743302c03859851dd7` |
| `qa/UNIT_027_BUILD_FINAL.log` | 86,569 | `b18386c3273612276813fa1c9fa00a606becc3d35e980e68351f258bfc893cb4` |

Build D and the final artifact are byte-identical. All three PDFs have seven pages.

## Rendering gate

Poppler and MuPDF rendered every PDF at 144 dpi (998 × 1418 pixels per page). Equality uses decoded RGB pixels rather than PNG compression.

- poppler build-c vs build-d: all seven decoded RGB pages identical.
- poppler build-d vs artifact: all seven decoded RGB pages identical.
- mupdf build-c vs build-d: all seven decoded RGB pages identical.
- mupdf build-d vs artifact: all seven decoded RGB pages identical.

All 42 renders have zero ink pixels in their outer three-pixel band. Six contact sheets and every PNG/decoded-pixel identity are recorded in `qa/unit-027-evidence/render-hash-inventory.json`.

Final-artifact decoded RGB identities:

| Page | Poppler SHA-256 | MuPDF SHA-256 |
|---:|---|---|
| 1 | `dc5811e3e2cad79027d15a325c2a677756d22c5b8626b5c7724099d5161dd155` | `79fcaeb8ec8613365e965b207ed0d9997ab4e51a65129b85140d0dd440b80a48` |
| 2 | `40db10b2241f1548968d9ad615cbf23561aa813fa2443e7caab031f8b619850e` | `8b9abdb52b333d3d7d9ca0ccd0619eca080ca49e5252447c1ce5011d3d8f894d` |
| 3 | `1aaea1115a50d3adaa160854ef71fcf8ea7738a604a2fcf757f83958e205ef05` | `a8194981c454cad54be42721066319fe028d8bd6658cd88af44e5e6f9866b988` |
| 4 | `c185764bcd0f32c88075691302467e6f39032c362391a9a2b0c1c198acbd8f37` | `1eb4633fc03ab396bd77fdb1cdf8a8bfa7ba32eecd2d491e5e34301d9f451111` |
| 5 | `9faf9f75bdde970b296742fc8295948e24584c6b2cc2f99c95806d7e68b69da3` | `d6154f3ce3d3d91086150fe680444f50143254681340413bdcf015651bfd15f2` |
| 6 | `0742a494d0ac7fe194181cd31fecee508173ddac277bf14fc94dbaca95f20542` | `2237a8a7c5a05a640f131a9b031933453612b6da2d72230623241cf35bf3e6f4` |
| 7 | `7d18a3a9a54cefb6324914ccc36dc0cdde1446d42fb9bba865a7818fdad837fe` | `aa193621b5b1a2190a57d9d4af599d24cfd47f2712a9fac12bd1df8c2d1f1994` |

## PDF gate

- PDF `%PDF-1.7`; `/Lang id-ID`; seven pages; unencrypted; exact metadata; no form, JavaScript, additional action, or embedded file.
- The three-entry outline resolves to Section 4.3 on page 3 and both indexes on page 7. All 30 named destinations resolve.
- All ten `/GoTo` actions close over the destination inventory; all three `/URI` actions are HTTPS. `/OpenAction` is a safe direct page destination.
- Link rectangles and MuPDF text blocks are in bounds. All 22 pypdf font objects and 22 `pdffonts` rows are embedded.
- pypdf, Poppler layout text, and MuPDF text hashes match separately across C, D, and artifact. There are no replacement characters; Poppler has no NULs, while pypdf has eight and MuPDF one at conventional mathematics-font loci without Unicode maps.

## Independent full-resolution review

All pages were reviewed independently in Poppler and MuPDF.

| Page | Finding |
|---:|---|
| 1 | Cover hierarchy, wrapped Unit 27 subtitle, scope box, date, and trim margins are balanced and readable. |
| 2 | Edition, source attribution, ISBN, licence, non-endorsement, model provenance, links, and CC badge are unclipped and collision-free. |
| 3 | Section 4.3 heading reflows cleanly; direct-product definition, bullets, displayed projection, universal diagram, lemma, and proof remain centered and readable. |
| 4 | Semidirect-product definition, numbered explanation, equation (4.1), and Lemma 4.3.4 are aligned with no overflow. |
| 5 | Proof, dihedral-group example, all three polygon/reflection diagrams, captions, and Lemma 4.3.6 have clear strokes and labels. |
| 6 | Internal direct-product display, exact-sequence definition, equations, extension diagram, and page transition are centered and unclipped. |
| 7 | Split-extension diagrams, two-column term index, and symbol index are readable; lower-page whitespace is intentional. |

No clipping, overflow, collision, broken mathematical or diagram stroke, missing label, tofu box, unintended sparse page, or edge contact was found.

## Warnings

1. `/Lang id-ID` is correct, but the PDF is untagged; no tagged-accessibility claim is made.
2. dvipdfmx assigns volatile six-letter subset tags, explaining why build C is not byte-identical to build D. Normalized font inventories, three independent text surfaces, and both renderers agree; build D and the final artifact are byte-identical.
3. The final log has 3 LaTeX release warnings, 1 xeCJK warning, 1 frozen `braids` warning, 6 fontspec CJK advisories, 4 visually benign underfull hboxes (badness 3168, 2865, 10000, 1406), and 1 visually benign underfull vbox (badness 1478). Fatal/error, unresolved-reference/citation, missing-character, and overfull diagnostics are zero.
4. Three embedded mathematics fonts lack Unicode maps. This yields the stable NUL counts above in pypdf/MuPDF extraction, but Poppler extraction, visible glyphs, and same-renderer comparisons pass.
5. The raw log contains an absolute profile path; generated evidence is sanitized and does not reproduce it.

Evidence: `structure-and-pdf-qa.json` holds exact structures, metadata, destinations, actions, fonts, text hashes, geometry, and final-log checks. `render-hash-inventory.json` holds all 42 render identities, comparisons, edge results, and six contact-sheet identities.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict: **PASS WITH WARNINGS; zero actionable defects.**
