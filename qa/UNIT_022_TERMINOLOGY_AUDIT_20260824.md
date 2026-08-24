# Unit 022 terminology audit — 2026-08-24

Status: **PASS; retain the reviewed Unit 022 wording and admit eight exact
controlled terms.** No canonical chapter, reader, backend, release, Git, or
publication state was changed.

Model provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.

## Frozen inputs

- Reviewed candidate:
  `build/unit-022-candidate/chapter3-enriched-categories-id.tex`, 17,541
  bytes, SHA-256
  `e1fa8da94c0c2431660f690aa9b2193e3c966e2d71b9d5a029da12a76bc0e255`.
- Frozen authority span: `chapter3.tex` lines 513–722, 15,089 bytes,
  SHA-256
  `85332852a2b9808a5a9e7ec240adffdd5b286d44d724be38833aed53e65bd53d`.
- Controlled glossary before this audit: 39,866 bytes, SHA-256
  `45e7b1500533e4fa8a8a257efe2982261704bd00a27f056030112141e5ed0efe`.

## arXiv source-package gate

The official arXiv Atom API was queried for the same-field Indonesian terms
[`kategori diperkaya`](https://export.arxiv.org/api/query?search_query=all%3A%22kategori%20diperkaya%22&start=0&max_results=20),
[`kategori aditif`](https://export.arxiv.org/api/query?search_query=all%3A%22kategori%20aditif%22&start=0&max_results=20),
[`funktor`](https://export.arxiv.org/api/query?search_query=all%3Afunktor&start=0&max_results=20),
[`morfisme`](https://export.arxiv.org/api/query?search_query=all%3Amorfisme&start=0&max_results=20),
and
[`aljabar homologis`](https://export.arxiv.org/api/query?search_query=all%3A%22aljabar%20homologis%22&start=0&max_results=20).
Each query returned zero entries. A deliberately broader
[`all:kategori`](https://export.arxiv.org/api/query?search_query=all%3Akategori&start=0&max_results=20)
query returned only [arXiv:1606.07604](https://arxiv.org/abs/1606.07604), an
Indonesian computer-science thesis on Web-document classification in `cs.IR`,
not algebra or category theory. It is therefore not a terminology witness and
its source package was not used. No suitable Indonesian same-field arXiv TeX
source was found in this bounded gate.

## Primary Indonesian fallback witnesses

1. Universitas Gadjah Mada, *Dokumen Kurikulum 2022 Program Magister FMIPA*,
   [official PDF](https://mkom.ugm.ac.id/wp-content/uploads/sites/690/2026/01/Dokumen-Kurikulum-Progam-Magister-FMIPA-UGM-tahun-2022.pdf),
   510 physical pages, 4,213,305 bytes, SHA-256
   `aab71b299cf141c63069f3b2a061d23be1d6b06abac7c9dd912c321cbe362bc7`.
   Physical page 122 directly uses `Teori Kategori dan Fungtor`, `fungtor`,
   `transformasi natural`, `ekuivalensi kategori`, `produk`, and `koproduk`.
2. Fitriani and Ahmad Faisol, *Kategori Modul yang Dibangun oleh U_V*,
   *Limits* 17(1), 2020,
   [official record](https://iptek.its.ac.id/index.php/limits/article/view/6030),
   [official PDF](https://iptek.its.ac.id/index.php/limits/article/download/6030/4666),
   DOI `10.12962/limits.v17i1.6030`, 8 physical pages, 191,003 bytes,
   SHA-256
   `18ee89fd891cc6bc9e2ef58ffc0d62ffe4554146efd92b6c7e6d27f488a3361f`.
   The PDF directly uses `fungtor`, `kategori pre-aditif`, `kategori aditif`,
   ordinary Hom-sets, and the Cartesian product sign between two Hom-sets.
3. Ikrom Al Furqon, *Kategori U-Kompleks Lemah: Kajian Rantai U-Kompleks
   Lemah dan Kategori Aditif*, 2023,
   [official institutional record](https://repository.uinjkt.ac.id/dspace/handle/123456789/72417),
   [public PDF](https://repository.uinjkt.ac.id/dspace/bitstream/123456789/72417/1/IKROM%20AL%20FURQON-FST.pdf),
   43 physical pages, 867,339 bytes, SHA-256
   `056a4f62b929f3307b0e9abf2e14fdbaca99caab9c512e4425f3e37eb1919b86`.
   It independently and repeatedly uses `kategori aditif`, `morfisma`, and
   `koproduk`.

This is a terminology sample, not a claim that Indonesian field usage is
uniform. None of these witnesses discusses enriched categories, Hom-objects,
or biproducts by those complete names. Direct attestation is distinguished
below from a controlled compositional choice.

## Decisions

| Concept | Unit 022 form | Evidence and decision |
|---|---|---|
| enriched category | `kategori diperkaya` | Retain. Already admitted in the lane; no complete direct phrase was found in the bounded witnesses. |
| enriched functor | `fungtor` between categories enriched over `V`; index case `diperkaya` | Retain and control as `fungtor diperkaya`. `Fungtor` is directly attested by UGM and *Limits*; the complete compound is compositional, not directly attested. |
| enriched natural transformation | `transformasi natural` in the enriched setting | Retain and control as `transformasi natural diperkaya`. UGM directly attests the base phrase; `diperkaya` marks the specialized setting. |
| enriched category equivalence | `ekuivalensi kategori` for categories enriched over `V` | Retain and control as `ekuivalensi kategori diperkaya`. UGM directly attests the base phrase; the complete compound is not directly attested. |
| Hom-object | `objek-$\Hom$` | Retain and normalize in the glossary as `objek-Hom`. It correctly distinguishes an internal Hom-object from the ordinary `himpunan Hom`; no direct complete-phrase attestation is claimed. |
| topological category | `kategori topologis` | Retain. This is a category enriched over `CGHaus`, not merely a category of topological objects. `Topologis` follows the admitted `ruang topologis` family; the complete phrase was not directly attested. |
| Ab-enriched category | `kategori-$\cate{Ab}$` | Retain and normalize as `kategori-Ab`. It preserves the source notation and is explained in prose as enrichment in abelian groups. |
| preadditive category | `kategori praaditif` | Retain. *Limits* directly attests the alternative `kategori pre-aditif`; the edition uses the productive Indonesian bound form `pra-`, consistently with its admitted `praterurut`, while recording the field variant rather than claiming uniform usage. |
| additive category | `kategori aditif` | Retain. Directly attested by both Indonesian algebra witnesses and already admitted. |
| biproduct | `biproduk` | Retain. The witnesses attest `produk`, `koproduk`, and the shared `oplus` construction but not the complete word `biproduk`; the edition's already admitted form remains mathematically unambiguous. |
| additive functor | `fungtor aditif` | Retain and add explicitly. The two components are directly attested, while the complete compound is a controlled compositional choice. |

The source correction from a tensor symbol to a Cartesian product between two
ordinary Hom-sets is also terminologically and typologically consonant with
the *Limits* witness, but that witness is corroboration only; the correction
remains justified by the internal mathematical typing recorded in the Unit 022
source-correction receipt.

## Glossary result

Eight exact records were added: `enriched functor`, `enriched natural
transformation`, `enriched category equivalence`, `Hom-object`, `topological
category`, `Ab-enriched category`, `preadditive category`, and `additive
functor`. The existing `enriched category`, `additive category`, and
`biproduct` records were retained unchanged.

The resulting `00_control/TERMINOLOGY.id-ID.csv` has 287 data rows, 41,824
bytes, SHA-256
`bbe7c8906aa94a96766bb1aacbf1425527593d514fbe83649eea96095ff0d882`.
Strict UTF-8 CSV parsing passed with the expected five columns and no duplicate
`source_term`. The reviewed candidate remained byte-identical to its frozen
identity above.
