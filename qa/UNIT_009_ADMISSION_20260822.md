# Unit 009 admission receipt - Bab 2: Kategori dan Morfisme

Date: 2026-08-22

Decision: admitted as the ninth independently buildable `id-ID` reader unit.

## Frozen source and target

- Upstream repository: `https://github.com/wenweili/AlJabr-1`
- Upstream commit/tree: `c4f7a01f68f5f407906b4b970640cddbbad85f6b` / `0f9fd52748165ec89a85ba602ccb949a2ce04694`
- Complete frozen `chapter2.tex`: 139,983 bytes; SHA-256 `56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840`.
- Complete Section 2.1 boundary, lines 39-198: 16,442 bytes; SHA-256 `1fa6ecc8f3ec477611f05ddd07297f9e115b7bb118e5fd5be4b7981cde7747ae` under `sha256-utf8-lines-lf-v1`.
- Current target `repo/source/chapter2.tex`: 145,511 bytes; SHA-256 `09231954639e6c12b1dd3107e9e4ff5af6113de1970010a49f23dc2ec8fb5f7b`.
- Indonesian target boundary, lines 39-198: 20,682 bytes; SHA-256 `b20dfbefb909ffe91c4857df6c183dffbdd7fd2c316156f5d7d9274efa3b41e2` under `sha256-utf8-lines-lf-v1`.

## Translation, mathematics, and topology

The complete source-order Section 2.1 was translated into natural formal
Indonesian. The protected source and target each retain 25 balanced
environments, seven labels, ten references, five citation occurrences, 31
index entries, 28 ordinary list items, eighteen emphasis spans, and 268
mathematical surfaces. The normalized mathematical multiset is exact. Four
`tikzcd` surfaces and one `tikzpicture` surface preserve their source bodies and
all eleven arrows. The unit contains no exercise, hint, answer, or solution.

Independent structural, mathematical, semantic, and Indonesian-language
review found no remaining P1 or P2 defect. The final target span and the ten
cover/content PDF pages contain no Han-script residue, replacement character,
or NUL.

The seven protected labels, in source order, are `sec:cat-and-morphism`,
`def:category`, `def:subcategory`, `def:U-cat`, `con:U-small`,
`eg:categories`, and `eg:fundamental-groupoid`. The ten protected reference
occurrences, in source order, are `def:monoid`, `def:group`,
`sec:Grot-universe`, `hyp:universe`, `def:partial-order`, `sec:order`,
`eg:Ab-cat`, `sec:enriched-cat`, `con:U-small`, and the second
`sec:Grot-universe`. The five citation occurrences retain keys `Xiong`,
`May99`, `You`, `Xiong`, and `May99`, with only their prose locators localized.

## Disclosed interventions

- `O013-LI-U009-CORR-001`: normalize the proper name `MacLane` to the standard
  spelling `Mac Lane` without changing the attribution.
- `O013-LI-U009-CORR-002`: repair the authority's punctuation/spacing sequence
  `) .我们` as ordinary Indonesian sentence punctuation.
- `O013-LI-U009-SOURCE-NOTE-001`: retain the authority's inconsistent
  `\text{Vect}_f` notation exactly rather than silently changing it to
  `\cate{Vect}_f`.
- `O013-LI-U009-CLR-001`: state explicitly that the displayed ordinal chain
  omits non-adjacent composite arrows as well as identity morphisms. The source
  diagram already omits both but names only identities in its parenthesis.
- `O013-LI-U009-REFLOW-001`: wrap that same wide ordinal display in a local
  `\small` group. The first build exposed a 17.89233-point overfull box; the
  admitted build is centered and has zero overfull boxes, while the display's
  mathematics and line boundary remain unchanged.

## External-reference witness

`repo/source/unit-009-crossrefs.aux` freezes eight official-book destinations
outside the standalone unit: Definitions 4.1.1 and 4.1.2; Section 1.5 and
Hypothesis 1.5.2; Definition 1.2.1 and Section 1.2; Example 3.4.7 and Section
3.4. Values and page labels were checked against the frozen source counter
rules and official 445-page PDF. The driver imports the numbers with an empty
external URL so the references print correctly without advertising links to
an absent companion PDF.

## Exact admitted build

- Driver: `repo/source/unit-009-bab-2-kategori-dan-morfisme.tex`, 4,445 bytes, SHA-256 `7fa5b0da8f6b1aacc12ec8eb6fea4df5e2ead8a0c079dfadb5bbaa78ccb97a17`
- Cover: `repo/source/coverpage-id-unit-009.tex`, 4,337 bytes, SHA-256 `8152b057d0be2e273be23bf29d97a585f4b6bb80ba7e8100b47da97691c15672`
- Frozen cross-reference witness: `repo/source/unit-009-crossrefs.aux`, 554 bytes, SHA-256 `95ec27bcb09377a1a90f1d956bda68242191b53f50db2a091d8e42c1d9fcb755`
- Build script: `scripts/build_unit_009.ps1`, 2,851 bytes, SHA-256 `8242117c53dd3ad9176416311ef3953ca33e1baaf0ed553ed777f0d808639add`
- Structural gate: `scripts/check_unit_009_structure.py`, 10,719 bytes, SHA-256 `fc463ca895eca1ae783c74cba1ff1f68dcfbe5a1f30f4cc25596a0ff24701932`
- Backend generator: `scripts/generate_unit_009_backend.py`, 41,880 bytes, SHA-256 `3e21c8738fdbcea91f6b06aeb59737361f34fe60b64904387ef2ac4f6d9a1d70`
- Reader: `artifacts/unit-009-bab-2-kategori-dan-morfisme.pdf`, 13 pages, 143,207 bytes, SHA-256 `1a71610ba997348ce22db69944fec3529d9d6e6c2ef6ece48faa30df90ac5ce6`
- Final log: `qa/UNIT_009_BUILD_FINAL.log`, 85,064 bytes, SHA-256 `523242a89f71a31d03a3bd753e125a4dac4bb7e79b4a3e93fafb0cd122c689bf`
- Clean comparison PDF: 143,192 bytes, SHA-256 `ea4f2845bdb0b3dc04aac01fe6fd1b15a2227e69b0ae0c7f69a1496d479e777b`; all thirteen Poppler and all thirteen MuPDF page PNGs and extracted text are pairwise identical to the admitted build.

The final log has zero TeX errors, undefined citations or references, duplicate
destinations, missing characters, or overfull boxes. One inherited underfull
cover-table alignment is visually acceptable. Nine hyperref warnings are the
deliberate consequence of suppressing false external links while retaining
frozen reference numbers. Deterministic rendered pages and semantic text
equality are established; bit-identical XeTeX PDF containers across output
directories are not claimed.

## PDF and all-page visual QA

The admitted PDF has catalog language `id-ID`, thirteen nonblank pages, four
outline entries, 49 named destinations, 42 internal GoTo annotations, and three
intentional URI annotations. It has no form, widget, embedded file, JavaScript,
GoToR, Launch action, encryption, replacement character, or NUL. All 28 fonts
are embedded and subset; only the CMSY10 mathematics subset lacks a ToUnicode
map. MuPDF and Poppler rendered every page, and all pages were inspected without
clipping, collision, missing glyph, unreadable formula, or blank page.

The main prose fills the page consistently. The commutative diagrams and
fundamental-groupoid drawing remain crisp, the ordinal display is centered and
legible after its narrow reflow, and the bibliography and both indexes are
readable. The two Chinese bibliography titles are intentional source metadata.
The PDF remains untagged and is not represented as tagged-PDF conformance.

## Backend representation

The language-neutral backend assigns stable UUIDv5 identities to the unit,
section, seven labels, ten reference occurrences, five citation occurrences,
31 index entries, five diagram surfaces, build surface, component rights, and
QA event. Repeated citation keys are occurrence-specific. Source/target hashes,
mathematics, topology, build evidence, intervention provenance, and component
rights are fail-closed inputs to generation and validation.

## Rights and provenance

The source text and Indonesian translation are handled under CC BY 4.0 with
Wen-Wei Li credited and independent, non-endorsed derivative status stated.
The attributed `AJbook.cls` fragment remains CC BY-SA 3.0 and bundled Noto
fonts remain OFL 1.1. No component rights are flattened.

The 2026-08-22 terminology QA changed the attested technical term `funktor` to
`fungtor` in this unit. The primary evidence and keep/change adjudications are
recorded in `qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md`.
The structural gate and all-page QA were rerun; mathematics, identifiers,
topology, and pagination are unchanged. Model: OpenAI Codex gpt-5.6-sol,
Ultra.

## Cursor and publication state

Unit 009 completes Section 2.1. The next contiguous source-order target begins
at `chapter2.tex:199`, Section 2.2. GitHub access is restored; after backend
validation this complete boundary must be narrowly committed, pushed to the
existing public corpus repository, and anonymously read back. Zenodo and
Figshare remain the same existing work-level lineages and must receive only a
coherent linked checkpoint update, never a duplicate concept.
