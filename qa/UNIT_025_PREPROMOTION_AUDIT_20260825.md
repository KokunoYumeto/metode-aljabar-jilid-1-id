# Unit 025 prepromotion audit — 2026-08-25

Status: **PASS; exact canonical splice authorized within this lane.**

- Current canonical `repo/source/chapter4.tex` is still byte-identical to the
  frozen authority: 154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Authority lines 1-176 are 15,528 bytes, SHA-256
  `d88ca03645fd4c781d16907e063b06cd072ad5fbe0e48ce2149d8fdecfb76a52`.
- The terminology-refined Unit 025 candidate is 20,409 bytes, SHA-256
  `a1a60706d405f7f672b2cbcf99598911db93c1b4fa079779c7501ce4c00b7665`.
- The untouched authority suffix beginning at source line 177 is 139,216
  bytes, SHA-256
  `20e588a6d9f8361acad3deb3cdbfbb7e0d2a2495156c458bfe15897d21289b68`.
- Exact in-memory concatenation `candidate + authority suffix` yields 159,625
  bytes, 1,899 LF delimiters, SHA-256
  `e85de8011d0e05e7934d525e893ea38d18aac2f099d15380abaf757f3f168894`.
  The candidate ends with `\end{remark}` and one LF; the suffix begins directly
  with Section 4.2. No source line is duplicated or omitted.
- The patch writer normalizes the inherited source's missing terminal newline.
  Therefore the admitted canonical byte form is exactly the concatenation
  above plus one final LF: 159,626 bytes, 1,900 LF delimiters, SHA-256
  `6d2ebda2e8b291bcc0d104d00af0eea06bfb2c88b6bfa479d1c5e07147deebe1`.
  Every byte of the source suffix remains contiguous and unchanged before that
  disclosed terminal-file normalization.

The pinned candidate checker passes twice after the two terminology repairs.
The glossary has 341 unique rows and binds the Unit 025 foundational
group-theory terms. The exact promotion operation is therefore limited to
replacing the current authority prefix through line 176 with the complete
candidate while retaining the byte-identical suffix from line 177 onward.

Post-promotion admission must prove the predicted target identity, exact
candidate prefix and authority suffix, protected TeX topology, language
residue, labels/references/citations/indexes, correction provenance, reader
build and all-page visual QA, modular backend, and public-byte readback.
