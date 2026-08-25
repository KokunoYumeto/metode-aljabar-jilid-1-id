# Checkpoint 0.6.0 evidence normalization - 2026-08-25

Status: **PASS; identity-only evidence correction, with no reader change.**

The first public checkpoint content commit recorded the Windows working-tree
CRLF byte identity of `VISUAL_REVIEW.md` inside the machine QA JSON, while Git
correctly published the repository-normalized LF form. The visual receipt's
substance was unchanged, but its recorded byte count and SHA-256 therefore did
not describe the public repository blob.

The machine QA record now binds the actual repository-normalized visual receipt:

- `qa/checkpoint-0.6.0-evidence/VISUAL_REVIEW.md`: 1,493 bytes, SHA-256
  `c685ecf54eafbb0be7482ee25fe6382826525ed83e16621c93cce3c7cd22ff99`;
- corrected machine QA JSON: 127,824 bytes, SHA-256
  `5e1ee5fcc9a6a3d6578a71d3771b8a3eea1389ca71e708ee489cbec6fe68d084`.

The QA writer is pinned to LF output so subsequent deterministic runs do not
reintroduce platform newline drift. The 229-page reader remains exactly
3,658,991 bytes with SHA-256
`a147c05617e61a5d22a0038f2b5b995d668f387f9531514261d273fe9b6618c5`;
its pages, links, renders, and mathematical content are unchanged.
