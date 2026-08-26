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

Current admitted boundary: Li Units 001-031 through complete Section 4.7.
Unit 031 authority is chapter4.tex:936-1107, 172 normalized-LF records / 16,048
bytes / SHA-256 647d22446e75cde39b7b9f53d6658f39de78c5d773d51d6f446d651e1734967b; blank boundary line 1107 is excluded from the
171-record target mapping at canonical lines 933-1103. The final candidate is
19,855 bytes / SHA-256 6bc4b1f7dd6cde6673915eba75cdf96cca6e8312d060d1fda0da25cb7073ee81; canonical chapter4.tex is 176,533 bytes / SHA-256 440ed304a808c687d2e431eff1dbdbe0fe01458d7f8c82b47f515659307cf28f.
Its centered nine-page reader is 126,053 bytes / SHA-256 313667c3f87439ccaac3f8708653bb352af0ba7a16c9d09b159ad1b836cc32fb, and its schema-valid
backend is 367,588 bytes / SHA-256 307828cd0dc47e8229a01fd08beaad3cb3c6fdd4aa09e4f973ba28d86f92f391. Backend validation is
5,837 bytes / SHA-256 51fe7f83d5b2c6a192d322b3e96899affb52045e16d9958f285497fe6840f7ca; the admission receipt is
4,547 bytes / SHA-256 ee981426d7d15c47d975315c10c7566566d4397bb34e1be3c8bca3f20f334f06; and the final audit is
5,539 bytes / SHA-256 64e2e14a1824bb2311c37f371446a95f20e2113743cd6869111d20df9b5b38d7.

All deterministic source, mathematics, terminology, topology, build, PDF,
dual-renderer visual, backend, rights, privacy, and independent-audit gates
pass. O013-LI-U031-COR-001 is separately provenanced. The first reader exposed
a 42.13312 pt overflow in a four-term display; target-only reflow
O013-LI-U031-REFLOW-001 splits it without changing equality, signs, terms, or
order. Compact final indexes remove the sparse tenth page. The final reader has
nine centered pages and no actionable visual or build defect; its untagged
accessibility limitation is disclosed.

Content commit 257fafa97f8582e243b4f69b67c68a0e287b7b3d, tree 87f0db21f8e76e71c0a9f01757a3bffa93d557b9, passed
anonymous readback for 54 paths /
5,016,055 bytes. Receipt commit ca10067c2602ca7a93bb721fd46614ae0c16cdaa,
tree 93271eadcaa3ed557314de89d3f9baaf3995b489, passed anonymous readback for
3 paths / 99,685 bytes
and is the verified remote base. The 229-page checkpoint reader 0.6.0 remains
the nonduplicative Zenodo preservation release.

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
anonymously read back on both GitHub and Zenodo. Unit 031 and complete Section 4.7 are public and byte-verified.
The following source-order admission boundary is Unit 032 at chapter4.tex:1108-1388; its
27,685-byte isolated candidate has SHA-256
19583aa71814bbed580d51f39eeaf113a399ec13fef5773a39b6e6cf16289140. Its checker has SHA-256 5bbaa33eb27b6acf6f1530f5473926cb0a2a9b6216ff4c492f88840795ab4d89. The candidate
remains isolated until Unit 032 terminology, integration, reader, backend,
build, all-page visual, publication, and anonymous-readback gates pass. The
active cursor is chapter4.tex:1108 and the cursor after Unit 032 will be
chapter4.tex:1389. Units 032-042 remain strictly source-ordered. The isolated
translation cursor remains chapter5.tex:1184; Unit 043 has not started.

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
