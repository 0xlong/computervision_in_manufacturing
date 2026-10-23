# What resizing does to defect detail — 24 October 2026

I built a repeatable picture-size check. It measures all 93 reference outlines
and prepares at most two original/resized comparisons per run. In the two examples
viewed, a small dark spot stays clear at 256 pixels, while fine scratch detail
becomes less distinct. This does not establish AI detection quality or a safe final
resolution. The website still shows the starter page.

One agent on `main`; no worktrees. Supports EN-02/EN-03, US-06, Gate 1 and
DATA-TRANSFORM-001. No dependency changes, fitting, inference, thresholds, provider
requests, source modifications, publication or changes to preparation membership.

## Method and scope

The [review tool](../pipeline/review_resolution.py) re-audits the unpacked category,
rebuilds the preparation plan and requires equality with the saved plan before
producing evidence. Each decoded picture/mask is read from the bytes whose hash
was checked. Unknown/normal/duplicate selections, more than two selections, changed
plans/assets, unsupported resize settings, existing output and output within the
dataset are rejected. Reports use relative source members, never private absolute
paths. Outputs are local evaluator records with label-bearing paths and mask
information; they must never be passed to specialist or provider inference.

The configuration fingerprint identifies the existing
[specialist candidate](../configs/specialist-smoke.v1.json). RGB uses its full-frame
Pillow BILINEAR resize to 256×256, without orientation changes, crop or padding.
The saved 256px input is the spatial RGB representation before division by 255
and channel normalization. These affine per-channel operations are not simulated
by a display effect. The tool rejects other resize descriptions rather than
silently substituting a filter. Reference masks independently use NEAREST at
256², 384² and 512²; those larger mask measurements are not RGB visibility evidence.

Each comparison places an untouched 700×700 original beside the 256×256 result
enlarged to 700×700 with NEAREST. Enlargement makes pixels inspectable and adds no
detail. No reference overlay obscures RGB, no contrast enhancement is applied,
and no model output is displayed. Coordinates use continuous image edges:
`source = input * 700/size`, with zero offsets. Pixel centers use
`(input + 0.5) * 700/size - 0.5`. At 256px the scale is 2.734375 in both axes.

Pillow 13.0.0 is already locked. Its official
[resize documentation](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize)
was checked for explicit filters and default full-image bounds.

## Actual visual sample and observations

Exactly **two comparison sheets were viewed**, one original and one resized
representation each: **four displayed examples**, below the five-example task
limit. The separate input PNGs were checked by code and were not visually opened.
Both selected images had been reviewed in the earlier native-size work; selection
uses known small-spot/fine-scratch examples, not model outputs or a search for a
favorable result. No other real images were viewed during this task.

| Image | Reason for selection | Actual observation at 256px |
| --- | --- | --- |
| `img-000026`, `test/color/000.png` | Smallest complete source mask: 2,135 pixels; previously reviewed small spot | Dark spot on the upper-right face remains clearly distinguishable; surrounding fine surface texture is blurred. |
| `img-000113`, `test/scratch/020.png` | Previously reviewed subtle scratches on the lower face | Broad light/texture variation remains, but the fine individual scratch detail is substantially less distinct; this view cannot certify preservation of every annotated scratch. |

These are human visual observations from a bounded sample. No pass/fail detection
threshold, model-quality measure, annotation correction or claim of complete RGB
visibility is supported. Display enlargement also does not reproduce a model's
feature maps. Test pictures were accessed only for this explicit feasibility
inspection, not fitted, scored, calibrated or used to tune a detection rule.

## Automated measurements and saved evidence

All 93 complete reference masks retain some pixels at each measured size:

| Size | Minimum nonzero mask pixels | Empty complete masks |
| --- | ---: | ---: |
| 256×256 | 284 | 0 |
| 384×384 | 642 | 0 |
| 512×512 | 1,139 | 0 |

These reproduce the earlier aggregate counts. They do not prove that every small
disconnected component survives, that RGB defects remain visible, or that a model
detects them. The selected scratch mask retains 2,235 pixels at 256²; its much
larger area than the spot does not establish better visibility or detectability.

Ignored evidence directory: `data/metal_nut.resolution-review.v1/`. `review.json`
retains all 93 source/mask fingerprints, measurements, coordinate mappings,
configuration fingerprint and four PNG hashes. Its visual status intentionally
remains `pending_separate_observations`: generating files cannot certify viewing.
This document and `visual-observations.v1.json` record the separate completed
sample observation; neither marks a final resolution approved.

| Fingerprint | SHA-256 |
| --- | --- |
| Checked source membership | `e0c75a7d552ed53999cba5cf385470976149e8339134771a3097290da3083aa1` |
| Canonical preparation plan | `6351bfdb5e3732446cab20cae7ea96cae956245d46e4d60086cfdd28f8316c62` |
| Specialist configuration bytes | `03a874b3d82635764ad6fde41e94e1c45eda9a19c1ab1c6b2c76635b3ea35087` |
| Generated review JSON bytes | `e64c711fd90a18df4f1b06f96aee03fa8945990e05efe841d55e806a05848bd6` |
| Viewed spot comparison PNG | `8f21282d9ed0604a000822a43f2257f2b751545b0f2b223ccb35d1ba465598a9` |
| Viewed scratch comparison PNG | `734121f7d571b7133d877b23aa4011be0f7467a3d8205bcd26b391dab27f75a2` |

All original 176 fitting, 44 calibration and 115 evaluation members are retained.
Related-object identity and acquisition limitations remain as recorded in
[data preparation](DATA_PREPARATION.md#current-continuation).

## Executed checks and reproduction

Working folder: `C:\Users\Longin\Desktop\Projects\computervision_in_manufacturing`.
These commands **were executed**:

```powershell
.\.venv\Scripts\python.exe -m pipeline.review_resolution data/downloads/metal_nut --plan data/metal_nut.preparation-plan.v1.json --config configs/specialist-smoke.v1.json --image-id img-000026 --image-id img-000113 --output-dir data/metal_nut.resolution-review.v1
powershell -NoProfile -File scripts/pipeline.ps1 test
python scripts/check_environment.py
```

The first produced 93 mask measurements and four displayed examples. Repeating
requires a **new output directory**, such as `data/metal_nut.resolution-review.v2`;
previous evidence is never overwritten. It reports visual review pending until
actual observations are recorded separately.

**194 pipeline tests passed**, including 20 new generated-image cases. They check
known BILINEAR pixel values, original preservation, NEAREST viewing enlargement,
coordinate mapping, disappearance of a tiny reference region, mask validity,
bounded selection, rejected stale inputs/settings, repeatability, fingerprints,
output preservation and honest CLI messages. The first restricted run hit the
documented Windows temporary-directory access restriction; all unchanged tests
then passed with normal local file access. No check or requirement was weakened.

Independent code checks verified every generated PNG fingerprint and compared
both saved 256px RGB arrays against direct BILINEAR resizing of the original
source bytes. The workspace check passed; it establishes workspace readiness only.
A fresh single-agent review checked code/tests/findings against the requirement,
source preservation, sample budget, mappings and evidence claims. Frontend/browser
checks were not rerun because no frontend changed. No new AI results were produced.

## Decision and next step

Keep 256px as an **unapproved development candidate**, with the fine-detail risk
explicit. Do not freeze the benchmark, silently change model settings, or claim
that this sample proves dataset-wide visibility. A larger input may preserve more
detail but has not been visually reviewed or measured with full fitting here.

Next: measure full-normal-fitting memory/time on provisional preparation data,
with a bounded resource plan, before choosing final model resolution. Resolve
remaining related-object/split risk explicitly before benchmark freeze. Final
calibration and all final-test inference remain pending.

For something to try now, open `data/metal_nut.resolution-review.v1/img-000026-comparison.png`
in VS Code. Expect the original on the left and the enlarged 256px picture on the
right. The dark spot should remain visible. This is a review aid, not AI detection.
