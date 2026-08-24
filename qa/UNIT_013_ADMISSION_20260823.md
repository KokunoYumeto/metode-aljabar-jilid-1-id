# Unit 013 admission - Fungtor Representabel dan Lema Yoneda

Status: admitted locally after independent source comparison, protected-topology
review, corrected Chapter 2 equation continuity, two clean builds, PDF checks,
terminology QA, and all-page visual QA.

## Frozen content

- Authority: Li commit `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Range: complete `chapter2.tex:678-765` (88 physical lines), ending immediately
  before Section 2.6 on adjoint functors at line 766.
- Source span: 7,413 bytes; SHA-256
  `9b30201ad8df7822e2e6bb20080097bff6ef663c763653f859f6ab4e028b2928`.
- Indonesian span: 8,643 bytes; SHA-256
  `eeb6bbb2aca0ea17277e7afea39492729996cd9d8648deccc94bcebe9111327d`.
- Full target at the original Unit 013 admission boundary: 154,532 bytes;
  SHA-256 `81d89e8d4f94f4aea8358e4997175abdf69ec9b537eff9c788b0beafa26b5e2e`.
  Later source-order units may extend that shared file; Unit 013 is bound to its
  frozen span above.
- Standalone driver: 4,776 bytes; SHA-256
  `f3a7b9e2351288eaf273930572d564cb8d0011e44441cd22246e8f385985cdf2`.
- Reader: `artifacts/unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.pdf`,
  7 pages, 106,162 bytes; SHA-256
  `03ced2b80bf14814d01bc73cf378bfab820ec40ad0571eaa33cf514d79d760cf`.
- Final log: `qa/UNIT_013_BUILD_FINAL.log`, 86,834 bytes; SHA-256
  `605c9d68009fcfa0d9b746864ebad7e1618943932cd6d8cd1140e84fbd657039`.

## Content, terminology, and source corrections

The span preserves 98 normalized mathematics surfaces after the two disclosed
source corrections; all 17 environment tokens; seven labels; ten ordinary
references; three equation references; five index entries; two TikZ-CD
diagrams; and zero citations, exercises, hints, answers, or solutions. Han
residue is zero and line 766 remains the next source-order boundary.

- `O013-LI-U013-COR-001`: source line 753 writes
  `Hom_{\mathcal C}` in the power-set example although the domain category is
  `Set`; the target uses `Hom_{\cate{Set}}`.
- `O013-LI-U013-COR-002`: source line 762 says Eilenberg-MacLane spaces
  represent homology; the target correctly states cohomology.

The bounded Indonesian field-usage recheck found no suitable same-field arXiv
TeX source, so it reinspected the documented UNDIP and UGM PDFs, the Pusat
Bahasa glossary, and a narrowly identified UI Yoneda witness. It supports the
controlled forms `fungtor`, `Lema Yoneda`, `transformasi natural`, `morfisme`,
`fungtor representabel`, `representasi fungtor`, `keluarga universal`,
`fungsi karakteristik`, and `fungsi rampat`. `pragemal (presheaf)` and `teori
gemal (sheaf theory)` are explicitly standards-based choices, not falsely
claimed as broad field attestation. No admitted Unit 001-012 reader required a
new correction.

## Standalone equation continuity

The complete Chapter 2 source has two numbered equations before this unit:
`eqn:naturaltrans-def` at line 255 is (2.1), and `eqn:horizontal-comp` at line
290 is (2.2). The standalone driver now sets `equation` to 2 immediately before
loading `chapter2.tex:678-765`. Its final AUX therefore records
`eqn:Yoneda-cat-duality` as (2.3), page 1, anchor `equation.2.3`, and
`eqn:Yoneda-map` as (2.4), page 1, anchor `equation.2.4`. This repairs only the
standalone inherited counter state; it changes no translated prose, formula,
diagram, source correction, terminology decision, label, or reference target.

## Build and reader QA

Two clean builds (`build/unit-013-equation-fix-a` and
`build/unit-013-equation-fix-b`) produced 7 pages. All 7 MuPDF pages and all 7
Poppler pages are pixel-identical between the builds at 144 dpi. Relative to
the prior reader, pages 1, 2, 5, 6, and 7 remain pixel-identical in both
renderers; only page 3 (the two equation numbers) and page 4 (their three
references) changed.

The final log has no undefined reference or citation, multiply-defined label,
overfull box, empty bibliography, missing glyph, fatal TeX error, or emergency
stop. The seven suppressed empty external-document links are intentional: the
frozen cross-reference witness supplies numbers without inventing external
URLs.

All seven pages were visually inspected in both Poppler and MuPDF. The corrected
(2.3) and (2.4) numbers and all their references are legible, and there is no
clipping, overlap, missing content, blank page, or unreadable surface. Both
nonempty indexes remain on one final page. The PDF declares `id-ID`, has 21
named destinations, three outline entries, 11 GoTo and three URI actions, and
no Launch, GoToR, JavaScript, or other action. All fonts are embedded.

## Rights and provenance

The source author remains Wen-Wei Li. The principal text and Indonesian
translation are CC BY 4.0; closure-specific CC BY-SA 3.0 and OFL 1.1 notices
remain separate. This is an independent, non-endorsed derivative. Production
provenance records the exact model identification `OpenAI Codex gpt-5.6-sol, Ultra`
separately from source authorship and every human-contributor credit.
