# Fastener download check — 23 October 2026

The downloaded fastener folder **passes the local file and published-summary
checks**. All pictures and defect outlines open correctly. Nothing was deleted,
renamed, resized, fitted or sent to a model. The website still shows the starter page.

**Current update:** a replacement download is in `data/downloads/metal_nut/`, with
both notices. Its 430 files pass current checks and match the pinned reference.
A 176/44/115 preparation draft is saved. See [current preparation](DATA_PREPARATION.md)
for actual paths, fingerprints, source limits and next work. Sections below retain
the earlier mirror investigation; old ignored input/report paths are no longer present.

## What was found

Checked folder: `data/downloads/mvtec-ad-metal-nut/metal_nut/`.

| Contents | Files checked |
| --- | ---: |
| Normal training pictures | 220 |
| Normal test pictures | 22 |
| Damaged test pictures | 93 |
| Defect outlines, called masks | 93 |
| Licence notice | 1 |
| Total | 429 |

There are **335 photographs**, each decoded as **700 × 700 pixels**. The 93
damaged test images comprise `bent` 25, `color` 22, `flip` 23 and `scratch` 23.
Every one has a readable, nonempty binary mask with the same dimensions and
matching defect folder/filename. No missing/orphan masks or exact-byte duplicate
photographs were found. All 428 PNGs passed integrity and full pixel-decoding
checks. All 429 files were hashed, totaling 165,862,034 bytes.

Table 1 of [MVTec's original paper](https://www.mvtec.com/fileadmin/Redaktion/mvtec.com/05_research_teaching/datasets/mvtec_ad.pdf),
linked by the [official dataset page](https://www.mvtec.com/research-teaching/datasets/mvtec-ad),
reports 220 training images, 22 normal test images, 93 defective test images, four
defect groups and side length 700 for Metal Nut. The local counts/dimensions match
that summary. This comparison does **not** compare every local file against an
official per-file checksum list.

## Source identified — third-party mirror

The user identified [MSherbinii/mvtec-ad-metal-nut on Hugging Face](https://huggingface.co/datasets/MSherbinii/mvtec-ad-metal-nut).
On 23 October 2026 the saved local audit was compared with repository revision
`8db7371c35a94709cbb3e69ac69f80d2716e2f8a`. **All 428 photograph/mask SHA-256s and
sizes match** its large-file metadata. No image download was needed for this check.
The revision is the one compared now, not an asserted original download commit.

The mirror has 430 category files, while the supplied folder has 429:

- `readme.txt` is missing locally. It supplies MVTec attribution, the dataset's
  noncommercial licence and the original paper citation. An 881-byte copy from
  the pinned mirror revision is preserved separately under ignored
  `data/source-notices/huggingface-8db7371c35a94709cbb3e69ac69f80d2716e2f8a/`.
  It was not inserted into or substituted for the original download.
- `license.txt` differs in bytes only because the local copy uses CRLF line
  endings and the mirror uses LF. Normalizing those line endings produces equal
  bytes. The mirror's 20,845-byte notice is preserved alongside its readme.
- The mirror's dataset card says **MIT**, while its included notices and the
  [official MVTec page](https://www.mvtec.com/research-teaching/datasets/mvtec-ad)
  identify **CC BY-NC-SA 4.0**. The card metadata is not used to relicense images.
  Its unrelated model-performance claim is not this project's evidence.

Read-only comparison used the public API category tree:
`https://huggingface.co/api/datasets/MSherbinii/mvtec-ad-metal-nut/tree/8db7371c35a94709cbb3e69ac69f80d2716e2f8a?recursive=true&limit=1000`.
The response had no continuation page. All 428 PNGs had matching LFS SHA-256/size
metadata. The non-LFS licence first failed exact Git-blob/size comparison; fetching
its small pinned notice established the line-ending-only difference. The first
comparison's missing/mismatched notices remain visible in
`data/metal_nut.source-check.v1.json`; the explanation and separately retained
notice hashes are in `data/metal_nut.source-check.v2.json`. The original audit is
unchanged. No personal details, images or credentials were sent to the service.

This establishes agreement with a third-party repository, **not** official
acquisition. `DATA-SOURCE-001` still requires data from an official source. Next,
the user completes [MVTec's own download step](DATA_SOURCES.md#your-download-step--mvtec-ad)
and saves its unchanged archive in `data/downloads/official/`. The agent can then
compare it without discarding the supplied files.

## What remains unknown

The supplied folder contains unpacked images, not a separate Git checkout: no
`.git` entry was found at either download-folder level. Git commands from there
resolve to the parent application repository; its checkpoint is not dataset
provenance. No repository URL or dataset commit can be recovered from that layout.

The source URL is now recorded in the separate source check above. Acquisition
time and original archive/hash remain unknown. These were `null` in the original
local audit, whose `local_source_unverified` status is preserved as a historical
record. Official acquisition or comparison with an authorized official copy is
still needed before accepting the mirror as benchmark evidence.

The included `license.txt` identifies Attribution-NonCommercial-ShareAlike 4.0
International. Its 21,283 bytes have SHA-256
`f49cf55a29781741358cbd12947832813b1d014d7432fce94e8e21d3c976a75d`.
This records the included notice; it does not certify source authenticity or
publication suitability. No visual mask-overlay alignment, related-image/near-
duplicate audit, preparation split or AI performance has been verified here.
Only the selected fastener category is present; the separate AD2 surface track
remains unacquired.

## Reproduce the check

Working folder: `C:\Users\Longin\Desktop\Projects\computervision_in_manufacturing`.
The following command **was executed**:

```powershell
.\.venv\Scripts\python.exe -m pipeline.audit_mvtec_ad_directory data/downloads/mvtec-ad-metal-nut/metal_nut --output data/metal_nut.local-audit.v1.json
```

Purpose: read and fingerprint the unpacked category, decode its PNGs, check mask
pairing and compare the published count/dimension summary. Result: exit 0,
`PASS local file integrity: 429 files`, and `Published count/dimension summary:
MATCH; original source UNVERIFIED`. The report is ignored local data, with no
private absolute paths. Its membership fingerprint is
`388343e5141dbe3b0a36defd2f478ca9bce20e8deba38c231a35c74a4c2826b5`.
It hashes the path/size/SHA-256 list, sorted by relative path and encoded as compact
UTF-8 JSON with sorted object keys. It is a local fingerprint, not a published
MVTec checksum.

For another run, use a **new** output filename such as
`data/metal_nut.local-audit.v2.json`; existing reports are never overwritten.
The checker writes a diagnostic report but exits 1 when the summary differs.
Unreadable files or broken mask relationships fail without a successful report.
Excluded private/configuration entries prevent a summary match. Original dataset
files stay untouched.

Verification of the tool: 123 pipeline tests passed, including seven new generated
directory cases for repeatable fingerprints, unknown provenance, summary mismatch,
report preservation, corrupt/missing assets, excluded paths, links and duplicate
reporting. No extra dependency was needed. Dataset checking is separate from those
synthetic tests; routine tests do not require or download the real dataset.

Next: acquire/compare the official archive, retain its acquisition evidence, then
build the fixed preparation split and validated real-image manifest. The data
requirement remains partly incomplete until official provenance is resolved.
