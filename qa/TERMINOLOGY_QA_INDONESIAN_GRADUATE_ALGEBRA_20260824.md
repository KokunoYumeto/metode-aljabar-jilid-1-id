# Bounded Indonesian graduate-algebra terminology QA — 2026-08-24

Status: **PASS with a five-row glossary addition and one backend-only wording refinement.** No admitted reader prose or Unit 019 candidate prose required replacement.

## Search boundary and fallback

A finite official arXiv search for Indonesian-language graduate-algebra usage used the terms `gelanggang`, `morfisme`, `homomorfisme`, `grup abelian`, `kategori monoidal`, `hasil kali tensor`, and `modul bebas`. It found no suitable Indonesian same-field record with downloadable TeX. Unrelated Bahasa Indonesia NLP/computing papers were excluded rather than treated as mathematical-language evidence.

The selected fallback is Nikken Prima Puspita, “Pengaruh Kenon-Unitalan Modul Terhadap Hasil Kali Tensor,” *Seminar Nasional Matematika dan Pendidikan Matematika* (2010), from the [institutional UNY record](https://eprints.uny.ac.id/10473/) and its [direct PDF](https://eprints.uny.ac.id/10473/1/A6-Niken%20Prima.pdf). The seven-page A4 PDF was inspected in full, both as rendered pages and extracted text:

- local PDF: `authority/terminology-qa-20260824/A6-Niken-Prima.pdf`;
- 450,227 bytes; SHA-256 `767e89f16a31f952ad4a5c3df74f7422f49abf5a4a4af1e1d1506654b0ad02f6`;
- local layout-preserving text: `authority/terminology-qa-20260824/A6-Niken-Prima.txt`;
- 22,175 bytes; SHA-256 `4b230c6b5f268216231d474a3db69fed2551726760a5f7c1551ab3f4d120d609`;
- evidence manifest: `authority/terminology-qa-20260824/MANIFEST.json`.

The source remains credited to its author and venue. It is retained locally only as terminology evidence; no redistribution or derivative-license grant is inferred.

## Observed usage and decisions

| Concept | Observed Indonesian usage | Decision for this edition |
|---|---|---|
| module | `modul`, `modul unital`, `modul non-unital` (pp. 1, 3–7) | Retain `modul`; admit `modul unital` and `modul non-unital`. |
| tensor product | `hasil kali tensor` (pp. 1–3, 7) | Exact match; retain. |
| ring | `ring`, `ring dengan elemen satuan`, `subring` (pp. 1, 3) | Retain controlled `gelanggang`; record the loanword only as an attested variant. |
| unital ring | `ring dengan elemen satuan` (p. 1) | Retain `gelanggang dengan unsur satuan`; `unsur` versus `elemen` is harmless controlled variation. |
| nonunital ring | prose stating that a ring need not have an identity (p. 3) | Refine to `gelanggang yang tidak disyaratkan memiliki unsur satuan`; this avoids falsely asserting that an identity is absent. |
| homomorphism/isomorphism/epimorphism | `homomorfisma`, `isomorfisma`, `epimorfisma` (pp. 1–2, 4, 6–7) | Retain the internally consistent `-isme` family; record `-isma` only as an observed variant. |
| abelian group | `grup Abel` (p. 1) | Retain corpus-wide `grup abelian`. |
| exact sequence | `barisan eksak kanan`, `eksak kanan`, `keeksakan kanan` (pp. 2–3) | Admit `barisan eksak`, `barisan eksak kanan`, and `keeksakan kanan`. |

The source does not contain generic `morfisme`, ideals, or monoidal-category terminology, so it does not adjudicate `kategori monoidal`, `objek satuan`, `kendala satuan`, or the lax-monoidal qualifiers.

## Propagation check

A bounded search of translated Chapters 1–2 and the isolated Unit 019 candidate found zero prose occurrences of `morfisma`, `homomorfisma`, `isomorfisma`, `epimorfisma`, `cincin`, `produk tensor`, or `grup Abel`. Unit 019 already consistently uses `hasil kali tensor`, `gelanggang komutatif`, `modul`, and `grup abelian`. Therefore no reader text or candidate text changed.

The controlled glossary gains `unital module`, `nonunital module`, `exact sequence`, `right exact sequence`, and `right exactness`. Its prior nonunital-ring label is refined only in the Unit 018 machine backend and deterministic CSV projection; the published four-page reader contains no occurrence of that label. The Unit 018 backend generator and validators must reproduce and admit the updated backend before the next public commit.

Production provenance: `OpenAI Codex gpt-5.6-sol, Ultra`. This provenance is separate from Wen-Wei Li’s authorship and from every human source credit.
