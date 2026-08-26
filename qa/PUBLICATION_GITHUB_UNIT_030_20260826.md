# GitHub publication receipt — Unit 030 — 2026-08-26

Status: **PASS.** The complete Unit 030 content boundary is public. Every path
changed by the content commit was anonymously read back from its immutable
GitHub URL and matched the committed blob byte-for-byte. Public `main`
resolved to the content commit before and after every fetch.

## Public identity

- Repository: <https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id>
- Branch: `main`
- Content commit:
  `cff3f5537a86fd2feb21609f2c47b533b51c99bf`
- Parent: `bc55f1f527529718a41978b880666b6a0fa96f32`
- Tree: `39cca775954c9d2e097d3bdd413f7c03cf9719a6`
- Commit page:
  <https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id/commit/cff3f5537a86fd2feb21609f2c47b533b51c99bf>

## Anonymous byte readback

The verifier used credential-disabled anonymous `git ls-remote` for the
public `main` ref and immutable `raw.githubusercontent.com` URLs for every
changed path. It sent no credential or `Authorization` header.

All 49 changed paths, totaling 3,068,734 public bytes, returned HTTP 200 and
matched the exact local committed blobs. The public branch ref resolved to
`cff3f5537a86fd2feb21609f2c47b533b51c99bf` before and after all immutable
path fetches.

Complete per-path evidence is
`qa/PUBLICATION_GITHUB_UNIT_030_CONTENT_READBACK.json`, 21,524 bytes, SHA-256
`350935011c75afe1c091c4f0edc06029941acb0c299e7ac624352986cdbb6c22`.
The credential-free verifier is
`scripts/verify_unit_030_github_readback.py`, 6,501 bytes, SHA-256
`f27c3f5cf8df0ee179643faa874dd258a105139f751cfeb7554f7be62787fc6d`.
The inventory records all 49 immutable URLs, HTTP status, byte counts, hashes,
and `matches_committed_blob: true`, with `all_match: true` and stable public
`main` before and after the transaction.

## Published admission boundary

- Authority: `chapter4.tex:796-935`, complete Section 4.6; 140 normalized-LF
  records and 7,981 bytes, SHA-256
  `7803452c4285c57e419a2cb2a288b3733975555fafd6b7a88c5732da369220c1`.
  Line 935 is the excluded blank boundary record; Section 4.7 begins at
  authority line 936.
- Reviewed target candidate:
  `build/unit-030-candidate/chapter4-group-composition-series-id.tex`, 139
  substantive records, 10,044 bytes, SHA-256
  `7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b`.
- Canonical target: `repo/source/chapter4.tex`, 172,726 bytes, SHA-256
  `245a891930cefb1c18cbd1208386ba5131c56b8b5930510c329577eeeb96cddc`.
- Reader: `artifacts/unit-030-bab-4-deret-komposisi-grup-id.pdf`, seven pages,
  91,961 bytes, SHA-256
  `43ad2ffa2516f2f4394bcb82ad2e585f21c1e9e36a87870f4406a78597f18d74`.
- Backend: `backend/data/unit-030-bab-4-deret-komposisi-grup.json`, 179,924
  bytes, SHA-256
  `1dae77cebf984b8a1dfad0a3d90714d3b4f69c0632042cea768939eb1a77f806`.
- Backend validation:
  `qa/unit-030-evidence/backend-validation.json`, 5,716 bytes, SHA-256
  `f175a22f2b8d9df56038b880b332d3a862681d5da7cea31cb2313af501753a50`.
- Local admission receipt: `qa/UNIT_030_ADMISSION_20260826.md`, 11,879 bytes,
  SHA-256
  `9ea189ac1cb7997861dc7a6af6c993ecb5fe6293610185e6f6ae8b98889680c0`.
- Independent final audit: `qa/UNIT_030_FINAL_AUDIT_20260826.md`, 4,610
  bytes, SHA-256
  `c752b8eb28c4f2667f501b4b0298e521cd01752724139b947029f8f6f1032baf`.
- Structural/PDF evidence:
  `qa/unit-030-evidence/structure-and-pdf-qa.json`, 57,377 bytes, SHA-256
  `5b11c997ca331611871e22928f560f89757651053803bffc91ac1d118b89be02`.
- All-page render inventory:
  `qa/unit-030-evidence/render-hash-inventory.json`, 34,392 bytes, SHA-256
  `2d77180e791121c76abbf097936bc69036113c1bebb3232346897619d4f9b131`.

The public boundary includes the canonical source and reader driver, PDF
artifact, six deterministic CSV projections, 421-row terminology control,
non-flattened component rights, sanitized final build log, dual-renderer
all-page evidence, admission and independent-audit receipts, and the exact
generators, checkers, validator, and public-readback verifier used by the
admitted lane.

The admitted mathematical surface preserves 26 paired environments, ten
labels, nine references, six index entries, 88 protected mathematical zones,
and six `tikzcd` diagrams with 23 arrows. It contains no exercise, hint,
answer, solution, or citation surface. One explicitly provenanced correction,
`O013-LI-U030-COR-001`, restores the uniquely forced missing `\supset` at
authority line 895 / target line 893. Two Indonesian diagram-text
localizations preserve the diagram topology. Han residue and placeholders are
zero.

The two independent seven-page builds differ by one byte due to volatile font
subset tags; normalized structure, extracted text, and same-renderer decoded
pixels agree. Poppler and MuPDF rendered all seven pages for both builds and
the release artifact. All 42 page-edge checks have zero ink, and the final
reader is byte-identical to clean build J. The PDF is untagged, so no tagged
accessibility claim is made.

All source, structural, mathematical, terminology, build, PDF, dual-renderer
visual, backend, rights, privacy, and public-byte gates pass. Principal text
and translation are CC BY 4.0; the credited `AJbook.cls` fragment retains CC
BY-SA 3.0, bundled fonts retain OFL 1.1, and unused `Lanzhou.png` retains CC
BY-SA 3.0. The aggregate closure is not described as unqualified CC BY 4.0.
The derivative is independent and non-endorsed. Production provenance is
recorded separately as `OpenAI Codex gpt-5.6-sol, Ultra`.

This release advances the canonical Li cursor to `chapter4.tex:936`, the
beginning of Section 4.7. It does **not** claim that Chapter 4, Li Volume 1, or
the O013/D70 Graduate Algebra corpus is complete. Subsequent units remain
subject to their own source, translation, backend, build, QA, publication, and
anonymous-readback gates.
