# Unit 027 independent pre-admission review — 2026-08-25

Status: **PASS after one bounded Indonesian precision repair and two
controlled-style normalizations.** This review is
limited to the isolated Unit 027 candidate. It does not admit or modify the
canonical Chapter 4 source, glossary, backend, controls, README, reader,
artifact inventory, Git history, or any public release.

## Frozen boundary and identities

- Authority: `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
- Complete authority identity: 154,744 bytes; SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Exact selected span: authority lines 365–517 inclusive. The 153-record,
  normalized-LF slice is 10,209 bytes; SHA-256
  `bb7cb2d385018971fe325c417bcafdccd9e92376c02e7cb72d3af038097f8db8`.
- Lines 365–516 are the 152 substantive records of Section 4.3. Line 517 is
  the blank boundary record and is intentionally absent from the candidate.
  Section 4.4 begins at line 518 and remains excluded.
- Reviewed candidate:
  `build/unit-027-candidate/chapter4-products-group-extensions-id.tex`.
- Final candidate identity: 12,675 bytes; SHA-256
  `aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563`;
  strict UTF-8 without BOM, LF-only, 152 records and exactly one final LF.
- Final checker: `scripts/check_unit_027_candidate.py`, 14,054 bytes;
  SHA-256
  `a98d407c23ce2ae28f3fbe1776387c96b9d2cc4db6c987e089227fbc92fd556e`.

## Independent source, language, and mathematics review

I reread the entire source span and candidate record by record rather than
relying on the earlier translation review. Coverage is complete and ordered:
products of monoids and their universal property; external and internal
semidirect products; the dihedral example and all three polygon drawings;
internal direct products; exact sequences; group extensions, equivalence,
splittings, and the split-extension/semidirect-product correspondence.

The mathematical pass separately checked the direct-product operation,
identity, inverse and projections; the product universal-property diagram;
the semidirect-product multiplication and inverse; the conjugation action and
normal-form computation; both normalizer hypotheses in the internal-product
lemma; the dihedral action; the internal direct-product hypotheses; every
image/kernel exactness assertion; both extension diagrams; and the maps
`p`, `s`, and `(n,h) \mapsto n s(h)`. No formula, hypothesis, quantifier,
implication, diagram direction, or reference target is missing or altered
outside the two declared source corrections below.

The Indonesian prose is formal, readable, and consistent with the admitted
vocabulary. One phrase required a type-precision repair:

### `O013-LI-U027-TR-001` — do not call the restricted action inner on `N`

- Authority location: line 510; candidate record 146.
- Prior candidate wording: `sebagai automorfisme dalam`.
- Final wording: `melalui pembatasan automorfisme adjoin`.
- Reason: `\Ad(s(h))` is an inner/adjoint automorphism of `G`, but its
  restriction to the normal subgroup `N` need not be an inner automorphism of
  `N`; in general it may represent a nontrivial element of `Out(N)`. The final
  wording accurately says that `\alpha(h)=\Ad(s(h))|_N` is obtained by
  restricting the adjoint automorphism. It also uses the admitted term
  `automorfisme adjoin`. This is a translation-precision repair, not an
  additional correction to the mathematical source.

No other Indonesian or mathematical correction was warranted.

The terminology gate subsequently normalized candidate records 8 and 41 from
the accepted synonym `unsur satuan` to the controlled corpus form `unsur
identitas`. These two prose-only changes preserve every mathematical and TeX
surface counted below.

## Reconfirmation of the two source corrections

1. `O013-LI-U027-COR-001`, authority line 384: changing the undefined codomain
   of `\varphi` from `M` to `\prod_{i \in I} M_i` is necessary. The diagram
   and the proof's componentwise definition both force that codomain.
2. `O013-LI-U027-COR-002`, authority line 442: restricting only the regular
   polygon interpretation to `n \geq 3` is necessary. The algebraic
   semidirect product remains meaningful in the source's wider range, whereas
   the stated nondegenerate regular-polygon geometry does not.

There is no third source correction.

## Preserved formal topology

Independent counts match the authority after the two explicit correction
normalizations:

- 28 paired environments / 56 ordered begin/end markers: 3 `align*`, 1
  `center`, 1 `compactenum`, 3 `compactitem`, 3 `definition`, 1 `enumerate`,
  1 `example`, 1 `gather`, 1 `inparaenum`, 3 `lemma`, 3 `proof`, 4 `tikzcd`,
  and 3 `tikzpicture`;
- 8 ordered labels and 5 ordered `ref`/`eqref` uses, all identifiers unchanged;
- 0 citations and 6 index commands with source streams and sort keys preserved;
- 171 protected mathematical zones;
- 4 commutative diagrams with 30 arrow commands, plus 3 polygon drawings
  containing 6 `foreach`, 6 `draw`, and 3 `node` commands;
- 15 item records, 308 unescaped dollar delimiters, and balanced braces
  (155 opening / 155 closing);
- 0 exercise, problem, hint, answer, or solution environments in this span;
- 0 Han characters, Chinese punctuation residues, placeholders, or crossings
  into Section 4.4.

## Deterministic result

After the precision repair, `python scripts/check_unit_027_candidate.py` was
run twice independently. Both runs returned **PASS** with the same final
identities and counts: 153 source-slice records / 10,209 bytes, 152 candidate
records / 12,675 bytes, 56 environment markers, 8 labels, 5 references, 0
citations, 6 indexes, 171 protected mathematical zones, 2 declared source
corrections, 1 translation-precision repair, zero Han residue, and next source
boundary `chapter4.tex:518`.

Conclusion: the final isolated Unit 027 candidate is suitable for canonical
admission subject to the parent lane's separate integration, build, backend,
reader, visual-QA, receipt, and publication gates.
