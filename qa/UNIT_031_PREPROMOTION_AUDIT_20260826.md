# Unit 031 pre-promotion audit — 2026-08-26

Status: PASS. The pinned authority is `chapter4.tex:936-1107` (172 LF
records, 16,048 bytes, SHA-256
`647d22446e75cde39b7b9f53d6658f39de78c5d773d51d6f446d651e1734967b`).
Line 1107 is the blank boundary; Section 4.8 begins at line 1108. The reviewed
candidate contains the 171 substantive records from lines 936-1106 (19,855
bytes, SHA-256
`6bc4b1f7dd6cde6673915eba75cdf96cca6e8312d060d1fda0da25cb7073ee81`)
and is promoted byte-for-byte to canonical target lines 933-1103. The
canonical Chapter 4 identity is 176,533 bytes, SHA-256
`440ed304a808c687d2e431eff1dbdbe0fe01458d7f8c82b47f515659307cf28f`.
The untranslated Section 4.8 sentinel now begins at target line 1104.

The splice preserves the admitted Units 025-030 prefix, omits only the
authority blank boundary record, and leaves the authority suffix beginning at
line 1108 untouched. Before the splice, the canonical authority mirror occupied
target lines 933-1103, its blank boundary was line 1104, and the Section 4.8
sentinel was line 1105. The fourteen-row terminology delta was already the
exact glossary tail and remained byte-identical throughout promotion; the
result has 435 controlled rows.

The current fail-closed candidate checker is 16,303 bytes, SHA-256
`64bb71b1ca1a301ab341dbf5ac6a25601663507df2c93a5028bc63cb1d64beb1`.
The canonical structure checker is 10,542 bytes, SHA-256
`933d1d12f220ec09346a62e1c308ffd68c3fe3d0db550a760b42c792cbec8f83`.
Both return the same PASS record on two independent runs; each structure run
also executes the pinned candidate checker twice and requires byte-identical
output.

The sole declared proof repair is at authority line 1016 (target line 1013):
it makes explicit that induced composition factors may be trivial and that
repeated terms are removed, after which the remaining factors have prime
cyclic order. This supplies the omitted justification in the subgroup and
quotient argument without changing any formula, identifier, or theorem claim.
The eight protected-text localizations occur at authority lines 1014, 1061,
1097, and 1098, mapping to target lines 1011, 1058, 1094, and 1095. No other
source-order content was added or removed.

One separately declared digital reflow occurs at authority line 1061 /
candidate line 126 / target line 1058. A display break is inserted after the
term containing only $q$, splitting the four-term right-hand side into two
readable rows. The equality, plus signs, and all four terms remain present and
ordered. This corrects the measured 42.13312 pt overfull line; it is a digital
layout operation, not a source correction, proof repair, or terminology
change. Candidate and canonical span contain the identical five-byte delta.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**, acting on the
user's instruction. Source-author and human-contributor credits remain intact.
