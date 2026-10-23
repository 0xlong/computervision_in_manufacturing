# Official data discovery and acquisition

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

## Your download step — MVTec AD

The blank AD download form was inspected on 23 October 2026. It requires **First
Name, Last Name, Email**, and acknowledgment of noncommercial use. **Position/Function**
and the **MVTec Campus Newsletter** checkbox are optional. No personal values were
entered, form submitted, newsletter selected, or dataset downloaded by the agent.
The form button says **SUBMIT AND CONTINUE TO DOWNLOAD PAGE**. The destination after
submission and exact archive choices have not been inspected. AD2's form has not
been inspected in this increment.

1. In VS Code, run **Browser: Open Integrated Browser**
   (`workbench.action.browser.open`) and open the
   [official AD download section](https://www.mvtec.com/research-teaching/datasets/mvtec-ad#c3391).
2. Complete the required fields yourself with accurate details. Read the linked
   privacy/licence information and acknowledge noncommercial use if applicable.
   Leave the newsletter unchecked unless you want it. Submit the form yourself.
   If the form is missing, the official page advises disabling its ad blocker;
   browser consent settings may also affect embedded forms. The agent has not
   verified interactive rendering in VS Code's integrated browser.
3. On the resulting page, download **metal_nut** if a separate category archive is
   offered. Save the original archive, without unpacking or renaming it, in
   `data/downloads/` inside this project. This ignored folder has been created.
   Keep any accompanying licence/readme notices. If only a full archive is offered,
   share its public download link so the agent can check its size before acquisition.
4. Tell the agent the local archive path, public download URL, and approximate
   download time/timezone. Do not send personal details, form responses, credentials,
   or a private/signed access link. If access is private, download it yourself and
   report the local path; provenance must then record that access limitation rather
   than invent a public URL. The current inventory CLI accepts public HTTPS URLs
   only and will need a scoped change for that case.

The embedded form is supplied by `software.mvtec.com`, linked in the official page
HTML (form ID `c92559d1-5797-4de8-aa04-48d75107de76`, account `43208`). Read-only HTML
and the blank form were retrieved using the normal MVTec page Origin/Referer.
No personal data or submission request was sent. No unofficial mirror was used.

## Local archive checker — ready, official archive still pending

`pipeline.inventory_mvtec_ad` can inspect local TAR, TAR.GZ and TAR.XZ archives
without extracting them. It supports `metal_nut/` at the root or a category-only
`train/test/ground_truth` layout; unfamiliar layouts fail for review. It records
archive byte size/SHA-256, supplied URL/acquisition time, exact selected image/mask
membership, decoded PNG dimensions/modes, per-file hashes, and hashes of other
selected/root-level files, keeping their bytes unchanged in the archive.

The checker verifies PNG integrity and fully decodes pixels, requires nonempty
binary masks for anomalies, matches masks by defect folder/filename, rejects
missing/orphan masks and unequal dimensions, and checks unsafe paths, links,
case-colliding members and resource limits. It preserves every recognized test
member. Other categories are scanned for path/type safety but not decoded.
It never submits a form, makes a network request, extracts files or overwrites an
existing report. The [pipeline guide](../pipeline/README.md#inventory-a-downloaded-fastener-archive)
owns exact command syntax and limits.

Verification uses generated tiny PNGs/TARs labelled `fixture`. No exact official
counts, real dimensions, archive hash or authentic AI results are claimed.
`acquired` means the operator supplied a downloaded archive, not verified origin.
URL/time and official completeness require review; equal decoded dimensions alone
do not prove visual mask alignment. This inventory is not the release manifest.

Once the official archive is available:

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
