# Unit 029 terminology audit — 2026-08-25

Status: **PASS; the exact five-row Unit 029 delta is the controlled glossary
tail.** This audit covers the Sylow-section terminology gate only; reader,
backend, Git, and publication remain separate downstream work.

## Bound identities

- Candidate: `build/unit-029-candidate/chapter4-sylow-theorems-id.tex`,
  10,028 bytes, SHA-256
  `234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d`.
- Pre-Unit-029 glossary: 408 data rows / 64,585 bytes / SHA-256
  `fdd00a574f7f93837688e2d9bc9707677c889eab1174b8f0121a119498557fe7`.
- Delta: `build/unit-029-staging/terminology-delta.csv`, five data rows /
  1,030 bytes / SHA-256
  `e0e00678dc46fd8c702c17614ea2d1e1e71ee6ff622f8986097dfd296e759ecc`.
- Resulting glossary: `00_control/TERMINOLOGY.id-ID.csv`, 413 data rows /
  65,573 bytes / SHA-256
  `adc2152dc08131e0098ac159137378aa50cd7b54cb282a8e713899662d335ca3`.

The complete glossary parses under
`source_term,target_term,status,scope,note`; all 413 source terms are unique.
Its last five records equal the delta record-for-record, all five have status
`admitted`, and none collides with the 408-row prefix.

## Admitted vocabulary

1. `p-group` → `p-grup`
2. `p-subgroup` → `p-subgrup`
3. `Sylow p-subgroup` → `subgrup Sylow p`
4. `binomial coefficient` → `koefisien binomial`
5. `coprime` → `saling koprima`

The TeX surfaces bind the prime mathematically (`$p$-grup`, `$p$-subgrup`,
and `subgrup Sylow $p$`). `P-subgrup` remains broader than a Sylow subgroup;
the latter is reserved for a subgroup whose order realizes the full
`p`-part of the ambient finite-group order. `Saling koprima` records the
pairwise relation used in the final direct-product proof. The candidate also
reuses admitted Chapter 4 vocabulary such as `aksi grup`, `stabilisator`,
`produk langsung`, `grup hasil bagi`, and `saling konjugat` without creating
duplicate rows.

No mathematical source correction is introduced by this terminology gate.
Production provenance for this decision: OpenAI Codex gpt-5.6-sol, Ultra,
acting on the user's instruction; source authorship and credits are unchanged.
