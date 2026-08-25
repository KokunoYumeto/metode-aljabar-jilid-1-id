# Unit 027 prepromotion audit — 2026-08-25

Status: **PASS; bounded canonical promotion authorized by deterministic gates.**

## Exact boundary

- Frozen authority: `chapter4.tex:365-517`, 153 normalized-LF records,
  10,209 bytes, SHA-256
  `bb7cb2d385018971fe325c417bcafdccd9e92376c02e7cb72d3af038097f8db8`.
- Substantive candidate maps authority lines 365-516 one-for-one; blank
  boundary line 517 is omitted. Candidate: 152 records, 12,675 bytes,
  SHA-256
  `aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563`.
- Section 4.4 begins at authority line 518 and remains outside this admission.

## Translation and terminology gates

- `scripts/check_unit_027_candidate.py`, 14,054 bytes, SHA-256
  `a98d407c23ce2ae28f3fbe1776387c96b9d2cc4db6c987e089227fbc92fd556e`,
  passed twice with identical output.
- Independent source, language, and mathematics review:
  `qa/UNIT_027_INDEPENDENT_REVIEW_20260825.md`, 6,104 bytes, SHA-256
  `28d0834da4d076a4926ccc10b956c32a3445453567abff9c449ee7eeeae843ef`.
- Terminology audit:
  `qa/UNIT_027_TERMINOLOGY_AUDIT_20260825.md`, 4,590 bytes, SHA-256
  `21f794e503efc4c24924e48e0520bff601474c3d8b1e0f0c37fcf0a3d3cbd806`.
- Approved delta: 9 admitted, nonduplicative rows / 1,959 bytes / SHA-256
  `5a661682e425f53ed0bd25a3f1badd6cdc83b396946901573bcb0c7d8e1a977e`.
  Every target form occurs in the candidate. The resulting controlled
  glossary is predicted as 383 data rows / 60,575 bytes / SHA-256
  `61e45adc844d8fd6beccf1cbb2216340913d6eb3b55cdd487817820171899f97`.

## Preserved and corrected content

The candidate preserves 28 paired environments, 8 labels, 5 references, 6
indexes, 171 protected mathematical zones, 4 commutative diagrams, 3 polygon
drawings, and 15 list items; it has no citations, exercises, hints, solutions,
or source-language residue. Two source corrections are explicit: the direct
product universal-property codomain and the `n >= 3` scope of the regular
polygon interpretation. One translation-precision repair avoids calling the
restricted adjoint action inner on `N`. Two style-only normalizations use the
controlled term `unsur identitas`.

## Predicted bounded mutation

- Current canonical Chapter 4: 163,745 bytes, SHA-256
  `fc3fd6ef470d41f146456bfc889eb7c7ec84bb48890f1b23f18e51a195e7d463`.
- Untouched authority suffix from line 518: 113,647 bytes, SHA-256
  `c9d69fabd6720d01a02b52c11e995065b58b12851a40510dccf17ccec956d7f4`.
- Predicted canonical Chapter 4: exact Unit 025 + Unit 026 + Unit 027 +
  authority suffix from line 518 + terminal LF; 1,898 records / 166,211 bytes
  / SHA-256
  `5a4ec3ec5f420c694f7e1207f02a79c558da0f18c6c1f23969856c481f9a7420`.
- Promotion script: `scripts/promote_unit_027.py`, 6,605 bytes, SHA-256
  `f0e1ad03616a0bd8155eb3d27479c4f7c60e0cd8a4c63776a05219dbe28a6f16`.

The promotion is fail-closed and idempotent. It mutates only the canonical
Chapter 4 target and controlled glossary, and rolls the glossary back to its
exact prior bytes if the target write fails.
