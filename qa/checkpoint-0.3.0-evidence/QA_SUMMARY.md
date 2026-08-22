# Checkpoint Reader 0.3.0 - Build and QA Receipt

Status: **PASS**

## Final artifact

- Path: `output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-0.3.0-reader.pdf`
- Pages: 96
- Bytes: 1,517,117
- SHA-256: `1752f4535ea2f564aa6931ea0c4ba1da0daa4e7e90ae0c2433bedbb3f22d0dda`
- Page geometry: 96/96 at 498.90 x 708.66 pt, rotation 0
- Document language: `id-ID`
- Page mode: `/UseOutlines`
- Exact visible and metadata model identification: `OpenAI Codex gpt-5.6-sol, Ultra.`

Two consecutive executions of the deterministic builder produced the same byte
count and SHA-256. The build script is
`scripts/build_checkpoint_reader_0_3_0.py`, 10,240 bytes, SHA-256
`5459615841546be948d4547afdff8b00bdb0209acccb8de5d708e2d6940c9049`.

## Exact scope and assembly

The checkpoint contains the complete Pendahuluan, complete Bab 1, the Bab 2
introduction, and complete Bagian 2.1. Bagian 2.2 and everything after it are
explicitly absent. Unit starts are physical checkpoint pages 2, 23, 35, 46, 54,
66, 75, 79, and 84.

| Unit PDF | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `unit-001-pendahuluan.pdf` | 21 | 199,926 | `b3fca2af76b793a19877ffc822d6ec89c2494641f7e1dfa468b158c7bec30a3e` |
| `unit-002-bab-1-zfc.pdf` | 12 | 161,147 | `ff2eb3fd1ec5abaa7989d0c29c419c04f99368dc3f278799be460e30042bfe58` |
| `unit-003-bab-1-struktur-urutan-dan-ordinal.pdf` | 11 | 134,858 | `031e231bc5d2ac74cada865700d8f76dda327941c7f442e6d47324b848103df8` |
| `unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf` | 8 | 107,332 | `e48aa97d15ad9c192df5d744bfc8290fc816c4b681322295352517a02e267c13` |
| `unit-005-bab-1-kardinal.pdf` | 12 | 128,556 | `232d41f4e7f03123818ae14272958c8269242ebcbec68b832aaaf7ba295ebf3e` |
| `unit-006-bab-1-semesta-grothendieck.pdf` | 9 | 120,808 | `1fe15c59de6021b376643269423f2ef12e7b986f048ae39a31d8b1df9f7562c4` |
| `unit-007-bab-1-latihan.pdf` | 4 | 100,435 | `e7d4d6745f88b56c7ef840499c8e1d759b2bbbc14a245e8fc477fb0a6504a2b1` |
| `unit-008-bab-2-pengantar-teori-kategori.pdf` | 5 | 100,805 | `0db18bfbae3ffd2194447781a77effb4f57f8bd8521baa3acb334b474f0773cd` |
| `unit-009-bab-2-kategori-dan-morfisme.pdf` | 13 | 143,207 | `1a71610ba997348ce22db69944fec3529d9d6e6c2ef6ece48faa30df90ac5ce6` |

All 95 admitted unit page content streams are byte-identical to their source
unit PDFs after assembly. A separate 120 dpi MuPDF render of every source unit
is pixel-identical to checkpoint pages 2-96 (95/95). This proves that the merge
did not alter unit typography, diagrams, formulas, or page geometry.

## Structural and safety QA

- 299 named destinations; all 9 unit namespaces are present.
- 10 top-level outline entries: checkpoint status plus Units 001-009.
- 234 link annotations: 40 `/URI` and 194 `/GoTo` actions.
- Zero broken named links, unprefixed unit link targets, unsafe actions,
  additional actions, root open actions, forms, or JavaScript.
- 234 unique font objects; 234/234 embedded. Of these, 218 carry ToUnicode
  maps. The remaining 16 are inherited mathematical/CJK subset fonts from the
  admitted unit PDFs; the checkpoint does not claim a fully tagged PDF.
- The cover visibly preserves Wen-Wei Li's authorship and source commit,
  independent-edition/non-endorsement status, principal CC BY 4.0 text rights,
  CC BY-SA 3.0 component rights for `Lanzhou.png` and the credited `AJbook.cls`
  fragment, and OFL 1.1 font rights.

## All-page visual QA

Both Poppler and MuPDF rendered all 96 pages at 120 dpi. Poppler completed the
full render but reported local Adobe-GB1 mapping and legacy font-tag warnings on
some inherited source-unit pages. MuPDF rendered every page without omission;
its 95 admitted pages are pixel-identical to separately rendered source units.

Eight contact sheets covering pages 1-96 were inspected, together with the
cover, the intentional blank checkpoint page 5, all nine unit boundaries, and
the final page at full render size. No clipping, overlap, missing content,
broken diagrams, malformed formulas, or unreadable pages were observed. Page 5
is the intentional blank separator already present in the admitted Pendahuluan
unit, not a merge loss.

Machine-readable evidence, including every rendered-page hash and bounding box,
is in `qa/checkpoint-0.3.0-evidence/structure-and-render-qa.json`, 49,142 bytes,
SHA-256 `9655da3f16019bfd2bca59d68e2d3e1992fc5f499bcdbbc86f1c4b9aed3a6f48`.
The self-contained QA program is `scripts/qa_checkpoint_reader_0_3_0.py`,
20,496 bytes, SHA-256
`c76bdc0b70ef0fcbad023af2f7f90e3bd5c6b2a984a35fdab3ec5b6e772c2cf2`.
