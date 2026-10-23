# Fastener download check — 23 October 2026

The downloaded fastener folder **passes the local file and published-summary
checks**. All pictures and defect outlines open correctly. Nothing was deleted,
renamed, resized, fitted or sent to a model. The website still shows the starter page.

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

## What remains unknown

The supplied folder contains unpacked images, not a separate Git checkout: no
`.git` entry was found at either download-folder level. Git commands from there
resolve to the parent application repository; its checkpoint is not dataset
provenance. No repository URL or dataset commit can be recovered from that layout.

The download URL, acquisition time and original archive/hash remain unknown.
These are `null` in the local audit, whose evidence status is
`local_source_unverified`. The user has been asked for the public repository or
download link. If it is a third-party mirror, the project still requires official
acquisition or comparison with an authorized official copy before accepting it as
benchmark evidence. No unofficial source was silently accepted.

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

Next: establish the source, retain acquisition evidence, then build the fixed
preparation split and validated real-image manifest. The data requirement remains
partly incomplete until provenance is resolved.
