# Unit 018 independent mathematics and structure audit — 2026-08-24

Status: **PASS**

Unit: Chapter 2 exercises, authority `chapter2.tex:1603-1645`

Audit provenance: **OpenAI Codex gpt-5.6-sol, Ultra**

This is an independent, read-only audit of the isolated Indonesian candidate.
It does not replace the translation review, admit a reader build, or modify the
authority, canonical target, candidate, controls, Git history, or publication
state.

## Frozen inputs

- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex`
  - full file: 139,983 bytes;
  - full-file SHA-256:
    `56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840`;
  - audited normalized-LF span, physical lines 1603-1645: 5,197 bytes,
    43 records;
  - span SHA-256:
    `24417872734a2dc72c1d52d0df30246a427c5bbb714faf5238679e19c8dd7cce`.
- Candidate:
  `build/unit-018-candidate/chapter2-exercises-id.tex`
  - 6,523 bytes, 43 LF-terminated records;
  - SHA-256:
    `d69667baae061a5d06a57dcc25033b6a971986ea704c72a0f53d687707837b55`.

## Boundary verdict

**PASS.** Authority line 1602 is the blank separator after Section 2.8, line
1603 is exactly `\begin{Exercises}`, and line 1645 is exactly
`\end{Exercises}` and the end of `chapter2.tex`. The candidate begins and ends
with those same delimiters on records 1 and 43. Thus lines 1603-1645 are the
smallest coherent source boundary containing the complete Chapter 2 exercise
block; neither adjacent prose nor a partial environment is included.

The only interior blank record is authority line 1638 / candidate record 36,
so physical blank-line topology is preserved as well.

## Deterministic topology census

| Surface | Authority | Candidate | Verdict |
|---|---:|---:|---|
| Physical records | 43 | 43 | exact one-to-one map |
| Top-level exercises | 13 | 13 | preserved |
| Nested exercise items | 5 | 5 | preserved |
| All `\item` calls | 18 | 18 | preserved |
| Hints | 1 | 1 | preserved at line 1632 / record 30 |
| Begin/end environment calls | 6 / 6 | 6 / 6 | balanced, same ordered topology |
| Inline-math occurrences | 80 | 80 | 79 exact; one declared correction |
| Bracket-display formulae | 2 | 2 | byte-identical |
| `align*` displays | 1 | 1 | math exact apart from translated `\text` |
| `cases` environments | 1 | 1 | preserved inside `align*` |
| `tikzcd` diagrams | 1 | 1 | byte-identical |
| Diagram arrows | 10 | 10 | byte-identical |
| Ordinary references | 3 | 3 | same labels and mapped records |
| Labels / equation references / citations | 0 / 0 / 0 | 0 / 0 / 0 | preserved |
| TeX command occurrences | 250 | 250 | same inventory; prose-order movement only |
| Han residue in candidate | n/a | 0 | pass |

The ordered environment sequence is identical:
`Exercises`, `align*`, `cases`, `compactitem`, `inparaenum`, and `tikzcd`, with
each close paired in the proper nesting order. The three compact-list items
remain nested under the quotient-category exercise; the two roman-numbered
items remain nested under the adjunction exercise; the hint remains attached
to that same exercise.

The reference topology is exact:

- `eg:forgetful-adjunction`, authority line 1625 / candidate record 23;
- `prop:Yoneda-lemma`, authority line 1637 / candidate record 35;
- `def:diagonal-functor`, authority line 1639 / candidate record 37.

## Formula and diagram audit

All 80 source and target inline formula occurrences remain on their
corresponding physical records. Same-record multiset matching finds 79
byte-identical formulae. The only changed formula is the declared binding of
`U` at authority line 1644; its adjudication appears below. Formula order moves
within Indonesian sentences at authority lines 1617, 1619, 1632, and 1639,
but the complete same-line mathematical multisets are unchanged.

Both bracket displays are byte-identical:

- adjunction/Yoneda naturality diagram, lines 1633-1636, SHA-256
  `ee0f3fa4ef776b74abea09e1e065f8b8b11120dc804c9b53e0d3e027098adb08`;
- natural-transformation Hom equality, line 1642, SHA-256
  `dc389c0fe67312cbefb0078ebc2810d49f736b20ba6755017ef8849c423b3b18`.

The complete `tikzcd` environment is byte-identical in source and candidate,
including all ten arrows, `mapsto` directions, pullback labels, and
`\varphi`, `\eta` expressions. Its SHA-256 is
`c5c3921b8f34030da53d02a098ffa92b7bdbe076236fbec0efa4ede3b6323ec3`.

The `align*`/`cases` construction of the category join preserves every object,
Hom-set, direction, condition, separator, and empty-set case. Its differing raw
hashes are wholly explained by the faithful localization of
`\text{独点集}` as `\text{himpunan tunggal}`. Replacing only those `\text`
bodies with one neutral marker makes the displays byte-identical, with
normalized SHA-256
`276261c9028024c8ae5edf47763f77064c341880ab542493cf678c427166d905`.

## Mathematical and semantic review

The candidate preserves the complete tasks and hypotheses for:

1. the isomorphism criterion for a three-morphism composite;
2. the categorical join and its finite-ordinal calculation;
3. the skeleton of finite total orders;
4. the quotient-category universal property;
5. composition of categorical equivalences;
6. counits of the previously defined adjunctions;
7. unitization as a left adjoint from `Ring` to `Rng`;
8. the fully-faithful criteria for the unit and counit, including the complete
   Yoneda hint and commuting diagram;
9. left and right adjoints of the diagonal functor;
10. vector spaces and abelian groups as filtered colimits of finite or
    finitely generated subobjects;
11. full inclusion and natural-transformation Hom-sets;
12. products, coproducts, completeness, and cocompleteness of pointed sets and
    pointed spaces; and
13. the left adjoint and right-adjoint obstruction for the forgetful functor
    from pointed sets.

No hypothesis, conclusion, universal-property clause, exercise, nested part,
hint step, or mathematical dependency is omitted or weakened. Terminology such
as `fungtor`, `pasangan adjoin`, `kounit`, `kategori hasil bagi`, `kerangka`,
`penuh dan setia`, `limit`, and `kolimit` is used consistently with the
already admitted Indonesian lane.

## Adjudication of the two proposed corrections

### O013-LI-U018-COR-001 — authority line 1640

**Accept; confidence: certain.** The authority phrase `设域 $\Bbbk$ 为域`
duplicates the field predicate (literally, “let the field K be a field”). The
candidate's `Misalkan $\Bbbk$ medan` removes only that grammatical duplication.
All six inline mathematical expressions on the record, including `\Bbbk`,
`\cate{Vect}(\Bbbk)`, `\varinjlim`, and `\cate{Ab}`, remain unchanged. This is
a disclosed source-language repair with no mathematical alteration.

### O013-LI-U018-COR-002 — authority line 1644

**Accept; confidence: certain.** The authority says “consider the forgetful
functor `\cate{Set}_\bullet \to \cate{Set}`” and immediately asks for the left
adjoint of `U`, although `U` has not been bound in that exercise. The candidate
minimally changes the first formula to
`U: \cate{Set}_\bullet \to \cate{Set}`. This binds the exact functor used in
the two following clauses and changes no domain, codomain, or assertion. It is
the sole non-byte-identical inline formula among the 80 mapped occurrences.

## Apparent issues deliberately not changed

- Authority line 1624 does not spell out the order of the composite
  quasi-inverse. The candidate's prose “dalam urutan yang sesuai” is a faithful
  clarification, not a new mathematical claim; no source correction is needed.
- The equality sign between the two natural-transformation Hom-sets on line
  1642 is retained exactly. In the context of the full inclusion it denotes the
  canonical identification induced by horizontal composition and is not a
  high-confidence defect.
- The term `gabungan` for the explicitly defined `\star` construction does not
  alter its object, Hom, or composition data. The definition, rather than an
  English naming convention, controls the mathematics.

## Final disposition

**PASS.** The 43-record candidate is mathematically faithful, structurally
complete, formula-safe, and boundary-exact. Both proposed corrections are
necessary, minimal, and correctly implemented. No additional high-confidence
mathematical, formula, diagram, reference, exercise, or hint defect was found.
