# Larger-picture feasibility — 24 October 2026

This checks whether a 384px input is a practical next candidate after the earlier
256px review found softened scratch detail. The small spot remains clear, and
several scratch lines remain visible at 384px, with fine detail still softened.
These observations do not establish detection quality or approve a final size.
The website still shows the starter page.

**Direction changed:** further local experiments are deferred at the user's
request. Prefer fast, efficient API models; see [the model-selection plan](MODEL_SELECTION.md).
The findings below are retained historical evidence, not the next work assignment.

One agent on `main`, as requested. Parent EN-02/EN-03, supporting US-06, Gate 1
and DATA-TRANSFORM-001. No new dependencies, downloads, provider calls, source
image changes, split changes, threshold selection, final-test inference,
publication or remote changes. Earlier work remains preserved.

## Candidate and checks

The [384px configuration](../configs/specialist-384-candidate.v1.json) differs
from the [existing 256px candidate](../configs/specialist-smoke.v1.json) in
`input_size_px` only. It does not replace or approve the earlier configuration.
Both use seed 42, two CPU threads, batch size one, the same checkpoint and
preparation fingerprints, full-frame Pillow BILINEAR resize and ImageNet
normalization. No detection result selects settings or examples.

The existing [review tool](../pipeline/review_resolution.py) rechecks the source
dataset and saved preparation plan. Its mask measurements cover all 93 masks at
256/384/512px; those measurements were already recorded and are not new evidence
of RGB visibility or survival of every disconnected reference region.

The existing [bounded model runner](../pipeline/profile_specialist.py) uses all
176 permitted normal fitting IDs and only the first sorted normal calibration
picture, `img-000118`. The other calibration inputs are validated, not scored.
It never reads an evaluation index, mask or reference label. Input and checkpoint
bytes are checked; there is no new download or random-weight fallback.

Models run sequentially, with the unchanged **3 GiB committed-process-memory
cap**, **600-second worker timeout** and **4 GiB free physical RAM launch check**.
The actual interpreter attaches to a Windows Job Object before model imports or
input access. Previous evidence is retained and outputs use new ignored folders.
The [earlier resource guide](MODEL_RESOURCES.md#plan-and-safeguards) explains the
limits and why committed memory differs from physical working-set memory.

## Bounded visual sample

Exactly two sheets were viewed: each contains one 700px original and one 384px
derivative enlarged with NEAREST to make its pixels inspectable. This is **four
displayed examples**, within the five-example task limit. Neither the standalone
input PNGs nor any model map was visually opened. Earlier 256px findings were
read from [the saved observations](RESOLUTION_REVIEW.md#actual-visual-sample-and-observations);
those sheets were not reopened. There is no simultaneous visual comparison of
256px and 384px in this task.

| Example | Observation at 384px |
| --- | --- |
| `img-000026`, small spot | The dark spot on the upper-right face remains clearly distinguishable; fine surface texture is softened. |
| `img-000113`, fine scratches | Several diagonal lines on the lower face remain distinguishable; finer line separation and texture are softened relative to the original. Preservation of every annotated scratch cannot be certified. |

Selection reused the two previously known examples, without a broader search or
model-output selection. These are human observations of preprocessing only.
They are not a dataset-wide visibility review, a detection score, or proof that
the larger candidate improves model quality. Test photographs were used only for
this declared preprocessing feasibility check, never fitted, scored or calibrated.

Generated evaluator-only evidence is in ignored
`data/metal_nut.resolution-review-384.v1/`. Its `review.json` intentionally keeps
`pending_separate_observations`; the separate `visual-observations.v1.json`
records actual viewing. Label-bearing review records must not reach inference.

## Resource results

PaDiM completed all 176 fitting pictures and the one normal probe. Its peak
committed memory was **3,139,190,784 bytes (2.924 GiB)**, leaving only about
**78 MiB** below the 3 GiB cap in this attempt. That small margin is a practical
constraint; one successful attempt does not guarantee repeat-run headroom.

| Measurement | PaDiM | PatchCore |
| --- | ---: | ---: |
| Outcome | Success | Timed out during fitting |
| Normal fitting pictures completed | 176 | Completion not established |
| Setup/import/weight loading | 14.571 s | 14.107 s |
| Full fitting | 65.898 s | Incomplete |
| One normal probe including resize/normalization | 0.771 s | Not reached |
| Worker model-stage total including saving | 81.270 s | No completed worker result |
| Supervised worker wall time including validation | 90.385 s | 600.013 s |
| Peak physical working set | 2,742,657,024 bytes (2.554 GiB) | Not retained before timeout |
| Peak committed process memory | 3,139,190,784 bytes (2.924 GiB) | 2,636,984,320 bytes (2.456 GiB) |

PatchCore reached the unchanged 600-second limit while its saved worker stage
was `fitting`; the supervisor stopped the interpreter. The supervisor records
`incomplete` / `timed_out`, while the partial worker snapshot remains `started`.
There is no completed fit, probe score or heatmap for this attempt. This is a
timeout, not evidence of exhausting the memory cap. No retry was made.
Resource samples
are local feasibility observations, with normal OS/chat/file activity and cache
effects; they are not controlled speed comparisons or evidence of model quality.
No pipeline test suite was rerun: the user redirected work to documentation,
and no runner or test code changed. Saved-record and documentation checks are
reported in the current progress entry.

## Commands executed

Working folder: `C:\Users\Longin\Desktop\Projects\computervision_in_manufacturing`.
All three commands below were executed sequentially. Use new output names for any future repeat.

```powershell
.\.venv\Scripts\python.exe -m pipeline.review_resolution data/downloads/metal_nut --plan data/metal_nut.preparation-plan.v1.json --config configs/specialist-384-candidate.v1.json --image-id img-000026 --image-id img-000113 --output-dir data/metal_nut.resolution-review-384.v1
.\.venv-models\Scripts\python.exe -m pipeline.profile_specialist --model padim --inputs data/metal_nut.inputs.v2/model-inputs --checkpoint checkpoints/resnet18-f37072fd.pth --config configs/specialist-384-candidate.v1.json --output-dir artifacts/resource-probes/padim-384-v1
.\.venv-models\Scripts\python.exe -m pipeline.profile_specialist --model patchcore --inputs data/metal_nut.inputs.v2/model-inputs --checkpoint checkpoints/resnet18-f37072fd.pth --config configs/specialist-384-candidate.v1.json --output-dir artifacts/resource-probes/patchcore-384-v1
```

## Saved evidence

| Artifact | SHA-256 |
| --- | --- |
| 384px candidate | `746e7e9dcccf3eecd2cdf047aaed6f9ddff8eb54c0199c9dcea6e873f65e1aa0` |
| PaDiM supervisor report | `2893e3b2e5ee2384f136e6c024fad9356a697faa6e90653737fdcab22024a595` |
| PatchCore supervisor report | `84ec50bc430deddb85ff8bb1120035d5bba565c19b1a6f5a141e8014068b7400` |

The reports retain configuration and worker-report fingerprints, exact bounds,
launch free RAM, stage and termination status. No inference is repeated for
saved-file checks. A planned broader independent audit was not executed after
the user redirected work; this task does not claim that audit or new passing tests.

## Decision limits

384px remains a development candidate. Resource success alone cannot establish
scratch detection quality, calibration quality or final resolution suitability.
All 176/44/115 preparation groups remain provisional, and all 115 final-test
inputs remain unscored. Related-object identity is still unresolved; no group is
invented or silently moved. Source/licence and free-provider feasibility evidence
also remain Gate 1 work. No application story or release gate is complete here.
