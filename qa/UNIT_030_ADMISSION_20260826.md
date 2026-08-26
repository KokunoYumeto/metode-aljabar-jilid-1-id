# Unit 030 local admission receipt — 2026-08-26

Status: **LOCALLY ADMITTED; PUBLICATION AND PUBLIC-BYTE READBACK ARE NEXT.**

This receipt admits the complete Bahasa Indonesia rendering of Section 4.6,
“Deret Komposisi Grup,” as `O013-LI-U030`. It records a local deterministic
boundary only. It does **not** claim a Git commit, push, public release, or
anonymous readback. All paths below are relative to the canonical O013 lane.

## Frozen authority and exact boundary

- Frozen upstream repository: `https://github.com/wenweili/AlJabr-1` at commit
  `c4f7a01f68f5f407906b4b970640cddbbad85f6b`, tree
  `0f9fd52748165ec89a85ba602ccb949a2ce04694`.
- Frozen archive:
  `authority/archives/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b.zip`,
  6,050,739 bytes, SHA-256
  `6c8c416baa8f5ffc8810bbad6470c780413bd7917af739e07340e4b07e7eaff6`.
- Official 445-page PDF: `authority/pdfs/Al-jabr-1.pdf`, 3,647,113 bytes,
  SHA-256
  `dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38`.
- Authority Chapter 4:
  `authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex`,
  154,744 bytes, SHA-256
  `63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3`.
- Exact Unit 030 authority slice: `chapter4.tex:796-935`, 140 normalized-LF
  records, 7,981 bytes, SHA-256
  `7803452c4285c57e419a2cb2a288b3733975555fafd6b7a88c5732da369220c1`.
  Line 935 is exactly the blank boundary record. Section 4.7 begins at line
  936 and remains excluded.
- Authority control: `00_control/SOURCE_AUTHORITY.md`, 1,920 bytes, SHA-256
  `4da3fbed427e175e584a803c21c1d30aed1761dffdfcaae8952d7e44213b1afc`;
  source manifest: `00_control/SOURCE_MANIFEST.csv`, 3,383 bytes, SHA-256
  `40125010171d4fa37c3312c454c3c2767325bcb27c4229c255a25b297265eb99`.

## Candidate, canonical promotion, and mathematical topology

- Reviewed candidate:
  `build/unit-030-candidate/chapter4-group-composition-series-id.tex`, 139
  substantive LF records, 10,044 bytes, SHA-256
  `7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b`.
- Canonical Chapter 4: `repo/source/chapter4.tex`, 1,895 records, 172,726
  bytes, SHA-256
  `245a891930cefb1c18cbd1208386ba5131c56b8b5930510c329577eeeb96cddc`.
- Canonical lines 794-932 are 10,044 bytes, SHA-256
  `7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b`
  and are byte-for-byte identical to the candidate. Canonical line 933 is the
  untouched Section 4.7 sentinel corresponding to authority line 936.
- Candidate checker: `scripts/check_unit_030_candidate.py`, 14,417 bytes,
  SHA-256
  `e8cf6de679203e4cf1173310c88767248463f9961b0dd556286cf863075f0b2e`.
  Fresh command `python -B scripts/check_unit_030_candidate.py`: **PASS**.
- Canonical checker: `scripts/check_unit_030_structure.py`, 9,684 bytes,
  SHA-256
  `a5be61b32119946f587dab1471e7d1c5fd89082a683646e49c68554c0997683d`.
  Fresh command `python -B scripts/check_unit_030_structure.py`: **PASS**.
- The admitted surface has 26 active paired environments / 52 ordered
  begin-end markers, ten labels, eight ordinary references and one equation
  reference, six index entries, 88 protected mathematical zones, six
  `tikzcd` diagrams with 23 arrows, and no citation, exercise, hint, answer,
  or solution surface. Han residue and placeholders are zero.
- One disclosed source correction, `O013-LI-U030-COR-001`, restores the
  uniquely forced missing `\supset` at authority line 895 / target line 893.
  Two diagram-label localizations at authority lines 836 and 839 / target
  lines 834 and 837 change only `\text{...}` prose and preserve diagram
  topology.
- Eight reviewed terminology rows were appended without rewriting the prior
  413 rows. Delta:
  `build/unit-030-staging/terminology-delta.csv`, 1,377 bytes, SHA-256
  `fe0b91971953c8d14568fd1144f0799d8c36b6c6a7cc09be8dd11d688de3c7a4`;
  resulting 421-row glossary: `00_control/TERMINOLOGY.id-ID.csv`, 66,908
  bytes, SHA-256
  `2fdad27f02b31ea2f29f9aecd8ef2e015a456b02636c402c3e985e5e0a5d7991`.

## Modular backend admission

- Schema: `backend/schema/open-math-corpus-unit.schema.v1.json`, 21,358
  bytes, SHA-256
  `bad45d310e429926f1c05283232e6f8ccc7a7461c0c99faea8509497054efbc3`.
- Canonical unit JSON:
  `backend/data/unit-030-bab-4-deret-komposisi-grup.json`, 179,924 bytes,
  SHA-256
  `1dae77cebf984b8a1dfad0a3d90714d3b4f69c0632042cea768939eb1a77f806`.
- Exact CSV projections:

  | Projection | Bytes | SHA-256 |
  |---|---:|---|
  | `backend/csv/unit-030-bindings.csv` | 17,056 | `ee8553d1b18e7804e84200bb2756d321392cf5273268ef52b876e69784400f7d` |
  | `backend/csv/unit-030-entities.csv` | 47,986 | `bb61cc8d97250c98b6b481cb0c3a83e06f0e05aa4b69ec684d96c29dfae93b62` |
  | `backend/csv/unit-030-qa.csv` | 6,622 | `4ee7bde23901f1197913f0714b417a4937a5f07d945af455c185746584c5f4e2` |
  | `backend/csv/unit-030-relations.csv` | 119,343 | `498e6e24f3cea0d9809d380068fd605f9ceed06e9fd31a22a55bcf36110bb32e` |
  | `backend/csv/unit-030-rights.csv` | 1,287 | `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e` |
  | `backend/csv/unit-030-surfaces.csv` | 2,966 | `264aff425f61c6e085de320077edc142cf2fc4988b1705b415130554f0aa625a` |

- Generator: `scripts/generate_unit_030_backend.py`, 52,396 bytes, SHA-256
  `9d48c8edd97506b112d9a58c55a41ac14777055a2cbdfb9cf923a6abd1de93fa`;
  validator: `scripts/validate_unit_030_backend.py`, 25,432 bytes, SHA-256
  `d4ebee5adad836b52ed145786ce2fb5f9e7e9f183b4fa7040bf326724eb0ce1a`.
- Fresh command `python -B scripts/validate_unit_030_backend.py`: **PASS**.
  It verified schema and UUIDv5 integrity, two deterministic regenerations,
  exact CSV projection, all 81 file/line-span binding occurrences over 39
  unique paths, exact source/target boundaries, all TeX surfaces, terminology,
  correction/localization provenance, component rights, build/PDF/visual
  bindings, and that validation mutated no outputs.
- Admitted backend census: one section, 181 stable concept/surface records,
  242 audited UUIDv5 entities, 17 QA events, four visual-QA witnesses, and six
  CSV projections.

## Reproducible build and final reader

- Build script: `scripts/build_unit_030.ps1`, 5,014 bytes, SHA-256
  `25552031826138ecaaf3d17d29752f71fee5f58f0f5105c284f6caa3ba036b6e`.
- Driver: `repo/source/unit-030-bab-4-deret-komposisi-grup.tex`, 5,900
  bytes, SHA-256
  `55a88b462ec61c82800d4936801b6f9cac5ded15261eb6df57351eb30deb312d`;
  cover: `repo/source/coverpage-id-unit-030.tex`, 3,645 bytes, SHA-256
  `02a9d37e2df8ec66f352359f71c6badb71a5b0fdcb79c1b604580a4539342781`;
  cross-unit label witness: `repo/source/unit-030-crossrefs.aux`, 486 bytes,
  SHA-256
  `a49a2bae0c325cd302bcf890d427a0ba2be76837f290ff6fdd2453c11f015bc2`.
- Independent clean build I: 7 pages, 91,960 bytes, SHA-256
  `cb5b2c5279e7c5574457846873a456cb644d2a1d54ace7ddc975378e036e00cd`.
- Independent clean build J: 7 pages, 91,961 bytes, SHA-256
  `43ad2ffa2516f2f4394bcb82ad2e585f21c1e9e36a87870f4406a78597f18d74`.
  Volatile font subset tags explain the one-byte binary difference; normalized
  structure, text surfaces, and same-renderer decoded pixels agree.
- Sanitized final log: `qa/UNIT_030_BUILD_FINAL.log`, 76,370 bytes, SHA-256
  `728d7f4f2845e87132e6bf494784a16eced1b9f9f2644f97a10ae477a9df43f9`.
  It preserves all 2,269 log records and has zero fatal/error, undefined
  reference/citation, missing-character, overfull, Windows-user-path, or local
  profile-name diagnostics. The disclosed release/xeCJK/braids/fontspec and
  underfull-box warnings are non-fatal and visually benign.
- Final reader: `artifacts/unit-030-bab-4-deret-komposisi-grup-id.pdf`, seven
  pages, 91,961 bytes, SHA-256
  `43ad2ffa2516f2f4394bcb82ad2e585f21c1e9e36a87870f4406a78597f18d74`;
  byte-identical to build J.
- Fresh strict PDF inspection confirms `%PDF-1.7`, unencrypted, `/Lang id-ID`,
  exact title/author/subject metadata, no form or active payload, 25 resolving
  named destinations, eleven closed `/GoTo` actions, three HTTPS `/URI`
  actions, three outline entries, and 21 embedded fonts. The PDF is untagged;
  no tagged-accessibility claim is made.

## Visual and PDF evidence

- Preflight: `qa/UNIT_030_VISUAL_PREFLIGHT_20260826.md`, 1,847 bytes,
  SHA-256
  `5b7ec706ac995b08a7ddbc10953156bddd75250a575ba9019ee3f1f266edd41d`.
- Full review: `qa/UNIT_030_VISUAL_QA_20260826.md`, 6,557 bytes, SHA-256
  `5a4f2992a1251b58bf293a0fd5388e1db3c6fb0a093ece6b8104010dd567e033`.
- Structural/PDF evidence:
  `qa/unit-030-evidence/structure-and-pdf-qa.json`, 57,377 bytes, SHA-256
  `5b11c997ca331611871e22928f560f89757651053803bffc91ac1d118b89be02`.
- Render inventory:
  `qa/unit-030-evidence/render-hash-inventory.json`, 34,392 bytes, SHA-256
  `2d77180e791121c76abbf097936bc69036113c1bebb3232346897619d4f9b131`.
- Poppler and MuPDF each rendered all three PDFs across all seven pages: 42
  full-page renders. Every build-I/build-J and build-J/artifact same-renderer
  decoded-pixel comparison passed; all 42 outer three-pixel bands contain zero
  ink. Both seven-page contact sheets were inspected again for this receipt.
  No clipping, collision, overflow, broken mathematical stroke, tofu box,
  missing label, edge contact, ambiguous progress block, or unintended sparse
  page was found. Verdict: **PASS WITH WARNINGS; zero actionable defects**.

## Rights and attribution disposition

- Rights statement: `LICENSES.md`, 1,545 bytes, SHA-256
  `5e09add2b65bd432824f52c5b581c7349db274ef89066fb189f05fd31ce0af29`;
  source notice: `repo/source/LICENSE`, 19,045 bytes, SHA-256
  `48a83a6e39f7b2f166763b30776132c9a99aa816f17cb06f87ad5b8542a7b71f`;
  machine projection: `backend/csv/unit-030-rights.csv`, 1,287 bytes,
  SHA-256
  `4836630530f87a11a64fe233c59970e2ff7942695a8dbf404f7a0583a275197e`.
- The principal source text and Indonesian translation are CC BY 4.0, with
  source/author attribution, identification of translation and changes,
  license link, and non-endorsement retained.
- The credited `AJbook.cls` fragment is separately CC BY-SA 3.0 and applies to
  this build; the embedded Noto fonts are separately OFL 1.1. `Lanzhou.png` is
  separately CC BY-SA 3.0 but is marked not applicable to Unit 030. The
  aggregate closure is therefore **not** relabeled as unqualified CC BY 4.0.

## Supporting review identities

- `qa/UNIT_030_TRANSLATION_REVIEW_20260825.md`: 8,672 bytes, SHA-256
  `958408aac2f261622973be5248932525e2d54399df3c798201bc9ea70a25cf85`.
- `qa/UNIT_030_TERMINOLOGY_AUDIT_20260826.md`: 1,241 bytes, SHA-256
  `45e11fd3eb0da54792fff0a7c7c5e5ffcb6207c053dec39b310dc46c338d49f6`.
- `qa/UNIT_030_PREPROMOTION_AUDIT_20260826.md`: 1,583 bytes, SHA-256
  `f33ae9745fe4f6b9eab05efab034d2681c2e94b88bc105325269e804079370df`.
- `qa/UNIT_030_FINAL_AUDIT_20260826.md`: 4,610 bytes, SHA-256
  `c752b8eb28c4f2667f501b4b0298e521cd01752724139b947029f8f6f1032baf`.
  Its “isolated candidate only” wording accurately describes that audit's
  write boundary; the later canonical, backend, build, PDF, and visual gates
  recorded above complete local admission without rewriting that witness.

Production and review provenance is recorded as **OpenAI Codex gpt-5.6-sol,
Ultra**, acting on the user's instruction. Source-author and contributor
credits remain intact.

## Admission decision and next transaction

The authority boundary, complete Indonesian candidate, canonical splice,
terminology append, mathematical/TeX topology, stable backend, component
rights, reproducible build, seven-page reader, and all-page visual evidence
are mutually hash-bound and pass their deterministic gates. Unit 030 is
therefore **locally admitted**.

Next: commit and push the exact admitted file set to the existing public lane,
then anonymously read back the public control and reader bytes and compare
their sizes and SHA-256 values before advancing the durable cursor. Until that
transaction succeeds, this receipt makes no public-state claim.
