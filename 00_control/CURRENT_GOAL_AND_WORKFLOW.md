# Current goal and workflow

Updated: 2026-08-25  
Task: O013 / D70 Graduate Algebra  
Owner task: `01a02163-e2bf-7a93-950a-b9ab84d7e8b9`  
Lane: repository root (`.`); resolve all listed paths relative to this control file's repository.

## Objective and selected architecture

Produce one complete, coherent Bahasa Indonesia O013 edition with a modular,
language-neutral backend and one corpus-specific public GitHub. Translation and
reader production dominate. The selected course has three separately
provenanced components: (A) complete Wen-Wei Li, *Methods in Algebra, Volume
1* (445 pages), the organizing core; (B) the complete licensed repository of
Alexander Duncan's representation-theory notes at commit
`c62d36f41189da4bd3da4671668f68720df54ff7` (seven TeX roots plus
`rep_theory.bib`, 135 author-hosted rendered pages); and (C) only the six
selected CRing line spans (60 page-intersecting source pages). Etingof remains
reference-only. Connective exposition and the solved-mastery layer are
separately provenanced original work. The exact revised architecture is bound
in `00_control/O013_COMPOSITE_SELECTION_REVISED_20260824.md`.

Finish the already-started complete Li edition first and in source order:
`prelude.tex`, then `chapter1.tex` through `chapter10.tex`. Do not use completed
work as evidence for curricular selection. After Li, freeze and reconstruct a
deterministic target closure for the complete pinned Duncan repository. Exclude
the six author-site assignment sheets, their 49 problems, and the partial
solution because they are outside the licensed repository. Then repair and
translate only the six CRing spans recorded in the older exact span packet
`00_control/O013_COMPOSITE_SELECTION_20260821.md`; do not translate all CRing.

## Authority and rights

Li is frozen at commit `c4f7a01f68f5f407906b4b970640cddbbad85f6b`,
tree `0f9fd52748165ec89a85ba602ccb949a2ce04694`, archive SHA-256
`6c8c416baa8f5ffc8810bbad6470c780413bd7917af739e07340e4b07e7eaff6`,
and official 445-page PDF SHA-256
`dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38`.
Preserve formulas, topology, labels, references, citations, indexes, diagrams,
active exercises, hints, attribution, and edition identity. Li has 161 active
top-level exercises, 268 active items including subparts, 51 hints, and no
solutions; the commented `chapter10.tex:1471` item stays excluded.

Keep rights non-flattened: Li CC BY 4.0; Duncan CC BY 4.0; selected CRing GFDL
1.2-or-later with no invariant sections/cover texts; connective and mastery
material is separately provenanced original work. Etingof is reference-only:
the OCW PDF is CC BY-NC-SA 4.0 and the arXiv TeX is not a redistributable CC
source. Li closure exceptions remain explicit: the credited `AJbook.cls`
fragment and `Lanzhou.png` are CC BY-SA 3.0, and bundled Noto fonts are OFL
1.1. State independent/non-endorsed derivative status.

## Recovery after context loss

Chat history and compaction summaries are not authority. Read, in order:

1. `00_control/RECOVERY_POINTER.json`.
2. This file, `CURRENT_STATE.md`, and `CURRENT_CURSOR.json`.
3. `O013_COMPOSITE_SELECTION_REVISED_20260824.md`, then the older exact CRing
   span record `O013_COMPOSITE_SELECTION_20260821.md`, `SOURCE_AUTHORITY.md`,
   `SOURCE_SELECTION.md`, `BUILD_BASELINE.md`, and `RIGHTS_COMPONENTS.csv`.
4. `TERMINOLOGY.id-ID.csv`, `DECISION_LOG.md`, `ADVERSE_LEDGER.jsonl`, and
   `WORKLOG.jsonl`.
5. Rehash the exact source/target named by the cursor and resume its next action.

The user's exact retained instructions are
`00_control/USER_INSTRUCTIONS_UNTITLED_1693.md`, 10,476 bytes, SHA-256
`cf913e8cb4d487f4c6958c079b372ccbb2fb5929dd483068441e80cefd6794f2`.

## Per-unit production loop

1. Freeze the exact contiguous source range and hash.
2. Translate natural formal `id-ID`, preserving all protected structures and
   source-vs-original provenance.
3. Record stable terminology once; preserve exercise/hint correspondence.
4. Run bounded residue, structural, mathematical, language, reference/index,
   clean-build, PDF-structure, accessibility, and all-page visual checks.
5. Extend stable corpus/component/unit/section/concept/term/exercise/hint IDs,
   source-target mappings, prerequisites, rights, assets, build and QA events.
6. Validate schema, UUIDv5 identity, references, order, live hashes and exact
   deterministic CSV projections. QA supports production; do not loop on it.
7. Admit only verified bytes, update cursor/state/receipts, commit and push the
   meaningful boundary immediately, then verify public bytes and continue.

Current admitted boundary: Li Units 001-029. Unit 029 is complete Section 4.5,
`chapter4.tex:666-795`; its 129-record Indonesian target is 10,028 bytes,
SHA-256 `234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d`.
Canonical `chapter4.tex` is 170,663 bytes, SHA-256
`8cbd766360a3c7cd214876e297c45de3b8938daa9a3623192efdf1d6ebc766fc`.
Its centered six-page reader is 99,689 bytes, SHA-256
`64fde52948525fc5b159f76fbed6571c150e4184a87e47e715164aec135e5012`,
and its schema-valid backend is 243,849 bytes, SHA-256
`918e1f3cbf30ec950bb83dc6427f63190dde41c766cbc38d5d349728ee92cced`.
All source/math/terminology/structure/build/PDF/visual/backend and independent
audit gates pass; one protected-text localization is separately provenanced,
and the disclosed untagged-PDF/Poppler Adobe-GB1 limitations remain.
Unit 029 content commit `e9bc26191e422ab055ead3cb39fedbc228237b23`, tree
`c4226d550b9ff3266045d76a7928b2351cbd6d53`, passed anonymous readback for
all 44 changed paths / 3,398,169 bytes. Receipt commit
`458e6e32797e2310bd7fa53c21e78bc133723851`, tree
`aa9f69be9e5319dd61d0d6e1e57edecbe89dcb7b`, passed anonymous readback for
all three changed paths / 88,954 bytes and is the verified remote base.
The 229-page checkpoint reader `0.6.0`, covering Units 001-024 and complete
Chapters 1-3, remains public at content commit
`5641d5453c85cf007135603037db8805f7fa4f42`; all GitHub checkpoint and Zenodo
release bytes passed anonymous readback.

A bounded Indonesian field-usage check found no suitable Indonesian arXiv TeX
after a finite search and therefore used two openly readable Indonesian
category/algebra PDFs plus the official 2008 mathematics glossary as an honest
fallback. The evidence and decision are in
`qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md`, 18,608 bytes,
SHA-256
`cc6400d922951ab474cf1dee0df3d12dc93183267723df0119b2b93731bb16e5`.
The controlled glossary is 36,770 bytes, SHA-256
`1aaf02e1146b6a47b29090ac58cb0c8436a5b97708d23969b8253f07a99a98a3`.
The adjudicated corrections are `funktor` to `fungtor` and the sole
`transformasi alami` occurrence to `transformasi natural`; all other audited
terms remain justified. A fresh official arXiv API recheck returned zero results
for the two bounded same-field/Indonesian queries; the exact fallback PDFs are
retained locally with a non-redistribution manifest at
`authority/terminology-qa-20260822/MANIFEST.json`. The glossary now also binds
the already-correct `natural isomorphism` to `isomorfisme natural`. Units 001,
008, and 009 were rebuilt and rebound after the substantive propagation. The
original correction is public at `f0d7221a56508c939a3b91947eb551ba7f1c24c2`.
The Unit 016 and 017 deltas each add sixteen controlled category/topology
terms; the Unit 018 delta adds eight admitted exercise terms. A second bounded
2026-08-24 check against a complete seven-page Indonesian tensor-product paper
adds five exactness/module terms and refines one backend-only nonunital-ring
label; no admitted reader page changes. Its manifest and receipt are
`authority/terminology-qa-20260824/MANIFEST.json` and
`qa/TERMINOLOGY_QA_INDONESIAN_GRADUATE_ALGEBRA_20260824.md`. Exactly fifteen
monoidal rows were promoted after Unit 019, four strictness/coherence rows
after Unit 020, nine braiding rows after Unit 021, and eight enriched/additive
category rows after Unit 022 terminology QA, then seventeen higher-category
rows after Unit 023; the controlled glossary is now 45,230 bytes, SHA-256
`9e2d946520a1c9f8984abd1b78935c2fe052e5bfdf79e9c9091d41a29b7cd68a`.
Exact fallback identities remain explicit rather than being misrepresented as
direct attestation for every term.
The Zenodo/terminology reconciliation is public at content commit
`3e27180c6d12ac9000f8880333a07e69a8771e19` (12 paths / 324,611 bytes
verified) and receipt commit `0b214e2d8967d26cb25023bbee23d39b4e4b2795`
(three files / 11,654 bytes verified).

The current preservation release is Zenodo version `0.6.0`, DOI
`10.5281/zenodo.22088395`, under unchanged concept DOI
`10.5281/zenodo.22059759`. Its reader-first five-file payload totals
70,182,496 bytes; every public file passed anonymous byte/hash readback. The
existing Figshare item `33314766` was found as a private draft with five stale
`0.3.0` files. Its license selector has no option that can represent the mixed
component rights, so its lawful next version is a CC0 metadata/link record for
the Zenodo release, not a false-license file mirror. Unit 024 and complete
Chapter 3 are public. Its source boundary is
`chapter3.tex:873-911`, 4,954 bytes, SHA-256
`2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857`.
Its three required prose refinements and seven-row terminology promotion are
complete. The final Unit 024 candidate is 6,071 bytes, SHA-256
`576c39746534853cd5127298cf0c2ba7f6afb239e4d7b83f368b7a9969c5f43a`;
the controlled glossary is 46,585 bytes, SHA-256
`4fa4c6d2720dd7ab9c4ebe570a1124794bc8282af1b4491201fb61b7b973ce1b`.
The canonical target lines `872-910` are candidate-identical and the complete
target is 89,608 bytes, SHA-256
`443b71b515aef66c6ba8e259e65083604d227370c1ee7ca3ed49bdb5996f45fb`.
Both fail-closed checkers preserve eight exercises, three nested items, two
hints, four references, one index entry, 69 inline formulas, six displays, and
two `tikzcd` diagrams with eight arrows; correction `O013-LI-U024-COR-001` is
independently proved. The centered four-page reader is 86,255 bytes, SHA-256
`1b61a1e2b856f2ef5d9dbc800c6e593aeb776fd85e2480a53b26286639292e71`.
Its 32-render dual-engine visual gate, PDF structure/safety gate, and clean
extraction/font checks pass; the recorded accessibility limitation is that the
PDF is untagged. A preflight-discovered missing `page.1` index destination was
repaired without changing any decoded pixel; all named links now close. Its
schema-valid backend is 137,184 bytes, SHA-256
`5053a0c5398b256390f3f8abcdf31d423eb24460bc4f670539895ee5bd9e88b5`,
with 187 entities / 139 concepts, exact exercise ownership, six deterministic
CSV projections, and 65 verified live bindings across 34 paths. Dedicated and
shared validators pass twice after an independent review corrected prerequisite
ownership, exercise/hint counts, language metadata, and missing semantic
assertions. Content commit `bb913c53781e06b9a5fd0f57b981581faa7649c8`,
navigation correction `b9909c801f7bc1123e274c8036bb5b75f4ed0414`, and
receipt commit `a3dcc9dbba79a31a2212109c90b070fa5e6bcf8e` all passed
anonymous readback. Checkpoint 0.6.0 is now built, inspected, public, and
anonymously read back on both GitHub and Zenodo. Unit 029 content and sanitized
receipt are public and byte-verified. The following admission boundary is
Chapter 4 Unit 030 at `chapter4.tex:796`. Units 030-042 are isolated
source-order candidates and may not skip admission order; Units 030-035 finish
Chapter 4, Unit 036 begins Chapter 5, and Units 037-041 continue through the
complete monoid- and polynomial-ring section. Unit 041 covers
`chapter5.tex:783-956`; its candidate is 20,217 bytes, SHA-256
`e9e3d7d1c518e4fbb85a32f819a228d5077f59088fd6ea353d675d87ce71bc72`.
Its checker passes twice with four separately proven source corrections. Unit
042 then covers the complete unique-factorization section at
`chapter5.tex:958-1182`; its 225-record candidate is 29,674 bytes, SHA-256
`a76cf155134f6ae7a4a5e7a94cd9a5424ac83e277264f8d4228bdc5a2ed4b41a`,
and its checker passes twice with seven separately proved source corrections.
The isolated translation cursor is now `chapter5.tex:1184`; Unit 043 has not
started.

The Duncan source/build gate is independently admitted: exact source freeze
42,710 bytes / SHA-256
`ae02590a7842212b18ef09cc0a0010c041f54c1d1678521a6c301e00402844e1`
and build evidence 241,384 bytes / SHA-256
`e3aa03f34f2ac9f2735b3ed5ab9c703eeea1e0656c53df8dc3cb76dae050e0bb`.
All seven roots build twice to byte-identical PDFs and pixel-identical renders
on 135 pages. Preserve two empty `lin_alg.tex` TODO subsections transparently
and do not import excluded assignment material.
Maintain both public preservation routes at substantial verified boundaries
without creating duplicate lineages or flattening component rights.

## Ownership, publication, and completion

This task alone owns O013. O014/Li Volume 2 belongs to
`01a02164-3741-72b2-a48d-bab561ef5cd9`; Judson belongs to
`01a01f57-ebb2-73d3-bd55-e3ac48dd1dd7`; the central curriculum hub belongs to
the coordinator. Share interfaces only; never edit their files or releases.

The user has authorized bounded commits and pushes at every verified boundary;
never request another release confirmation. Use narrow Git operations and
perform public-byte readback. Do not contact authors during production. Only
after the complete O013 corpus may at most one deduplicated high-confidence
upstream issue be sent, signed `Codex, on instructions of the user.`

The goal is complete only when all Li, the complete licensed Duncan repository,
the selected repaired CRing content, and the separately provenanced connective
and mastery layer are translated or authored, backend-indexed, reproducibly
built, all-page QA-admitted, publicly pushed, and left with exact recovery and
release receipts. Etingof remains reference-only. Missing the mastery layer
does not block source translation, but does block calling the package a
complete independent-study product.
