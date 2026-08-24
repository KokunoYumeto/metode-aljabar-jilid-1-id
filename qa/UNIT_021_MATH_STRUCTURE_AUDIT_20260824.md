# Unit 021 Mathematics and Protected-Topology Audit — 2026-08-24

Status: **PASS**. The isolated Indonesian Unit 021 candidate and its canonical
integration preserve the reviewed mathematics and protected TeX topology of
the frozen authority span, subject only to the three explicit source repairs
below. No additional candidate defect was found.

## Frozen scope and integration

| Object | Exact scope | Bytes | SHA-256 |
|---|---:|---:|---|
| Frozen authority `chapter3.tex` | 911 LF records | 75,571 | `7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0` |
| Authority prefix | lines 1–306 | 27,816 | `ffce6a027b6d3ceacffd30548553b7539688ff552f075127dd769a9900bbfff5` |
| Unit 021 authority span | lines 307–512 | 15,276 | `cbbf8714c3e5a387e42e2653900a8f3911e41df530b39a86701261c89de64ff8` |
| Authority suffix | lines 513–911 | 32,479 | `0184b127cecf8e973aa395e050385ed75280b898d5ea22293572d6513d7a6c83` |
| Isolated Indonesian candidate | lines 1–206 | 17,968 | `57f5bc8a211b6a9b76a096742fbfc94989c890f11d5140ad449d0e76e2c67085` |
| Canonical target `chapter3.tex` | 910 LF records | 83,581 | `ce310d940819f0fc51ee6459f73a8380b602edee42ef666720e225451adee9f9` |
| Canonical target prefix | lines 1–305 | 33,134 | `db4b9e76f638eb4338f496664e58213102c1ccc6b8933e890bb5d00fa1702ae0` |
| Canonical Unit 021 span | lines 306–511 | 17,968 | `57f5bc8a211b6a9b76a096742fbfc94989c890f11d5140ad449d0e76e2c67085` |
| Canonical target suffix | lines 512–910 | 32,479 | `0184b127cecf8e973aa395e050385ed75280b898d5ea22293572d6513d7a6c83` |

The canonical span is byte-identical to the isolated candidate. Authority line
512 and canonical line 511 are the included blank separator. Authority line
513 and canonical line 512 are the unchanged next boundary
`\section{充实范畴}\label{sec:enriched-cat}`. The complete post-Unit-021
canonical remainder is byte-identical to authority lines 513–911, so the next
section did not enter this unit and was not disturbed by integration.

All inputs are UTF-8, LF-only, LF-terminated files. The audit used no inferred
or reconstructed source text.

## Explicit source repairs

### `O013-LI-U021-COR-001` — naturality-square codomains

Authority lines 485–487 display the naturality square for the braiding. Its
vertical arrows are labelled `f \otimes g` and `g \otimes f`, but authority
line 487 repeats the upper objects `X \otimes Y` and `Y \otimes X` on the
lower row. Those cannot be the codomains of the displayed vertical arrows.

Candidate line 181 / canonical line 486 changes only that lower row to
`X' \otimes Y'` and `Y' \otimes X'`, including the lower horizontal label
`c(X',Y')`. This is the unique mathematical delta in the six `tikzcd`
payloads and restores the naturality square. The commands, four arrows, arrow
labels, matrix shape, and surrounding diagram are otherwise unchanged.

### `O013-LI-U021-COR-002` — objects misnamed as braids

Authority line 448 fixes `X=m` and `Y=n`, where objects of `\cate{Braid}` are
nonnegative integers. Authority lines 450 and 452 then call `X` and `Y`
“braids” while introducing the bundles of `m` and `n` unentangled strands.
Candidate lines 144 and 146 / canonical lines 449 and 451 correctly call them
objects. The formulas, colors, strand counts, and two inline `tikzpicture`
payloads are unchanged.

### `O013-LI-U021-ED-001` — duplicated noun

Authority line 508 contains `无穷循环群群`, duplicating the final noun in the
phrase “infinite cyclic group.” Candidate line 202 / canonical line 507 gives
the intended `grup siklik tak hingga`. This is an editorial source typo, not a
mathematical change.

## Protected mathematics and topology census

The checker compared the authority and Indonesian span line by line and
failed on any unreviewed structural delta.

- TeX command multisets agree on every one of the 206 relative lines: 527
  commands in each span.
- There are 144 dollar-delimited math surfaces. After normalizing only
  translated `\text{...}` contents and `COR-001`, each relative line has the
  same formula multiset. The sole within-line order changes are on relative
  lines 100, 132, 144, and 146, where Indonesian sentence order moves intact
  formulas; no formula is added or lost.
- Six bracket displays agree after the same `\text{...}` localization rule.
  The three `equation`, two `align*`, and one `multline*` payloads are
  byte-identical.
- There are 43 balanced environment pairs (86 ordered events): 17
  `tikzpicture`, 6 `tikzcd`, 4 `center`, 3 `definition`, 3 `equation`, 2
  `remark`, 2 `align*`, 2 `example`, and one each of `proposition`, `proof`,
  `multline*`, and `array`. Their ordered line topology is identical.
- All 17 `tikzpicture` payloads are byte-identical. The first five `tikzcd`
  payloads are byte-identical; the sixth becomes byte-identical after the
  exact `COR-001` row substitution.
- Diagram/control census and line positions agree: 30 nodes, 2 coordinates,
  32 draws, 0 paths, 15 `edge` tokens, 26 `\arrow[...]` commands, 10
  `\braid` commands, and 3 `\hline` commands.
- Raw braces balance at 282/282 in both spans; excluding six escaped literal
  braces, structural braces balance at 276/276 with depth never below zero.
- Neither span contains a TeX comment. The authority span contains 1,446 Han
  characters; the Indonesian span contains zero.

The nine labels are preserved in order and on the same relative lines:
`sec:braiding`, `def:braiding`, `eqn:hexagon-axiom-1`,
`eqn:hexagon-axiom-2`, `rem:hexagon-axiom-strict`,
`def:symm-monoidal-cat`, `prop:YBE-cat-strict`,
`rem:YBE-cat-strict`, and `eg:braid`.

Reference topology is unchanged: 10 `\ref` plus 3 `\eqref` occurrences, with
the same ordered identifiers and duplicate structure. The two citations are
unchanged: `\cite{JS93}` and `\cite[Corollary 2.6]{JS93}`. The unit contains
no `\item`. All eight index commands remain on their corresponding relative
lines; their Indonesian sort/display text is localized while both symbol
entries retain their exact mathematical payloads.

The separate terminology evidence was not used to relax this mathematics
gate. Its frozen identities at this boundary are:

- glossary: 39,866 bytes, SHA-256
  `45e7b1500533e4fa8a8a257efe2982261704bd00a27f056030112141e5ed0efe`;
- `qa/UNIT_021_TERMINOLOGY_AUDIT_20260824.md`: 4,653 bytes, SHA-256
  `baaf37af9e72cb487636b07369403432d6a02e8bd6b2960fda1ca7d9537c2ef2`.

## Deterministic checker evidence

`scripts/check_unit_021_structure.py` is 28,404 bytes with SHA-256
`f5ef89d6fcfa7196e54a43e1a13377df93d985bc7407f60b3f58ecef0aeb2cce`.
Two consecutive executions exited 0 with byte-identical stdout. A negative
probe supplying an unexpected path-override argument exited 1 with the
fail-closed message that the checker accepts no path overrides or arguments.
The checker pins every authority/candidate/canonical identity above and fails
before reporting PASS if any boundary, hash, correction signature, formula
census, environment topology, identifier, citation, index, diagram structure,
brace balance, or Han-residue gate changes.

## Verdict

**PASS for Unit 021 mathematics/protected topology.** The Indonesian candidate
and canonical span preserve the admitted Unit 021 mathematics and protected
reader structure. The only source-to-target departures are the two necessary
corrections and one editorial normalization recorded above. No additional
source defect or candidate defect was found in this bounded audit.

Audit provenance: OpenAI Codex gpt-5.6-sol, Ultra.
