# Unit 025 — source and translation review — 2026-08-24

Status: **PASS as an isolated candidate; not yet integrated, built, backend-admitted, or published.**

## Frozen boundary and identities

- Upstream authority: Wen-Wei Li, *Methods in Algebra*, Volume 1, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`.
- Frozen source file:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`.
- Full source file: 1,898 LF records, 154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Selected source slice: physical source lines 1–176 inclusive, 15,528 bytes,
  SHA-256
  `d88ca03645fd4c781d16907e063b06cd072ad5fbe0e48ce2149d8fdecfb76a52`.
- Natural boundary: the slice contains the Chapter 4 opening and all of §4.1,
  “Semigroups, Monoids, and Groups,” including its final remark. Source line
  177 begins §4.2, “Homomorphisms and Quotient Groups.”
- Indonesian candidate:
  `build/unit-025-candidate/chapter4-group-basics-id.tex`, 178 LF records,
  20,409 bytes, SHA-256
  `a1a60706d405f7f672b2cbcf99598911db93c1b4fa079779c7501ce4c00b7665`.
- Fail-closed checker: `scripts/check_unit_025_candidate.py`, 12,628 bytes,
  SHA-256
  `0ac89e89fb0218bbd0714c3ffe6a19391463fd932230707c01dd21b096e596bc`.

This is the first coherent source-order unit after the complete Chapter 3
candidates. It is intentionally not extended into §4.2 merely to enlarge the
chunk.

## Coverage and structural preservation

The candidate translates the complete selected prose, including the chapter
orientation and reading guidance, binary operations, semigroups, monoids,
groups, invertibility, basic examples, subgroups, normal and simple groups,
generated and cyclic groups, cosets, Lagrange's theorem, centers,
centralizers, and normalizers.

The checker binds both the full authority file and exact slice before checking
the candidate. It reports:

- 27 ordered `begin`/`end` environment pairs;
- 10 labels and 11 references, with their keys and order unchanged;
- 3 citations, with their keys unchanged;
- 25 index entries, preserving the index-option topology;
- 24 item markers;
- 280 inline or display mathematical spans;
- 7 definitions, 4 examples, 1 lemma, 1 proposition, 1 remark, 2 proofs,
  and 1 convention;
- 0 exercises, 0 hints, and 0 TikZ/tikzcd diagrams in this source slice;
- 0 Han characters in the Indonesian candidate.

Formula inventory is exact after whitespace normalization and replacement of
language-bearing `\text{...}` bodies, except for the one explicitly authorized
source correction below. The candidate hash is itself pinned, so the
inventory comparison cannot silently admit later prose or formula changes.
Brace balance, environment nesting, strict UTF-8, LF-only encoding, terminal
newline, rights text, model provenance, correction marker, and non-endorsement
are also fail-closed checks.

Validation command and result:

```text
python scripts/check_unit_025_candidate.py
UNIT 025 CANDIDATE CHECK: PASS
```

## Translation and terminology review

The prose is formal id-ID rather than a word-for-word Chinese calque. Formula
order and TeX topology remain intact where Indonesian syntax permits; repeated
inline symbols may move within the same translated sentence, but the checker
requires the complete mathematical-span inventory.

Existing controlled choices used without alteration include `grup`,
`himpunan`, `medan`, `kardinal`, `invertibel`, `himpunan tunggal`, `bijeksi`,
`gabungan saling lepas`, `produk langsung`, `grup bebas`, `grup kepang`,
`grup abelian yang dibangkitkan secara berhingga`, `hasil kali kardinal`, and
the provisional Chapter 10 choice `kompletisasi`. The global order-theory term
`urutan` is not misapplied to group theory: group and element order are
rendered as `orde`.

The following candidate-local choices are coherent but are not written into
the controlled glossary by this task: `semigrup`, `monoid`, `operasi biner`,
`unsur identitas`, `hukum pembatalan kiri/kanan`, `grup unit`, `subgrup`,
`subgrup normal`, `grup sederhana`, `grup siklik`, `koset`, `pusat`,
`sentralisator`, `normalisator`, `grup simetris`, `grup selang-seling`,
`grup permutasi`, and `grup linear umum`. They should be adjudicated and then
added in one controlled terminology update when Unit 025 is integrated.

The pre-admission terminology pass replaced the earlier candidate-local form
`grup alternasi` with `grup selang-seling`. The latter is directly attested by
the official 2008 Indonesian mathematics glossary for *alternating group* and
already used by the independently reviewed Unit 033 candidate. This is a
terminology-consistency refinement, not a source-content correction.

The same pass replaced `hukum kanselasi` with `hukum pembatalan` at all four
occurrences across three physical lines. The official glossary directly attests *cancellation law* as
`hukum pembatalan`, and admitted Chapter 2 already uses that form. The text
retains `unsur identitas` while giving the official synonym `unsur satuan` at
its defining occurrence; it retains corpus-wide `grup simetris` and the
group-theoretic sense `orde`, rather than applying the order-theory term
`urutan` or the glossary's contextually unsuitable `tingkat`.

No untranslated Chinese prose, source-language punctuation, placeholder,
exercise, hint, label, reference, citation, or index entry was dropped.

## Explicit source correction

`O013-LI-U025-COR-001` is one high-confidence mathematical-variable repair:

- source location: `chapter4.tex:115`, the example asserting that the additive
  group of integers is cyclic;
- source expression: `$H \subset G$`;
- candidate expression: `$H \subset \Z$`;
- reason: the example's ambient group is explicitly `\Z`, no `G` is introduced
  in that example, and the asserted classification
  `$H=n\Z=\{m\in\Z:n\mid m\}$` is specifically the classification of
  subgroups of the integers;
- disclosure: the candidate carries the correction ID immediately before the
  changed sentence, and the checker permits exactly one decrement of the
  `$H\subset G$` math-span inventory and exactly one increment of
  `$H\subset\Z$`.

No other high-confidence mathematical source correction was found in lines
1–176. No upstream contact was made.

## Rights, attribution, and provenance

The selected principal-text source states CC BY 4.0 and credits Wen-Wei Li.
The candidate preserves that notice and URL. This isolated slice does not
contain the separately licensed image, class-fragment, or font components, and
this review makes no blanket license claim about the complete build closure.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. This independently
produced translation is not endorsed by Wen-Wei Li or by any terminology
witness or other human source. Authorship, translation provenance, and
non-endorsement remain distinct.

## Handoff boundary

The candidate is ready for the owning task to integrate after the prior
source-order units. Integration still requires a controlled glossary decision,
canonical range replacement, isolated reader build, source/math/language QA,
all-page visual QA, modular backend generation and validation, durable cursor
updates, and publication readback. None of those later gates is claimed here.
