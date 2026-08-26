# Unit 032 terminology audit — 2026-08-26

Status: **candidate terminology corrected and exact glossary promotion
admitted.** The live 465-row glossary is 74,335 bytes, SHA-256
`bb58d18ad5802c5c2159db092f0fc322761f8f9559ea7efd3789ab8d7317e582`.

## Live-glossary corrections applied to the isolated candidate

The independent review found three families in which the isolated 2026-08-25
candidate had drifted from terminology already admitted after its preparation:

- `himpunan kuosien`, `struktur kuosien`, `kuosien dari suatu grup bebas`, and
  `ruang kuosien` are now, respectively, `himpunan hasil bagi`, `struktur hasil
  bagi`, `grup hasil bagi dari suatu grup bebas`, and `ruang hasil bagi`, in
  accordance with the admitted quotient family;
- `ruang topologis bertitik pangkal` is now the admitted `ruang topologis
  bertitik dasar`; and
- the two identity annotations inside the display corresponding to authority
  line 1188 now use the admitted corpus form `unsur identitas`, rather than the
  defining-occurrence synonym `unsur satuan`.

These changes affect Indonesian prose or `\text{...}` only. They do not change
any formula, quantifier, operator, identifier, label, reference, citation key,
index stream, diagram command, environment, or source correction.

## Proposed Unit 032 delta

The bounded proposed delta is
`qa/UNIT_032_TERMINOLOGY_DELTA_20260826.csv`: 4,745 bytes, SHA-256
`a8410a1c9c725d29f142ec877ab91b376e80b8599afe92bdac32d91996b624bd`.
It contains exactly 30 proposed rows. The status-normalized admitted copy is
`build/unit-032-staging/terminology-delta.csv`: 4,745 bytes, SHA-256
`3d742473a35c0bdd890fecbfe3f0dc37e8dc96f8452287c6fadc35dda46d6fad`;
all 30 rows occur exactly once at the live glossary tail.
The rows cover:

- free-word constructions: `monoid bebas`, `alfabet`, `kata`, `konkatenasi`,
  `panjang kata`, `ungkapan tereduksi`, `representasi tereduksi`, and `kata
  tereduksi`;
- amalgamation and presentation theory: `produk teramalgamasi`, `monoid
  komutatif bebas`, `grup komutatif bebas`, `penutup normal`, `presentasi
  grup`, the presentation sense of `relasi`, the two finiteness forms, and
  Dehn's three decision-problem names;
- fields: `teori grup kombinatorial` and `teori rekursi`; and
- graph/topology terms in the Nielsen--Schreier proof: `grup fundamental`,
  `realisasi geometrik`, `verteks`, `sisi`, `sirkuit`, `pohon rentang
  maksimal`, `retraksi deformasi`, `ruang penutup`, and `sifat pengangkatan
  lintasan`.

Existing admitted rows continue to govern `grup bebas`, `produk bebas`,
`jumlah langsung`, `grup kepang`, `ruang topologis bertitik dasar`, and the
complete `hasil bagi` family. The delta deliberately does not duplicate those
rows.

## Candidate decision

The final candidate is 27,910 bytes, SHA-256
`28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc`.
The rebound checker is 18,668 bytes, SHA-256
`318a57bf22d50baef5102ebc07bb9fd83943682b44d01dac4de5150e770a2cc0`
and passes twice with deterministic output. The canonical structure checker
also passes twice, proving exact target integration and glossary-tail identity.
Terminology and canonical integration are therefore safe and complete; reader,
backend, controls, and publication remain downstream.
