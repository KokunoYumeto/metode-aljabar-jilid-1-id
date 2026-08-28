# O013-LI-U038 Translation Review — 2026-08-25

Status: isolated translation candidate complete and checker-admissible; not
promoted into canonical source, glossary, backend, reader, README, durable
controls, Git, or any publication lane.

## Exact authority and boundary

- Frozen authority:
  authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex.
- Full authority identity: 122,998 bytes; 1,382 LF-delimited records; SHA-256
  e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143.
- Selected source records: absolute lines 292–461 inclusive, 170 records,
  13,040 normalized-LF bytes; SHA-256
  742556293c463c59fc9dfd06b328e70f337a367e5cd739fb3ccd940793565955.
- The span is exactly the complete section
  \section{交换环初探}\label{sec:comm-ring-intro}. It introduces prime and
  maximal ideals and their spectra; proves pullback functoriality of Spec and
  quotient characterizations; proves existence of maximal ideals using Zorn;
  defines principal ideal domains; constructs localization and its universal
  property; identifies units, the total ring of fractions, and the field of
  fractions; and proves the localization correspondence for prime ideals.
- Authority line 291 is the blank separator after Unit 037. Line 462 is the
  blank separator after this section. The next content record is line 463,
  \section{间奏: Möbius 反演}\label{sec:Mobius}. Lines 292–461 are therefore
  the smallest complete coherent source-order boundary beginning at the
  supplied cursor.
- Next source-order cursor: chapter5.tex line 463.

## Candidate identity and census

- Candidate:
  build/unit-038-candidate/chapter5-commutative-rings-localization-id.tex.
- Identity: 16,799 bytes; 170 LF-delimited records; SHA-256
  e48edae4d77c5be8206f8e18b0d4c71c307444830594295a338cbf8313d03607.
- Every selected authority record maps to exactly one candidate record. The
  candidate has strict UTF-8 without BOM or CR, no extra boundary record, and
  exactly one final LF.
- TeX census: 66 begin/end markers (33 matched pairs), 12 labels, 15 ordered
  ref/eqref references, zero citations, 10 indexes, 247 protected mathematical
  zones, 452 unescaped dollar delimiters, and 246 opening plus 246 closing raw
  braces.
- Environment-begin census: align* 3; compactitem 1; corollary 1; definition 3;
  enumerate 2; example 2; gather 2; gather* 1; lemma 3; proof 6; proposition 4;
  remark 1; tikzcd 2; and tikzpicture 2.
- Diagram census: two tikzcd environments with five arrow commands and two
  tikzpicture direction glyphs with one draw command each. Directions,
  coordinates, labels, spacing parameters, and arrow paths match the authority.
- The eight item records are exactly the two ideal-definition items and the two
  three-part proposition lists. Neither authority nor candidate contains an
  Exercises, exercise, hint, or solution environment or any comment record.

## Semantic and structural review

- The opening scope retains commutativity and the presence of an identity
  element. Prime and maximal ideals preserve properness, product implication,
  strict containment, Spec/MaxSpec notation, and both symbol-index entries.
- The pullback lemma preserves the direction
  \varphi^\sharp:\Spec R_2\to\Spec R_1, the inverse-image formula, composition
  order, opposite-category exponent, and CRing-to-Set functor.
- The quotient-ideal correspondence retains all hypotheses and the three exact
  equivalences for primality, maximality, integral domains, and fields. The
  proof preserves arbitrary lifts, the zero ideal, principal ideal Rx, and the
  two-sided inverse conclusion.
- The maximal-ideal proposition retains arbitrary possibly noncommutative
  rings, proper two-sided ideals, reduction through the quotient theorem, the
  inclusion poset, chains, their union, the upper-bound proof, and Zorn's lemma.
  The separately documented zero-ring qualification below repairs only the
  overbroad prose following the proposition.
- The principal-ideal-domain definition retains the integral-domain hypothesis,
  I=\langle a\rangle=Ra, and the integer example.
- The localization relation, addition, multiplication, zero criterion,
  canonical homomorphism, invertibility of S, universal mapping property, and
  both universal-property diagrams preserve every variable, quantifier,
  operation, exponent, arrow, and direction.
- The unit criterion, localization kernel, injectivity criterion, non-zero-
  divisor multiplicative set, total ring of fractions, and field of fractions
  preserve all zero and nonzero hypotheses. The integer example contains the
  separately proven ambient-ring correction below.
- Extension and contraction of ideals preserve both directional glyphs,
  surjectivity/injectivity, the prime-ideal bijection, disjointness from S,
  inclusion order, the Spec set difference, and the local example at
  \mathfrak p, including uniqueness of its maximal ideal.
- Ordered environment markers, labels, reference identifiers, citation
  absence, index streams, TeX commands, per-record structural signatures, and
  comment state match the normalized authority exactly.
- All 247 inline, display, and mathematical-environment zones match after
  whitespace normalization, the six explicitly enumerated protected-text
  localizations, and O013-LI-U038-COR-002. No broad replacement of
  \text{...} payloads is used.
- The six protected-text localizations are the two occurrences of 理想 at
  authority 333; both naturally reordered “ideal dari” diagram labels at 427;
  或 to atau at 449; and 引理 to Lema at 451.
- Six ordinary index displays are localized while the original sort keys are
  retained; all four sym1 index entries remain exact.
- The candidate contains zero Han characters, Chinese punctuation,
  placeholders, invisible controls, malformed UTF-8, BOM, or CR/CRLF.

## Proven source corrections

### O013-LI-U038-COR-001 — authority line 355

The proposition at authority 352–354 assumes a proper two-sided ideal I and
then proves that such an ideal lies in a maximal two-sided ideal. Authority 355
then takes I={0} and concludes without qualification that every ring R has a
maximal two-sided ideal.

For the zero ring, {0}=R is not proper and there is no maximal proper ideal.
Thus the preceding proposition cannot be applied with I={0} in that case. The
candidate retains the source's formulas and adds only the necessary condition:

asalkan gelanggang ini bukan gelanggang nol.

This prose repair adds no mathematical token or TeX-topology change.

### O013-LI-U038-COR-002 — authority line 416

The example explicitly concerns the integer ring \Z and concludes that its
field of fractions is \Q, but the authority writes

[r,s] \in \text{Frac}(R).

No R is introduced locally in the example. The elements must belong to the
fraction field of the integer ring named in the same sentence, so the candidate
uses

[r,s] \in \text{Frac}(\Z).

The checker permits and pins this one-symbol ambient-ring repair only at
authority line 416. No other mathematical source correction is asserted.

## Terminology

- Controlled forms used directly include gelanggang, medan, himpunan hasil
  bagi, himpunan terurut parsial (poset), rantai, Lema Zorn, bijeksi, fungtor,
  gelanggang dengan unsur satuan, unsur identitas, and surjektif.
- Candidate-local transparent forms include ideal sejati, ideal prima, ideal
  maksimal, spektrum prima, spektrum ideal maksimal, ideal dua sisi, ideal
  utama, daerah ideal utama, himpunan bagian multiplikatif, lokalisasi,
  gelanggang pecahan total, medan pecahan, and prabayangan.
- The isolated task did not mutate the controlled terminology ledger.

## Rights, non-endorsement, and provenance

- Frozen Chapter 5 authority records 1–6 carry the 2018 source-author
  attribution and CC BY 4.0 permission notice with its license URL. Unit 038 is
  a continuation fragment and does not duplicate or replace that chapter-level
  header. The checker binds the full authority identity and all six header
  records; any later integration must retain the already translated Chapter 5
  header unchanged.
- This Indonesian translation is an independent derivative and does not imply
  endorsement by the source author, licensor, or any associated institution.
- Translation and formal review provenance: OpenAI Codex, acting on the user's
  instruction on 2026-08-25.

## Deterministic validation and handoff

- Checker: scripts/check_unit_038_candidate.py.
- Checker identity: 19,625 bytes; SHA-256
  6cd4526e2aa84b4d8d8e176960fd14f3e9a931c3a3d4cc2fb5f52c4a135ac665.
- The checker binds the authority, source slice, boundary sentinels, inherited
  rights header, candidate bytes, record topology, comment state, identifiers,
  indexes, diagrams, all protected math, exact protected-text localizations,
  controlled terms, and both correction records. It rejects Han or Chinese
  punctuation residue, placeholders, invisible controls, unexpected exercises,
  and uncontrolled terminology.
- Final validation command: python scripts/check_unit_038_candidate.py.
- Required terminal result: two consecutive executions of
  PASS: O013-LI-U038 isolated complete Section 5.3 commutative rings.
- Parent admission, canonical splicing, control/glossary promotion, backend and
  reader construction, build/visual QA, Git, and publication are outside this
  isolated task. The next source cursor is chapter5.tex line 463.
