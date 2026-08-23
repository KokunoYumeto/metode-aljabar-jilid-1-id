# Zenodo publication blocker — 0.4.0 attempt

Date: 2026-08-23

The existing Zenodo concept was selected through the authorized
`actions/newversion` route. The resulting draft is record `22071178` with
pre-reserved DOI `10.5281/zenodo.22071178` and concept DOI
`10.5281/zenodo.22059759`. No new concept was created.

The local, verified 0.4.0 payload is retained at
`tmp/release-0.4.0-20260823-zenodo/`. It contains the 128-page reader,
compact source/backend ZIP, `20-LICENSES.md`, manifest, checksums, and twelve
admitted unit readers. Its Figshare-sized common payload is 72,492,306 bytes;
the source ZIP is 70,504,782 bytes / SHA-256
`7f5f6f1a8877ad8f14d9293ccc45cdb1a191e8b7782f76b8c8d530e1cd3bf087`.
The complete staged inventory is preserved in
`qa/RELEASE_0.4.0_LOCAL_PAYLOAD_20260823.json`, 3,966 bytes / SHA-256
`5f173bf2b260b9596b3c4a30b91867113f09dbd664d047221679f2d19c497c61`.

The inherited 0.3.0 draft files were being replaced in that existing draft.
Zenodo then began returning gateway timeouts and finally an explicit HTTP 403
response:

> Access to this resource has been restricted due to unusual traffic from
> your network.

Because the service block prevents a reliable inventory/readback/publish
transaction, this lane makes no public 0.4.0 claim and does not retry through
an alternate proxy or evade the restriction. The draft ID and local payload
are the exact resume points once the platform accepts requests again. No
credential material is recorded here.
