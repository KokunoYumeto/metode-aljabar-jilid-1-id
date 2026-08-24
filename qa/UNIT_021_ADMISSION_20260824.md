# Unit 021 admission — Struktur Kepang

Status: **admitted locally** after continuous source/translation review,
fail-closed mathematics and TeX-topology comparison, bounded Indonesian
terminology adjudication, two clean builds, PDF structure and safety checks,
deterministic backend replay, and all-page visual QA in Poppler and MuPDF.

## Frozen content and boundary

- Authority: Wen-Wei Li, *Methods of Algebra*, Volume 1, commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Range: complete Section 3.3, `chapter3.tex:307-512`. Authority line 512 is
  the included blank separator; line 513 begins Section 3.4 on enriched
  categories and is excluded.
- Authority span: 206 LF records, 15,276 bytes, SHA-256
  `cbbf8714c3e5a387e42e2653900a8f3911e41df530b39a86701261c89de64ff8`.
- Indonesian target span: `repo/source/chapter3.tex:306-511`, 206 LF records,
  17,968 bytes, SHA-256
  `57f5bc8a211b6a9b76a096742fbfc94989c890f11d5140ad449d0e76e2c67085`.
- Full current target: 83,581 bytes, SHA-256
  `ce310d940819f0fc51ee6459f73a8380b602edee42ef666720e225451adee9f9`.
  The admitted span is byte-identical to the reviewed isolated candidate;
  target lines 512-910 remain byte-identical to authority lines 513-911.
- Independent continuous review:
  `qa/UNIT_021_TRANSLATION_SOURCE_REVIEW_20260824.md`, 9,460 bytes, SHA-256
  `b22feafa193ed118bbe7c559a97e05817f720575bda8cfe190b8827c5f47fe4e`.

## Mathematics, topology, and declared interventions

The fail-closed checks preserve 43 ordered environment pairs, nine labels,
ten ordinary references, three equation references, two citation
occurrences, eight index entries, 144 inline-mathematics surfaces, six bracket
displays, and six display environments. The diagram census is seventeen
`tikzpicture`, six `tikzcd`, thirty nodes, two coordinates, thirty-two draws,
fifteen edge tokens, twenty-six arrows, ten braid commands, and three
horizontal rules. The span contains no list item and no Han residue.

Three minimal source interventions are disclosed:

- `O013-LI-U021-COR-001` restores the codomain objects and component label in
  the naturality square from repeated `X,Y` to `X',Y'`.
- `O013-LI-U021-COR-002` calls `X=m` and `Y=n` objects of the braid category,
  rather than braids, without changing any symbol or diagram.
- `O013-LI-U021-ED-001` removes the duplicated Chinese noun in “infinite
  cyclic group.”

The dedicated record is `qa/UNIT_021_SOURCE_CORRECTIONS_20260824.md`, 3,492
bytes, SHA-256
`53cdb481310e76a2b2025b9086b884f7c6a7b1071606ce1c545cf24ac559db55`.
The independent mathematics audit is
`qa/UNIT_021_MATH_STRUCTURE_AUDIT_20260824.md`, 7,530 bytes, SHA-256
`099d3d9e31111b79b8b1fac0490176a18bb2b773a7493e7b731e1241f71279d0`.
The canonical checker is `scripts/check_unit_021_structure.py`, 28,404 bytes,
SHA-256
`f5ef89d6fcfa7196e54a43e1a13377df93d985bc7407f60b3f58ecef0aeb2cce`;
it passed twice and rejects unexpected path overrides.

## Terminology gate

Nine specialized rows are admitted: `struktur kepang`, `kategori monoidal
berkepang`, `fungtor monoidal berkepang`, `kategori monoidal simetris`,
`aksioma segienam`, `persamaan Yang--Baxter`, `kepang`, `grup kepang`, and
`grup kepang Artin`. A bounded Indonesian journal witness directly attests
`persamaan Yang-Baxter` and the alternative `grup Braid`. The edition keeps
transparent `kepang` consistently while retaining English lookup labels in
the index; it does not misrepresent that witness as direct attestation for all
nine choices.

The audit is `qa/UNIT_021_TERMINOLOGY_AUDIT_20260824.md`, 4,653 bytes,
SHA-256
`baaf37af9e72cb487636b07369403432d6a02e8bd6b2960fda1ca7d9537c2ef2`.
The controlled glossary is 39,866 bytes, SHA-256
`45e7b1500533e4fa8a8a257efe2982261704bd00a27f056030112141e5ed0efe`;
all nine rows are admitted and no earlier reader requires propagation.

## Reader, reflow, build, and PDF QA

The admitted reader is
`artifacts/unit-021-bab-3-struktur-kepang.pdf`: nine pages, 115,395 bytes,
SHA-256
`ff12bd0dbff7ba40d16050aef9f51b2b676dcfbeaa2e5808407373936fc37371`.
Its centered cover states `Cakupan parsial Bab 3` and the complete Section 3.3
scope in prose, with no ambiguous filled/unfilled progress blocks. The body
uses the canonical `3.3` heading at full readable width. Page 9 combines the
one-entry bibliography, six-entry term index, and two-entry symbol index in a
legible two-column composition. An attempted eight-page merge caused a 21.58
pt overfull vertical box and still spilled; the clean nine-page reflow was
therefore retained rather than crowding the reader.

Clean builds A and B have different raw PDF containers: 115,400 bytes,
SHA-256
`3307ea4ff631081e1e7e70ae9e7c4453bba8be0a2c861283e4ba96bd7ab042b0`,
and the admitted artifact identity above. Their page content, metadata,
navigation, text, links, and renders are equivalent. Seventy-two page renders
and eight contact sheets cover two builds, two renderers, and two replay runs;
all within-renderer and cross-build comparisons are decoded-pixel- and
PNG-byte-identical.

The reader driver now loads canonical `chapter3.tex` lines 306--511 directly;
neither it nor the build script depends on the ignored isolated candidate.
The build script validates strict UTF-8, 910 LF records, and the exact
17,968-byte span hash. It records the current whole-file identity without
rejecting later translations outside this unit, so the closure remains usable
as the Chapter 3 suffix advances.

The reader declares `id-ID`, preserves Wen-Wei Li as author, and has five
outline entries, 29 named destinations, eighteen internal links, four
intentional URI links, and thirty embedded subset fonts. It is unencrypted
and has no form, JavaScript, embedded file, additional action, invalid
destination, unresolved token, overfull box, missing character, or blank
page. Its keyword metadata uses clean ASCII `Yang-Baxter`. The untagged state
and a PyPDF-only ToUnicode mapping of two visible long arrows to NUL are
recorded honestly; Poppler extracts the arrows and both visual renderers show
them correctly.

The final log is `qa/UNIT_021_BUILD_FINAL.log`, 85,345 bytes, SHA-256
`5495764755137cd39cac890bba5f0779b9f96c378330c8e46f7ea3c02bc11f08`.
Structured evidence is
`qa/unit-021-evidence/structure-and-pdf-qa.json`, 13,834 bytes, SHA-256
`110959bf80801379ec2d1cee26aaa969fd4b288cd752adc8fa9d891f1e3e697e`.
The final visual report is `qa/UNIT_021_VISUAL_QA_20260824.md`, 6,813 bytes,
SHA-256
`b87cc24343d7a3d748a1b7af8bb1cf7ca8e5a0fda48fc589addf23bfc64021d4`.

## Modular backend

The canonical record
`backend/data/unit-021-bab-3-struktur-kepang.json` is 275,815 bytes,
SHA-256
`9e6ee43fcca4856a0ade17aecddf3273f441414797b0af80a7934135ff17453c`.
It contains 404 stable entities, including 334 concept-compatible entities,
nine labels, thirteen reference occurrences, two citation occurrences over
one native bibliography record, 156 formula entities, 23 diagrams, eight
index entries, nine terminology bindings, three declared interventions, and
eighteen prerequisites.

The six deterministic CSV projections are:

- `unit-021-bindings.csv`: 25,772 bytes, SHA-256
  `4d4ded991c63e4ab2cddcfa2135c378324e0109f1a0d3d53897a5beab7859537`;
- `unit-021-entities.csv`: 73,000 bytes, SHA-256
  `85e52ee1c93db3f489d07ceb13e3edc09f30ed4e1a6ded5d2c9aa0841694c588`;
- `unit-021-qa.csv`: 4,212 bytes, SHA-256
  `c370346e07dcf6e62e8d9aefe23d4d63c889e506e8aaeb2efabea1f42153327e`;
- `unit-021-relations.csv`: 189,214 bytes, SHA-256
  `f5d8f5f591cf6b02cbb80a51b6f2cbb77bbf5d45bf84cb25cf564c1509aa0a45`;
- `unit-021-rights.csv`: 1,287 bytes, SHA-256
  `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e`;
- `unit-021-surfaces.csv`: 6,838 bytes, SHA-256
  `9652a8511751fae1546acc00e79c239c6549aabc1d77a3a9e16e87ab0dbdaea4`.

Two consecutive generator runs reproduced all seven backend outputs
byte-for-byte. Both the dedicated Unit 021 validator and shared schema,
UUIDv5, relation, ordering, live-hash, rights, build, terminology,
correction, and QA validator pass. Validation evidence is
`qa/unit-021-evidence/backend-validation.json`, 3,980 bytes, SHA-256
`4e84a588f5d4217e47542f67da6af886a9686af53096b109eb3f18b753ea0984`.

## Rights and provenance

Wen-Wei Li remains the source author. Principal source text and Indonesian
translation are CC BY 4.0. The credited `AJbook.cls` fragment retains CC
BY-SA 3.0; `Lanzhou.png` in the wider closure also retains CC BY-SA 3.0 but is
not used by this reader; bundled Noto fonts retain OFL 1.1. Rights are not
flattened into one blanket claim. This is an independent, non-endorsed
derivative.

Production provenance is separate from authorship and records the exact
identification `OpenAI Codex gpt-5.6-sol, Ultra`.
