# Unit 032 pre-promotion audit — 2026-08-26

Status: **PASS**. The pinned authority is `chapter4.tex:1108-1388` (281 LF
records, 22,547 bytes, SHA-256
`5a7083cd89d13e776bbf94189f7f96f5d976cd962cba7a8d4c6b2453bd59c8af`).
Line 1388 is the blank boundary; Section 4.9 begins at line 1389. The reviewed
candidate contains the 280 substantive records derived from lines 1108-1387
(27,910 bytes, SHA-256
`28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc`)
and is promoted byte-for-byte to canonical target lines 1104-1383. The
canonical Chapter 4 identity is 181,896 bytes, SHA-256
`4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680`.
The untranslated Section 4.9 sentinel begins at target line 1384.

The splice preserves the admitted Units 025-031 prefix, omits only the
authority blank boundary record, and leaves the authority suffix beginning at
line 1389 untouched. The exact 30-row terminology delta is the live glossary
tail; the controlled glossary now contains 465 data rows and is 74,335 bytes,
SHA-256
`bb58d18ad5802c5c2159db092f0fc322761f8f9559ea7efd3789ab8d7317e582`.

The fail-closed candidate checker is 18,668 bytes, SHA-256
`318a57bf22d50baef5102ebc07bb9fd83943682b44d01dac4de5150e770a2cc0`.
The canonical structure checker passes and binds 1,893 target records, the
exact target span, next-section sentinel, glossary, and terminology delta.
Together the gates preserve 52 paired environments / 104 ordered markers, 10
labels, 20 references, six citations, seven indexes, 367 protected
mathematical zones, 11 diagrams, 28 arrows, and eight drawing commands. This
unit contains no exercise, hint, answer, or solution environment.

Two high-confidence source corrections are explicit: the normal-closure
endpoint at authority line 1335 is repaired from `w_n` to the relation count
`w_m`, and the misspelled author name `R.\ Guranlnick` at authority line 1345
is repaired to `R.\ Guralnick`. Thirteen protected `\text{...}` fragments and
four citation locators are localized without changing their surrounding
mathematics or bibliography keys.

Two separately declared digital reflows split the finite-support set-builder
displays into `aligned` rows. They preserve set membership, quantifiers,
finite-support conditions, and term order while removing measured 22.16992 pt
and 27.03485 pt overfull lines. The reflows add two balanced environment pairs
and six balanced raw-brace pairs; normalized mathematical zones remain
identical. They are layout operations, not source corrections.

The 13-page reader is 149,624 bytes, SHA-256
`904330916e20f0782b6464cb85e07001851940f4adf153f6592cd34087dbadbf`.
Two clean builds are semantically and pixel-identical in both Poppler and
MuPDF. Metadata, `/Lang id-ID`, outline, destinations, safe links, embedded
fonts, extraction, and every page pass. Logs contain zero errors, unresolved
references/citations, missing characters, empty targets, and overfull boxes.
Exactly three underfull hboxes were inspected and are non-actionable. The PDF
is untagged, so no tagged-accessibility claim is made.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**, acting on the
user's instruction. Source-author and human-contributor credits remain intact.
