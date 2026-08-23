# Unit 013 admission - Fungtor Representabel dan Lema Yoneda

Status: admitted locally after independent source comparison, protected-topology
review, two clean builds, PDF checks, terminology QA, and all-page visual QA.

## Frozen content

- Authority: Li commit `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Range: complete `chapter2.tex:678-765` (88 physical lines), ending immediately
  before Section 2.6 on adjoint functors at line 766.
- Source span: 7,413 bytes; SHA-256
  `9b30201ad8df7822e2e6bb20080097bff6ef663c763653f859f6ab4e028b2928`.
- Indonesian span: 8,643 bytes; SHA-256
  `eeb6bbb2aca0ea17277e7afea39492729996cd9d8648deccc94bcebe9111327d`.
- Full current target: 154,532 bytes; SHA-256
  `81d89e8d4f94f4aea8358e4997175abdf69ec9b537eff9c788b0beafa26b5e2e`.
- Reader: `artifacts/unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.pdf`,
  7 pages, 106,154 bytes; SHA-256
  `4db806c3a0c42449b1333e25109d135176931880a48982a70b776e04be7ffa2a`.
- Final log: `qa/UNIT_013_BUILD_FINAL.log`, 86,810 bytes; SHA-256
  `a407323233d53e8f20d952dbacaea16000ccb96b7c03bf9854695f9110311b91`.

## Content, terminology, and corrections

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

## Build and reader QA

Two clean builds (`build/unit-013-admission-f` and
`build/unit-013-admission-g`) produced 7 pages. All 7 MuPDF pages and all 7
Poppler pages are pixel-identical within each renderer at 144 dpi. The final
log has no undefined reference or citation, multiply-defined label, overfull
box, empty bibliography, missing glyph, fatal TeX error, or emergency stop.
The seven suppressed empty external-document links are intentional: the frozen
cross-reference witness supplies numbers without inventing external URLs.

All pages were visually inspected. The long Yoneda isomorphism was reflowed as
a display, removing the original 18 pt overflow. Both nonempty indexes remain,
but the one-entry symbol index now shares the final page instead of consuming a
separate nearly blank page. The PDF declares `id-ID`, has 21 named destinations,
three outline entries, 11 GoTo and three URI actions, and no Launch, GoToR, or
JavaScript action.

## Rights and provenance

The source author remains Wen-Wei Li. The principal text and Indonesian
translation are CC BY 4.0; closure-specific CC BY-SA 3.0 and OFL 1.1 notices
remain separate. This is an independent, non-endorsed derivative. Production
provenance records the exact model identification `OpenAI Codex gpt-5.6-sol, Ultra`
separately from source authorship and every human-contributor credit.
