# O013 Unit 026 terminology recommendation — 2026-08-25

## Decision

**PASS WITH DETERMINISTIC TERMINOLOGY REFINEMENTS.** Stage the 33 non-duplicative rows in `build/unit-026-staging/terminology-delta.csv`, then apply the 12 candidate-occurrence refinements listed below when Unit 026 is next edited. This is not a human-review hold. The controlled glossary and candidate were intentionally not changed by this gate.

## Bounded authority and integrity

Only the requested inputs were inspected. No network, Git, PDF, repository-wide search, or publication operation was used.

| Input | Bounded portion | Bytes | SHA-256 |
|---|---:|---:|---|
| `repo/source/chapter4.tex` | lines 177–364 (Unit 026 begins at line 179) | 159681 | `b1b055416d392a66708047afb20a14175566c7839286979baac6289d3d125419` |
| `build/unit-026-candidate/chapter4-homomorphisms-quotients-id.tex` | inspected candidate snapshot, 187 lines | 19299 | `cd62bf509f32ea141e20301187f5460a88c9b4e65615e4050df374a23c2e73e9` |
| `00_control/TERMINOLOGY.id-ID.csv` | complete controlled baseline, 341 data rows | 51472 | `3ed2a7a30aa06e9e574e36b237bf13ab6cec6779703ce91bc3238a107fe526b1` |
| `authority/terminology-qa-20260822/pusat-bahasa-glosarium-matematika-2008.txt` | exact retained text authority | 596063 | `2cfb7dd5aca6489cac6ecd8b08426a022c9938611d79d129ed212d1a38445de4` |
| `authority/terminology-qa-20260822/MANIFEST.json` | complete manifest | 10890 | `b7693af6ac42028a8de495ee044c26cc1106837487f371b7402f7fb88134007a` |

The retained text has exactly the byte count and SHA-256 recorded by the manifest. The manifest identifies it as the local text extraction of *Glosarium Matematika* (Pusat Bahasa, 2008), while explicitly declining a byte-identity claim against the official-host response because that host timed out. This recommendation therefore claims evidence only from the retained bytes, not from an unverified official download.

Concurrency note: this gate did not edit the candidate, but final verification after drafting found that its live path had changed to SHA-256 `1c3f92e8a5ab9389d558cff60cb06b6b48df9da06600970293c145c9e1a7e432`. The terminology findings and candidate line references therefore identify the inspected `cd62...73e9` snapshot above; the live change was made outside this bounded terminology task.

The staged delta has 33 data rows, no duplicate `source_term`, and no `source_term` collision with the 341-row controlled baseline. Its current identity is 7178 bytes, SHA-256 `432346e919a0836cf21fbf54640a8435b1100a352aa90f9f629106c300812eea`.

## Unit 026 terms already controlled

The following reader-facing Unit 026 terms already have exact baseline rows and need no duplicate delta row. Numbers are physical CSV lines, with the header on line 1.

- Core language: line 2 `algebra -> aljabar`; 3 `set -> himpunan`; 4 `group -> grup`; 8 `category -> kategori`; 9 `morphism -> morfisme`; 119 `object -> objek`; 121 `functor -> fungtor`.
- Morphisms: line 10 `homomorphism -> homomorfisme`; 11 `isomorphism -> isomorfisme`; 12 `endomorphism -> endomorfisme`; 13 `automorphism -> automorfisme`; 34 `invertible -> invertibel`; 116 `bijection -> bijeksi`.
- Structural language: line 14 `commutative diagram -> diagram komutatif`; 125 `structure-preserving map -> peta pelestari struktur`; 130 `universal property -> sifat universal`.
- Sets and quotients: line 58 `quotient set -> himpunan hasil bagi`; 59 `equivalence relation -> relasi ekuivalensi`; 60 `equivalence class -> kelas ekuivalensi`; line 32 `congruence class -> kelas kongruensi` already controls the preferred `kongruensi` component.
- Basic algebra/group theory: line 313 `binary operation -> operasi biner`; 314 `semigroup -> semigrup`; 315 `monoid -> monoid`; 317 `identity element -> unsur identitas`; 320 `unit group -> grup unit`; 321 `subgroup -> subgrup`; 322 `normal subgroup -> subgrup normal`; 326 `cyclic group -> grup siklik`; 328 `element order -> orde unsur`; 329 `coset -> koset`; 333 `center (group theory) -> pusat`; 335 `normalizer -> normalisator`.
- Categorical/set-theoretic tail: line 64 `Grothendieck universe -> semesta Grothendieck`; 105 `universe -> semesta`; 106 `U-set -> himpunan-U`; 138 `adjoint functor -> fungtor adjoin`; 139 `adjunction -> pasangan adjoin`; 140 `adjunction pair -> pasangan adjoin`; 151 `abelian group -> grup abelian`; 162 `forgetful functor -> fungtor pelupa`; 242 `full subcategory -> subkategori penuh`.

Three of these controlled terms are present in non-controlled wording in the candidate and therefore appear in the refinement table: `structure-preserving map`, `identity element`, and `unit group`. `commutative diagram` also merits a small normalization.

## Exact staged rows and evidence class

Evidence codes:

- **D** — the proposed target itself is directly present in the retained official text, either as the standalone entry or in an exact relevant phrase.
- **DN** — the concept is directly present, but the proposed target applies a bounded normalization already compelled by controlled house usage (modern `-isme`, corrected OCR, or removal of glossary hyphenation).
- **C** — the full target is a transparent composition of controlled or directly attested components; no exact full-target attestation is claimed.

All rows have status `admitted`; the CSV carries the exact scope and evidence note.

| # | Source term | Proposed target | Evidence | Candidate locus |
|---:|---|---|:---:|---|
| 1 | semigroup homomorphism | homomorfisme semigrup | C | 2 |
| 2 | identity map | peta identitas | C | 10 |
| 3 | trivial homomorphism | homomorfisme trivial | C | 10 |
| 4 | inverse | invers | C | 12, 17, 55, 90 |
| 5 | isomorphic | isomorfik | D | 12, 142 |
| 6 | automorphism group | grup automorfisme | C | 20 |
| 7 | group homomorphism | homomorfisme grup | DN | 23, 25, 36, 43, 95, 100 |
| 8 | group isomorphism | isomorfisme grup | C | 23, 144 |
| 9 | group automorphism | automorfisme grup | C | 23, 31 |
| 10 | inner automorphism | automorfisme dalam | DN | 31 |
| 11 | adjoint isomorphism | isomorfisme adjoin | C | 31 |
| 12 | image of a homomorphism | bayangan homomorfisme | C | 43, 46, 136 |
| 13 | kernel | kernel | D | 43, 46, 97, 100, 136, 142 |
| 14 | quotient map | peta hasil bagi | DN | 48 |
| 15 | well-defined | terdefinisi dengan baik | C | 50, 168 |
| 16 | quotient structure | struktur hasil bagi | C | 55 |
| 17 | quotient monoid | monoid hasil bagi | C | 55 |
| 18 | induced homomorphism | homomorfisme terimbas | C | 64, 70, 124 |
| 19 | surjective | surjektif | DN | 70, 97, 107, 142 |
| 20 | quotient group | grup hasil bagi | DN | 1, 87, 90, 140 |
| 21 | quotient homomorphism | homomorfisme hasil bagi | C | 95, 97, 116, 136 |
| 22 | coset space | ruang koset | C | 88 |
| 23 | surjectivity | surjektivitas | C | 118 |
| 24 | inclusion relation | relasi pencakupan | D | 118 |
| 25 | generator | pembangkit | D | 140 |
| 26 | cyclic subgroup | subgrup siklik | D | 153 |
| 27 | congruence | kongruensi | C | 146 |
| 28 | commutative monoid | monoid komutatif | C | 156, 158, 182 |
| 29 | monoid homomorphism | homomorfisme monoid | C | 160, 182 |
| 30 | Grothendieck group | grup Grothendieck | D | 157, 165, 170 |
| 31 | cancellation law | hukum pembatalan | D | 168 |
| 32 | additive inverse | invers aditif | C | 168 |
| 33 | U-category | kategori-U | C | 179 |

### Direct-text anchors

- `isomorphic ... -> ... isomorfik`: official-text lines 5293–5295.
- `kernel -> kernel` and `kernel of a homomorphism`: lines 5411–5412.
- `inclusion relation -> relasi pencakupan`: line 4848.
- `generator -> pembangkit` and `generator of a group -> pembangkit grup`: lines 4303–4305.
- `cyclic subgroup -> subgrup siklik`: line 2669.
- `Grothendieck group -> grup Grothendieck`: line 4437.
- `cancellation law -> hukum pembatalan`: line 1410.
- Direct concepts requiring normalization: group homomorphism at 4660–4661 (`kehomomorfan` family), inner automorphism at 5009 (`keautomorfan dalam`), surjective at 9523 (OCR `suijektif`), quotient group at 8051 (OCR `basil-bagi`), and quotient map at 8052 (`peta hasil-bagi`). The exact generic `quotient -> hasil-bagi` entry at line 8049 resolves the quotient OCR.

### Honest compositional boundaries

- `induced homomorphism -> homomorfisme terimbas` is not present as a whole phrase; it composes official `induced morphism -> morfisme terimbas` (line 4919) with admitted `homomorphism -> homomorfisme`.
- `image of a homomorphism -> bayangan homomorfisme` is not directly attested. The official text instead gives `image of a function -> peta fungsi` (line 4789), which is unsuitable here because `peta` is already the controlled noun for a map. The proposed `bayangan` is an explicit contextual choice, not a fabricated direct citation.
- `additive inverse` is directly represented in the official text as `balikan aditif` (line 296), but the staged target `invers aditif` preserves the corpus-wide `invers` family (`inverse limit`, `quasi-inverse`). Thus its exact target is classified C rather than D.
- Bare `congruence` is staged as `kongruensi` because the baseline already admits `kelas kongruensi`; the official glossary's predominant older form `kekongruenan` remains an observed variant.
- No exact retained-text hit was found for `well-defined`, `surjectivity`, or `U-category`; their targets are transparent, bounded compositions.

## Candidate terminology refinements

These are recommendations only. This gate did not mutate the candidate; see the concurrency note for the later live-path hash change.

| Candidate line(s) | Current text | Recommended text | Controlling reason |
|---:|---|---|---|
| 2 | `peta yang melestarikan struktur` | `peta pelestari struktur` | Exact controlled row at CSV line 125. |
| 2 | `unsur satuan` | `unsur identitas` | Exact controlled row at CSV line 317. |
| 19 | `grup unsur invertibel` | `grup unit` | Exact controlled row at CSV line 320. |
| 20 | `grup unsur invertibel dari monoid tersebut` | `grup unit monoid tersebut` | Exact controlled row at CSV line 320. |
| 55 | `unsur satuan $S/\sim$` | `unsur identitas $S/\sim$` | Exact controlled row at CSV line 317. |
| 64 | `Homomorfisme ... ini disebut homomorfisme yang diinduksi` | `Homomorfisme ... ini disebut homomorfisme terimbas` | Staged row composes official `morfisme terimbas` with controlled `homomorfisme`; also removes internal variation. |
| 64 | `Diagram yang komutatif berarti` | `Diagram komutatif berarti` | Exact controlled row at CSV line 14. |
| 70 | `homomorfisme terinduksi` | `homomorfisme terimbas` | Same induced-homomorphism normalization. |
| 90 | `unsur satuannya` | `unsur identitasnya` | Exact controlled row at CSV line 317. |
| 118 | `relasi inklusi` | `relasi pencakupan` | Exact official `inclusion relation` target at retained-text line 4848. |
| 124 | `homomorfisme terinduksi` | `homomorfisme terimbas` | Same induced-homomorphism normalization. |
| 140 | `generatornya` | `pembangkitnya` | Exact official `generator -> pembangkit` target at retained-text line 4303. |

The following candidate choices should be retained:

- `bayangan` for `\Image(\varphi)`: clear in this algebraic context and avoids collision with `peta` meaning map; record the lack of exact full-phrase attestation.
- `isomorfisme adjoin`: a transparent rendering of the source's alternate name for `\Ad_x`; do not reinterpret it as an adjunction.
- `invers` and `invers aditif`: consistent with existing controlled inverse terminology; record official `balikan` as an observed synonym.
- `kongruensi`: consistent with controlled `kelas kongruensi`; record official `kekongruenan` as an older variant.

## Deterministic gate summary

- Controlled baseline coverage: the exact rows enumerated above, with four candidate-normalization points (`structure-preserving map`, `identity element`, `unit group`, `commutative diagram`).
- Staged additions: 33 rows — 7 D, 5 DN, 21 C.
- Candidate refinements: 12 exact occurrences on 10 distinct candidate lines.
- CSV validation: parse succeeded; 33 rows; zero duplicate staged source terms; zero baseline source-term collisions.
- Write boundary honored: only `build/unit-026-staging/terminology-delta.csv` and this recommendation were created. No controlled, candidate, canonical, README, backend, control, Git, or publication mutation was performed.
