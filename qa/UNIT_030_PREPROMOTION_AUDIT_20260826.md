# Unit 030 pre-promotion audit — 2026-08-26

Status: PASS. The pinned authority is `chapter4.tex:796-935` (140 LF records,
7,981 bytes, SHA-256
`7803452c4285c57e419a2cb2a288b3733975555fafd6b7a88c5732da369220c1`). Line
935 is the blank boundary; Section 4.7 begins at line 936. The reviewed
candidate contains the 139 substantive records from lines 796-934 (10,044
bytes, SHA-256
`7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b`) and is
promoted byte-for-byte to canonical target lines 794-932. The canonical
Chapter 4 identity is 172,726 bytes, SHA-256
`245a891930cefb1c18cbd1208386ba5131c56b8b5930510c329577eeeb96cddc`.

The splice preserves the admitted Units 025-029 prefix, omits only the
authority blank boundary record, and leaves the untranslated Section 4.7
suffix untouched. The eight-row terminology delta is appended without
rewriting the previous 413 rows, producing the 421-row glossary identity
`2fdad27f02b31ea2f29f9aecd8ef2e015a456b02636c402c3e985e5e0a5d7991`.

The candidate checker and canonical structure checker were each run twice
with identical output. The sole declared source correction restores the
missing `\supset` at authority line 895 (target line 893), which is forced by
the surrounding chain topology. Two diagram-label localizations at authority
lines 836 and 839 map to target lines 834 and 837. No source-order content was
added beyond those explicitly provenanced repairs.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**, acting on the
user's instruction. Source-author and human-contributor credits remain intact.
