# Unit 010 admission — Fungtor dan Transformasi Natural

Status: admitted locally after independent semantic review, two clean builds,
structural/mathematical checks, PDF inspection, and all-page visual QA.

## Frozen content

- Authority: Li commit `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Range: complete `chapter2.tex:199-467` (269 physical lines).
- Source span: 23,553 bytes; SHA-256
  `316db06a11ca7b1caeb316a1285a7d506effb5d8c7c88459f33192a5ca94092a`.
- Indonesian span: 28,112 bytes; SHA-256
  `84cd01f4bfb9b2dcf6720991b72d714335e3f977e2bee88d40b2b64733572053`.
- Full target: 150,070 bytes; SHA-256
  `35e41d457ca14564a6da9d91272fe16d57f29a809d8b3297a608dc33ec252681`.
- Reader: `artifacts/unit-010-bab-2-fungtor-dan-transformasi-natural.pdf`,
  15 pages, 153,352 bytes; SHA-256
  `a06c4152e6233270cfa138b6c99ae9f307246fe2e1eac6b72a9533c9d74bfce4`.

## Content and structure QA

The translated span preserves the exact multiset of 291 normalized mathematics
surfaces; all 51 begin/end environments; 13 labels; seven ordinary references;
two equation references; two citations; 15 index commands; 17 list items; 13
emphasis commands; 81 tikzcd arrows; two TikZ draw commands; and the next
section boundary. Han residue is zero. An independent reviewer found no
mathematical-direction error, mistranslation, omission, or blocker.

Controlled terminology includes `fungtor`, `transformasi natural`,
`isomorfisme natural`, `fungtor penuh`, `fungtor setia`, `surjektif secara
esensial`, `komposisi vertikal`, `komposisi horizontal`, and `fungtor
kuasi-invers`. The glossary was extended without changing earlier admitted
meanings.

Three outside-span references were frozen from the official 445-page PDF and
pinned source: Lemma 4.7.3 (page 126), Section 3.5 (page 92), and Theorem
2.6.12 (page 56). The page offset is proven by the official PDF page labels.
The line-415 equivalence index entry was normalized to its complete display
form. This is a portability/source-consistency repair; the official xindy index
already merged the short source entry correctly.

## Build and reader QA

The no-shell-escape builder completed twice in clean directories. The PDF
containers differ by six serialization bytes, so byte identity is not claimed;
all 15 pages render pixel-identically under MuPDF at 144 dpi. The final log has
no unresolved citation/reference, multiply-defined label, overfull box, or
LaTeX/package fatal error. All fonts are embedded. The PDF declares `id-ID`,
has 54 named destinations and 27 links, and contains no Launch, GoToR, or
JavaScript actions. Poppler and MuPDF renders of every page were visually
inspected; no clipping, overlap, missing glyph, blank page, or unreadable
diagram was found.

## Rights and provenance

The source author remains Wen-Wei Li. The principal text and translation are
CC BY 4.0; closure-specific CC BY-SA 3.0 and OFL 1.1 notices remain separate.
This is an independent, non-endorsed derivative. Production provenance retains
the exact model identification `OpenAI Codex gpt-5.6-sol, Ultra`; it does not
replace or diminish source or human-contributor credit.

Backend validation and public GitHub byte readback are the remaining admission
transaction steps; this receipt does not claim either prematurely.
