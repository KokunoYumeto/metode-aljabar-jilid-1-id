# Unit 027 admission — 2026-08-25

Status: **PASS — admitted locally; publication readback is the next gate.**
Unit 027 is the complete contiguous Indonesian translation of Section 4.3 of
Wen-Wei Li, *Methods in Algebra, Volume 1*: direct and semidirect products,
internal decompositions, the dihedral example, exact sequences, group
extensions, splittings, and split extensions. Translation, mathematical
topology, terminology, correction provenance, canonical integration, reader,
component rights, modular backend, deterministic projections, clean build,
all-page visual QA, and independent final audit pass.

Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. This provenance is
separate from Wen-Wei Li's authorship and all retained human/source credits.

## Frozen source and canonical translation

- Authority: `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`,
  154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Boundary: physical lines 365–517 inclusive, 153 LF records / 10,209 bytes /
  SHA-256
  `bb7cb2d385018971fe325c417bcafdccd9e92376c02e7cb72d3af038097f8db8`.
  Line 517 is the blank section separator; lines 365–516 map one-for-one.
- Reviewed candidate:
  `build/unit-027-candidate/chapter4-products-group-extensions-id.tex`, 152
  records / 12,675 bytes / SHA-256
  `aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563`.
- Canonical target: `repo/source/chapter4.tex`, 166,211 bytes / SHA-256
  `5a4ec3ec5f420c694f7e1207f02a79c558da0f18c6c1f23969856c481f9a7420`.
  Target lines 366–517 are candidate-identical; source Section 4.4 resumes at
  target line 518.
- Controlled glossary: 383 data rows / 60,575 bytes / SHA-256
  `61e45adc844d8fd6beccf1cbb2216340913d6eb3b55cdd487817820171899f97`.
  Exactly nine Unit 027 terminology rows are admitted.

The fail-closed candidate and integration checkers pass. They preserve 28
environment pairs, eight labels, four ordinary references plus one equation
reference, 171 protected mathematics zones, 15 items, four `tikzcd` diagrams
with 30 arrows, three polygon drawings with 15 drawing commands, and six index
entries. The span contains no citations, exercises, hints, answers, solutions,
Han residue, or Section 4.4 material.

## Mathematical and language closure

Two source corrections and one translation-precision repair are explicit:

1. `O013-LI-U027-COR-001` restores `\prod_{i\in I}M_i` as the codomain in
   the direct-product universal property.
2. `O013-LI-U027-COR-002` restricts only the regular-polygon interpretation
   of `D_{2n}` to `n\geq3`; the wider algebraic construction remains intact.
3. `O013-LI-U027-TR-001` describes the action induced by a splitting as the
   restriction of an adjoint automorphism. Its restriction to `N` need not be
   an inner automorphism of `N`.

Two controlled-style normalizations use the established phrase `unsur
identitas`. They change no formula or formal topology. The nine admitted terms
include `homomorfisme proyeksi`, `produk semilangsung`, `grup dihedral`,
`produk langsung internal`, `ekstensi grup`, `ekuivalensi ekstensi grup`,
`pemecahan`, and `ekstensi terpecah`.

## Reader and visual QA

- Driver:
  `repo/source/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup.tex`,
  5,206 bytes / SHA-256
  `724ce2e32023fff81dc3f67cdf34e33557de506891d78eb2566abc4c31f8ce94`.
- Cover: `repo/source/coverpage-id-unit-027.tex`, 3,689 bytes / SHA-256
  `66e4499e39304e21fbca012bd0941c22a8af497257e7481aaa42b9c20b527b0e`.
- Reference witness: `repo/source/unit-027-crossrefs.aux`, 49 bytes / SHA-256
  `90d0014732a38f49fb82e4e9c1f446ff061ccc1dc6ce230f833e9126d1dfa49b`.
- Reader:
  `artifacts/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup-id.pdf`,
  seven pages / 97,427 bytes / SHA-256
  `8eeab2d34a745b0e5a12acc29c0c5474e9c84d1248686d743302c03859851dd7`.
- Final build log: `qa/UNIT_027_BUILD_FINAL.log`, 86,569 bytes / SHA-256
  `b18386c3273612276813fa1c9fa00a606becc3d35e980e68351f258bfc893cb4`.
- Structure/PDF evidence: 57,622 bytes / SHA-256
  `e43de32df9e1cef83da6fc1539a160de3d093afe6ebedcbf12b7bcd0264cb789`.
- Render inventory: 34,438 bytes / SHA-256
  `2f9e5b102f29b7a3480e80c1db413a547368f1638e9b669f4de7a4e9f685fd15`.
- Visual receipt: 6,180 bytes / SHA-256
  `370bf47ef7defb494ad3b227f1280f01bcfc081f1c92b0c5ef7986d4dddc95c9`.

The centered 142 mm reader uses an explicit prose scope panel rather than the
ambiguous filled/unfilled progress-block convention. Two clean builds and the
artifact yield 42 Poppler/MuPDF renders; all same-renderer C-to-D and
D-to-artifact pixels match and all outer edge bands are clear. All seven pages
were inspected in both engines. The PDF has `id-ID` metadata, three outline
entries, 30 closed destinations, ten safe `GoTo` actions, three HTTPS actions,
22 embedded fonts, and no unsafe action, form, JavaScript, embedded file, or
encryption. It is untagged, which remains a disclosed accessibility limitation.

## Modular backend

Canonical JSON:
`backend/data/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup.json`,
262,798 bytes / SHA-256
`c014e552acfa52db88c15784d4150708465faf9fe54a5fcd839d8742dec8abf4`.
It contains 364 audited UUIDv5 entities, including 304 concept-compatible
entities, and exactly represents the formal census above. Six deterministic
CSV projections contain 80 bindings, 364 entities, 16 QA events, 683
relations, four rights records, and 14 build/reader surfaces.

The dedicated validator passed repeatedly after two regenerations per run; the
shared schema/UUIDv5 validator also passes. All 80 binding occurrences across
38 live paths—including 30 line spans—match. Final backend evidence is 5,871
bytes / SHA-256
`5139e94b9cf6863d2c47887fddc51b657f04553ed7ba15e35fd082f4303e2c84`.
The final independent audit is
`qa/UNIT_027_FINAL_AUDIT_20260825.md`, 6,107 bytes / SHA-256
`7b099f3f663ca023ff696f67bf8a14f94757848e86972fb849c08a62e707f969`.

## Rights, architecture, and conclusion

Principal source text and Indonesian translation remain CC BY 4.0. The
credited `AJbook.cls` fragment remains CC BY-SA 3.0; bundled Noto fonts remain
OFL 1.1; `Lanzhou.png` remains CC BY-SA 3.0 and is unused by this reader. No
blanket license or endorsement is implied.

The final O013 architecture remains bound without restart: complete Li Volume
1 first; then Alexander Duncan's complete pinned CC BY 4.0 repository; then
only the six selected repaired CRing GFDL spans; then separately provenanced
connective/mastery material. Etingof remains reference-only.

Unit 027 is reproducible, source-bound, independently audited, and locally
admitted. The next canonical Li boundary is `chapter4.tex:518`, Section 4.4.
Zenodo checkpoint `0.6.0` remains the latest chapter-complete preservation
version through Unit 024; this single Section 4.3 unit does not justify a
duplicate preservation record.
