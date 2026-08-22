# Indonesian category/algebra terminology QA - 2026-08-22

Status: complete; bounded terminology correction admitted before further
translation.

## Method and arXiv result

A bounded search of official arXiv surfaces was performed first, as directed.
Search families covered the Indonesian phrases `teori kategori`, `morfisme`,
`fungtor`/`funktor`, `gelanggang`, `Bahasa Indonesia`, and exact combinations
of those algebra/category terms. The official `all:gelanggang` query returned
no results. The only Indonesian-language arXiv hit found in the bounded search
was an unrelated engineering paper (`1607.04760`), so it was excluded. The API
then returned HTTP 429; the search stopped rather than becoming an inventory
loop. No suitable Indonesian algebra/category arXiv paper with downloadable
TeX was found, and no arXiv source package is represented as evidence.

The authorized Indonesian PDF fallback was therefore used.

## Primary Indonesian evidence

1. Luluk Atul Khasanah, *Kategori Produk dan Produk Dua Obyek dalam Suatu
   Kategori* (2025), master's thesis, Fakultas Sains dan Matematika,
   Universitas Diponegoro. Official record:
   `https://eprints2.undip.ac.id/id/eprint/40977/`. The full archive is
   staff-restricted; the repository makes Chapter I public at
   `https://eprints2.undip.ac.id/40977/6/12.%20BAB%20I%20-%20PENDAHULUAN.pdf`.
   Downloaded Chapter I: 163,251 bytes, SHA-256
   `611b78c88407037489f22814bf054e00ff0f283c702a06082a3a583e9ab35fcb`.
   Extracted text: 7,059 bytes, SHA-256
   `50f061191b7309c0a3a35785e06b62be1603e24a0a12c72f8ce8caf5caa3d1ee`.
   The actual PDF prose uses `teori kategori`, `fungtor`, `transformasi
   natural`, `teori grup`, `teori gelanggang`, `ruang topologi`, `obyek`,
   `morfisma`, `homomorfisma`, `monomorfisma`, `epimorfisma`, `R-Modul`,
   `produk`, `koproduk`, and `bifungtor`. One occurrence of `funtor` is an
   internal typo and was not adopted.

2. Ema Carnia, Sri Wahyuni, Irawati, Setiadji, and Zhao Dongsheng,
   *Fungtorialitas pada Aljabar Insidensi Berhingga*, BIMIPA 18(2), 129-135
   (issued 2008-05-26). Official record and file:
   `https://jurnal.ugm.ac.id/bimipa/article/view/33497` and
   `https://jurnal.ugm.ac.id/bimipa/article/download/33497/20161`.
   Downloaded PDF: 382,376 bytes, SHA-256
   `4099c3d8aff59e723470f69b4d152b037261bc26d54ef74f1365377f05c25834`.
   Extracted text: 24,169 bytes, SHA-256
   `a963cb78d61e847f670a58185ad3b1508edd3e7566b27eca927426b35d906810`.
   Its title, abstract, and body repeatedly use `fungtor`; its algebra prose
   uses `lapangan`, `ring komutatif`, `kategori`, `modul`, `morfisma`,
   `homomorfisma`, and `obyek`.

## Terminological adjudication

The 2008 Pusat Bahasa *Glosarium Matematika* by Kerami and Sitanggang was used
as an adjudication aid. Official record/file URL:
`https://repositori.kemendikdasmen.go.id/2662/1/glosarium%20matematika%20tahun%202008%20%20%20%20%20281a.pdf`.
The official host timed out during the bounded check, so a byte-identical public
comparison copy was inspected rather than claiming a fresh official-host
download. Comparison PDF: 11,427,806 bytes, SHA-256
`d1407fd49c0af0f7025f16406b9610430778a4f32f1a77bce2efa2a25f699b2a`.
Its entries include category -> `kategori`, field -> `medan; lapangan`,
functor -> `fungtor`, groupoid -> `grupoid`, module -> `modul`, morphism ->
`kemorfan; morfisme`, ring -> `gelanggang; gelang`, and topological space ->
`ruang topologis`. ITB's official 2024 MA5033 curriculum independently maps
“Topological spaces” to `Ruang topologi`:
`https://six.itb.ac.id/pub/kur2024/matakuliah/50765`.

| Concept | Observed Indonesian usage | Decision |
|---|---|---|
| functor | `fungtor` in UNDIP, UGM, and Pusat Bahasa; house had `funktor` | Change globally to `fungtor`. |
| natural transformation | UNDIP and the house glossary use `transformasi natural`; one prelude occurrence had `transformasi alami` | Change only the outlier to `transformasi natural`. |
| field | UGM uses `lapangan`; Pusat Bahasa admits both `medan` and `lapangan` | Keep house `medan`; record `lapangan` as an accepted observed synonym. |
| ring | UNDIP and Pusat Bahasa use `gelanggang`; UGM uses loanword `ring` | Keep `gelanggang`. |
| object | Sources use older `obyek` | Keep modern `objek`. |
| morphism / homomorphism | Sources use `morfisma` / `homomorfisma`; Pusat Bahasa explicitly admits `morfisme` | Keep `morfisme` / `homomorfisme` and the internally consistent `monomorfisme` / `epimorfisme`. |
| topological space | UNDIP and ITB use `ruang topologi`; Pusat Bahasa uses `ruang topologis` | Keep `ruang topologis`; record `ruang topologi` as an institutional variant. |
| groupoid | Pusat Bahasa uses `grupoid` | Keep `grupoid`. |

## Propagation and invariants

The glossary now records the evidence and variants. `repo/source/prelude.tex`
changes `funktor` to `fungtor` and the single inconsistent `transformasi alami`
to `transformasi natural`. `repo/source/chapter2.tex` changes every admitted
`funktor` occurrence to `fungtor`; the Unit 008 PDF keyword and backend labels
follow the same decision. Units 001, 008, and 009 were rebuilt twice and
reinspected on every page. Their mathematics, TeX environments, identifiers,
labels, references, citations, indexes, diagrams, source boundaries, and page
counts are unchanged. No unsupported terminology or mathematical change was
introduced.

## Provenance note

This independent Indonesian derivative preserves Wen-Wei Li's authorship and
all source/component credits. Model: OpenAI Codex gpt-5.6-sol, Ultra.
Terminology comparison, translation correction, build integration, and QA were
performed on instructions of the user. This does not imply endorsement by the source
author, UNDIP, UGM, Pusat Bahasa, ITB, or any cited contributor.

## Independent bounded recheck

Before scaling the next translation unit, the primary-source search and fallback
witnesses were checked again. Two official arXiv API queries returned HTTP 200
with zero results: `all:fungtor OR all:"teori kategori" OR all:gelanggang`, and
`all:"Bahasa Indonesia" AND cat:math*`. This corroborates the earlier decision
that no suitable same-field Indonesian arXiv source package was available within
the bounded search; it does not claim that no such source can ever exist.

Fresh downloads from the two official fallback hosts reproduced the exact PDF
hashes above. All four UNDIP pages and all seven UGM pages were extracted and
inspected. Their durable local identities, page counts, byte counts, extraction
hashes, URLs, and non-redistribution boundary are recorded in
`authority/terminology-qa-20260822/MANIFEST.json` (local authority evidence,
excluded from Git and release packages).

The recheck found no stale `funktor`, `transformasi alami`, `obyek`, `morfisma`,
or `ruang topologi` in the admitted Indonesian spans or their backend records.
The already-used form `isomorfisme natural` lacked its own controlled glossary
row, so `natural isomorphism -> isomorfisme natural` was added. No translated
prose, mathematics, identifiers, or reader bytes required correction.
