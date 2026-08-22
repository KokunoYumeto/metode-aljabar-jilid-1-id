# Modular backend

This directory contains the language-neutral, hash-bound backend for the O013
edition. Canonical records for the admitted reader units are
`data/unit-001-pendahuluan.json`, `data/unit-002-bab-1-zfc.json`,
`data/unit-003-bab-1-struktur-urutan-dan-ordinal.json`, and
`data/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.json`,
`data/unit-005-bab-1-kardinal.json`,
`data/unit-006-bab-1-semesta-grothendieck.json`, and
`data/unit-007-bab-1-latihan.json`; files in `csv/` are deterministic
projections, not independent sources of truth.

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
one LF, and hash the resulting UTF-8 bytes. For an unranged binding, the live
file must match its exact byte count and hash. For a ranged binding, the exact
file identity is retained as the admission-time witness while the normalized
span is the live integrity boundary. Later translation outside an admitted
span therefore cannot invalidate the earlier unit.

Units 001 through 007 are `admitted` and `visually_checked`. Admission
requires passing translation, build, and visual states plus bound reader,
build-summary, build script, and QA-receipt evidence. A green backend
validation proves that the schema, identities, references, order, hashes,
citations, diagrams, brace-aware index provenance, admission state, and
projections agree with the live files; it does not substitute for the human
language and all-page visual audits recorded in the bound receipt.

Schema v1.1.0 has no first-class exercise, subpart, or hint arrays and its
current validator requires those scalar surface counts to remain zero. Unit 007
therefore retains all six exercises as ordered section entities and gives every
one of its six subparts and six hints a deterministic concept-compatible UUIDv5
entity linked to the parent exercise. The live topology gate and QA event record
the true `6/6/6` surface census; this compatibility encoding does not relabel
learner exercises as ordinary exposition concepts.

## Validation and export

From the lane root, run:

```text
python -B scripts/validate_backend.py --data backend/data/unit-001-pendahuluan.json --write-csv
python -B scripts/validate_backend.py --data backend/data/unit-002-bab-1-zfc.json --write-csv
python -B scripts/validate_backend.py --data backend/data/unit-003-bab-1-struktur-urutan-dan-ordinal.json --write-csv
python -B scripts/validate_backend.py --data backend/data/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.json --write-csv
python -B scripts/validate_backend.py --data backend/data/unit-005-bab-1-kardinal.json --write-csv
python -B scripts/validate_backend.py --data backend/data/unit-006-bab-1-semesta-grothendieck.json --write-csv
python -B scripts/validate_backend.py --data backend/data/unit-007-bab-1-latihan.json --write-csv
python -B scripts/validate_backend.py --data backend/data/unit-001-pendahuluan.json
python -B scripts/validate_backend.py --data backend/data/unit-002-bab-1-zfc.json
python -B scripts/validate_backend.py --data backend/data/unit-003-bab-1-struktur-urutan-dan-ordinal.json
python -B scripts/validate_backend.py --data backend/data/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.json
python -B scripts/validate_backend.py --data backend/data/unit-005-bab-1-kardinal.json
python -B scripts/validate_backend.py --data backend/data/unit-006-bab-1-semesta-grothendieck.json
python -B scripts/validate_backend.py --data backend/data/unit-007-bab-1-latihan.json
```

Each command with `--write-csv` validates one canonical JSON record and then
rewrites that unit's six CSV views deterministically. The commands without the
flag validate again and compare every projection byte-for-byte. The script uses
only the Python standard library and rejects
unsafe paths, missing files, hash drift, duplicate or nondeterministic IDs,
unresolved references, unordered sections, citation/ref drift, diagram-count
drift, index-key drift, and stale projections.

`scripts/generate_unit_003_backend.py` and
`scripts/generate_unit_004_backend.py` and
`scripts/generate_unit_005_backend.py` and
`scripts/generate_unit_006_backend.py` and
`scripts/generate_unit_007_backend.py` reconstruct their units' canonical JSON
from reviewed source/target spans, artifacts, build inputs, and bound QA
evidence. They are deterministic for unchanged admitted inputs; rerun one only
when intentionally re-admitting that exact unit boundary.

After a reviewed derivative-source edit changes an unranged bound file, or
changes bytes inside a recorded semantic line range, the explicit
`--refresh-derivative-bindings` option may be added to that unit's export
command. It refreshes only paths under `repo/`; immutable `authority/` and
`00_control/` bindings are never rewritten automatically. Ranged bindings keep
their admission-time whole-file witness and refresh only their live span hash.

## CSV views

- `unit-NNN-entities.csv`: normalized entity inventory;
- `unit-NNN-relations.csv`: contains/covers/requires/rights/surface links;
- `unit-NNN-bindings.csv`: exact source, target, authority, rights, and build
  bindings;
- `unit-NNN-rights.csv`: component-level rights and required treatment;
- `unit-NNN-surfaces.csv`: citations, diagrams, index entries, and build surface;
- `unit-NNN-qa.csv`: narrowly typed QA event state.

JSON is retained as the lossless representation because nested localized
labels, component rights, and source/target spans become awkward and fragile in
a single flat table. CSV remains a deterministic normalized exchange
projection, so editors can inspect or merge it without treating rendered PDF
text as source; JSON remains necessary for a lossless round trip.
