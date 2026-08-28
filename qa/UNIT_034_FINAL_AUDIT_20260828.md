# Unit 034 independent source-and-reader final audit - 2026-08-28

Status: **PASS WITH WARNINGS; zero actionable source, reader, or backend
defects.** This final local audit binds the translation, reader, and modular
backend surfaces. It does not claim publication.

## Boundary, translation, and correction

The frozen authority is `chapter4.tex:1609-1744`, 136 normalized-LF records,
15,005 bytes, SHA-256
`9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab`.
Line 1744 is blank and Section 4.11 begins at line 1745. The final candidate
contains 135 substantive records, 19,019 bytes, SHA-256
`8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62`.
Canonical `repo/source/chapter4.tex` is 189,935 bytes, SHA-256
`37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569`;
target lines 1604-1738 are byte-identical to the candidate, followed by the
blank boundary and untouched Section 4.11 sentinel.

Repeated checks preserve 25 paired TeX environments, 11 labels, 16
references, six citation occurrences over `FL14` and `Xiong`, six index
entries, 276 protected mathematics zones, five list items, and one diagram
with 12 arrows. The span contains no exercises, hints, answers, or solutions,
and none were invented. Thirty-seven terminology rows are admitted; the
513-row glossary is 82,586 bytes, SHA-256
`59e66d5acf8f8e792327730c01a236d3bc7570b9f71a200b9a6d7b9a71fa3955`.

`O013-LI-U034-COR-001` changes the compatible-family index in the p-adic
integer example from `i >= 1` to `i >= 0`. This is forced by the same source
sentence's declared index set `I = Z_{>=0}`, the definition
`H_i = p^{i+1}Z`, the quotient `Z/p^{i+1}Z`, and the source's own later
convention. Nine protected
mathematical-text fragments, three citation locators, and six index targets
are localized without changing commands, keys, or occurrence order.

`O013-LI-U034-REFLOW-001` changes only one display's line breaking. Its exact
normalization recovers the same ordered mathematical zones and removes the
measured 26.11896 pt overflow. It is recorded as a target-only digital reflow,
not as an upstream mathematical correction.

## Reader, PDF, and visual evidence

The final reader has nine pages, 136,702 bytes, SHA-256
`e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272`.
Clean build I is 136,700 bytes, SHA-256
`970402b3ab3e510c2f72c44723528616eb3456020433ed9cf7b7cce2d56ce83a`;
clean build J is byte-identical to the reader. All 54 Poppler/MuPDF renders are
edge-clear, and all defined same-renderer build/build/artifact comparisons are
decoded-pixel-identical. Every page was inspected at full readability,
including the reflowed display on page 5.

Both builds are derived from the exact hash-gated canonical target span at
lines 1604-1738. The build script materializes that span locally and proves it
byte-identical to the admitted candidate before the driver reads it, so the
admitted build closure is canonical rather than candidate-path dependent.

No clipping, collision, missing glyph, tofu, broken formula, broken diagram,
edge contact, or unintended blank page remains. The final unencrypted PDF 1.7
has `/Lang id-ID`, exact metadata, four outline entries, 39 named
destinations, 20 internal actions, five safe URI actions, and 31 embedded font
objects. It contains no unsafe active payload. The sanitized log records zero
errors, unresolved references/citations, missing characters, empty targets,
overfull boxes, and underfull boxes.

The warnings are bounded: the PDF is untagged, so no tagged-accessibility
claim is made; mathematical-font text extraction limitations are disclosed;
and nonfatal toolchain advisories remain in the sanitized evidence. Neither
renderer exhibits a corresponding visual defect.

Controlling evidence:

- `qa/UNIT_034_VISUAL_QA_20260827.md`, 5,015 bytes, SHA-256
  `ceefb6b40c21b99ca4a673e32223323dcdb19373dbcdcf6822a79c8e0111a2a6`;
- `qa/unit-034-evidence/structure-and-pdf-qa.json`, 31,319 bytes, SHA-256
  `4c37064eaa05cfcb0b70718b27c2213a36e1dfa0eda6bf098fd92c06fd641e2d`;
- `qa/unit-034-evidence/render-hash-inventory.json`, 41,802 bytes, SHA-256
  `c1e54d2d0d2527542b8b0f575614d8cc27d7c7238a3ea859074d271d9945c3ba`;
- `qa/UNIT_034_BUILD_FINAL.log`, 77,357 bytes, SHA-256
  `bb4b9b6d7de341239eb137173b7dc774f4774298cccf534645cb2561ca9a779d`.

## Backend evidence

The canonical backend is 341,684 bytes, SHA-256
`c475108a1d6ed5d4c2084adc00c122e1a3294b5d44e6af3e302d39a06d7a6c35`.
Its 419 concept-compatible records and 482 audited UUIDv5 entities preserve 82
binding occurrences over 44 live paths and 18 line spans. Twenty-two ordered
QA events distinguish source correction, protected-text/citation/index
localizations, terminology control, target-only display reflow, cross-unit
reference isolation, reader evidence, and production provenance. Six CSV
projections reproduce the JSON exactly.

`qa/unit-034-evidence/backend-validation.json` is 6,315 bytes, SHA-256
`41e019eaca9e2af1363b1ed573817e7d08ae2c895547fb57153ffb41c98a2eaf`.
The dedicated validator regenerates the admitted JSON/CSV outputs twice,
requires both generations to be byte-identical, then runs shared schema
validation, UUID/reference/order/hash checks, JSON/CSV round-trip validation,
and candidate/structure replay. The shared validator does not mutate the
regenerated outputs. The receipt binds the exact generator, dedicated
validator, schema, and shared-validator identities.

## Rights, provenance, and bounded verdict

Principal text and translation remain CC BY 4.0; the credited AJbook fragment
remains CC BY-SA 3.0; bundled Noto fonts remain OFL 1.1; Fandol 0.3 remains
GPLv3 with its document-embedding font exception; unused `Lanzhou.png` remains
CC BY-SA 3.0. Source attribution, component rights,
independent-derivative status, and non-endorsement are preserved.

The separate Fandol rights record binds official CTAN package 0.3 at
26,688,406 bytes / SHA-256
`9278f01b417ded5766d98c3937192a1a6a2c73a5e94a3493fdfc932b2a55005a`,
its unmodified GPLv3-plus-font-exception `COPYING`, package README, build font
identities, font setup, reader, and embedded-font evidence.

Production and review provenance is **OpenAI Codex gpt-5.6-sol, Ultra**,
acting on the user's instruction; it does not replace source-author or human
credits.

Verdict: Unit 034's source boundary, translation, mathematics, TeX topology,
terminology, canonical integration, reader, visual/PDF surfaces, modular
backend, provenance, and component-rights statements are mutually bound and
pass. Git publication, public-byte readback, and cursor transition remain
pending and are outside this local verdict. This does not claim that Chapter
4, Li Volume 1, or O013/D70 is complete.
