# Unit 033 source and translation review — 2026-08-25

Status: **PASS; the reviewed translation is integrated into the canonical
Chapter 4 source and its reader passes deterministic PDF and visual QA.** This
record does not claim completion of the modular backend, Git publication, or
public-byte readback.

## Scope and authority

- Corpus/unit: `O013-LI-U033`.
- Work: Wen-Wei Li, *Methods in Algebra*, Volume 1.
- Frozen upstream commit:
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`; tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
- Authority identity: 154,744 bytes; SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`;
  1,898 LF-delimited records and no final LF.
- Exact source boundary: authority lines **1389–1608**, all of Section 4.9,
  symmetric groups. Line 1608 is the blank boundary record. Section 4.10
  begins at authority line **1609** and remains excluded.
- Exact normalized-LF authority slice: 220 records, 19,076 bytes; SHA-256
  `c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a`.

The complete span covers symmetric groups and their natural embeddings;
cycles, cycle decomposition and type; integer partitions and conjugacy;
adjacent transpositions; the sign map and alternating groups; simplicity of
`A_n` and nonsolvability of `S_n`; braid groups, diagrams and presentation;
the quotient onto the symmetric group; the Coxeter presentation and its
cardinality proof; and the general definition of a Coxeter group. No exercise,
hint, answer, solution, assessment, or citation command occurs in the span.

## Candidate and canonical integration

- Final candidate:
  `build/unit-033-candidate/chapter4-symmetric-groups-id.tex`.
- Candidate identity: 219 substantive records, 23,099 bytes; SHA-256
  `1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76`.
  It is strict UTF-8 without BOM, LF-only, and ends in exactly one LF.
- Canonical target: `repo/source/chapter4.tex`, 185,920 bytes; SHA-256
  `a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde`.
- Target lines 1384–1602 are byte-identical to the complete candidate. Target
  line 1603 is the preserved blank boundary and line 1604 is the untouched
  Section 4.10 source sentinel.

The splice preserves the complete admitted Units 025–032 prefix and the
untouched source suffix. The candidate contains no Han prose, Chinese
punctuation, invisible control, placeholder, untranslated editorial block, or
disabled source content.

## Translation, terminology, and semantic review

The candidate uses the established edition forms `grup simetris`, `grup
kepang`, `persamaan Yang--Baxter`, `grup solvabel`, `subgrup turunan`,
`presentasi grup`, `pembangkit`, `relasi`, and `grup dihedral`. The admitted
13-row terminology delta covers the new surfaces actually used in the span,
including `permutasi`, `siklus`, `permutasi siklik`, `panjang siklus`,
`transposisi`, disjoint-cycle terminology, `dekomposisi siklus`, `tipe
siklus`, `kelipatan persekutuan terkecil`, parity terminology, braid `untai`,
and `grup Coxeter`.

Two target occurrences of the older synonym `unsur satuan`, aligned to
authority lines 1407 and 1516, were normalized to the corpus form `unsur
identitas`. The first sentence also makes the plural antecedent explicit by
saying that all cycles of length one may be omitted. These are two terminology
normalizations, not source corrections. One separately recorded display
reflow changes only line breaking; it is likewise not a source correction.

A complete source-to-target semantic pass checked every definition,
hypothesis, implication, quantifier, proof step, formula, label, reference,
index entry, and diagram. Particular attention was given to the disjoint-cycle
and conjugacy arguments, construction of the sign map, both cases of the
fixed-point proof of simplicity, the low-degree `A_4` calculation, all braid
relations and endpoint actions, and every generator-moving step in the Coxeter
cardinality proof. No mathematical claim or active source environment was
omitted.

## Declared source corrections

Exactly two high-confidence repairs are applied openly; neither appears in the
pinned current, v1, or v0 TeX errata.

1. `O013-LI-U033-COR-001`, authority line 1580: the endpoint
   `\tilde{\tau}_n` is repaired to `\tilde{\tau}_{n-1}` because the adjacent
   generators are defined only for `1 <= i < n` and every surrounding map and
   recursion uses the same endpoint.
2. `O013-LI-U033-COR-002`, authority line 1591: the cardinality comparison
   begins with `$|\mathfrak{S}'_n|` rather than the group object
   `$\mathfrak{S}'_n`; the proof is explicitly bounding an order by the numeric
   quantity `n|\mathfrak{S}'_{n-1}|`.

No other source correction is required or claimed.

## Protected surfaces and deterministic gates

Five `\text{...}` fragments inside mathematics are localized without changing
their surrounding formulas. Nine index commands preserve stream, sort key,
symbol, and order. The final candidate preserves 43 paired environments / 86
ordered markers, ten labels, twenty ordered `ref`/`eqref` occurrences, zero
citations, nine index entries, 311 protected mathematical zones, twelve
diagrams, four exact `\arrow` commands, nine `\braid`, three `\draw`, and ten
`\node` commands.

The fail-closed candidate checker is
`scripts/check_unit_033_candidate.py`, 18,099 bytes, SHA-256
`643b1ccc5fe1f47aa185cbb8d2813e971c1381cbcc032fac8cc01c2c941c2a1d`.
The canonical structure checker is 12,660 bytes, SHA-256
`d018a2966e46fe44045c2159a420769fa2f1a0bd5992ecceb454ab98ebfc4e65`.
Repeated checks bind the complete authority identity and slice, candidate,
canonical target span, blank boundary, Section 4.10 sentinel, glossary tail,
TeX topology, two source corrections, two terminology normalizations, and one
target-only digital reflow.

## Reader closure

The final reader `artifacts/unit-033-bab-4-grup-simetris-id.pdf` has ten pages,
118,964 bytes, SHA-256
`0af07d45c9aee57e28a6f27fe6162afda253e15c44779ccf07ac591516bd1f1d`.
Two independent clean builds, Poppler and MuPDF rendering of all pages, PDF
structure inspection, and full-resolution visual review pass. Diagnostics are
zero for errors, unresolved references/citations, missing characters, empty
targets, and overfull boxes. Exactly one visually accepted, nonfatal underfull
hbox remains disclosed. The PDF is untagged, so no tagged-accessibility claim
is made.

The reader driver contains a local, reader-surface-only robust redefinition of
`\xlongequal`: Poppler dropped the extensible rule emitted by dvipdfmx, so the
driver retains the same labelled equality semantics with a standard embedded
math equality glyph. The candidate and canonical source mathematics are
unchanged by this renderer workaround; both supported renderers show the
labelled equality visibly and without clipping.

Production and review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**, acting
on the user's instruction. Wen-Wei Li remains credited as source author and
all source and human-contributor credits are preserved. Backend generation,
Git publication, public-byte readback, and cursor advancement remain separate
subsequent gates; the next source-order cursor is authority line **1609**.
