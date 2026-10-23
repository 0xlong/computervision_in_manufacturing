# Full-normal-fitting resource checks — 24 October 2026

Current direction: further local experiments are deferred. Prefer fast, efficient
API models after verified free access and bounded checks. See
[model-selection plan](MODEL_SELECTION.md); older next steps below are historical.

Follow-up: a separate [384px feasibility check](LARGER_RESOLUTION.md) examines
the recorded fine-detail risk under the same bounds. The 256px measurements below
remain unchanged historical evidence; they do not approve a final picture size.

Both planned models successfully fitted all 176 permitted normal fitting
pictures on this computer. Each produced a real score and heatmap for the same
separate normal picture. Both stayed inside the memory and time bounds. This
measures resources, without testing defect-detection quality or choosing a final
picture size. The website still shows the starter page.

Owner: one agent on `main`; no delegation or worktrees. Parent EN-03, supporting
US-06 and Gate 1. No new dependencies, downloads, provider calls, source edits,
image viewing, threshold selection, final-test inference, publishing or remote
changes. Earlier eight-picture runs remain separate in
[MODEL_FEASIBILITY.md](MODEL_FEASIBILITY.md).

## Plan and safeguards

The [supervisor](../pipeline/profile_specialist.py) derives a saved configuration
from the unchanged [256px candidate](../configs/specialist-smoke.v1.json). Only
the fitting count (all available images), calibration probe count (one) and
development purpose are set. Both runs use the same pinned indexes/checkpoint,
seed 42, full-frame BILINEAR resize, ImageNet normalization, two CPU threads and
model settings recorded in the earlier feasibility guide. Batch size stays one.
No score, mask, defect label or final-test result selects these settings.

Runs are sequential, each with a **3 GiB committed-process-memory cap** and a
**600-second worker timeout**, including worker input validation/imports. Require
at least 4 GiB available physical RAM before launch (cap plus 1 GiB headroom).
Parent preflight validation is outside the worker's time/memory measurements.
This headroom is a launch check, not a reservation against other programs.

The Windows Job Object is configured before a start signal is sent. The actual
Python interpreter attaches before model imports or model-input access, including
when a Windows virtual-environment launcher creates another process. Failure to
attach stops execution. The job permits one interpreter and kills it if the
supervisor exits; timeout closes the job and waits for process exit. A generated
process test also checks abrupt supervisor exit without Python cleanup.

The cap restricts committed virtual memory, which differs from physical RAM in
the working set. Both peak committed memory (job measurement) and peak physical
working set (worker measurement) are retained; do not compare the cap against
working set as if they were the same measure. See Microsoft's
[extended job limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)
and [process assignment](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject),
checked 24 October 2026, and Python's
[process timeout handling](https://docs.python.org/3.13/library/subprocess.html#subprocess.Popen.communicate).

Outputs must use a new directory below ignored project `artifacts/`; existing
evidence and source inputs are preserved. The supervisor records started,
success, incomplete or failed status and bounded error types. Timeout cannot
become success even if partial worker files exist. A nonzero exit alone does not
prove a memory-limit failure. Worker logs are discarded because third-party
messages can contain private paths; safe stage/error metadata remains in JSON.

## Measured results

Computer/environment: the same Intel i7-6500U CPU, Windows x64 Python 3.13.2
and hash-locked model packages recorded in [the setup](MODEL_FEASIBILITY.md#computer-and-isolated-setup).
Available physical RAM at launch was 6,699,077,632 bytes for PaDiM and
6,405,263,360 bytes for PatchCore. Models ran in separate processes without
overlap. Routine checks ran in the background during portions of these probes;
these are feasibility observations with other machine activity and cache effects,
not controlled timing comparisons or proof that either model is better.

| Measurement | PaDiM | PatchCore |
| --- | ---: | ---: |
| Normal fitting pictures | 176 | 176 |
| Setup/import/weight loading | 14.613 s | 16.173 s |
| Full fitting | 43.127 s | 187.379 s |
| One normal probe including resize/normalization | 0.218 s | 0.150 s |
| Worker model-stage total including output saving | 57.973 s | 203.719 s |
| Supervised worker wall time including input checks/process overhead | 65.208 s | 212.116 s |
| Peak physical working set | 1,571,360,768 bytes (1.463 GiB) | 1,399,242,752 bytes (1.303 GiB) |
| Peak committed process memory | 1,960,620,032 bytes (1.826 GiB) | 1,701,593,088 bytes (1.585 GiB) |

Both workers used exactly the 176 sorted permitted fitting IDs. Both scored only
`img-000118`, the first sorted normal calibration member. The remaining 43
calibration pictures were validated but not scored. No threshold was selected.
PatchCore's actual 1% coreset bank is **1802×384**. PaDiM uses the unchanged
100-channel Gaussian configuration. Neither run reads an evaluation index,
reference label or mask; no final-test picture is fitted or scored.

Each map is finite float32, shape `1×1×256×256`, aligned to its 700×700 input
with edge-coordinate scale 2.734375 and zero offset. Pixel-center mapping is
`(map + 0.5) * 2.734375 - 0.5`. These maps are genuine model outputs, not
reference outlines, calibrated probabilities or evidence of defect quality.
No real image or map was visually opened during this task (zero visual examples).

Evidence under ignored `artifacts/resource-probes/`:

| File | SHA-256 |
| --- | --- |
| `padim-256-v1/profile.json` | `7eb81ca5cb98eedb7cd92da8d07bc50891583bd2dd4076143f5c929d4eaa2b9e` |
| `patchcore-256-v1/profile.json` | `b96c90e7c92fa93ba4605c4fedf9791a3cd3e360bc0fed12136c34a2383e6217` |
| Both derived `probe-config.json` files | `cc3f67cf7274e21d88d9e0279ff239123dc13379d65fe9f81e293b87d81e1e01` |
| `padim-256-v1/worker/result.json` | `9806f1e7878aea56b0f3b96cce07b49dd75e72ba07ba374ae7442cf7d03d5a89` |
| `patchcore-256-v1/worker/result.json` | `ce8e0429500681ce3123472675f9e4d2a46563eca376ff22117426fdc32bf0e6` |
| `padim-256-v1/worker/img-000118.map.npy` | `57c21b3f7544e5f745d0076c0661c0a98c1d761c239635c6472be4425ae12859` |
| `patchcore-256-v1/worker/img-000118.map.npy` | `cd746a4463a338972037a07bfd127dd0a9b6c313094642cf722acfa41168d924` |
| Independent `verification.v1.json` | `74761c285db670c6d733dff10bc2048aac06edcbdafbbc129c1d0f8f6686cf82` |

The original candidate-config fingerprint remains
`03a874b3d82635764ad6fde41e94e1c45eda9a19c1ab1c6b2c76635b3ea35087`.
Checkpoint and both index fingerprints are unchanged from the earlier feasibility
guide. Independent saved-file checks revalidated every fitting/calibration asset,
all-fitting membership, absence of preparation-ID overlap, exact derived settings,
loaded pretrained features, output fingerprints, finite score/map values, shape,
coordinates and successful termination inside the bounds. No inference was repeated.

## Reproduce

Working folder: `C:\Users\Longin\Desktop\Projects\computervision_in_manufacturing`.
The following commands were executed, sequentially:

```powershell
.\.venv-models\Scripts\python.exe -m pipeline.profile_specialist --model padim --inputs data/metal_nut.inputs.v2/model-inputs --checkpoint checkpoints/resnet18-f37072fd.pth --output-dir artifacts/resource-probes/padim-256-v1
.\.venv-models\Scripts\python.exe -m pipeline.profile_specialist --model patchcore --inputs data/metal_nut.inputs.v2/model-inputs --checkpoint checkpoints/resnet18-f37072fd.pth --output-dir artifacts/resource-probes/patchcore-256-v1
```

Purpose: measure full-normal-fitting resources using the existing locked model
environment. A repeat requires new output names; expect `SUCCESS` only when the
worker finishes all fitting members and emits the one normal probe output.
Limits may be reduced with `--memory-mib` (1024–3072) and `--timeout-seconds`
(1–600). The CLI cannot increase these bounds. A failed probe is useful evidence,
not permission to bypass limits or silently change model settings.

Each directory retains `profile.json`, `probe-config.json`, `worker/result.json`
and any actual normal-probe map. These are internal development evidence, not the
versioned release run/prediction/evaluation contracts. A model checkpoint is not
saved, so future final evaluation still requires fitting a frozen configuration.

## Remaining decisions

The full 176/44/115 membership remains provisional; related-object independence
is unresolved. One normal calibration output is an execution probe, not threshold
calibration. All 115 final-test inputs remain unscored. The prior
[small RGB sample](RESOLUTION_REVIEW.md) found loss of fine scratch detail at 256px.
A feasible 256px run cannot establish that this resolution is suitable for defects.
Larger resolutions and their resource needs remain unmeasured here.

Next: combine the resource findings with that detail risk to settle the picture
size, and explicitly resolve preparation-risk disposition before freeze. Gate 1
also needs complete licence/source and free-provider feasibility evidence.

## Verification

**215 pipeline tests passed**, including 21 new resource-runner cases. Generated
inputs cover all-fitting configuration, changed indexes/pixels, output preservation,
bad resources, insufficient RAM, checkpoint changes, guarded failure and partial
or timed-out output rejection. Actual Windows process tests verify memory
allocation denial, timeout cleanup, abrupt-supervisor-exit cleanup and failure to
attach a missing job. These synthetic processes are separate from the two real
model runs above.

The first restricted test attempt hit the known temporary-folder permission
problem. Unchanged file/process tests passed with normal local permissions; no
check was weakened. The workspace check passed (workspace readiness only).
A fresh single-agent review checked limits, actual-interpreter attachment, input
separation, evidence claims, preservation and the requirements. Documentation
links/fences and whitespace were checked. No frontend changed, so browser/build
checks were not repeated and no browser journey is claimed.
