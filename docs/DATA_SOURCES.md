# Official data discovery — EN-02-T01

Checked 23 October 2026 (Europe/Warsaw). This records published source information,
not downloaded archives, exact category counts, legal clearance or model evidence.
The [specification](AI_Inspection_Pilot_Lab_SPEC.md) owns category selection.

| Track | Planned data | Published information checked | Still to establish locally |
| --- | --- | --- | --- |
| `fasteners` | MVTec AD, `metal_nut` | Official page describes defect-free training and normal/anomalous test images with pixel annotations | Official archive/access route, selected category counts, hashes, train-to-calibration membership |
| `metal_surfaces` | MVTec AD2, `sheet_metal`, public annotated test portion | Official page describes normal training/validation and separate public/private test portions | Official archive/access route, category layout/counts/hashes, public membership and annotation correspondence |

Sources: [MVTec AD](https://www.mvtec.com/research-teaching/datasets/mvtec-ad),
[MVTec AD2](https://www.mvtec.com/research-teaching/datasets/mvtec-ad-2).
Category names above are the project selections; their acquired archive contents
have not been verified. Private AD2 evaluation is outside this project.

## Licence and publication record

Both official pages identify **CC BY-NC-SA 4.0** and explicitly exclude commercial
use. The [Creative Commons summary](https://creativecommons.org/licenses/by-nc-sa/4.0/)
requires attribution, a licence link, indication of changes, noncommercial use,
and ShareAlike for distributed adaptations; the linked legal code is authoritative.
These are published conditions, not a finding that a particular portfolio release
meets them. Both dataset pages direct uncertain users to contact MVTec.

The specification chooses a personal noncommercial showcase. Before distribution,
record why the actual release fits that purpose, preserve downloaded notices,
credit MVTec and the appropriate dataset publication, identify transformed assets,
and retain the dataset licence separately from any source-code licence. Do not
claim GIS validation, affiliation or endorsement. No publication occurred here.

## Acquisition handoff

The retrieved official pages show a **Fill in the form** download section. This
increment did not inspect/submit that form, supply personal details, contact MVTec,
verify a direct archive URL or download data. The acquisition task must inspect the
official route first. If it requires the user's contact details or an external
message, prepare the exact step and request that missing input/authorization then.
Do not substitute an unofficial mirror just to avoid that step.

Once official access is available:

1. Record the download URL, UTC acquisition time, exact archive filename, byte size,
   SHA-256 and included licence notices. Keep source archives under ignored `data/`.
2. Inspect archive member names before extraction; reject traversal/absolute paths
   and extract only the selected category to an isolated data directory.
3. Inventory every selected image/mask, preserving official test membership. Verify
   decoded dimensions, anomaly labels/masks and exact content hashes. Do not infer
   exact category counts from whole-dataset summaries or fixture metadata.
4. For AD, implement seed-42 sorted-ID shuffling with a documented integer rounding
   rule for the 20% calibration holdout. For AD2 use official normal validation.
   Keep identifiable duplicates/related images together; report test contamination
   without dropping official test members. Record exact split IDs and hashes.
5. Build the identity-transform manifest, run contract and asset checks, and review
   real small defects visually before selecting any resize/model configuration.

No exact counts, archive hashes, measured dimensions, real mask alignment,
distribution suitability or authentic sample outputs are claimed in this increment.
The schema-backed test fixture remains clearly separate from acquired evidence.
