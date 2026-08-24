# Unit 024 mathematics and canonical-structure audit — 2026-08-25

## Disposition

**PASS.** The complete Chapter 3 exercise block is integrated in source order.
Every exercise, nested item, hint, reference, formula, index entry, and diagram
is present. The three prepromotion changes are prose refinements only. The sole
mathematical intervention, `O013-LI-U024-COR-001`, repairs a demonstrably false
source demand and is disclosed rather than silently attributed upstream.

Model provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.

## Frozen identities and boundary

- Authority: `chapter3.tex:873-911`, 39 LF records, 4,954 bytes, SHA-256
  `2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857`.
- Final Indonesian candidate: 39 LF records, 6,071 bytes, SHA-256
  `576c39746534853cd5127298cf0c2ba7f6afb239e4d7b83f368b7a9969c5f43a`.
- Canonical target: `repo/source/chapter3.tex`, 910 LF records, 89,608 bytes,
  SHA-256
  `443b71b515aef66c6ba8e259e65083604d227370c1ee7ca3ed49bdb5996f45fb`.
- Integrated target span: lines `872-910`, byte-identical to the candidate.
- Preserved admitted prefix: target lines `1-871`, 83,537 bytes, SHA-256
  `96da59f64d8c6ec8185bd1e35fa434ada484cfd9f3d533a7069d8aef95728542`.
  A narrow byte comparison against public base commit
  `8393b331180a4e87d52488801abcb53b413dd1b7` confirms equality.
- The authority and target both end after this exercise environment; no
  untranslated Chapter 3 suffix remains.

## Protected topology

The isolated checker, independent prepromotion verifier, and canonical
structure checker agree on:

- eight top-level exercises and three nested construction clauses;
- two hints;
- four references, with identical targets and relative positions;
- one `YBE` index entry;
- 69 position- and value-identical inline mathematics zones;
- six byte-identical displayed-mathematics blocks;
- two byte-identical `tikzcd` diagrams and eight arrows;
- 248 TeX commands with identical per-line command multisets;
- seven balanced environment pairs and 83 balanced unescaped brace pairs;
- zero Han residue in the Indonesian span.

The complete sequence covers Catalan parenthesizations, commutativity of
`\End(\munit)`, ordinal-sum monoidality, the naturality failure below, both
parts of the Yang--Baxter problem, all Drinfeld-center data, the
`\cate{Ab}`-enrichment check, and the comma-category 2-cell.

## Correction `O013-LI-U024-COR-001`

The source asks the learner to prove that the unique order isomorphisms

```tex
c(\sigma,\tau):\sigma\sqcup\tau\rightiso\tau\sqcup\sigma
```

form a symmetry on finite total orders with all order-preserving maps. The
objectwise isomorphisms exist, but the family is not natural. Take
`\sigma=\sigma'=\tau'=\mathbf 1`, `\tau=\mathbf 2`, the unique map
`f:\mathbf 1\to\mathbf 1`, and constant `g:\mathbf 2\to\mathbf 1`. The two
composites in the naturality square send source ranks `1,2,3` respectively to
`[1,2,2]` and `[1,1,2]`. The target therefore asks whether the family is a
symmetry and, if not, requests a counterexample. This preserves the intended
concept while avoiding an impossible proof.

## Language and terminology closure

The three required refinements explicitly say `isomorfisme natural
antarfungtor`, use the grammatically unambiguous `objek satuan dari`, and call
`\alpha` a `transformasi natural` twice. The seven associated glossary rows
are admitted. The 311-row controlled glossary is 46,585 bytes, SHA-256
`4fa4c6d2720dd7ab9c4ebe570a1124794bc8282af1b4491201fb61b7b973ce1b`.

## Reproduction

- `python -B scripts/check_unit_024_candidate.py`: PASS.
- `python -B build/unit-024-staging/qa/check_unit_024_prepromotion.py`: PASS.
- `python -B scripts/check_unit_024_structure.py`: PASS.

Reader, visual, backend, admission, and publication gates are separate and
remain outside this mathematics/structure receipt.
