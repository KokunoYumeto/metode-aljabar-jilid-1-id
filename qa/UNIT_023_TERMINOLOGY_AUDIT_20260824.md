# Unit 023 terminology audit — 2026-08-24

Status: **PASS — the integrated Unit 023 wording is retained, seventeen exact
controlled rows are admitted, and no mathematical or prose propagation is
required.**

Model provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.

## Frozen scope

This bounded audit covers the complete Section 3.5 target at
`repo/source/chapter3.tex:722-871` and the matching authority at
`authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex:723-872`.

- authority span: 12,436 bytes, SHA-256
  `2cb843048ffcb6378c3995e5b80c341000098187638e32af6aa918b87f5e5856`;
- isolated candidate and canonical target span: 14,894 bytes, SHA-256
  `c15e079bc551b30ad7cc6daf72bee58a90108dc7fa5f101f768275e99d1dad05`;
- complete canonical `chapter3.tex`: 88,491 bytes, SHA-256
  `8ade04d16a5b71d4d1ffdf3bcee6736bb199c631a8851336d692e7ebdced5e7f`.

The audit does not reopen corpus selection, infer a national terminology
consensus, or treat generic dictionary equivalence as direct attestation of a
higher-categorical concept.

## Bounded Indonesian evidence check

Five exact official arXiv API queries were run with ten results as the hard
maximum: `all:"2-kategori"`, `all:bikategori`, `all:pseudofungtor`,
`all:"transformasi pseudonatural"`, and `all:"komposisi horizontal"`.
Each returned `opensearch:totalResults = 0`. Four bounded institutional-domain
searches for the same compounds likewise surfaced no Indonesian mathematical
paper on higher category theory. The apparent results for `2 kategori` were
ordinary counts of assessment categories and were rejected. No Indonesian
same-field arXiv source package or direct higher-category attestation was
found.

The audit therefore reuses only the applicable primary fallback evidence
already frozen and adjudicated for Unit 022:

1. Universitas Gadjah Mada's official graduate curriculum directly uses
   `Teori Kategori dan Fungtor`, `fungtor`, `transformasi natural`, and
   `ekuivalensi kategori`. It supports those base forms, not any complete
   two-dimensional compound.
2. Fitriani and Ahmad Faisol's Indonesian algebra article in the institutional
   *Limits* journal directly uses `fungtor`, `kategori pre-aditif`, and
   `kategori aditif`. It independently supports `fungtor` but does not discuss
   higher categories.
3. The retained 2008 Pusat Bahasa mathematics glossary explicitly records
   `category` -> `kategori`, `functor` -> `fungtor`, and `morphism` ->
   `morfisme` among its variants. It offers generic `interchange` -> `saling
   tukar`, but it does not attest the technical phrase `interchange law`.

These witnesses justify the lexical bases. The compounds below are controlled
mathematical compositions selected for meaning and internal consistency; they
are not represented as directly attested or uniquely standard Indonesian
usage.

## Decisions

| English concept | Controlled Indonesian form | Decision boundary |
|---|---|---|
| higher category | `kategori tingkat lebih tinggi` | Transparent introductory phrase used by the reader; no direct same-field attestation claimed. |
| 2-category | `2-kategori` | Hyphenated numerical compound, parallel to the admitted `2-sel`; title capitalization may produce `2-Kategori`. |
| strict 2-category | `2-kategori ketat` | Extends the admitted `ketat` family and correctly denotes literal associativity and identity equalities. |
| weak 2-category | `2-kategori lemah` | Broad weakened notion; it is not silently equated with the more specific `bikategori`. This term does not occur in Unit 023 prose. |
| bicategory | `bikategori` | Productive `bi-` compound for the structure named in the strictification remark. |
| 0-, 1-, 2-morphism | `0-morfisme`, `1-morfisme`, `2-morfisme` | Preserve the source's explicit dimensional levels and the controlled `morfisme` spelling. |
| 2-cell | `2-sel` | Existing admitted row retained; use for the diagrammatic cell presentation of a 2-morphism. |
| 2-functor | `2-fungtor` | Hyphenated numerical compound using the directly attested `fungtor` base. |
| pseudofunctor | `pseudofungtor` | Bound `pseudo-` plus controlled `fungtor`; keep distinct from a strict `2-fungtor`. This term does not occur in Unit 023 prose. |
| 2-natural transformation | `2-transformasi natural` | Extends the directly attested base phrase while keeping the dimensional level explicit. |
| pseudonatural transformation | `transformasi pseudonatural` | Indonesian head noun first, followed by the categorical qualifier; not a synonym for a strict 2-natural transformation. This term does not occur in Unit 023 prose. |
| modification | `modifikasi` | Use only in higher-category scope for the appropriate cell between transformations; generic Indonesian availability is not direct technical attestation. This term does not occur in Unit 023 prose. |
| vertical composition | `komposisi vertikal` | Existing admitted row retained; the source/target typing and diagram order remain correct. |
| horizontal composition | `komposisi horizontal` | Existing admitted row retained; the source/target typing and diagram order remain correct. |
| interchange law | `hukum pertukaran` | Natural theorem-name phrase for compatibility of the two compositions; all four 2-morphisms and both composition directions remain in source order. |
| vertical category | `kategori vertikal` | Correctly names the Hom-category whose objects are 1-morphisms and morphisms are vertically composed 2-morphisms. |
| horizontal identity | `identitas horizontal` | Identity 2-cell associated with an object under horizontal composition. |
| vertical identity | `identitas vertikal` | Identity 2-morphism of a 1-morphism under vertical composition. |

The candidate's `2-transformasi natural` is retained rather than changed to
`transformasi 2-natural`: the former keeps the dimensional prefix parallel to
`2-kategori` and `2-fungtor`, while `natural` remains the already controlled
technical adjective. The phrase `hukum pertukaran` is retained rather than
the dictionary-like `hukum saling tukar` because it is concise, unambiguous in
the defining sentence, and labels an equation rather than the general act of
interchanging two things.

## Glossary and propagation result

Seventeen records were added: `higher category`, `2-category`, `strict
2-category`, `weak 2-category`, `bicategory`, `0-morphism`, `1-morphism`,
`2-morphism`, `2-functor`, `pseudofunctor`, `2-natural transformation`,
`pseudonatural transformation`, `modification`, `interchange law`, `vertical
category`, `horizontal identity`, and `vertical identity`.

The existing `2-cell`, `vertical composition`, and `horizontal composition`
rows were retained unchanged. The resulting
`00_control/TERMINOLOGY.id-ID.csv` contains 304 data rows, 45,230 bytes, with
SHA-256
`9e2d946520a1c9f8984abd1b78935c2fe052e5bfdf79e9c9091d41a29b7cd68a`.
Strict UTF-8 CSV parsing passed with exactly five columns and no duplicate
`source_term`.

No reader text required a change. The isolated candidate and canonical span
remain byte-identical to their frozen identities. `O013-LI-U023-ED-001`
remains the already documented index-only localization
`\index{bansuidui}` -> `\index{bansuidui@pasangan adjoin}`; it is not a
mathematical source correction, so no separate correction record is created.

## Fail-closed verification

Both commands passed after the glossary update:

```text
python -B scripts/check_unit_023_candidate.py
python -B scripts/check_unit_023_structure.py
```

The candidate gate reconfirmed 25 environment pairs, 2 labels, 16 references,
19 items, 156 inline-math occurrences, 11 bracket displays, 14 `tikzcd`
diagrams with 64 arrows, balanced braces, and zero Han characters. The
canonical gate reconfirmed exact candidate identity at target lines 722-871,
the unchanged admitted prefix, and byte-identical authority continuation from
the Chapter 3 exercise boundary onward.
