# GitHub publication receipt - Unit 015

Published: 2026-08-24

Repository: `https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id`

Branch: `main`

Content commit: `a66d2bd8d569f8a6f26533e18285ef8f2cd58b5a`

Commit subject: `Add Indonesian Unit 015 adjunction examples`

## Public scope

The existing repository lineage now includes the complete Indonesian
translation of `chapter2.tex:910-1110`: adjunction examples, pointwise
characterization, uniqueness and composition, and adjoint equivalence. The
release also includes the standalone reader, reproducible source and build
script, exact final log, deterministic modular backend and six CSV projections,
terminology QA, structural checks, dual-render evidence, and admission record.
It does not claim that Volume 1 or the composite O013 course is complete.

Key immutable identities:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `artifacts/unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin.pdf` | 120,466 | `6f2a9be12465300ac7af2ea086b643b6891b1f9e23af66241a40086ac476c8ef` |
| `repo/source/chapter2.tex` | 158,252 | `a106ec94b9c2b4a276371e6527b0c7c86dfd84538dde0be8e31848d59d2caf8c` |
| `backend/data/unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin.json` | 78,807 | `a8630f4f3b6b4b697bd63d47341da719de539429ebcbec567c1c1af7697a1e20` |
| `qa/UNIT_015_BUILD_FINAL.log` | 84,703 | `6d7fa510890ee32c19b65b2b51046b771f8e93570f6d6f1a9f17f0745fcc5874` |
| `qa/UNIT_015_ADMISSION_20260824.md` | 6,821 | `cc81bc9121c5967873b96f38be2d95f7b1cd5954eef1a84b585c9e0c74e9811c` |
| `qa/unit-015-evidence/structure-and-pdf-qa.json` | 5,910 | `c1363c5e19161269fb6667781505f06238d3c3bed06c9445d2883fb391f61aca` |
| `qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md` | 12,619 | `4ceeb7920e6e6ad8c717c430a02efe7778dfb667b661fc9de83622d7cd870c75` |
| `00_control/TERMINOLOGY.id-ID.csv` | 26,776 | `7980b5982e84c3d2c5e2d662119cd6fb9ad02eadcd2d475ff5ba31e937290a2a` |

## Verification

The structural checker passes all 232 mathematical surfaces, 35 environments,
nine labels, eight ordinary references, twelve equation references, one
citation, three index entries, four TikZ-CD diagrams, and sixteen TikZ
pictures. Two disclosed source corrections repair a misplaced prime and a
cross-picture midpoint reference. Two clean builds reproduce identical page
renders in both Poppler and MuPDF, and all ten pages were visually inspected.
The backend validates with 87 stable entities and no dependency on an ignored
local build cache.

## Anonymous readback

After the push, an unauthenticated client fetched every changed path at the
immutable content commit from `raw.githubusercontent.com`. All 23 paths,
totaling 670,473 bytes, matched the local byte counts and SHA-256 identities.
This includes the reader PDF, translated source, build inputs and final log,
backend JSON/CSV, terminology record and glossary, and QA evidence.

## Rights and provenance

Wen-Wei Li remains the source author. Principal text and the Indonesian
translation remain CC BY 4.0; the credited AJbook fragment remains CC BY-SA
3.0; bundled Noto fonts remain OFL 1.1. The derivative is independent and
non-endorsed. Production provenance: OpenAI Codex gpt-5.6-sol, Ultra.
