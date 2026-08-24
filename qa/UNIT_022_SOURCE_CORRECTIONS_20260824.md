# Unit 022 source-correction provenance — 2026-08-24

Status: **REVIEWED AND CANONICALLY INTEGRATED; READER/BACKEND ADMISSION
PENDING**

Production provenance: `OpenAI Codex gpt-5.6-sol, Ultra`

## Frozen boundary

The frozen authority is
`authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`,
75,571 bytes, SHA-256
`7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
The exact Unit 022 authority span is physical lines 513–722 inclusive, 15,089
bytes, SHA-256
`85332852a2b9808a5a9e7ec240adffdd5b286d44d724be38833aed53e65bd53d`.
Authority line 723 begins the separate Section 3.5 and is excluded.

The reviewed Indonesian span is 17,541 bytes, SHA-256
`e1fa8da94c0c2431660f690aa9b2193e3c966e2d71b9d5a029da12a76bc0e255`.
Its deterministic integration is now applied at canonical target lines
512–721. The complete integrated target is 86,033 bytes, SHA-256
`b395e1014becb462dae95eda5fde37da9b4edd0b477df8f0b5cefef43edbefa2`.
The earlier integration proof was temporarily restored byte-for-byte to the
Unit 021 boundary so that Unit 021 could complete its already-running build and
publication. After Unit 021 passed public readback, the same hash-bound
integrator reapplied the reviewed bytes. The canonical structure checker now
passes for the resulting target, and Section 3.5 remains untouched.

## O013-LI-U022-COR-001 — Cartesian product of ordinary Hom-sets

Authority line 588 defines composition in the ordinary category underlying a
category enriched over `\mathcal V`. Its first diagram row has domain

```tex
\Hom_{\mathcal{V}}\left( \munit, \iHom(Y, Z) \right)
  \otimes
\Hom_{\mathcal{V}}\left( \munit, \iHom(X, Y) \right).
```

Both factors are ordinary Hom-**sets**. No tensor product between those sets is
defined by the hypotheses. Functoriality of the monoidal product instead takes
a pair of morphisms and induces a function from their Cartesian product into

```tex
\Hom_{\mathcal V}(\munit\otimes\munit,
  \iHom(Y,Z)\otimes\iHom(X,Y)).
```

The reviewed candidate line 76—and canonical target line 587 when Unit 022 is
applied—therefore replaces only the intervening `\otimes` with `\times`. The
enriched Hom-objects and the monoidal products in the codomain remain unchanged.
This makes the displayed map well-typed for an arbitrary monoidal category
`\mathcal V`.

## O013-LI-U022-COR-002 — domains of the biproduct injections

Authority line 665 defines, for `i=1,2`,

```tex
\iota_i: X_1 \to Z
```

but the immediately following equations require
`p_i\iota_i=\identity_{X_i}`. For `i=2`, that composite has domain `X_1` under
the printed definition and therefore cannot equal `\identity_{X_2}`. The
universal property of the product also supplies the injection corresponding to
the pair whose `i`-th component is `\identity_{X_i}`, so its domain must be
`X_i`.

The reviewed candidate line 153—and canonical target line 664 when Unit 022 is
applied—therefore uses

```tex
\iota_i: X_i \to Z.
```

No other symbol, equation, or proof step changes.

## Integration and verification boundary

Before integration, canonical target lines 1–511 were frozen at 51,102 bytes,
SHA-256
`5ea3a7c7b0c71bb69d1ed25b846fa7e859b5f0161644993eac8c38efac157d0c`.
They remained byte-identical through integration and restoration. In the
verified integrated target, lines 722–910 were byte-identical to authority
lines 723–911, 17,390 bytes, SHA-256
`db85619a873a826c4a417252b5268b9c85d068f18f9467664599fb9b0575b6af`.
Thus Section 3.5 is not included or modified.

The temporary restoration reconstructed target lines 512–910 directly from
authority lines 513–911: 32,479 bytes, SHA-256
`0184b127cecf8e973aa395e050385ed75280b898d5ea22293572d6513d7a6c83`.
Reapplication then reproduced the pinned 86,033-byte integrated identity above.
The final reader, terminology, backend, visual, and admission receipts remain
to be attached at this production boundary.

The independent translation/source review is
`qa/UNIT_022_TRANSLATION_SOURCE_REVIEW_20260824.md`, 9,175 bytes, SHA-256
`36d7650aa142da19d998dc8f1b6d39f24a94e2a19e51e988cbd2187691f56e9f`.
Its isolated fail-closed checker is `scripts/check_unit_022_candidate.py`,
23,938 bytes, SHA-256
`2fc366f8af4439ca0667b0111d836348d0742c3e9cec8dd2dbaf08a7edb81613`.

The fail-closed, reversible integrator is
`scripts/integrate_unit_022_candidate.py`, 9,213
bytes, SHA-256
`4f4b0c777b0851f5551cf5fffa7a222842fd8c824174afd42b1065ebef1cb5c8`.
Its default mode accepts only the exact Unit 021 boundary and constructs the
pinned Unit 022 target; its `--restore-unit021` mode accepts only that exact
integrated target and reconstructs the pinned Unit 021 boundary.
The canonical checker is `scripts/check_unit_022_structure.py`, 6,084 bytes,
SHA-256
`981d558ed0d237b002f014db390469046ce1a0f6034c22e5442f5bda6571380a`.
It reruns the isolated mathematics/topology checker and proves candidate-byte
identity, prefix preservation, and authority-suffix preservation.

These are disclosed, minimal corrections to the frozen source. They do not
imply upstream authorship or endorsement. Frozen authority bytes remain
unchanged, and no external source was consulted for either adjudication.
