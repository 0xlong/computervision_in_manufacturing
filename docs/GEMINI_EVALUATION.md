# Frozen fastener evaluation

Completed: 115/115 genuine final assessments, with one recovered server error.
The fixed policy missed 12/93 anomalous images and reviewed 5/22 normal images.
The [local journey and verification record](FASTENER_VERIFICATION.md) is current;
the plan and bounds below document how these results were obtained.

Local noncommercial development only; no publication or paid requests. The
[local-use review](GEMINI_LOCAL_USE.md) records the applicable terms interpretation.

## Selection before evaluation

The actual normal-only trial completed on 24 October 2026:

| Candidate | Real sample outcomes | Supervised request times | Selection |
| --- | --- | --- | --- |
| Gemini 3.8 Flash | 1 success; second probe timed out after 3 attempts | Success 31.100 s; timeouts 56.406, 56.388, 57.028 s | Excluded: failed the two-success trial requirement |
| Gemini 3.5 Flash-Lite | 2 successful structured answers with observed appearance text and reported model version | 6.048 s and 5.144 s | Selected for complete fastener evaluation |

Each Lite request used 2,277 reported input tokens and 34/36 output tokens.
Both normal probes were called acceptable. This checks useful response structure,
ordinary-normal behavior and the predeclared 60-second deadline, **not defect
recall or model superiority**. No final-test outcomes informed selection or prompt
changes. Source record IDs: `trial-gemini-3.8-flash-d8855e9ecb3c` and
`trial-gemini-3.5-flash-lite-f195f15da430`, under ignored `artifacts/gemini-trials/`.
Model aliases are mutable; reported versions are retained per response.

## Frozen scope and budgets

The complete 115-image neutral evaluation index from `data/metal_nut.inputs.v2`
is used, unchanged. Reference/prompt/schema/low-thinking settings are inherited
from the qualifying normal-fitting trial. Original 700 × 700 clean RGB pixels,
no crop/resize/padding/normalization; input PNGs at most 1 MiB each. Original
pixel visibility is preserved rather than inferred from a smaller transform.
The earlier source/outline review remains limited as recorded in DATA_REVIEW;
full defect sensitivity is established only by evaluation, not those observations.
No labels, masks or evaluator paths enter requests.

One request child at a time, 60-second hard deadline, at least 10 seconds between
starts (6 RPM, below the confirmed 15 RPM), or slower when access limits require.
Reserve 16,000 input tokens per request: at most 96,000 reserved per minute,
below 250,000 input TPM. This is planning headroom, not a tokenizer guarantee;
unexpected successful usage or missing usage stops execution. Output cap 2,048.
At most three attempts per image, 345 submissions for this run, plus the two
completed Lite trial calls: below the confirmed 500 RPD if no other app consumes
the allowance. No automatic reset/entitlement increase is assumed. Unknown,
failed and retry submissions all consume the recorded allowance.

Each invocation allows at most 12 submissions and 900 seconds of request/wait
budget, excluding local validation/serialization/cleanup. Longer provider waits
pause. Successes are reused across batches; transient errors have bounded retry,
quota pauses, access errors stop and unknown outcomes require reconciliation.
Journal-before-send, fixed-host transport, process deadline and provider-wide OS
lock reuse the tested trial mechanisms. The new supervisor has its own source
fingerprint. Changes produce another frozen run identity.

The run is a single immutable complete-set identity; batches do not select a
different benchmark or remove hard cases. Every member must finish as success
or a recorded terminal failure. There is no pending-as-failure conversion.

## Commands

From the project root, use the qualifying trial evidence and a current nonsecret
access record (paths below are the actual local configuration):

```powershell
.\.venv\Scripts\python.exe -m pipeline.run_gemini_evaluation --package data/metal_nut.inputs.v2 --trial artifacts/gemini-trials/trial-gemini-3.5-flash-lite-f195f15da430/evidence.json
```

This prepares/checks the frozen plan offline, without reading a key or sending
images. Add `--execute --access artifacts/access/gemini-3.5-flash-lite.evaluation.2026-10-24.json`
for one bounded live batch. Repeat only while the saved run is paused for a batch
limit and current access remains valid. Do not loop past quota/access/unknown
stops. Do not edit the frozen plan to resume. Final counters can be regenerated
using the [offline evaluator](EVALUATION.md) without repeating inference.

Initial verification: nine generated offline cases check fixed membership,
prompt/reference preservation, changed-plan refusal, full 115-image completion
across batches without repeated success, unknown journaling/restart stop, quota,
auth/entitlement, bounded retries, timing, access freshness/remaining quota,
missing usage and disk failure before submission. Authentic execution results
and the combined-suite count are recorded in PROGRESS, separately from fixtures.
