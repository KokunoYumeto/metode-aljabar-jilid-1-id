# Unit 026 source and translation review — 2026-08-24

Status: **PASS; the final translation candidate and its exact canonical Chapter
4 splice are admitted by bounded deterministic checks. Reader construction,
backend binding, version control, and publication remain outside this review.**

## Scope and authority

- Corpus/unit: `O013-LI-U026`.
- Work: Wen-Wei Li, *Methods in Algebra*, Volume 1.
- Frozen upstream commit: `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Frozen upstream tree: `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Authority file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
- Authority file identity: 154,744 bytes; SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`;
  1,898 LF-delimited records and no final LF.
- Selected contiguous boundary: authority lines **177–364**, comprising all of
  Section 4.2 (homomorphisms and quotient groups) through the adjunction
  paragraph immediately before Section 4.3. Line 364 is the blank
  section-boundary record.
- Exact normalized-LF slice: 188 records, 15,360 bytes; SHA-256
  `4377d6a31512cf3e2a56f4e8e1c3417b62ff1a6468eb85629c8d9867a4f975f8`.
- Content coverage: homomorphisms and isomorphisms of monoids and groups;
  inner automorphisms; image and kernel; quotient structures and quotient
  groups; the universal property of a quotient; three isomorphism results;
  cyclic groups and element order; Grothendieck group completion; and the
  categorical adjunction between commutative monoids and abelian groups.
- Next source-order boundary: Section 4.3 (direct products, semidirect products,
  and group extensions), beginning at authority line **365** and ending at the
  blank boundary line 517 before Section 4.4 at line 518. After the admitted
  reflow, authority line 365 resumes at canonical target line **366**.

## Candidate identity and provenance

- Candidate:
  `build/unit-026-candidate/chapter4-homomorphisms-quotients-id.tex`.
- Final candidate identity: 19,424 bytes; SHA-256
  `a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87`;
  strict UTF-8 without BOM, LF-only, 187 substantive records with a final LF.
  The 187 candidate records map one-for-one to authority lines 177–363; the
  boundary-only blank authority record 364 is intentionally omitted.
- Canonical target after promotion: `repo/source/chapter4.tex`, 163,745 bytes;
  SHA-256
  `fc3fd6ef470d41f146456bfc889eb7c7ec84bb48890f1b23f18e51a195e7d463`.
  Its exact byte construction is the admitted Unit 025 prefix, this complete
  Unit 026 candidate, the untouched authority suffix beginning at source line
  365, and one disclosed terminal LF. Unit 026 occupies target lines 179–365.
- Translation and formal review were performed by **OpenAI Codex
  gpt-5.6-sol, Ultra**, on instructions of the user. This provenance statement
  does not replace or diminish the upstream author credit.
- The principal source text is CC BY 4.0. The complete repository/build closure
  must continue to disclose its separately licensed components: `Lanzhou.png`
  and the credited TeX.StackExchange fragment in `AJbook.cls` are CC BY-SA 3.0,
  and the bundled fonts are OFL 1.1. This isolated candidate contains no copied
  external raster asset. The complete closure must never be described simply
  or unqualifiedly as CC BY 4.0.
- This independent Indonesian adaptation is not authored, approved, or
  endorsed by Wen-Wei Li or by any institution associated with the source.

## Translation and structural review

The candidate uses formal id-ID prose while retaining the controlled terms
`grup`, `homomorfisme`, `isomorfisme`, `endomorfisme`, `automorfisme`,
`himpunan hasil bagi`, `kelas ekuivalensi`, `sifat universal`, `fungtor`,
`fungtor pelupa`, `pasangan adjoin`, `grup abelian`, and `subkategori penuh`.
The controlled glossary now also admits the Unit 026 forms `homomorfisme
semigrup`, `automorfisme dalam`, `automorfisme adjoin`, `kernel`,
`homomorfisme terimbas`, `grup hasil bagi`, `relasi pencakupan`, `pembangkit`,
`grup Grothendieck`, and `kategori-U`. Symbols, quantifier order, hypotheses,
conclusions, and diagram directions were checked against the frozen Chinese
source.

The terminology pass applied the exact reader-facing normalizations recorded
in `qa/UNIT_026_TERMINOLOGY_AUDIT_20260825.md`: `peta pelestari struktur`,
`unsur identitas`, `grup unit`, `diagram komutatif`, `homomorfisme terimbas`,
`relasi pencakupan`, and `pembangkit`. It also corrected the source's alternate
name for `\Ad_x` from the type-weaker `isomorfisme adjoin` to
`automorfisme adjoin`: the displayed map is specifically an automorphism
`G \to G`, not categorical adjunction data. The four source occurrences of
`\text{ord}` remain unchanged; no undeclared `\ord` macro was introduced.

Preserved active topology:

- 36 paired environments: 6 `align*`, 2 `compactenum`, 2 `compactitem`,
  1 `definition-theorem`, 3 `definition`, 1 `example`, 2 `gather`, 8 `proof`,
  7 `proposition`, 1 `remark`, and 3 `tikzcd`;
- 12 labels, in their original order and with exact identifiers;
- 24 ordered `ref`/`eqref` targets;
- 1 citation key, `DN00`, with only its visible locator translated;
- 10 index commands with the original main/symbol index-stream topology;
- 12 TikZ arrow commands and 500 unescaped dollar delimiters;
- 224 opening and 224 closing braces, balanced as a whole;
- 0 exercises and 0 hints in this source section;
- 0 Han characters, 0 Chinese punctuation residues, and 0 translation
  placeholders.

The commented-out alternative proof in authority lines 306–311 is retained as
translated TeX comments. It therefore remains inactive while preserving the
source's editorial information and mathematical topology.

## Declared source corrections

No mathematical change is silent. Four high-confidence corrections are applied
in the final candidate and remain separately provenanced in the integrated
source.

### `O013-LI-U026-COR-001` — parenthesize the quotient kernel

- Authority locations: lines 301, 308 (inactive commented proof), and 312.
- Source form: `H/N \cap H`.
- Candidate form: `H/(N \cap H)`.
- Reason: the restricted quotient homomorphism has kernel `N \cap H`, so the
  first isomorphism theorem gives `H/(N \cap H) \simeq HN/N`. Without the
  parentheses, the printed expression parses as `(H/N) \cap H`, which is not
  the stated quotient and is not even well-typed in this setting.

### `O013-LI-U026-COR-002` — unify the homomorphism symbol

- Authority location: line 358.
- Source form: introduces `\phi: M \to N` but immediately uses
  `M \xrightarrow{\varphi} N` for the same map.
- Candidate form: introduces `\varphi: M \to N`, consistently with the
  subsequent composite and the surrounding section.
- Reason: the sentence describes one homomorphism; no second map `\phi` is
  defined or used.

### `O013-LI-U026-COR-003` — restrict the inverse formula to groups

- Authority location: line 231.
- Source claim: for the quotient of a semigroup, monoid, or group, the source
  first identifies the last two cases and then states both that their identity
  is `[1]` and that an element's inverse is `[x]^{-1}=[x^{-1}]`.
- Candidate clarification: quotient monoids and quotient groups both have
  identity `[1]`; **only in the group case** is every element invertible with
  `[x]^{-1}=[x^{-1}]`.
- Reason: an arbitrary monoid element need not possess an inverse. The original
  unqualified wording is therefore false for general quotient monoids. The
  corrected sentence leaves the group assertion and all displayed mathematics
  intact while supplying the necessary case restriction.

### `O013-LI-U026-COR-004` — make the cyclic-subgroup claim total and typed

- Authority location: line 320.
- Source form: assumes only `m \mid n`, writes the quotient
  `\Z/(n/m)\Z`, and assigns order `n/m` to `m\Z/n\Z` without excluding
  `n=0` or accounting for a negative quotient.
- Candidate form: the displayed finite-order statement assumes `n \ne 0`,
  gives the order as `|n/m|`, and then treats `n=0` explicitly: `m\Z` is
  infinite cyclic for `m\ne0`, while `0\Z/0\Z` is trivial.
- Reason: when `n=0`, the source quotient expression contains `0/0` for
  `m=0` and does not describe the infinite cyclic cases; when `n/m<0`, group
  order cannot be negative. The candidate preserves the intended finite case
  and closes both omitted edge cases.

No other source correction is claimed. The final semantic pass also confirmed
that `automorfisme adjoin` is a terminology refinement rather than a new
mathematical correction, and that all remaining translation and mathematics
agree with the frozen source.

## Deterministic admission

- Checker: `scripts/check_unit_026_candidate.py`.
- Checker identity: 13,906 bytes; SHA-256
  `42d3c8b669ac12ff5b29eb458c33123a04ad29e27f94acb2048d1cc72e0e92b5`.
- The checker is read-only and fails closed on the full authority identity,
  exact source-slice identity, candidate byte identity, strict UTF-8/LF shape,
  one-to-one substantive record topology, environment sequence, labels,
  references, citation keys, index streams, ordered TeX commands, protected
  inline/display/environment mathematics, controlled terminology, explicit
  correction locations, Han/Chinese-punctuation residue, and placeholders.
- Command: `python scripts/check_unit_026_candidate.py`.
- Result on 2026-08-25, in two consecutive runs: **PASS / PASS**, with
  byte-identical output.
- Reported identities and counts agree with this review: source slice 188
  records / 15,360 bytes / SHA-256 `4377d6a…f975f8`; candidate 187 records /
  19,424 bytes / SHA-256 `a3745af3…c9de87`; 72 ordered begin/end markers,
  12 labels, 24 references, 1 citation, 10 indexes, zero Han residue, and two
  mathematical-token corrections plus two bounded prose/edge-case corrections
  above (four declared corrections total).

The separate integration checker `scripts/check_unit_026_structure.py` binds
the authority, Unit 025 prefix, final Unit 026 candidate, untouched suffix,
canonical target, 374-row glossary, and all 33 exact Unit 026 delta rows. It
also invokes the pinned candidate checker twice. This review therefore proves
translation and canonical-splice integrity only; backend binding, reader
construction, build/replay, visual QA, version control, and publication belong
to the owning task's later admission sequence.
