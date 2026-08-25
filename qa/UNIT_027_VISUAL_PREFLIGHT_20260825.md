# Unit 027 visual and PDF preflight — 2026-08-25

Status: **PASS WITH WARNINGS**. No actionable defect was found. Both clean builds pass exact identity, same-renderer decoded-pixel, all-page visual, PDF structure, navigation, font, text, safety, and build-log gates.

This was a bounded, read-only preflight. No source, driver, candidate, glossary, backend, control, artifact, or Git state was changed. Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.

## Bound inputs

| Build | Path | Pages | Bytes | SHA-256 |
|---|---|---:|---:|---|
| C | `build/unit-027-c-20260825/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup.pdf` | 7 | 97,436 | `c8ec8a08e94c9f762b94029bc9b2fe68d4bf1e2242511f2464958c0548b817c3` |
| D | `build/unit-027-d-20260825/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup.pdf` | 7 | 97,427 | `8eeab2d34a745b0e5a12acc29c0c5474e9c84d1248686d743302c03859851dd7` |

The PDFs are not byte-identical. Their semantic projections are identical after removing only dvipdfmx's volatile six-letter font-subset prefixes and the embedded Type 1 program hashes whose internal PostScript names contain those prefixes. Metadata, page geometry, outline, destinations, annotations/actions, normalized font inventory and sizes, text hashes in three extractors, text-block geometry, and decoded rendering all agree.

## Rendering and decoded-pixel gate

Every page of C and D was rendered at 144 dpi by Poppler 24.04.0 and MuPDF 1.23.0, producing 28 full-resolution 998 × 1418 PNGs. Same-renderer comparisons use SHA-256 over decoded RGB bytes, not PNG-compressed bytes. All 14 C-versus-D page pairs are exactly equal. Every render has zero ink pixels in its outer three-pixel band.

| Page | Poppler C = D decoded RGB SHA-256 | MuPDF C = D decoded RGB SHA-256 |
|---:|---|---|
| 1 | `dc5811e3e2cad79027d15a325c2a677756d22c5b8626b5c7724099d5161dd155` | `79fcaeb8ec8613365e965b207ed0d9997ab4e51a65129b85140d0dd440b80a48` |
| 2 | `40db10b2241f1548968d9ad615cbf23561aa813fa2443e7caab031f8b619850e` | `8b9abdb52b333d3d7d9ca0ccd0619eca080ca49e5252447c1ce5011d3d8f894d` |
| 3 | `1aaea1115a50d3adaa160854ef71fcf8ea7738a604a2fcf757f83958e205ef05` | `a8194981c454cad54be42721066319fe028d8bd6658cd88af44e5e6f9866b988` |
| 4 | `c185764bcd0f32c88075691302467e6f39032c362391a9a2b0c1c198acbd8f37` | `1eb4633fc03ab396bd77fdb1cdf8a8bfa7ba32eecd2d491e5e34301d9f451111` |
| 5 | `9faf9f75bdde970b296742fc8295948e24584c6b2cc2f99c95806d7e68b69da3` | `d6154f3ce3d3d91086150fe680444f50143254681340413bdcf015651bfd15f2` |
| 6 | `0742a494d0ac7fe194181cd31fecee508173ddac277bf14fc94dbaca95f20542` | `2237a8a7c5a05a640f131a9b031933453612b6da2d72230623241cf35bf3e6f4` |
| 7 | `7d18a3a9a54cefb6324914ccc36dc0cdde1446d42fb9bba865a7818fdad837fe` | `aa193621b5b1a2190a57d9d4af599d24cfd47f2712a9fac12bd1df8c2d1f1994` |

## Independent all-page review

All pages were inspected at full resolution in both renderers.

| Page | Finding |
|---:|---|
| 1 | Cover hierarchy, wrapped Unit 27 subtitle, scope box, date, and trim margins are balanced and readable. |
| 2 | Edition, source attribution, ISBN, licence, non-endorsement, model provenance, links, and CC badge are unclipped and collision-free. |
| 3 | Section 4.3 heading reflows cleanly; direct-product definition, bullets, displayed projection, universal diagram, lemma, and proof remain centered and readable. |
| 4 | Semidirect-product definition, numbered explanation, equation (4.1), and Lemma 4.3.4 are aligned with no overflow. |
| 5 | Proof, dihedral-group example, all three polygon/reflection diagrams, captions, and Lemma 4.3.6 have clear strokes and labels. |
| 6 | Internal direct-product display, exact-sequence definition, equations, extension diagram, and page transition are centered and unclipped. |
| 7 | Split-extension diagrams, two-column term index, and symbol index are readable. Lower-page whitespace is intentional and not a lost-content symptom. |

No clipping, overflow, collision, broken diagram stroke, missing label, tofu box, unintended sparse page, or edge contact was found.

## PDF structure, navigation, fonts, text, and safety

- Both files are PDF 1.7, seven pages, 498.9 × 708.66 pt, unencrypted, unrotated, with identical CropBox and MediaBox on every page.
- `/Lang` is `id-ID`; metadata is exact and identical, including title, subject, author, keywords, producer, and frozen creation date.
- The three-entry outline resolves to Section 4.3 on page 3 and the two indexes on page 7.
- All 30 named destinations resolve. All 13 link annotations are in bounds: ten `/GoTo` actions close over the destination inventory and three `/URI` actions use HTTPS.
- `/OpenAction` is a safe direct page `/Fit` destination, not executable code. There is no AcroForm, JavaScript, embedded file, catalog/page/annotation additional action, unsafe action type, or non-HTTPS URI.
- All MuPDF text blocks lie within page bounds. C and D have equal per-page pypdf and MuPDF text hashes and equal whole-document Poppler layout-text hash (`bf528e344b6f3630c3f8bcb6abc8655dcf4099bd38b1bfd05103f3e579c2bbf`).
- All 22 font objects are embedded. Poppler reports Unicode maps for 19; the three without maps are conventional mathematics fonts. This did not produce lost glyphs or C/D extraction divergence.

## Build-log gate

| Build | Log bytes | Log SHA-256 |
|---|---:|---|
| C | 86,569 | `45ef70336241f55bfd45d26f3be8e0293d7e42a3d4809a5b1989d0380740c01f` |
| D | 86,569 | `b18386c3273612276813fa1c9fa00a606becc3d35e980e68351f258bfc893cb4` |

After replacing only the C/D build-directory token, the logs are byte-identical with normalized SHA-256 `81e93e3bbb19ea37ca9cda5092efd8f52947910aec02416bfc28313809043f30`. Both end with a seven-page output marker. Undefined controls, LaTeX errors, emergency/fatal stops, undefined references/citations, overfull hboxes, and overfull vboxes are all zero.

Reviewed non-blocking diagnostics per log: three LaTeX release warnings, one xeCJK family-redefinition warning, one frozen `braids` warning, six fontspec CJK advisories, four underfull hboxes, and one underfull vbox. The full-resolution inspection confirms that these diagnostics cause no visible defect.

## Warnings and evidence

1. `/Lang id-ID` is correct, but the PDF is untagged; no tagged-accessibility claim is made.
2. Volatile dvipdfmx font-subset tags explain the non-identical PDF bytes. Both same-renderer decoded-pixel comparisons and all normalized semantic checks pass.

Machine evidence is recorded in `qa/unit-027-staging-evidence/structure-and-render-preflight.json`. It contains both PDF/log identities, every PNG and decoded-pixel hash, pixel bounds, PDF structures, destinations, actions, fonts, text hashes, log censuses, and the all-page findings. The Poppler D contact sheet is 1,229,639 bytes with SHA-256 `0405a7abbc098e8a47482e2df7f54c177870ddc6a02a7b09bf4396537b425106`; the MuPDF D contact sheet is 1,221,175 bytes with SHA-256 `fd4f4a6a240f55b24f7dcffa7f7b1b4712f00bffb6a6e0a91e93bdbb501b75e2`.

Verdict: **PASS WITH WARNINGS; zero actionable defects.**
