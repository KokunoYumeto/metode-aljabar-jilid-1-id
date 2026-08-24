# Unit 021 terminology audit — 2026-08-24

Status: **PASS — nine bounded rows admitted; direct evidence and transparent
corpus choices remain explicitly distinguished.**

## Scope and method

This audit covers only specialized terminology used in complete Section 3.3,
canonical target `repo/source/chapter3.tex:306-511`. It reuses the frozen lane
glossary and performs one bounded Indonesian field check for the newly central
braid/Yang--Baxter vocabulary. It does not reopen corpus selection or claim
that a single witness fixes all Indonesian category-theory terminology.

Four exact institutional-domain queries were bounded to Indonesian academic
PDFs: combinations of `kategori monoidal` with `kepang`, the variants
`terkepang`, `berkepang`, and `teranyam`, `grup kepang`/Artin, and `persamaan
Yang-Baxter`. No Indonesian academic source directly discussing braided
monoidal categories surfaced. One directly relevant Indonesian mathematics
journal article did surface and was inspected completely.

## Retained field witness

Puguh Wahyu Prasetyo and Catur Yustika Melati, “Konstruksi Brace Dua Sisi
Dengan Menggunakan Ring Jacobson,” *Limits: Journal of Mathematics and Its
Applications* 17(2), 2020, DOI `10.12962/limits.v17i2.6650`, is hosted by
Institut Teknologi Sepuluh Nopember at
`https://iptek.its.ac.id/index.php/limits/article/view/6650`.

The complete fifteen-page PDF is retained at
`authority/terminology-qa-unit021-20260824/prasetyo-melati-2020-konstruksi-brace-dua-sisi.pdf`,
450,506 bytes, SHA-256
`25d998baa08dcaefa62aa9a06d91f0cf3fa45f5dd0f617d1d9a3b2114cf5cac4`.
Its extracted text is 39,469 bytes, SHA-256
`f9ab5aa509fc4236dc0399f03341a0e2e53ae73ee11ae780f79f175276b4e6cf`.
The exact retrieval and scope boundary are in
`authority/terminology-qa-unit021-20260824/MANIFEST.json`.

The article repeatedly uses **persamaan Yang-Baxter**, directly supporting the
edition's `persamaan Yang--Baxter`. It also repeatedly uses the English loan
phrase **grup Braid**, not `grup kepang`. That disagreement is preserved as
evidence: this edition retains transparent Indonesian `kepang`, consistent
with its already admitted `kategori kepang`, while its index entries retain
the English labels `braid`, `braid group`, and `braiding` for discoverability.
The witness is not misrepresented as direct support for `kepang`.

## Admitted Unit 021 delta

Exactly nine rows are admitted:

| Source term | Indonesian target | Evidence/decision boundary |
|---|---|---|
| braiding (monoidal category) | struktur kepang | Transparent `struktur` + `kepang`; English `braiding` retained in the index. No direct same-field attestation claimed. |
| braided monoidal category | kategori monoidal berkepang | Expresses a monoidal category equipped with a braiding; kept distinct from concrete `kategori kepang`. No direct same-field attestation claimed. |
| braided monoidal functor | fungtor monoidal berkepang | Extends the admitted `fungtor monoidal` family for preservation of the braiding square. |
| symmetric monoidal category | kategori monoidal simetris | Transparent mathematical adjective for the double-braiding identity; no direct same-field Indonesian attestation claimed. |
| hexagon axiom (monoidal category) | aksioma segienam | Transparent polygon name; English technical label remains in the index. No direct same-field attestation claimed. |
| Yang-Baxter equation | persamaan Yang--Baxter | Directly attested by the retained Indonesian journal article. |
| braid | kepang | Transparent Indonesian noun; `braid` remains in index metadata because the witness uses the loan form. |
| braid group | grup kepang | Corpus-consistent transparent form; `braid group` remains in the index and `grup Braid` is recorded as an attested alternative. |
| Artin braid group | grup kepang Artin | Composition of the controlled group term with the proper name; no direct full-phrase attestation claimed. |

Already admitted terms reused without duplication include `kategori monoidal`,
`kategori monoidal ketat`, `kategori kepang`, `fungtor monoidal`, `kendala
komutativitas`, `kendala asosiativitas`, `objek satuan`, `naturalitas`,
`hasil kali tensor`, and `grup simetris`. `untai` is ordinary contextual prose
and is not promoted as a separate technical concept row.

## Result

The terminology choices preserve mathematical distinctions and expose the
English lookup forms where Indonesian usage is non-uniform. No earlier reader
requires a propagated correction. The controlled glossary has no Unit 021
candidate row: all nine decisions are admitted with their evidence limits.

Production provenance: `OpenAI Codex gpt-5.6-sol, Ultra`.
