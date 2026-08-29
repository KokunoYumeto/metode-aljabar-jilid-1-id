# Fast completion cursor — 2026-08-29

This is the short live cursor. `CURRENT_GOAL_AND_WORKFLOW.md` retains the full
finite terminal workflow and authority chain.

## Complete Li boundary public

- Canonical source: `repo/source/prelude.tex` and `chapter1.tex` through
  `chapter10.tex`; 13,599 normalized-LF records / 1,459,865 bytes; 161 active
  top-level exercises and 51 hints. Translation freeze:
  `qa/LI_COMPLETE_TRANSLATION_FREEZE.json`.
- Complete reader: `artifacts/metode-aljabar-jilid-1-id-lengkap.pdf`, 521 pages,
  2,875,853 bytes, SHA-256
  `c2994530e3da1711d44f8c36315c40874e87f1968d1a81c1432105de2251c2ee`.
- Build log: `qa/LI_COMPLETE_BUILD_FINAL.log`, 113,458 bytes, SHA-256
  `95cb040d490d7dcc91a296b2a254604fa557b16cb07d4130a6dbf8c2b7a447d1`;
  no fatal or unresolved diagnostics.
- Visual receipt: `qa/LI_COMPLETE_VISUAL_QA_20260829.json`; all 521 pages in
  ordered contact sheets plus 24 targeted pages inspected once, PASS.
- Final modular backends: `backend/data/unit-045-*` through
  `backend/data/unit-048-*`, with 24 matching CSV projections and four
  `qa/li-complete-evidence/unit-*-backend-validation.json` receipts; all PASS.
- GitHub content commit: `b5dda2218c5fbd2b7e7fae7e05fdbbe88fdab10e`;
  anonymous readback passed for 58 paths / 8,134,778 bytes.
- Zenodo version `1.0.0`: DOI `10.5281/zenodo.22151447` in existing concept
  `10.5281/zenodo.22059759`; five reader-first files / 70,149,331 bytes all
  passed anonymous full-byte readback. Receipt:
  `qa/ZENODO_PUBLICATION_LI_COMPLETE_1_0_0.md`.

## Complete local four-component boundary

- Duncan: `artifacts/catatan-teori-representasi-duncan-id.pdf`, 114 pages,
  508,546 bytes, SHA-256
  `6779d6467463fde4ef0b4fae147dc63533dff0919eda684120d409f1f5f07d12`;
  seven roots / 8,121 target records / 41 exercises / 4,632 formulas. Backend,
  reproducible build, and all-page visual inspection PASS.
- CRing: `artifacts/pilihan-aljabar-komutatif-cring-id.pdf`, 74 pages,
  378,716 bytes, SHA-256
  `4596fd6a84f829e1e9c14cb87468226d6ef49c653d41886af5fab9f2bd96b5db`;
  six roots / 3,589 target records / nine repairs / three original bridges /
  27 exercises / two hints / 2,651 formulas. Full GFDL closure, backend,
  reproducible build, and all-page visual inspection PASS.
- Original route/mastery: `artifacts/o013-rute-pembelajar-dan-penguasaan-id.pdf`,
  7 pages, 79,365 bytes, SHA-256
  `31af67adf897519a1fef0ed53757c2a3d9d12b5ccc3bdd4cb74e9ce01dd27a18`;
  71 stable IDs, 114 closed references, eight diagnostics, eight mastery
  prompts with hints and answers. Build and all-page inspection PASS.
- Aggregate total: 716 reader pages; translation backlog zero. Controlling
  receipt: `qa/O013_COMPLETE_LOCAL_BOUNDARY_20260829.json`.

## Immediate executable action

Commit and push only the promoted component paths, readers, rights, README, and
durable controls. Anonymously compare every changed public blob. Then publish a
new nonduplicative reader-first aggregate Zenodo record with the four PDFs,
compact source/backend ZIP, rights notice, manifest, and checksums. Use record
license `other-open`, preserve CC BY 4.0 and GFDL boundaries in prose/files,
and anonymously read back every published byte. Do not rerun passing QA.
