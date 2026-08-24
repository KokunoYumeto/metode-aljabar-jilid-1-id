# Unit 020 mathematical source-correction provenance — 2026-08-24

Status: **APPLIED AND VERIFIED**

Correction identifier: `O013-LI-U020-COR-001`

Production provenance: `OpenAI Codex gpt-5.6-sol, Ultra`

## Frozen-source defect

The frozen authority is
`authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`,
75,571 bytes, SHA-256
`7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
The exact Unit 020 authority span is physical lines 228–306 inclusive, 6,071
bytes, SHA-256
`86f02abb667e1f03a99e89f34982527fbb715eb55496f9c76c576e041076d737`.

Authority line 254 defines the objects of `$\mathbf{e}(\mathcal{V})$` as
`$(F, \rho)$`, and line 255 defines the family
`$\rho(X,Y):FX\otimes Y\rightiso F(X\otimes Y)$`. The same datum controls
morphisms, the unit object, the tensor product, and the characterization of
`$F$` throughout authority lines 271–294. No datum `$m$` is introduced in this
construction.

Nevertheless, authority line 299 reads exactly:

```tex
		\item $L$ 本质满: 事实上 $(F, m) \simeq L(F(\munit))$,
```

An exact search of the complete frozen authority file finds this
`$(F, m)$` signature once. The defining `$(F, \rho)$` signature occurs once.
The mismatch is therefore a local notation error, not an alternative object
datum or a translation choice.

## Applied canonical correction

The isolated candidate at line 72 and integrated canonical target at line 298
both read:

```tex
		\item $L$ surjektif secara esensial: sesungguhnya $(F, \rho) \simeq L(F(\munit))$,
```

The canonical Unit 020 span contains zero `$(F, m)$` signatures and two
`$(F, \rho)$` signatures: the object definition and this corrected essential-
surjectivity statement. Relative to the authority, the sole TeX-command-count
difference is the one added `\rho` command on relative Unit 020 line 72
(authority line 299 / canonical line 298). All other inline-math surfaces,
five bracket displays, both diagrams, labels, references, citations,
environments, and items are preserved.

The correction is minimal and necessary: replacing `m` by the already defined
`\rho` restores the declared object type `$(F,\rho)$` without changing the
lemma, its proof strategy, or any mathematical hypothesis or conclusion. It is
a disclosed correction to the frozen source and does not imply endorsement or
upstream authorship.

## Deterministic identities and gate

- Integrated target: `repo/source/chapter3.tex`, 80,889 bytes, SHA-256
  `64d334af911539cbe844a250ab41c3e6d537e2c827919c21d41547e1f5782d7a`.
- Exact canonical Unit 020 span, target lines 227–305: 7,266 bytes, SHA-256
  `25f8aa41663253a28ac27c3cf635470ac2e20e69d48b168d98cb025a3a792270`.
- Reviewed isolated candidate: 7,266 bytes, the same SHA-256; it is
  byte-identical to the canonical span.
- Canonical checker: `scripts/check_unit_020_structure.py`, 21,048 bytes,
  SHA-256 `a4bdd19b4104d799cbb28a235898b8883aafecfbdb0bb5cca1e83d7e4f7b96b8`.

The checker requires the erroneous frozen signature exactly once, forbids it
in the target, requires the corrected target signature exactly once, verifies
the defining/corrected `$(F,\rho)$` census, and rejects every other command or
formula delta. Its current run exits `0` with
`PASS Unit 020 canonical structure checker`.

This provenance record modifies no frozen authority, reader, build, backend,
glossary, control, Git, or publication state.
