# GitHub publication receipt — Unit 029 — 2026-08-26

Status: **PASS.** The complete Unit 029 content boundary is public. Every path
changed by the content commit was anonymously read back from its immutable
GitHub URL and matched the committed blob byte-for-byte. Public `main`
resolved to the content commit before and after every fetch.

## Public identity

- Repository: <https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id>
- Branch: `main`
- Content commit:
  `e9bc26191e422ab055ead3cb39fedbc228237b23`
- Parent: `360dd1556e722bf89dff7fcad3ac36f08325a2b3`
- Tree: `c4226d550b9ff3266045d76a7928b2351cbd6d53`
- Commit page:
  <https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id/commit/e9bc26191e422ab055ead3cb39fedbc228237b23>

## Anonymous byte readback

The verifier used credential-disabled anonymous `git ls-remote` for the
public `main` ref and immutable `raw.githubusercontent.com` URLs for every
changed path. It sent no credential or `Authorization` header.

All 44 changed paths, totaling 3,398,169 public bytes, returned HTTP 200 and
matched the exact local committed blobs. The public branch ref resolved to
`e9bc26191e422ab055ead3cb39fedbc228237b23` before and after all immutable
path fetches.

Complete per-path evidence is
`qa/PUBLICATION_GITHUB_UNIT_029_CONTENT_READBACK.json`, 19,300 bytes, SHA-256
`e5ecc408710f0e61263baf3d9858807ff138278339f839cd93ef41bb3bd64540`.
The credential-free verifier is
`scripts/verify_unit_029_github_readback.py`, 6,501 bytes, SHA-256
`802b01eb19246303789c4f076d7733ef698da221131f1f680e8a0d05fc29ec19`;
it takes the immutable commit, expected parent, path count, and byte count as
explicit fail-closed arguments.

## Published admission boundary

- Authority: `chapter4.tex:666-795`, complete Section 4.5; boundary-inclusive
  source span 8,043 bytes, SHA-256
  `760366ac81aff9bd6170c96996ae16c29a02a93034a77f7d4c7f01485bbf3163`.
  Line 795 is the omitted blank separator; substantive lines 666-794 map
  one-for-one to the 129-record target span.
- Canonical target: `repo/source/chapter4.tex`, 170,663 bytes, SHA-256
  `8cbd766360a3c7cd214876e297c45de3b8938daa9a3623192efdf1d6ebc766fc`.
- Reader: `artifacts/unit-029-bab-4-teorema-sylow-id.pdf`, six pages,
  99,689 bytes, SHA-256
  `64fde52948525fc5b159f76fbed6571c150e4184a87e47e715164aec135e5012`.
- Backend: `backend/data/unit-029-bab-4-teorema-sylow.json`, 243,849 bytes,
  SHA-256
  `918e1f3cbf30ec950bb83dc6427f63190dde41c766cbc38d5d349728ee92cced`.
- Local admission receipt: `qa/UNIT_029_ADMISSION_20260826.md`, 7,912 bytes,
  SHA-256
  `e76ca9ddb8b1cb07a049ee300636a23b3a02bf038a9979ef23e5ff2eaf532204`.
- Independent final audit: `qa/UNIT_029_FINAL_AUDIT_20260826.md`, 10,744
  bytes, SHA-256
  `906533d079f13ae6a3de4cc168dc1b3013d4121fce63c75782537a9875a824fc`.

The public boundary includes both final-renderer artifact page sets,
structured PDF and render inventories, backend validation evidence, sanitized
final build log, canonical source and reader driver, PDF artifact, six
deterministic CSV projections, terminology, non-flattened rights, admission
and independent-audit receipts, and the source-bound generators and validators
used by the admitted lane. There is no mathematical source correction in this
unit. The sole Indonesian text-in-math localization is typed separately. The
centered 142 mm reflow keeps the bibliography and two-entry run-in index on a
readable sixth page; it does not shrink the main prose.

All source, structural, mathematical, terminology, build, PDF, dual-renderer
all-page visual, backend, rights, privacy, and public-byte gates pass. The PDF
is untagged, and the installed Poppler lacks its optional Adobe-GB1 mapping;
these limitations are disclosed and no tagged-accessibility claim is made.

This release advances the canonical Li cursor to `chapter4.tex:796`, the
beginning of Section 4.6 and Unit 030. It does not claim that Chapter 4, Li
Volume 1, or the O013 composite course is finished. Zenodo remains at the
nonduplicative `0.6.0` checkpoint through complete Chapter 3; this additional
partial Chapter 4 unit does not create a duplicate preservation version.

Wen-Wei Li remains the source author. Principal text and translation are CC BY
4.0; the credited `AJbook.cls` fragment and `Lanzhou.png` retain CC BY-SA 3.0,
and bundled fonts retain OFL 1.1. `Lanzhou.png` is not used by this reader. The
derivative is independent and non-endorsed. Production provenance is recorded
separately as `OpenAI Codex gpt-5.6-sol, Ultra`.
