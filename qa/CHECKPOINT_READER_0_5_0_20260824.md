# Checkpoint Reader 0.5.0 - Build and QA Receipt

Date: 2026-08-24  
Status: **PASS; ready for the parent lane's admission/publication workflow**

## Artifact

- path: `output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-0.5.0-reader.pdf`
- coverage: Pendahuluan, complete Chapter 1, and complete Chapter 2;
  18 admitted units in source order; Chapters 3-10 are not included
- physical pages: 183 (one checkpoint cover plus 182 admitted unit pages)
- bytes: 2,852,514
- SHA-256: `89ee546c7fc462dc2b050db36a5e130e391d628808f61c938ddd1e9f81f0e7eb`
- unit start pages: 2, 23, 35, 46, 54, 66, 75, 79, 84, 97, 112,
  119, 129, 136, 145, 155, 171, 180
- deterministic second build: byte-identical, same SHA-256

The cover names Wen-Wei Li as author, states exact partial coverage and
non-endorsement, preserves CC BY 4.0 / CC BY-SA 3.0 / OFL 1.1 component-rights
boundaries, and uses the exact provenance string `OpenAI Codex gpt-5.6-sol,
Ultra.` It has no filled/unfilled status legend: coverage is ordinary text
under a rule, and the sole filled region is the title masthead.

## Automated QA

- all 182 admitted unit content streams are unchanged after assembly;
- all 182 admitted unit pages are pixel-identical to independently rendered
  source-unit pages under MuPDF at 120 dpi;
- MuPDF and Poppler both rendered all 183 pages;
- expected blank inventory is exactly checkpoint page 5; no other blank or
  empty-text page exists;
- page geometry is 498.90 x 708.66 points throughout, with zero rotation;
- 585 named destinations; 19 top-level outlines in exact source order;
- 398 link annotations: 329 internal GoTo and 69 URI actions; zero broken named
  links, unsafe actions, additional actions, forms, or open actions;
- 446 of 446 discovered font objects are embedded;
- bespoke cover body clears 69 px left, 70 px right, 31 px below-masthead, and
  26 px bottom margins at 120 dpi;
- Poppler reports 149 inherited legacy font-resource diagnostics. A bounded
  replay of the 18 admitted sources reports the same 149 normalized messages
  with an exactly equal multiset, proving the merge introduced zero new
  warning class or count. MuPDF reports zero diagnostics.

## All-page visual QA

All 183 pages were inspected through 16 contact sheets. The cover and
representative transitions at pages 79, 129, 155, 171, and 180 were also
inspected at full 120 dpi resolution. No clipping, overlap, missing content,
broken diagram, black square, unreadable page, or accidental blank page was
observed.

## Evidence identities

- builder: `scripts/build_checkpoint_reader_0_5_0.py`, 11,414 bytes,
  SHA-256 `fd02ffc9cf3f960054526f611abaf3b6c4bd730e8da72b19dc6886c1bd70fff2`
- QA runner: `scripts/qa_checkpoint_reader_0_5_0.py`, 28,187 bytes,
  SHA-256 `16d96a1206323f304d17cb77c11a3a53ff4ebf96e7c53e9c5dfa5411e0b29fa4`
- machine evidence:
  `qa/checkpoint-0.5.0-evidence/structure-text-navigation-font-render-qa.json`,
  100,124 bytes,
  SHA-256 `d04ec5439a2dcc74ea2d0c1194ead868ad9478167d2b4697b9d063ba245aebf3`
- visual receipt: `qa/checkpoint-0.5.0-evidence/VISUAL_REVIEW.md`, 1,281 bytes,
  SHA-256 `024328b2b205ebeb25b46bb8f5f341954980321efc314c8bfc85f41c6ea121f2`
- 16 hashed contact sheets: 22,509,481 total bytes; individual identities are
  recorded in the machine evidence JSON

No canonical unit source, backend, durable control, Git state, or publication
record was changed by this bounded checkpoint build.
