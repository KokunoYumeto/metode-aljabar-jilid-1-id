# Figshare publication blocker — 0.4.0 attempt

Date: 2026-08-23

The intended existing work-level article was `33314766` (previous DOI lineage
`10.6084/m9.figshare.33314766.v3`) under project `280296` and Indonesian
collection `8668413`. Public API/UI checks now return HTTP 404 for that article;
the project and collection exist but expose no matching item. No competing
article was created.

The supplied local Figshare credential note was read only at runtime. The
official `/v2/token` endpoint returned HTTP 403 `InactiveAccount`, so no upload,
metadata mutation, project membership change, or collection insertion was
attempted. The verified reader-first payload remains local at
`tmp/release-0.4.0-20260823-zenodo/` and is below the 500,000,000-byte work
cap. Its exact staged inventory is preserved in
`qa/RELEASE_0.4.0_LOCAL_PAYLOAD_20260823.json`, 4,290 bytes / SHA-256
`5f173bf2b260b9596b3c4a30b91867113f09dbd664d047221679f2d19c497c61`. No
incompatible or substitute license was asserted, and no public 0.4.0 Figshare
claim is made.

Resume only with a working account credential and a fresh check for an
existing work item; if none exists, create exactly one work-level item under
the named project and collection, preserving the exact component rights and
anonymous full-byte readback requirement. No credential material is recorded
here.
