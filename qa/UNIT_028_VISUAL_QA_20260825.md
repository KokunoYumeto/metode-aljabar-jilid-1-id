# Unit 028 visual and PDF QA — 2026-08-25

Status: **PASS WITH WARNINGS**. No actionable defect was found. Exact identity, same-renderer decoded-pixel, structure, metadata, navigation, font, text, action/link, clipping, and final-build-log gates pass.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
| `build/unit-028-c-20260825/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan.pdf` | 108,700 | `ea6f6dea8bab77faf52f05517ad094fbabfb5e6f5294285269e565ab6edc084a` |
| `build/unit-028-d-20260825/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan.pdf` | 108,689 | `50c40ddefa870866568f8d1621d5fc204a1fd0fd0a45bdfc74659197c585790a` |
| `artifacts/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan-id.pdf` | 108,689 | `50c40ddefa870866568f8d1621d5fc204a1fd0fd0a45bdfc74659197c585790a` |
| `qa/UNIT_028_BUILD_FINAL.log` | 78,086 | `e34377e726cef55c50ead5b7a5e056ca332d653b0603a3e214f7b56d44594120` |

Build D and the final artifact are byte-identical. All three PDFs have seven pages.

## Rendering gate

Poppler and MuPDF rendered every PDF at 144 dpi (998 × 1418 pixels per page). Equality uses decoded RGB pixels rather than PNG compression.

- poppler build-c vs build-d: all seven decoded RGB pages identical.
- poppler build-d vs artifact: all seven decoded RGB pages identical.
- mupdf build-c vs build-d: all seven decoded RGB pages identical.
- mupdf build-d vs artifact: all seven decoded RGB pages identical.

All 42 renders have zero ink pixels in their outer three-pixel band. Six contact sheets and every PNG/decoded-pixel identity are recorded in `qa/unit-028-evidence/render-hash-inventory.json`.

Final-artifact decoded RGB identities:

| Page | Poppler SHA-256 | MuPDF SHA-256 |
|---:|---|---|
| 1 | `d380f4722b406819b3131040ef1528ebbfac88dfadcaac32921d164bd09a82b8` | `631cb63e956033e68264ba565ecc0f1fb2292ebb8950e4e5153023a747061e25` |
| 2 | `d783f7f5398f0b64768ed850973bf0b8790517d2e872f9bcc0a7ebc0377452e5` | `5a4fb60c3a91e559f9bef1b564f1607f9ff544f02ac89ed4362004cc98f4c315` |
| 3 | `ed4245dff425e5a212c85ef6ae91e84f3e4e6b6b0b85d0fade915447b85f2bda` | `c4d1862c82c9ffe93f06313c1d8cb832ae28061f32d5fe6b70a6dc7a3f2bb795` |
| 4 | `03b376580dab5825bc2a112b4e52152b63af3be7e8eb716e614770de83cb1291` | `b4ec10eb6e2c35b845d44dccb72b94fa56f63309f70b1dff1f1dfe28cdbe050c` |
| 5 | `18b36fe60ecf610c44b66d1cd1ae3b99a3f18a87b54ac7ce810325890fdf3488` | `840a4319d1c903287ae36c302ff1c320485ff1f045730738b7b1c92e42ec7df8` |
| 6 | `cd9aec9c42c0dfff3505161b561e35f26a104b25abb35154a04769f0f6b9544a` | `32b19411bd228d582bf030288a74ac5908aebba7f3b5cdfc0ed9c64f476f402f` |
| 7 | `361455154755ac139b325a9b0a48b7044cb55dff6eee5a6ec9ca1b4a06cb9652` | `51d2821bd861641f999858341760e8205e58ed473954ae0974d18eaab71a4573` |

## PDF gate

- PDF `%PDF-1.7`; `/Lang id-ID`; seven pages; unencrypted; exact metadata; no form, JavaScript, additional action, or embedded file.
- The four-entry outline resolves to Section 4.4 on page 3 and the bibliography plus both indexes on page 7. All 38 named destinations resolve.
- Both `/GoTo` actions close over the destination inventory; all three `/URI` actions are HTTPS. `/OpenAction` is a safe direct page destination.
- Link rectangles and MuPDF text blocks are in bounds. All 25 pypdf font objects and 24 `pdffonts` rows are embedded.
- pypdf, Poppler layout text, and MuPDF text hashes match separately across C, D, and artifact. There are no replacement characters; Poppler and MuPDF have no NULs, while pypdf has five at conventional mathematics-font loci without Unicode maps.

## Independent full-resolution review

All pages were reviewed independently in Poppler and MuPDF.

| Page | Finding |
|---:|---|
| 1 | Cover hierarchy, wrapped Unit 28 subtitle, scope box, date, and trim margins are balanced and readable. |
| 2 | Edition, source attribution, ISBN, licence, non-endorsement, model provenance, links, and CC badge are unclipped and collision-free. |
| 3 | Section 4.4 heading, action-group definition, orbit and stabilizer displays, and theorem hierarchy reflow cleanly without crowding. |
| 4 | Orbit-stabilizer proof, conjugation examples, and both citation links remain aligned, readable, and within the live area. |
| 5 | Counting formulas, fixed-point material, and displayed mathematics are centered with clear relation symbols and no overflow. |
| 6 | Burnside-type counting argument, examples, and final section transition remain coherent, unclipped, and typographically balanced. |
| 7 | Bibliography plus two-column term and symbol indexes are readable; lower-page whitespace is intentional. |

No clipping, overflow, collision, broken mathematical or diagram stroke, missing label, tofu box, unintended sparse page, or edge contact was found.

## Warnings

1. `/Lang id-ID` is correct, but the PDF is untagged; no tagged-accessibility claim is made.
2. dvipdfmx assigns volatile six-letter subset tags, explaining why build C is not byte-identical to build D. Normalized font inventories, three independent text surfaces, and both renderers agree; build D and the final artifact are byte-identical.
3. The final log has 3 LaTeX release warnings, 1 xeCJK warning, 1 frozen `braids` warning, 6 fontspec CJK advisories, 2 visually benign underfull hboxes (badness 2865, 10000), and no underfull vbox. Fatal/error, unresolved-reference/citation, missing-character, and overfull diagnostics are zero.
4. Two embedded mathematics fonts lack Unicode maps. This yields the stable pypdf NUL count above, but Poppler and MuPDF extraction, visible glyphs, and same-renderer comparisons pass.
5. Poppler reports the absent optional Adobe-GB1 language pack and two dependent F37/show-space diagnostics during layout-text extraction. The extracted text has no replacement characters or NULs, and both independent renderers show all visible glyphs correctly.

Evidence: `structure-and-pdf-qa.json` holds exact structures, metadata, destinations, actions, fonts, text hashes, geometry, and final-log checks. `render-hash-inventory.json` holds all 42 render identities, comparisons, edge results, and six contact-sheet identities.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict: **PASS WITH WARNINGS; zero actionable defects.**
