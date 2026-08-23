# Unit 012 admission — Sifat Universal dan Kategori Koma

Status: admitted locally after independent source comparison, protected-topology
review, two clean builds, PDF checks, and all-page visual QA.

## Frozen content

- Authority: Li commit `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Range: complete `chapter2.tex:564-677` (114 physical lines), ending immediately
  before the next source section `\section{可表函子}` at line 678.
- Source span: 9,095 bytes; SHA-256
  `b9c84bf31468f78576a80b096871d72fd6d109742b2f816c36724cac467f1239`.
- Indonesian span: 11,056 bytes; SHA-256
  `26a2e9a638fae91a1108c9a263a89b64b71ba5d351cae1bfae72eef6eba0649b`.
- Reader: `artifacts/unit-012-bab-2-sifat-universal-dan-kategori-koma.pdf`,
  10 pages, 121,388 bytes; SHA-256
  `1671beea4ab78c848d577f9b8428d5717de2ac55f309f4f075c455409fd878a9`.
- Final log: `qa/UNIT_012_BUILD_FINAL.log`, 85,731 bytes; SHA-256
  `1a0c18fa6efa5078e35c6bf9c42785888c57a209e0148b928773105f1ec55f7c`.

## Content and structure QA

The translated span preserves 159 normalized mathematics surfaces; all 20
environment tokens; seven labels; six protected references; one citation
(`Xiong` at source/target line 624); six index entries; eight TikZ-CD diagrams;
and zero exercises, hints, answers, or solutions. The next source boundary is
unchanged. Han residue is zero in the translated span. Terminology follows the
controlled forms `objek awal`, `objek terminal`, `objek nol`, `morfisme nol`,
`kategori koma`, `pelengkapan metrik`, `pembenaman diagonal`, `fungtor
representabel`, `kategori slice`, `kategori koslice`, and `terfibrasi`.

## Build and reader QA

Two clean builds (`build/unit-012-replay` and
`build/unit-012-replay-postmeta`) produced 10 pages. At 144 dpi, all 10 MuPDF
pages and all 10 Poppler pages are pixel-identical within each renderer; the
concatenated hashes are recorded in the build summary. The final log has no
undefined reference/citation, multiply-defined label, overfull box, fatal TeX,
or emergency-stop blocker. The three suppressed empty external-document links
are intentional: the frozen `unit-012-crossrefs.aux` witness supplies labels
without inventing external URLs. All ten pages were visually inspected; the
short final page is an intentional source-order boundary before the next unit.
The PDF declares the Indonesian title/author metadata, has 11 internal GoTo and
3 URI actions, and contains no Launch, GoToR, or JavaScript actions.

## Rights and provenance

The source author remains Wen-Wei Li. The principal text and Indonesian
translation are CC BY 4.0; closure-specific CC BY-SA 3.0 and OFL 1.1 notices
remain separate. This is an independent, non-endorsed derivative. Production
provenance records the exact model identification `OpenAI Codex gpt-5.6-sol, Ultra`
separately from source authorship and human-contributor credit.
