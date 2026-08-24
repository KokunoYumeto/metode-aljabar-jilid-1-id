# Unit 024 reader visual QA — 2026-08-25

Status: **PASS**

Artifact: `artifacts/unit-024-bab-3-latihan-kategori-monoidal.pdf`, 4 pages,
86,255 bytes, SHA-256
`1b61a1e2b856f2ef5d9dbc800c6e593aeb776fd85e2480a53b26286639292e71`.

## Inspection basis

Every physical page 1--4 was inspected at 998 x 1418 pixels in both renderer
families:

- Poppler (`pdftoppm`, 144 dpi);
- MuPDF (`mutool draw`, 144 dpi), with PyMuPDF independently used for PDF text,
  page geometry, and out-of-bounds-block inspection.

The inspected final-B contact sheets are:

- `build/unit-024-reader-linkfix-final-visual/contact-sheets/b-poppler.png`, 361,745
  bytes, SHA-256
  `3d67d56ed41ffe0fcb5214602d0617e6000579ac0a033d0b5a634585d4b56bed`;
- `build/unit-024-reader-linkfix-final-visual/contact-sheets/b-mupdf.png`, 363,395
  bytes, SHA-256
  `260c2f2be1e76d61929ecbe04119d83eb74ee360bf4ea91e5d44bcb171f67dc0`.

The A, B, replay, and artifact page rasters are decoded-pixel-identical within
each renderer family. The 32 page renders and 8 contact sheets are inventoried in
`qa/unit-024-evidence/render-hash-inventory.json`.

## Page-by-page adjudication

| Physical page | Inspection finding in both renderers |
|---:|---|
| 1 | Cover is centered and balanced. The prose scope box explicitly says this is the complete eight-exercise block but partial Bab 3 coverage; no ambiguous filled/unfilled progress blocks remain. No clipping, edge contact, or off-center composition. |
| 2 | Attribution, CC BY 4.0 notice, independent/non-endorsed status, component notices, correction `O013-LI-U024-COR-001`, and `OpenAI Codex gpt-5.6-sol, Ultra` provenance are legible. The three logged underfull horizontal boxes are confined to this deliberately narrow imprint alignment and cause no visible gap, overlap, or malformed line. |
| 3 | Exercises 1--5 and both boxed hints are present. Catalan and Yang--Baxter displays are centered; the long Hecke identity now stays inside the text measure. Mathematical glyphs, fractions, cases, subscripts, and reference numbers are intact. |
| 4 | Exercises 6--8 are present. Both commutative diagrams have complete nodes and all eight arrows across the two `tikzcd` environments. The one-entry term index follows the exercise block on the same page; its `YBE, 1` link resolves to physical page 3. The page is neither crowded nor an orphan. |

Pages inspected: `[1, 2, 3, 4]`.

Renderers inspected: `Poppler`, `MuPDF (mutool and PyMuPDF)`.

## Reflow decision

The first layout used the source book's 132 mm print measure. It produced a
21.85155 pt overfull tensor identity and sent the single `YBE` index entry to a
sparse fifth page. The admitted driver uses a centered 142 mm digital-reader
measure without reducing the type size, and renders the one-entry index without
the print-oriented multi-column break. The admitted result is four pages with
zero overfull boxes, zero empty-target link warnings, zero broken internal
destinations, and no lost or altered
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
  and `Indeks Istilah`; 6 named destinations, 1 internal `GoTo`, and 3 safe
  HTTPS URI actions are present. The sole `GoTo` target, `page.1`, exists and
  resolves to physical page 3; the broken-destination inventory is empty.
  Earlier-unit references are intentionally
  printed as frozen numbers without false links.

Structured evidence: `qa/unit-024-evidence/structure-and-pdf-qa.json`, 34,531
bytes, SHA-256
`d479638e9b1b4b9982354c157fb22ba0c92177cb7d5c823476ef03254fccc28a`.

Render inventory: `qa/unit-024-evidence/render-hash-inventory.json`, 7,134
bytes, SHA-256
`159d349baff97e40ec63300032d23e8fe91c9b0a7ff56f18fa4cf3a4a0ef2050`.
