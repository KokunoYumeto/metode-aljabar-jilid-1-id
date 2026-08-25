# GitHub publication receipt - Unit 024 - 2026-08-25

Status: **PASS.** The complete Unit 024 content boundary and its immediate
index-destination correction are public. Every path changed by both commits
was anonymously read back from its immutable GitHub URL and matched its local
committed blob byte-for-byte. Public `main` resolved to the correction commit
before and after the readback.

## Public identity

- Repository: <https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id>
- Branch: `main`
- Unit 024 content commit:
  `bb913c53781e06b9a5fd0f57b981581faa7649c8`
- Immediate navigation-correction commit and current public head:
  `b9909c801f7bc1123e274c8036bb5b75f4ed0414`
- Correction tree: `a53aa210afb56bcaf40246da82a45e87d5727f46`
- Current commit page:
  <https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id/commit/b9909c801f7bc1123e274c8036bb5b75f4ed0414>

## Anonymous byte readback

The verifier used credential-disabled anonymous `git ls-remote` for the
public `main` ref and immutable `raw.githubusercontent.com` URLs for file
bytes. It sent no credential or `Authorization` header. GitHub's anonymous
REST ref endpoint had exhausted its public rate quota, so no REST result is
used as evidence.

The two verified boundaries are:

| Boundary | Changed paths | Public bytes | Result |
|---|---:|---:|---|
| content commit `bb913c5...` | 38 | 2,071,731 | every immutable raw response HTTP 200 and byte-identical |
| correction commit `b9909c8...` | 13 | 465,946 | every immutable raw response HTTP 200 and byte-identical |

Total: 51 immutable path fetches and 2,537,677 verified bytes. The public
branch ref resolved to `b9909c801f7bc1123e274c8036bb5b75f4ed0414`
both before and after those fetches.

Complete per-boundary and per-path evidence is
`qa/PUBLICATION_GITHUB_UNIT_024_CONTENT_READBACK.json`, 27,432 bytes,
SHA-256
`a35012ba9dabd61259dc0f4a9777e225c5d2ebb54555ea1f0bfd96c8a154d66a`.
The reproducible verifier is
`scripts/verify_unit_024_github_readback.py`, 7,121 bytes, SHA-256
`8b97ef63f71f9d9e9b9a057c0f9f497c4cc3d77cc5b18bf218aea87d7a2b5636`.

## Corrected current identities

- reader: `artifacts/unit-024-bab-3-latihan-kategori-monoidal.pdf`, 86,255
  bytes, SHA-256
  `1b61a1e2b856f2ef5d9dbc800c6e593aeb776fd85e2480a53b26286639292e71`;
- reader driver:
  `repo/source/unit-024-bab-3-latihan-kategori-monoidal.tex`, 5,312 bytes,
  SHA-256
  `936fd9b09fb0220b9730627b10f032447b01c06b6d98ae15af4826ce5b03f0e8`;
- backend: `backend/data/unit-024-bab-3-latihan.json`, 137,184 bytes,
  SHA-256
  `5053a0c5398b256390f3f8abcdf31d423eb24460bc4f670539895ee5bd9e88b5`;
- structured PDF evidence:
  `qa/unit-024-evidence/structure-and-pdf-qa.json`, 34,531 bytes,
  SHA-256
  `d479638e9b1b4b9982354c157fb22ba0c92177cb7d5c823476ef03254fccc28a`;
- admission receipt: `qa/UNIT_024_ADMISSION_20260825.md`, 8,458 bytes,
  SHA-256
  `9aa16bcbc2fbaf953ea767c3698cf384754920d3cc227e0d12ebd75833472521`.

## Correction and admission truth

Checkpoint preflight found that the visible `YBE, 1` index annotation on
physical page 4 targeted absent destination `page.1`. The correction supplies
that exact local destination on physical page 3. All three clean builds and
the frozen artifact now contain six named destinations; the sole internal
`GoTo` resolves to physical page 3, and the broken-target inventory is empty.
Poppler and MuPDF comparisons prove that the correction changed no decoded
page pixel.

The publication completes the Indonesian Chapter 3 exercise tail and reaches
the canonical Chapter 3 EOF (`chapter3.tex:873-911` in the authority). It does
not claim that the full Li volume or the composite O013 course is complete.
Chapter 4 remains the next source-order production boundary.

Wen-Wei Li remains the source author. Principal text and translation are
CC BY 4.0; the credited `AJbook.cls` fragment and `Lanzhou.png` retain
CC BY-SA 3.0, and bundled fonts retain OFL 1.1. `Lanzhou.png` is not used by
this reader. The derivative is independent and non-endorsed. Production
provenance is separately recorded as `OpenAI Codex gpt-5.6-sol, Ultra`.
