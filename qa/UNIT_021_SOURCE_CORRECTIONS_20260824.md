# Unit 021 source-correction provenance — 2026-08-24

Status: **APPLIED TO THE CANONICAL TARGET; FINAL UNIT ADMISSION PENDING**

Production provenance: `OpenAI Codex gpt-5.6-sol, Ultra`

## Frozen boundary

The frozen authority is
`authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex`,
75,571 bytes, SHA-256
`7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0`.
The exact Unit 021 authority span is physical lines 307–512 inclusive, 15,276
bytes, SHA-256
`cbbf8714c3e5a387e42e2653900a8f3911e41df530b39a86701261c89de64ff8`.
Authority line 513 begins the next section and is excluded.

The reviewed Indonesian span is canonical target lines 306–511, 17,968
bytes, SHA-256
`57f5bc8a211b6a9b76a096742fbfc94989c890f11d5140ad449d0e76e2c67085`.
The complete integrated target is 83,581 bytes, SHA-256
`ce310d940819f0fc51ee6459f73a8380b602edee42ef666720e225451adee9f9`.

## O013-LI-U021-COR-001 — naturality-square codomains

Authority lines 485–487 display the naturality square for

```tex
f:X\to X', \qquad g:Y\to Y'.
```

Its vertical arrows are labelled `f \otimes g` and `g \otimes f`, but the
bottom row at authority line 487 incorrectly repeats the top-row objects:

```tex
X \otimes Y \arrow[r, "{c(X, Y)}"'] & Y \otimes X
```

Those are the domains of the vertical arrows, not their codomains. The
reviewed candidate line 181 and canonical target line 486 use the well-typed
bottom row

```tex
X' \otimes Y' \arrow[r, "{c(X', Y')}"'] & Y' \otimes X'
```

This is exactly the naturality square for the braiding. It restores the two
codomain objects and the corresponding component label while preserving the
four-node/four-arrow `tikzcd` topology and every surrounding claim.

## O013-LI-U021-COR-002 — objects misnamed as braids

Authority line 448 sets `X=m` and `Y=n`, hence `X` and `Y` are objects of
`\cate{Braid}`. Authority lines 450 and 452 then call them “the braid `X`” and
“the braid `Y`,” although the braiding morphism is introduced only afterward
as `c(X,Y)\in\mathcal B_{m+n}`.

Reviewed candidate lines 144 and 146, now canonical target lines 449 and 451,
therefore say that the unentangled strands correspond to **objek** `X` and
**objek** `Y`. No symbol, diagram, object assignment, or morphism changes.

## O013-LI-U021-ED-001 — duplicated word

Authority line 508 contains `无穷循环群群`, with the final noun “group” typed
twice. Reviewed candidate line 202 and canonical target line 507 normalize the
intended statement once as `grup siklik tak hingga` in
`\mathcal B_2\simeq\mathbb Z`. The mathematical assertion is unchanged.

## Verification boundary

The independent translation/source review is
`qa/UNIT_021_TRANSLATION_SOURCE_REVIEW_20260824.md`, 9,460 bytes, SHA-256
`b22feafa193ed118bbe7c559a97e05817f720575bda8cfe190b8827c5f47fe4e`.
Its fail-closed candidate checker is `scripts/check_unit_021_candidate.py`,
23,377 bytes, SHA-256
`6448b0fa51ac8741bab5b29c7ed339f318c073388e79ba2705bd34b8413a9af6`.
The checker pins all three authority and target signatures while preserving
the complete 206-line boundary, 43 environment pairs, nine labels, thirteen
reference calls, two citations, eight indexes, 144 inline-math surfaces, six
bracket displays, seventeen `tikzpicture` blocks, six `tikzcd` blocks, and zero
target Han residue.

These are disclosed, minimal corrections to the frozen source. They do not
imply upstream authorship or endorsement. Frozen authority bytes remain
unchanged.
