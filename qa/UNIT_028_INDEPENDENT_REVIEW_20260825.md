# Unit 028 independent canonical-admission review — 2026-08-25

Status: **PASS.** This review independently rechecks the complete Unit 028
authority span and Indonesian candidate. It supports canonical integration
only; it does not claim completion of the separate build, reader, backend,
visual-QA, version-control, or publication gates.

## Frozen boundary and identities

- Authority:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`,
  154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Exact selected span: authority lines 518–665 inclusive. The 148-record,
  normalized-LF slice is 10,550 bytes, SHA-256
  `af7b91d4650e637505555cc188056656cd02f400bc6e1dd1ded0f619040a80db`.
  Lines 518–664 are substantive Section 4.4; line 665 is the blank boundary
  record. Section 4.5 starts at line 666 and remains excluded.
- Candidate:
  `build/unit-028-candidate/chapter4-group-actions-counting-id.tex`, 147
  records, 13,017 bytes, SHA-256
  `027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd`;
  strict UTF-8 without BOM, LF-only, and exactly one final LF.
- Candidate checker: `scripts/check_unit_028_candidate.py`, 14,671 bytes,
  SHA-256
  `be2674c75fb17bf8dd8de43d4dd0230fd049f2b5640c72aa372aecc1742d1527`.

## Independent source, language, and mathematics pass

I reread all 148 authority records and all 147 candidate records rather than
accepting the earlier translation review as evidence. Coverage is complete and
in source order: monoid and group actions; equivariant maps and isomorphisms;
left and right actions; permutation, matrix, function-space, and heat-semigroup
examples; fixed points, orbits, stabilizers, and orbit decomposition; the
orbit–stabilizer cardinal identity; faithful, free, semiregular, transitive,
and multiply transitive actions; homogeneous spaces and torsors; translation,
double-coset, and conjugation actions; the isomorphism bitorsor; and the
bijective torsor criterion.

The mathematical pass checked both action axioms and their order, the inverse
conditions for equivariant isomorphisms, the opposite-monoid conversion, every
display in the heat-kernel example, the coset-to-orbit map, the stabilizer
conjugacy identity, each logical equivalence in the action-property list, the
left/right orientation of the translation and double-coset actions, both
commuting automorphism actions on `\Isom(G_1,G_2)`, and both directions of the
final injective/surjective torsor criterion. No formula, hypothesis,
quantifier, implication, citation, reference target, or active environment is
omitted or semantically altered outside the one declared correction below.

The Indonesian prose is formal and readable. Terms with easily confused
meanings remain distinct: `setia`, `bebas`/`semireguler`, and `transitif` are
not conflated; `orbit`, `ruang orbit`, `stabilisator`, `sentralisator`, and
`pusat` retain their separate objects; and left/right action and coset
orientation are explicit. No additional language or mathematical repair was
warranted in this pass.

## Reconfirmation of the one source correction

`O013-LI-U028-COR-001` repairs authority lines 533 and 535 as one logical
defect. The source declares `f:X\to Y` but its diagram and inverse identities
then use undefined `M_1,M_2`. The candidate consistently restores the declared
objects `X,Y`, with arrows between them and identities `\identity_X` and
`\identity_Y`. The surrounding definition forces this repair; there is no
second source correction.

The localized `\text{...}` fragments `pemetaan`, `unsur-unsur berbeda`, and
`isomorfisme` at authority lines 557, 610, and 646 are language localization,
not mathematical correction. The disabled source comment corresponding to
authority line 542 remains disabled in the candidate.

## Preserved formal topology

Independent deterministic counts agree with the candidate gate:

- 24 paired environments / 48 ordered begin/end markers;
- 5 labels, 8 ordered `ref`/`eqref` uses, 2 citations with keys `Zh2` and
  `Zh1`, and 9 index commands with their streams and sort keys preserved;
- 213 protected mathematical zones and 2 TikZ-cd arrow commands;
- no exercise, hint, answer, solution, or assessment environment;
- no Han prose, Chinese punctuation residue, invisible control, placeholder,
  or crossing into Section 4.5.

`python scripts/check_unit_028_candidate.py` was run twice independently. Both
runs returned code 0, emitted no stderr, and produced byte-identical PASS
output binding all identities and counts above, the one declared correction,
the three protected-text localizations, and next boundary
`chapter4.tex:666`.

Conclusion: Unit 028 is suitable for canonical admission. This conclusion is
bounded to the translated source and terminology integration and does not
prejudge downstream reader or publication evidence.

Production provenance for this review: OpenAI Codex gpt-5.6-sol, Ultra,
acting on the user's instruction; this does not alter or replace the source
author's credit.
