# Modular backend

This directory contains the language-neutral, hash-bound backend for the O013
edition. The canonical record for the first reader unit is
`data/unit-001-pendahuluan.json`; files in `csv/` are deterministic projections,
not independent sources of truth.

## Identity model

Every entity has a readable `stable_key` and a deterministic UUIDv5 URN. The
namespace is derived from the official upstream repository URI, while entity
keys omit mutable titles, translated wording, page numbers, and locale. The same
unit, section, concept, exercise, hint, or asset can therefore acquire another
language expression without changing semantic identity.

UUIDs make the identifiers globally collision-resistant; stable keys keep them
auditable by humans. The validator proves that every UUID was generated from
the recorded namespace and stable key rather than assigned ad hoc.

## Hash model

File bindings carry exact byte counts and SHA-256 hashes. Semantic TeX spans
also carry a normalized line-span hash named `sha256-utf8-lines-lf-v1`: decode
as UTF-8, select the inclusive one-based line range, join lines with LF, append
one LF, and hash the resulting UTF-8 bytes. Exact file hashes detect every byte
change; normalized span hashes let equivalent line-ending changes be compared
without weakening the exact binding.

Unit 001 is `admitted` and `visually_checked`. Its admission requires passing
translation, build, and visual states plus bound reader, build-summary, build
script, and QA-receipt evidence. A green backend validation proves that the
schema, identities, references, order, hashes, citations, diagrams, index
provenance, admission state, and projections agree with the live files; it
does not substitute for the human language and all-page visual audits recorded
in the bound receipt.

## Validation and export

From the lane root, run:

```text
python -B scripts/validate_backend.py --write-csv
python -B scripts/validate_backend.py
```

The first command validates the canonical JSON and then rewrites all CSV views
deterministically. The second command validates again and compares every CSV
byte-for-byte. The script uses only the Python standard library and rejects
unsafe paths, missing files, hash drift, duplicate or nondeterministic IDs,
unresolved references, unordered sections, citation/ref drift, diagram-count
drift, index-key drift, and stale projections.

After a reviewed derivative-source edit changes bytes without changing the
recorded semantic line ranges, `--refresh-derivative-bindings` may be added to
the first command. It refreshes only paths under `repo/`; immutable
`authority/` and `00_control/` bindings are never rewritten automatically.

## CSV views

- `unit-001-entities.csv`: normalized entity inventory;
- `unit-001-relations.csv`: contains/covers/requires/rights/surface links;
- `unit-001-bindings.csv`: exact source, target, authority, rights, and build
  bindings;
- `unit-001-rights.csv`: component-level rights and required treatment;
- `unit-001-surfaces.csv`: citations, diagrams, index entries, and build surface;
- `unit-001-qa.csv`: narrowly typed QA event state.

JSON is retained as the lossless representation because nested localized
labels, component rights, and source/target spans become awkward and fragile in
a single flat table. CSV remains a deterministic normalized exchange
projection, so editors can inspect or merge it without treating rendered PDF
text as source; JSON remains necessary for a lossless round trip.
