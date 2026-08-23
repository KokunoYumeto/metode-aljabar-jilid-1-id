# Unit 011 admission — Kategori Fungtor

Status: admitted locally after independent source comparison, protected-topology
review, two clean builds, PDF checks, and all-page visual QA.

## Frozen content

- Authority: Li commit `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Range: complete `chapter2.tex:468-563` (96 physical lines).
- Source span: 6,733 bytes; SHA-256
  `892e22da2db9e269a7bacf112e82e7795a4c4b3a7d38d34212e569470696b4ad`.
- Indonesian span: 8,004 bytes; SHA-256
  `a848cb6d7dfdd7edc1f5b07be14f421ed075a8124723ab9b73a207f86216e105`.
- Reader: `artifacts/unit-011-bab-2-kategori-fungtor.pdf`, 7 pages, 105,391
  bytes; SHA-256
  `f18ea37d945b08961f14e49581dd13a5a3024307fe3d33a77c7d5bb5631859fe`.
- Final log: `qa/UNIT_011_BUILD_FINAL.log`, 85,824 bytes; SHA-256
  `873f96fdb5ac604e23ed5f1ab6955ba2d4deca869bd433c1bc6b9d11907ef78a`.

## Content and structure QA

The translated span preserves the exact multiset of 102 normalized mathematics
surfaces; all 17 begin/end environments; four labels; five ordinary references;
one equation reference; eight index commands; two list items; three emphasis
commands; and four TikZ-CD arrows. Han residue is zero and the next section
boundary is unchanged. The category-theory terminology follows the controlled
forms `kategori fungtor`, `fungtor biner`, `produk`, `koproduk`, `fungtor
proyeksi`, `fungtor inklusi`, `tarik balik`, `dorong maju`, and `pusat kategori`.

## Build and reader QA

The no-shell-escape builder completed twice in clean directories. The two PDF
containers are not claimed byte-identical, while all 7 pages render
pixel-identically under both MuPDF and Poppler at 144 dpi. The final log has no
undefined reference/citation, multiply-defined label, overfull box, or fatal TeX
error. The five expected Hyperref "Suppressing link with empty target"
warnings are intentional: the frozen `externaldocument` witness supplies
labels without inventing external URLs. The PDF declares `id-ID`, has 22 named destinations and 11 links, and
contains no Launch, GoToR, or JavaScript actions. All fonts are embedded. Every
page was visually inspected; no clipping, overlap, missing glyph, blank page, or
unreadable diagram was found.

## Rights and provenance

The source author remains Wen-Wei Li. The principal text and translation are
CC BY 4.0; closure-specific CC BY-SA 3.0 and OFL 1.1 notices remain separate.
This is an independent, non-endorsed derivative. Production provenance records
the exact model identification `OpenAI Codex gpt-5.6-sol, Ultra` separately from
source authorship and human-contributor credit.
