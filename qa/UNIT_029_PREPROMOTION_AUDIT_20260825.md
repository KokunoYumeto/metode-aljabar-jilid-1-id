# Unit 029 canonical-promotion audit — 2026-08-25

Status: **PASS; the bounded promotion completed, its idempotent replay passed,
and the canonical bytes were read back by the structure checker twice.** The
historical filename uses `PREPROMOTION` to match the lane convention; this
record binds both the preconditions and observed result.

## Exact source boundary

- Frozen authority `chapter4.tex:666-795`: 130 normalized-LF records, 8,043
  bytes, SHA-256
  `760366ac81aff9bd6170c96996ae16c29a02a93034a77f7d4c7f01485bbf3163`.
- The substantive candidate maps authority lines 666–794 one-for-one; blank
  boundary line 795 is omitted. Candidate: 129 records / 10,028 bytes /
  SHA-256
  `234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d`.
- Section 4.6 begins at authority line 796 with
  `\section{群的合成列}\label{sec:composition-series-grp}` and remains
  untranslated and outside Unit 029.

## Translation and terminology gates

- `scripts/check_unit_029_candidate.py`: 14,830 bytes, SHA-256
  `3a67accdd9cbcace31547b4284fe65b4f4ab29ebd0efd04be325d450fe6936d7`.
  Two consecutive final runs returned code 0, empty stderr, and byte-identical
  output.
- Source/language/mathematics review:
  `qa/UNIT_029_TRANSLATION_REVIEW_20260824.md`.
- Terminology audit: `qa/UNIT_029_TERMINOLOGY_AUDIT_20260825.md`, 2,144 bytes,
  SHA-256
  `a5b766779eac0726ccd0d5fae220932c9afba08953ca1eefd94785251db86627`.
- The exact five-row admitted delta is 1,030 bytes, SHA-256
  `e0e00678dc46fd8c702c17614ea2d1e1e71ee6ff622f8986097dfd296e759ecc`;
  it extends 408 unique rows to 413 unique rows without collision.

The candidate preserves 25 paired environments / 50 ordered markers, six
labels, 16 references, one `Lang02` citation with locator, two indexes, and
211 protected mathematical zones. It contains no diagram, exercise, hint,
answer, or solution environment and no Han residue. Exactly one protected
`\text{...}` fragment is localized at authority line 746 (`子集` →
`subhimpunan`). All requested prose refinements retain the source's ordered
math-zone and TeX-command topology. A final rendered-page audit removed the
authority-absent period after the Sylow-II display because it appeared as a
standalone left-margin dot; the checker now explicitly rejects that regression.

No mathematical source correction is required or declared for Unit 029.

## Bounded mutation and readback

- Pre-Unit-029 canonical Chapter 4: 168,678 bytes, SHA-256
  `33ab68b169fad0f45815cbfa528e03eaa12efbb2add9a4599049a9823c86b0b3`.
- Untouched authority suffix from line 796: 95,054 bytes, SHA-256
  `79bffb7c169bc99af3e7b4354cba883ae036abb6287421099dc5d930f06895d1`.
- Promotion script: `scripts/promote_unit_029.py`, 8,634 bytes, SHA-256
  `825c157ddae9503c387803ba7a5eef6e8ca8c5729ae7c9ef1e6f49afe6dbafa0`.
  It is fail-closed, idempotent, and mutates only canonical Chapter 4 and the
  controlled glossary.
- Observed canonical Chapter 4: exact Unit 025–029 prefix plus untouched
  authority suffix from line 796 and one terminal LF; 1,896 records / 170,663
  bytes / SHA-256
  `8cbd766360a3c7cd214876e297c45de3b8938daa9a3623192efdf1d6ebc766fc`.
  Unit 029 occupies target lines 665–793 exactly; untranslated Section 4.6 is
  the exact sentinel at target line 794.
- Observed glossary: 413 data rows / 65,573 bytes / SHA-256
  `adc2152dc08131e0098ac159137378aa50cd7b54cb282a8e713899662d335ca3`;
  its final five rows equal the delta record-for-record.
- Read-only integration checker: `scripts/check_unit_029_structure.py`, 9,674
  bytes, SHA-256
  `64f422aafc03b4b2d8ab0c5995bb3e8ff420efdddc3f110c769c20ff827b44a7`.
  Two final runs returned **PASS** and independently reran the candidate
  checker twice per run. A second promotion invocation returned
  `ALREADY COMPLETE` without changing bytes.

This audit admits canonical source and terminology integration only. Reader,
backend, build/visual QA, README, Git, and public-byte readback are downstream
gates owned by the parent task.
