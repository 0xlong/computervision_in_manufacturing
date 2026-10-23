# Local model practice runs — 23 October 2026

Update, 24 October: the next resource-check step uses all 176 normal fitting
pictures with enforced memory/time bounds. See [full-fitting resource findings](MODEL_RESOURCES.md)
for current results and limits. The eight-picture measurements below remain the
unchanged historical sample evidence; their pending-work statements describe
the state on 23 October.

Both planned models ran successfully on this computer using its CPU. Each learned
from eight normal fitting pictures and produced an actual score and heatmap for
one separate normal calibration picture. This proves a small setup can execute;
it does not establish defect detection quality, full-data memory/runtime or a
finished benchmark. The website still shows the starter page.

One agent on `main`; no workers, provider calls, billing, upload or publication.
Requirements: Gate 1, EN-01/EN-03, partial DATA-TRANSFORM-001/DATA-FREEZE-001.
Preparation membership remains provisional: see [the remaining related-picture
risk](DATA_REVIEW.md#automated-follow-up-of-the-12-recorded-risks).

## Computer and isolated setup

Refreshed read-only measurements: Intel i7-6500U, 2 cores / 4 logical processors,
15.86 GiB installed RAM; 5.40 GiB free physical RAM at inventory time; 28.06 GiB
free disk after installation. AMD Radeon R5 M330 and Intel HD Graphics 520 were
reported; no NVIDIA GPU was reported. Runs used CPU with two PyTorch threads.
Ignored measurement record: `data/local-compute.v1.json` (UTC checking time retained).

The existing `.venv` data checker is unchanged. A separate ignored `.venv-models`
uses Windows x64 Python 3.13.2, anomalib 2.7.0, torch 2.14.1+cpu, torchvision
0.29.1, timm 1.0.30, NumPy 2.5.4 and Pillow 13.0.0. The
[82-package hash lock](../pipeline/requirements-models.lock) contains anomalib's
required dependency tree and the same four input-validator packages already used
by the project. Provider SDKs and optional full/CUDA extras were not added.

The binary-only resolution initially failed because FrEIA 0.2 is source-only.
Its PyPI source hash is pinned; a local wheel built successfully using pinned
setuptools 84.2.1 with build isolation disabled. The installer permits source only
for FrEIA; other dependencies remain binary-only. `pip check` and both model imports
passed. First imports built Matplotlib's font cache; library deprecation notices
remain visible. They did not prevent either actual run.

The model-package metadata record is `data/model-package-licences.v1.json`.
Anomalib and timm identify Apache-2.0; torchvision identifies BSD; torch records a
combined SPDX expression for its bundled code. FrEIA's metadata has no licence
value; its full source/licence review and the complete transitive notice inventory
remain release work. These metadata observations are not distribution approval.
Dataset CC BY-NC-SA notices remain in evaluator space. No checkpoint or dataset
asset was published.

## Exact sample and configuration

The runner accepts only the pinned fitting/calibration index hashes from the
[answer-free package](DATA_PREPARATION.md#current-continuation). It does not read
the evaluator folder or evaluation index, nor test labels/masks. Replaced indexes
are rejected before model loading. Fitting/calibration IDs and file hashes must
not overlap; input bytes are rechecked before tensor conversion.

Fitting IDs: `img-000116`, `img-000117`, `img-000122`, `img-000123`, `img-000124`,
`img-000125`, `img-000126`, `img-000127` (first eight sorted permitted fitting IDs).
Both models scored `img-000118`, the first sorted calibration member. This is a
normal-only execution probe, not operating-policy calibration. No threshold,
confusion matrix, accuracy claim or winner is produced.

[Candidate configuration](../configs/specialist-smoke.v1.json): seed 42 for Python,
NumPy and PyTorch; deterministic PyTorch algorithms; batch size one; full-frame
700×700 RGB input resized to 256×256 with Pillow BILINEAR, no rotation/crop/padding.
Float32 pixels are divided by 255 and normalized using ImageNet mean
`[0.485, 0.456, 0.406]` / standard deviation `[0.229, 0.224, 0.225]`.

- PaDiM: ResNet-18 layers 1/2/3, 100 selected feature channels. Pinned anomalib
  uses covariance diagonal regularization 0.01 plus 1e-5 stabilization. Image score
  is the maximum raw Mahalanobis map value.
- PatchCore: ResNet-18 layers 2/3, 3×3 feature averaging, 1% k-center greedy
  coreset, nine support neighbors; actual bank shape **81×384**. Global RNG seed
  42 controls the selection path; the library exposes no separate sampler seed.
  Image score is the maximum nearest-patch distance with the library's neighborhood
  weighting. This differs from simply taking the final smoothed map maximum.

Both use the pinned package's map upsampling and Gaussian blur (sigma 4).
Saved map arrays are finite float32, shape `1×1×256×256`. The recorded scale
`700/256 = 2.734375`, offset zero, describes continuous image-edge coordinates;
pixel-center mapping is `(x_map + 0.5) * scale - 0.5` and likewise for y.
No map was substituted for a reference annotation or displayed on the website.
No images were visually viewed in this continuation. Small-defect RGB visibility
at 256px remains unverified; mask survival alone is not that evidence.

The shared checkpoint was downloaded from the official PyTorch URL in the config:
`resnet18-f37072fd.pth`, SHA-256
`f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec`.
Every one of 75 used feature tensors loads from those bytes. The old checkpoint
omits 15 batch-tracking counters; PyTorch's standard strict-loader compatibility
initializes only those non-learned counters. Missing learned weights fail. Unused
classifier/deeper-layer weights are excluded. There is no random-feature fallback
or automatic Hugging Face/credential lookup. Weight redistribution suitability
remains a separate release check.

## Measured successful runs

Each model ran in a separate completed process; the runs did not overlap.

| Measurement | PaDiM | PatchCore |
| --- | ---: | ---: |
| Setup/import/weight loading | 11.480 s | 13.892 s |
| Fitting eight pictures | 3.474 s | 1.213 s |
| One inference including resize/normalization | 0.229 s | 0.128 s |
| Model-stage total including output saving | 15.203 s | 15.250 s |
| Windows peak process working set | 1,274,466,304 bytes (1.187 GiB) | 623,169,536 bytes (0.580 GiB) |

Input-package validation occurs before these timers. Peak working set covers the
whole process and native allocations, using Windows GetProcessMemoryInfo. These
are single samples with import/cache effects, not a speed benchmark or deployment
resource estimate. Full 176-image fitting, 44-image threshold setting and all 115
test predictions have **not** run. No performance comparison is supported.

Ignored evidence:

| File | SHA-256 |
| --- | --- |
| `artifacts/feasibility/padim-v2/result.json` | `34c298299a62e52cc9ea914c21c4962536cf0e1711a38e4940106cd717c42afe` |
| `artifacts/feasibility/patchcore-v1/result.json` | `b683d120403f8fe4ae0cdc770b406ca8fa9bd8fece2ae6a871b19987c2483568` |
| PaDiM `img-000118.map.npy` | `d9a99697413298185d1fb5b2b595de4ce2d3a5fef93cc91f4cb37f0484550b03` |
| PatchCore `img-000118.map.npy` | `af43d46b3761bf430a5b959fdb744303a7538722de632abf11dfe72a2d520f9b` |

The first PaDiM attempt (`padim-v1`) failed at the strict weight-integrity guard,
before fitting: the compatibility counters were not initially distinguished from
learned features. That failed record remains intact. After checking actual missing
keys and PyTorch's legacy counter handling, the runner was fixed and `padim-v2`
succeeded. Regression checks still reject missing learned features. This was a
runner correction, not a change to model settings or replacement of failed evidence.

## Reproduce

Working folder: `C:\Users\Longin\Desktop\Projects\computervision_in_manufacturing`.
These model commands were executed against the prepared data and local checkpoint:

```powershell
powershell -NoProfile -File scripts/models.ps1 check
.\.venv-models\Scripts\python.exe -m pipeline.smoke_specialist --model padim --inputs data/metal_nut.inputs.v2/model-inputs --checkpoint checkpoints/resnet18-f37072fd.pth --output-dir artifacts/feasibility/padim-v2
.\.venv-models\Scripts\python.exe -m pipeline.smoke_specialist --model patchcore --inputs data/metal_nut.inputs.v2/model-inputs --checkpoint checkpoints/resnet18-f37072fd.pth --output-dir artifacts/feasibility/patchcore-v1
```

Expected/observed: dependency/import PASS, then both `SUCCESS` results. Use new
output directory names to repeat. The runner makes no downloads; interrupted runs
retain a `started`/failed record and cannot be treated as success.

For another checkout, the following setup command is provided for future use;
its constituent pinned installation commands were executed for this check:

```powershell
powershell -NoProfile -File scripts/models.ps1 install
```

Purpose: create only `.venv-models`, install the pinned source-build tool and
hash-locked CPU packages, then check dependencies/imports. Expect PASS imports;
it does not train models. Acquire the official checkpoint separately at the URL
above and verify its full SHA-256. Recreate the ignored input package using the
[preparation guide](DATA_PREPARATION.md#current-continuation).

## Verification and next step

174 routine pipeline tests passed, including provenance v1/v2 behavior, output
preservation, clean pixels/metadata, leakage/path/hash rejection, deterministic
registration controls, saved-shortlist reconstruction, strict learned-feature
integrity and replaced-index rejection. These generated tests are separate from
the two authentic normal-only model runs above. The workspace check passed; no
frontend code changed, so web checks were not repeated. Browser rendering is
unchanged and was not rechecked.

Next: resolve preparation-risk disposition, check a small RGB defect sample at
candidate resolutions under the five-example limit, then measure full fitting
and select/freeze configuration before final evaluation. Gate 1 still needs those
data/model decisions, complete licence evidence and verified free-provider
feasibility (or its precise blocker). No paid/provider execution was performed.

Official interface sources checked on 23 October 2026:
[anomalib PaDiM](https://anomalib.readthedocs.io/en/latest/markdown/guides/reference/models/image/padim.html),
[PatchCore](https://anomalib.readthedocs.io/en/latest/markdown/guides/reference/models/image/patchcore.html),
[installation](https://github.com/open-edge-platform/anomalib#installation),
[PyPI metadata](https://pypi.org/pypi/anomalib/2.7.0/json),
[torchvision ResNet-18](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet18.html).
The installed pinned source supplied the exact Gaussian, sampler, score reduction
and legacy-counter details; latest documentation alone was not treated as proof
of local runtime compatibility.
