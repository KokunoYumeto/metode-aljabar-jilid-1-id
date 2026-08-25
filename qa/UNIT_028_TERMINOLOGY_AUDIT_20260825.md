# Unit 028 terminology audit — 2026-08-25

Status: **PASS; a 25-row additive glossary delta is present exactly at the
controlled glossary tail.** This audit is limited to Unit 028 terminology and
does not itself admit the backend, controls, reader, artifact, Git history, or
public release.

## Compared identities

- Candidate:
  `build/unit-028-candidate/chapter4-group-actions-counting-id.tex`, 13,017
  bytes, SHA-256
  `027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd`.
- Pre-Unit-028 controlled glossary prefix: 383 data rows / 60,575 bytes /
  SHA-256
  `61e45adc844d8fd6beccf1cbb2216340913d6eb3b55cdd487817820171899f97`.
- Unit 028 delta: `build/unit-028-staging/terminology-delta.csv`, 25 data rows
  / 4,052 bytes / SHA-256
  `601944b6058b9506655eca969d4d85506e59c24d9779d38567c19cb84bde41d7`.
- Resulting controlled glossary: `00_control/TERMINOLOGY.id-ID.csv`, 408 data
  rows / 64,585 bytes / SHA-256
  `fdd00a574f7f93837688e2d9bc9707677c889eab1174b8f0121a119498557fe7`.
- Independent semantic review:
  `qa/UNIT_028_INDEPENDENT_REVIEW_20260825.md`.

The complete current glossary parses under the five-column schema
`source_term,target_term,status,scope,note`; every row has a unique
`source_term`. Its last 25 rows are record-for-record identical to the Unit
028 delta, every delta row is marked `admitted`, and none collides with the
383-row prefix.

## Approved additive vocabulary

The 25 rows, in source order, are:

1. `group action` → `aksi grup`
2. `monoid action` → `aksi monoid`
3. `action map` → `pemetaan aksi`
4. `M-set` → `himpunan-M` (rendered `himpunan-$M$` in TeX)
5. `trivial action` → `aksi trivial`
6. `equivariant map` → `pemetaan ekuivarian`
7. `left action` → `aksi kiri`
8. `right action` → `aksi kanan`
9. `fixed point` → `titik tetap`
10. `orbit` → `orbit`
11. `stabilizer` → `stabilisator`
12. `orbit decomposition` → `dekomposisi orbit`
13. `orbit space` → `ruang orbit`
14. `faithful action` → `aksi setia`
15. `free action` → `aksi bebas`
16. `semiregular action` → `aksi semireguler`
17. `transitive action` → `aksi transitif`
18. `n-transitive action` → `aksi n-transitif`
19. `homogeneous space` → `ruang homogen`
20. `principal homogeneous space` → `ruang homogen utama`
21. `torsor` → `torsor`
22. `translation action` → `aksi translasi`
23. `conjugation action` → `aksi konjugasi`
24. `conjugacy class` → `kelas konjugasi`
25. `bitorsor` → `bitorsor`

Each concept has an exact evidence surface in the candidate, allowing for
ordinary TeX binding (`himpunan-$M$`, `$n$-transitif`) and list-form
definitions (`\item setia`, `\item bebas`, `\item transitif`). The delta notes
preserve the distinctions that matter mathematically: action side, orbit-space
orientation, faithfulness versus freeness versus transitivity, a torsor's
nonempty free-transitive condition, and a bitorsor's commuting actions.

## Reused controlled terms and style decision

The candidate also correctly reuses earlier admitted forms including `grup`,
`monoid`, `kategori`, `homomorfisme`, `isomorfisme`, `kardinal`, `grup
simetris`, `submonoid`, `subgrup`, `koset`, `koset ganda`, `surjektif`,
`bijeksi`, `normalisator`, `sentralisator`, and `automorfisme adjoin`.
The international technical forms `orbit`, `torsor`, and `bitorsor` are kept
rather than replaced by ad hoc paraphrases; their definitions make their
meaning explicit at first use. `Ekuivarian` is kept distinct from ordinary
`homomorfisme`, while `ruang orbit` is kept distinct from an individual
`orbit`.

No normalization of the pinned candidate was required by this audit. The
delta is an internal controlled-vocabulary decision grounded in the complete
mathematical context; it is not represented as direct external same-field
attestation.

Production provenance for this terminology decision: OpenAI Codex
gpt-5.6-sol, Ultra, acting on the user's instruction; this does not alter or
replace the source author's credit.
