# Unit 034 terminology audit — 2026-08-27

Status: **PASS; the final candidate, candidate-identical canonical splice, and
513-row live glossary are terminology-normalized and mutually consistent.**
This is a pre-admission evidence record; it does not claim backend, control,
Git, publication, or public-byte-readback completion.

## Bound evidence

The final live glossary `00_control/TERMINOLOGY.id-ID.csv` contains exactly 513
data rows with 513 unique source terms, 82,586 bytes, SHA-256
`59e66d5acf8f8e792327730c01a236d3bc7570b9f71a200b9a6d7b9a71fa3955`.
The admitted Unit 034 staging delta
`build/unit-034-staging/terminology-delta.csv` contains 37 unique data rows,
all with status `admitted`, 6,613 bytes, SHA-256
`077b2903a33cdcf2df893a9ef57926b3c5d5157fc4be670f5aad10bdfdccf659`.
Every staging row is exactly present in the live glossary.

The retained proposal
`qa/UNIT_034_TERMINOLOGY_DELTA_20260827.csv` also contains 37 unique data rows,
6,613 bytes, SHA-256
`ff783455f6434861f9780f7d78b504e1ccd4a97a890044b59fb1027f0442abdc`.
Exactly two proposal terms intentionally matched pre-existing source terms,
`completion` and `completeness`; they were replacement instructions, not rows
to append. The other 35 terms were new. Promotion applied that distinction and
did not create either duplicate.

The retained 2008 Pusat Bahasa *Glosarium Matematika* comparison PDF remains
11,427,806 bytes, SHA-256
`d1407fd49c0af0f7025f16406b9610430778a4f32f1a77bce2efa2a25f699b2a`.
Its 596,063-byte extracted text has SHA-256
`2cfb7dd5aca6489cac6ecd8b08426a022c9938611d79d129ed212d1a38445de4`.
Relevant entries directly support `grup topologis`, `barisan Cauchy`,
`kompak`, `ruang Hausdorff kompak`, `pelengkapan`, `filter`/`tapis`,
`jaring` as an alternative for `net`, `invarian topologis`, and the
`lingkungan` word family.

A bounded primary-source recheck was sufficient and was not expanded into a
new inventory loop:

- the official UGM dissertation record at
  `https://etd.repository.ugm.ac.id/penelitian/detail/89480` directly uses
  `grup topologis`, `ruang vektor topologis`, and `pemetaan kontinu`;
- UGM's mathematics teaching page at
  `https://analisisreal.mipa.ugm.ac.id/topologi/ruang-metrik-2/` directly uses
  `barisan Cauchy`, `kelengkapan`, and `lengkap`;
- the official UNY mathematics-thesis record at
  `https://eprints.uny.ac.id/2431/` directly uses `pelengkapan` for the
  construction from Cauchy-sequence classes and records density and
  completeness as its defining properties;
- UGM's mathematics teaching page at
  `https://analisisreal.mipa.ugm.ac.id/topologi/definisi-himpunan-kompak/`
  directly uses `liput terbuka` and `kompak`; and
- the official UGM thesis record at
  `https://etd.repository.ugm.ac.id/penelitian/detail/227947` uses the term
  `net` in Indonesian topological prose.

The retained UNDIP/UGM category-and-algebra witnesses continue to support the
general register (`kategori`, `fungtor`, `homomorfisme`, and related forms),
but are not represented as direct attestations for every specialized
topological or arithmetic-geometric term.

## Adjudications and candidate normalization

The prior live row `completion -> kompletisasi` was explicitly provisional and
restricted to Chapter 10. Both the official glossary and the Indonesian UNY
mathematics source favor `pelengkapan`; the already admitted row `metric
completion -> pelengkapan metrik` points in the same direction. Unit 034 now
uses `pelengkapan` consistently at all eleven surfaces, including the section
title and index. This avoids fossilizing a provisional loanword and keeps the
noun aligned with `lengkap` and `kelengkapan`.

The topology wording was tightened at three related surfaces. The closure
denoted by `\bar U` is now the set `penutup`, which is distinct from
`ketertutupan` as a property. The coset decomposition provides a `liput
terbuka`, not a literal `penutup terbuka`. The two profinite-characterization
sentences now state plainly that the group is `kompak dan Hausdorff` rather
than stacking the modifiers as `grup Hausdorff kompak`. A missing locative in
`setiap titik di G` was also restored.

The object constructed as
`\varprojlim_i \Z/p^{i+1}\Z = \Z_p` is named `bilangan bulat p-adik` at both
target surfaces. This is a terminology precision, not a second formula repair:
`\Z_p` denotes the p-adic integers, whereas the p-adic number field is
`\Q_p`. Every formula and the separately declared family-index correction
remain unchanged.

`Topologi produk` is retained instead of the older glossary variant `topologi
darab` because the corpus already controls `produk`, `produk langsung`, and
categorical products, and Indonesian university curricula use `topologi
produk`. `Homeomorfisme` retains the corpus's `-isme` morphology while
recording `homeomorfisma` as an observed variant. `Net` is retained because it
is current Indonesian graduate-mathematics usage; `jaring` remains a documented
official-glossary alternative. `Filter` is retained, with `tapis` documented
as the official alternative.

The specialized forms `grup profinit`, `modul Tate rasional`, `modul Tate`,
`torus kompleks`, `kisi`, `kurva eliptik`, and `medan tertutup secara
aljabar` follow mathematical meaning and the existing Indonesian word
families. In particular, `kisi` denotes the discrete subgroup defining the
complex torus and is kept distinct from order-theoretic `kekisi`.

## Applied promotion result

The exact 37-row plan has been applied and deterministically verified:

1. the live `completion` row is the single admitted row with target
   `pelengkapan` and scope `topology, algebra, and chapter 10`;
2. the live `completeness` row remains `kelengkapan` and its scope is exactly
   `category theory and topology`;
3. the other 35 staging rows are admitted exactly once; and
4. the final glossary has 513 unique source terms, while the promoted Unit 034
   range contains no uncontrolled `kompletisasi`, `penutup terbuka`, or bare
   `bilangan p-adik` residue.

The final candidate
`build/unit-034-candidate/chapter4-group-limits-completions-id.tex` contains
135 records, 19,019 bytes, SHA-256
`8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62`.
The canonical `repo/source/chapter4.tex` contains 189,935 bytes, SHA-256
`37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569`.
Its lines 1604–1738 are byte-identical to the candidate; line 1739 remains the
blank boundary and line 1740 remains the Section 4.11 sentinel.

## Reflow and deterministic checks

`O013-LI-U034-REFLOW-001` affects only the presentation of the neighborhood-
basis display in candidate record 53 / authority line 1661 / canonical line
1656. It adds an `aligned` wrapper, two row breaks, and three alignment markers
without changing a term, prose assertion, operand, operator, relation, label,
reference, citation, or index. Exact inverse normalization of that one live
occurrence yields the prior terminology-normalized candidate at 18,982 bytes,
SHA-256
`c5e91c2271ed44eb51ecaad442799c0312af243fd7ab27a79fa1ff1d0492cc94`.
Thus the final 37-byte increase is wholly attributable to one target-only
digital reflow; it does not alter this terminology adjudication.

The final read-only candidate checker
`scripts/check_unit_034_candidate.py` is 16,590 bytes, SHA-256
`7b444643a1ccc1705690c64d099722844a30f40f0d97f04200095f0aaa40caf7`.
The canonical/glossary checker `scripts/check_unit_034_structure.py` is 3,703
bytes, SHA-256
`c80e22ed46a8920c36b07ba5543c447bb851d9c0681429ebffafaf270057da0d`.
Two current replays of each pass. Together they bind the frozen authority,
record topology, exact reflow normalization, protected mathematics, labels,
references, citations, indexes, diagram, one declared source correction,
candidate-identical canonical span, glossary uniqueness, and all 37 admitted
staging rows.

The final artifact is
`artifacts/unit-034-bab-4-limit-dan-kompletisasi-grup-id.pdf`, 136,702 bytes,
SHA-256
`e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272`.
The final structure/PDF evidence and render inventory are respectively 31,319
bytes / SHA-256
`4c37064eaa05cfcb0b70718b27c2213a36e1dfa0eda6bf098fd92c06fd641e2d`
and 41,802 bytes / SHA-256
`c1e54d2d0d2527542b8b0f575614d8cc27d7c7238a3ea859074d271d9945c3ba`.
They record `PASS_WITH_WARNINGS`, zero actionable defects, and a page-5 visual
pass for the reflowed display. The warnings are disclosed PDF/toolchain
limitations, not terminology or layout defects.

This audit records the live promoted result. Updating its prose mutated no
candidate, canonical, glossary, build, artifact, backend, control, Git, or
publication bytes.

Production and review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**, acting
on the user's instruction. Source-author and human-contributor credits remain
intact.
