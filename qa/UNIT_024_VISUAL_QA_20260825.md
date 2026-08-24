# Unit 024 reader visual QA — 2026-08-25

Status: **PASS**

Artifact: `artifacts/unit-024-bab-3-latihan-kategori-monoidal.pdf`, 4 pages,
86,254 bytes, SHA-256
`eb4ee13fffe6a54a50357a0043aa82e0958b2f30feb92c440b6ea10a5efdc6b4`.

## Inspection basis

Every physical page 1--4 was inspected at 998 x 1418 pixels in both renderer
families:

- Poppler (`pdftoppm`, 144 dpi);
- MuPDF (`mutool draw`, 144 dpi), with PyMuPDF independently used for PDF text,
  page geometry, and out-of-bounds-block inspection.

The inspected final-B contact sheets are:

- `build/unit-024-reader-final-visual/contact-sheets/b-poppler.png`, 1,274,121
  bytes, SHA-256
  `e4a0ab5d8ddcdee1d359eb34c96c46dd1a956c5cfbd58359157698cf957a73d3`;
- `build/unit-024-reader-final-visual/contact-sheets/b-mupdf.png`, 1,270,968
  bytes, SHA-256
  `d36c84c70ba621e98ece3d4b49d1d1e7bfc2a8d12d7471993e9f63d9ad140c06`.

The A, B, replay, and artifact contact sheets are byte-identical within each
renderer family. The 32 page renders and 8 contact sheets are inventoried in
`qa/unit-024-evidence/render-hash-inventory.json`.

## Page-by-page adjudication

| Physical page | Inspection finding in both renderers |
|---:|---|
| 1 | Cover is centered and balanced. The prose scope box explicitly says this is the complete eight-exercise block but partial Bab 3 coverage; no ambiguous filled/unfilled progress blocks remain. No clipping, edge contact, or off-center composition. |
| 2 | Attribution, CC BY 4.0 notice, independent/non-endorsed status, component notices, correction `O013-LI-U024-COR-001`, and `OpenAI Codex gpt-5.6-sol, Ultra` provenance are legible. The three logged underfull horizontal boxes are confined to this deliberately narrow imprint alignment and cause no visible gap, overlap, or malformed line. |
| 3 | Exercises 1--5 and both boxed hints are present. Catalan and Yang--Baxter displays are centered; the long Hecke identity now stays inside the text measure. Mathematical glyphs, fractions, cases, subscripts, and reference numbers are intact. |
| 4 | Exercises 6--8 are present. Both commutative diagrams have complete nodes and all eight arrows across the two `tikzcd` environments. The one-entry term index follows the exercise block on the same page; the page is neither crowded nor an orphan. |

Pages inspected: `[1, 2, 3, 4]`.

Renderers inspected: `Poppler`, `MuPDF (mutool and PyMuPDF)`.

## Reflow decision

The first layout used the source book's 132 mm print measure. It produced a
21.85155 pt overfull tensor identity and sent the single `YBE` index entry to a
sparse fifth page. The admitted driver uses a centered 142 mm digital-reader
measure without reducing the type size, and renders the one-entry index without
the print-oriented multi-column break. The admitted result is four pages with
zero overfull boxes, zero empty-target link warnings, and no lost or altered
exercise, hint, diagram, reference, or index entry.

## Deterministic and PDF checks

- Canonical target lines 872--910 are byte-identical to the isolated candidate:
  39 LF records, 6,071 bytes, SHA-256
  `576c39746534853cd5127298cf0c2ba7f6afb239e4d7b83f368b7a9969c5f43a`.
- All 8 exercises, 3 nested items, 2 hints, 69 inline-math spans, 6 bracket
  displays, 2 `tikzcd` diagrams, 8 arrows, 4 references, and the `YBE` index
  entry pass the protected-topology checks.
- Clean A/B/replay PDFs differ only in regenerated six-letter embedded-font
  subset prefixes. Extracted-text hashes, normalized font families, PDF
  structure, and every decoded page pixel are identical; same-renderer pixel
  mismatches are Poppler 0 and MuPDF 0. Final-B is the frozen artifact.
- PDF safety checks found no encryption, AcroForm, JavaScript, embedded files,
  catalog additional actions, unsafe actions, out-of-bounds text, replacement
  characters, NULs, unresolved tokens, or Han residue. All 22 fonts are
  embedded. `/Lang` is `id-ID`; the PDF is not structurally tagged.
- Navigation is coherent: outlines are `Bab 3: Kategori Monoidal`, `Latihan`,
  and `Indeks Istilah`; 5 named destinations, 1 internal `GoTo`, and 3 safe
  HTTPS URI actions are present. Earlier-unit references are intentionally
  printed as frozen numbers without false links.

Structured evidence: `qa/unit-024-evidence/structure-and-pdf-qa.json`, 33,299
bytes, SHA-256
`12cf8ec6af6b51fee727e6554ae3f6a182b562f5349a726a6b81389885443c72`.

Render inventory: `qa/unit-024-evidence/render-hash-inventory.json`, 7,110
bytes, SHA-256
`d60e5a81bdd248b659d6440b6d442a8e4f6ca6a15dc0632e9dd45d9139f0c892`.

