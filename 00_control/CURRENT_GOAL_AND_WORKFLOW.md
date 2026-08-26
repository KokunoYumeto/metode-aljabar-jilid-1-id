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

Current admitted boundary: Li Units 001-032 through complete Section 4.8.
Unit 032 authority is chapter4.tex:1108-1388, 281 normalized-LF records / 22,547
bytes / SHA-256 5a7083cd89d13e776bbf94189f7f96f5d976cd962cba7a8d4c6b2453bd59c8af; blank boundary line 1388 is excluded from the
280-record target mapping at canonical lines 1104-1383. The final candidate is
27,910 bytes / SHA-256 28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc; canonical chapter4.tex is 181,896 bytes / SHA-256 4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680.
Its centered thirteen-page reader is 149,624 bytes / SHA-256 904330916e20f0782b6464cb85e07001851940f4adf153f6592cd34087dbadbf, and its schema-valid
backend is 460,681 bytes / SHA-256 a3f68cd45d5fc44720e769c7a12d745a4af78d7a361e6e8b81a1c5019be1a030. Backend validation is
5,422 bytes / SHA-256 b66c40151489b4d162e63e9edef3da1d7c593362002bb8e0b9a6f5ba3410be6d; the admission receipt is
4,274 bytes / SHA-256 065bba6285a1668abdd29f8d349f9f905b048755dc429e8e8d08d7944dc5c1f0; and the final audit is
5,421 bytes / SHA-256 e8d214df7a0feaf60a14a93e2b554db8fe881379caf98109737a9947f5d9e9e5.

All deterministic source, mathematics, terminology, topology, build, PDF,
dual-renderer visual, backend, rights, privacy, and independent-audit gates
pass. O013-LI-U032-COR-001 and O013-LI-U032-COR-002 are separately provenanced.
The first reader exposed 22.16992 pt and 27.03485 pt overflows in finite-support
set-builder displays; target-only reflows O013-LI-U032-REFLOW-001 and
O013-LI-U032-REFLOW-002 remove them without changing set membership,
quantifiers, finite-support conditions, or term order. The final reader has
thirteen centered pages and no actionable visual or build defect. Exactly three
visually non-actionable underfull hboxes and its untagged-PDF accessibility
limitation are disclosed.

Content commit bc5e43a75925d522a80600724d6d95e40ad55f75, tree 13afc9751570e15d24a77063606a455dc420f69a, passed
anonymous readback for 64 paths /
6,515,805 bytes. Receipt commit 5780621108e60521427b20a77090114590abe6b0,
tree 1f88e8d6901c01eed57ecb602484eb6c2bff1b87, passed anonymous readback for
3 paths / 104,435 bytes
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
anonymously read back on both GitHub and Zenodo. Unit 032 and complete Section 4.8 are public and byte-verified.
The following source-order admission boundary is Unit 033 at chapter4.tex:1389-1608; its
23,074-byte isolated candidate has SHA-256
09e8ec87919a6620e5baac6a07b470b2d03d24a5775d8c66bf6de9af43dc1953. Its checker has SHA-256 670016f2f054139c5da78fb2c412f68f7836d2bc4c1dab0282a4041e3a6baa4f. The candidate
remains isolated until Unit 033 terminology, integration, reader, backend,
build, all-page visual, publication, and anonymous-readback gates pass. The
active cursor is chapter4.tex:1389 and the cursor after Unit 033 will be
chapter4.tex:1609. Units 033-042 remain strictly source-ordered. The isolated
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
