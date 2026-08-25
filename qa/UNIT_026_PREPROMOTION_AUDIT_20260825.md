# Unit 026 prepromotion audit — 2026-08-25

Status: **PASS; the predicted exact splice and terminology append match the
promoted canonical readback byte for byte.**

## Frozen inputs

- Complete authority `chapter4.tex`: 154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`;
  1,898 records and no terminal LF.
- Authority lines 177–364: 15,360 bytes, SHA-256
  `4377d6a31512cf3e2a56f4e8e1c3417b62ff1a6468eb85629c8d9867a4f975f8`.
  Line 364 is a boundary-only blank record.
- Already admitted Unit 025 prefix: 20,464 bytes, 178 target records, SHA-256
  `5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a`.
- Final Unit 026 candidate: 19,424 bytes, 187 target records, SHA-256
  `a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87`.
- Untouched authority suffix beginning at source line 365: 123,856 bytes,
  1,534 records, SHA-256
  `377766774741a5a3e13776bf59c09780b18ee6dd08c42bdd6282335847a060f1`.

## Exact target construction

The only admitted construction is:

`Unit 025 bytes + Unit 026 bytes + authority bytes from line 365 + one terminal LF`.

That construction yields 163,745 bytes, 1,899 target records, SHA-256
`fc3fd6ef470d41f146456bfc889eb7c7ec84bb48890f1b23f18e51a195e7d463`.
The promoted `repo/source/chapter4.tex` has exactly that identity and is exactly
equal to the constructed byte sequence. Its mapping is:

- target lines 1–178: exact Unit 025 prefix;
- target lines 179–365: exact complete Unit 026 candidate, mapping one-for-one
  to substantive authority lines 177–363;
- authority line 364: deliberately omitted because it is only the blank
  boundary record;
- target line 366 onward: exact authority source line 365 onward; and
- file end: one disclosed terminal-LF normalization, with no other suffix-byte
  change.

The next source-order production boundary therefore remains authority line 365,
Section 4.3, which is still Chinese at canonical target line 366. No source
section, formula, identifier, or substantive record is duplicated or skipped.

## Terminology append

The controlled glossary before Unit 026 had 341 data rows, 51,472 bytes, and
SHA-256
`3ed2a7a30aa06e9e574e36b237bf13ab6cec6779703ce91bc3238a107fe526b1`.
The reviewed delta has 33 data rows, 7,238 bytes including its independent CSV
header, and SHA-256
`29da42f631cb8290e54335142e589c71939040e6f874a0e7f026b9d70caad408`.
Its 33 data-row bytes total 7,186 bytes. The promoted controlled glossary is
exactly the old 51,472-byte file followed by those 7,186 bytes: 374 unique data
rows, 58,658 bytes, SHA-256
`5ecccbbdbe99ce3dbe05baf42088c401e261663432d1116abcab66d2165abe17`.
No prior terminology row was rewritten or shadowed.

## Deterministic gates

The pinned candidate checker, `scripts/check_unit_026_candidate.py`, is 13,906
bytes, SHA-256
`42d3c8b669ac12ff5b29eb458c33123a04ad29e27f94acb2048d1cc72e0e92b5`.
It passes twice with identical output and reports 188 authority-slice records,
187 candidate records, 72 environment markers, 12 labels, 24 references, one
citation, ten indexes, zero Han residue, and four declared source corrections.

The integration checker, `scripts/check_unit_026_structure.py`, independently
pins every identity above; verifies the exact target-line mapping and suffix
continuity; checks all 374 glossary rows and all 33 exact delta mappings; and
executes the candidate checker twice. Result: **PASS**.

This gate admits the canonical source splice and terminology closure. It does
not claim completion of the Unit 026 reader, modular backend, build/replay,
visual QA, Git publication, or public-byte readback; those remain the owning
task's next production gates.
