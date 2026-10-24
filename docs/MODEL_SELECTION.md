# Model selection — 24 October 2026

Final local fastener outcome: select Gemini 3.5 Flash-Lite after its two successful
normal-only trial responses; exclude 3.8 Flash after a probe exhausted its timeout
attempts. Complete Lite evaluation and the local visitor journey are verified in
[FASTENER_VERIFICATION.md](FASTENER_VERIFICATION.md). Earlier planning/discovery
notes below are retained as history, not current pending work.

Use fast, efficient models, with API models preferred. The user changed this
direction after the local experiments took too long. Further PaDiM/PatchCore
fitting and resolution experiments are deferred. Two local specialists are no
longer required for release. The [specification](AI_Inspection_Pilot_Lab_SPEC.md)
owns the revised requirements.

## What is decided

- Prefer API models; include only candidates that meet recorded time/resource
  budgets and provide useful authentic inspection evidence.
- Among useful eligible candidates, prefer the fastest measured responses and
  lowest preparation/resource burden. Use a short candidate list, not a broad
  benchmark campaign just to discover which models are practical.
- Start with the existing Gemini route. OpenAI remains conditional on verified
  zero-cost entitlement. No additional hosted provider is authorized.
- Keep zero paid spend: no billing activation, paid fallback or unverified calls.
- Keep the static website with saved results. Visitors make no inference calls,
  provide no keys, and wait for no training.
- Preserve complete evaluation, honest failures, source/licence checks, answer-free
  inputs and separate preparation/test data. Speed does not replace quality checks.
- Keep old local outputs and failed attempts as historical evidence. Their tools
  remain available, but do not run more experiments without a justified new task.

The user's follow-up asked for a concrete recommendation before providing API
access. The updated [free API comparison](API_FEASIBILITY.md#trial-recommendation-after-the-users-follow-up)
recommends `gemini-3.8-flash` for the first bounded trial and
`gemini-3.5-flash-lite` for the speed-oriented comparison. Google lists Standard
free input/output for both and documents image input/structured output. This
supersedes the earlier 3.5/3.1 Lite trial priority. No model is tested or finally
selected; a general capability description does not establish inspection quality.
Final model IDs/count and actual response times remain unverified. The user has
confirmed free Gemini access and supplied model quotas; do not ask again. A
[bounded preparation trial](GEMINI_TRIAL.md) now fixes initial sample/configuration
and request/time budgets; it has been prepared offline, not executed. No API is claimed
to be the fastest. API round-trip time, one-time local fitting time and saved-page
loading time are different measurements; the local timeout does not prove API
superiority. No numerical speed target is invented from this request.

## Next small steps

| Step | Work | Completion check |
| --- | --- | --- |
| Verify free access | Check current official Gemini model availability, image support, terms and actual project entitlement/quotas without reading secrets | Dated sources plus account-specific zero-cost evidence, or a precise access blocker; no call before verification |
| Plan a short trial | Choose candidate IDs and permitted normal references; record request/total-time budgets, quota allowance, stop conditions and label-free image preprocessing | Concrete bounded plan before execution; no full-data fitting or evaluation |
| Measure authentic samples | After verified access, make only the planned small requests; save real structured outputs, latency, usage and failures | Outputs/observations validate and limits remain respected; no assumed speed winner or defect-quality claim from a small sample |
| Select and freeze | Retain only qualifying models; resolve preparation/source risks and model-specific image-size visibility before complete evaluation | Exact IDs/count/configurations and limitations recorded; complete selected public test membership preserved |

Use one agent. Avoid another long local-model experiment as a prerequisite for
API discovery. Any access question should identify the exact missing evidence;
do not ask the user to paste credentials into chat.

The public-source discovery step is complete, and user-provided free-tier/quota
confirmation is recorded in the trial guide. Regional terms and dataset/provider-use
suitability still need a
recorded conclusion for the offline-generation/static-site arrangement. See the
[dated findings and next tasks](API_FEASIBILITY.md). Keep all provider calls
disabled until the applicable prerequisites are verified.

## What the app can show

API models show real categorical decisions and concise observations. They have
no invented heatmaps, calibrated probabilities or adjustable sensitivity. The
existing fixed policy sends `needs_review`, `uncertain` and technical failures to
human review, with failure reasons visible.

Compare models only when at least two qualifying runs exist. If only one qualifies,
show its evidence and explain that model comparison is unavailable. Do not add a
slow model merely to fill a slot or substitute test fixtures for authentic results.
Specialist scores/maps and calibration requirements apply only if a local model
is subsequently selected on evidence.

## Existing evidence

At 384px, PaDiM completed in 90.385 seconds of supervised worker time, near the
3 GiB committed-memory cap. PatchCore was stopped automatically after 600 seconds
while fitting; no completed output exists for that attempt. These are development
resource findings, not defect-detection scores or API latency measurements.
See [the preserved experiment](LARGER_RESOLUTION.md).

Gate 1 and all application stories remain incomplete. No provider request,
model selection, public release or remote infrastructure change occurred in this
documentation update. The website still shows the starter page.
