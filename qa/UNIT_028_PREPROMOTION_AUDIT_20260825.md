# Unit 028 canonical-promotion audit — 2026-08-25

Status: **PASS; the bounded promotion gates are satisfied and the resulting
canonical bytes have been independently read back.** The historical filename
uses `PREPROMOTION` to match the lane convention. This record binds the exact
conditions and result of the already-executed promotion; it does not claim
that this Markdown file existed before that mutation.

## Exact boundary

- Frozen authority: `chapter4.tex:518-665`, 148 normalized-LF records,
  10,550 bytes, SHA-256
  `af7b91d4650e637505555cc188056656cd02f400bc6e1dd1ded0f619040a80db`.
- The substantive candidate maps authority lines 518–664 one-for-one; blank
  boundary line 665 is omitted. Candidate: 147 records / 13,017 bytes /
  SHA-256
  `027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd`.
- Section 4.5 starts at authority line 666 with the pinned Sylow-section
  sentinel and remains untranslated and outside Unit 028.

## Translation and terminology gates

- `scripts/check_unit_028_candidate.py`, 14,671 bytes, SHA-256
  `be2674c75fb17bf8dd8de43d4dd0230fd049f2b5640c72aa372aecc1742d1527`,
  passed twice with code 0, empty stderr, and byte-identical output.
- Independent source, language, and mathematics review:
  `qa/UNIT_028_INDEPENDENT_REVIEW_20260825.md`, 5,051 bytes, SHA-256
  `2fc54f16ba0da2ca280772bd986c2c7c8e44561d71e80ac7ec6419ed10734b0d`.
- Terminology audit: `qa/UNIT_028_TERMINOLOGY_AUDIT_20260825.md`, 3,981
  bytes, SHA-256
  `d10146b85cb798ad78e8a0c153ade50ebe80cb1fdd60fc15128e92ebc54f722a`.
- Approved delta: 25 admitted, nonduplicative rows / 4,052 bytes / SHA-256
  `601944b6058b9506655eca969d4d85506e59c24d9779d38567c19cb84bde41d7`.
  Every concept has a checked candidate evidence surface. The resulting live
  glossary is 408 data rows / 64,585 bytes / SHA-256
  `fdd00a574f7f93837688e2d9bc9707677c889eab1174b8f0121a119498557fe7`.

## Preserved and corrected content

The candidate preserves 24 paired environments / 48 ordered markers, 5
labels, 8 references, 2 citations, 9 indexes, 213 protected mathematical
zones, and 2 TikZ-cd arrows. The span contains no exercise, hint, answer, or
solution environment and no source-language residue.

One source correction is explicit. `O013-LI-U028-COR-001` restores the
previously declared `X,Y` as the objects in the equivariant-isomorphism
diagram and inverse identities, replacing undefined `M_1,M_2`. Three
`\text{...}` fragments are translated into Indonesian without changing their
mathematics. There is no second source correction.

## Bounded mutation and observed readback

- Pre-Unit-028 canonical Chapter 4: exact admitted Unit 025–027 prefix plus
  authority suffix from line 518, 166,211 bytes, SHA-256
  `5a4ec3ec5f420c694f7e1207f02a79c558da0f18c6c1f23969856c481f9a7420`.
- Pre-Unit-028 glossary: 383 data rows / 60,575 bytes / SHA-256
  `61e45adc844d8fd6beccf1cbb2216340913d6eb3b55cdd487817820171899f97`.
- Promotion script: `scripts/promote_unit_028.py`, 7,522 bytes, SHA-256
  `38a82ea5e45251c53acba661373a808aa54eaa8ec648f4873b95a06bfb2a9193`.
  It is fail-closed, idempotent, and limited to the canonical Chapter 4 target
  and controlled glossary.
- Untouched authority suffix from line 666: 103,097 bytes, SHA-256
  `e7c66981deb8f755ea97539b25d4b71742e5137f76238d8dfe5e3b351d18a4e7`.
- Observed canonical Chapter 4: exact Unit 025 + Unit 026 + Unit 027 + Unit
  028 candidate + authority suffix from line 666 + terminal LF; 1,897 records
  / 168,678 bytes / SHA-256
  `33ab68b169fad0f45815cbfa528e03eaa12efbb2add9a4599049a9823c86b0b3`.
  Candidate bytes occupy target lines 518–664 exactly; untranslated Section
  4.5 begins at target line 665.

The read-only integration checker
`scripts/check_unit_028_structure.py`, 10,010 bytes, SHA-256
`b1b3812cfe250a3f4ba3bcfa216927ff43158cdab8a08c6a31f7b1942f6a90b4`,
binds every identity above, the full Unit 025–028 prefix, authority suffix,
glossary prefix and exact delta tail, terminology evidence surfaces, promotion
script, and exact two-run candidate-checker output. It returned **PASS** on the
promoted bytes.

This audit admits only canonical source and terminology integration. Reader
build, backend, visual QA, release receipt, Git push, and public-byte readback
remain separate downstream gates.
