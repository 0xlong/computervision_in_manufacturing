# Free-tier comparison runs — 25 October 2026

This record continues the user's request for a genuine model comparison. The
[comparison display](MODEL_COMPARISON.md) already works; additional real runs
must be completed before new website benchmark rows are shown.

## Account screenshot received

The user supplied a headed AI Studio limits screenshot and identified it as Free
tier. This is user-supplied account evidence, not an independent account/billing
audit. Capture time and project identifier are not visible. Record the observed
usage as supplied; do not assume a reset or ask again whether the account is Free.

| Displayed model | API identifier | RPM | Input TPM | RPD | Used / daily limit in screenshot |
| --- | --- | ---: | ---: | ---: | ---: |
| Gemini 3.5 Flash Lite | `gemini-3.5-flash-lite` | 15 | 250,000 | 500 | 118 / 500 |
| Gemini 3.8 Flash | `gemini-3.8-flash` | 5 | 250,000 | 20 | 4 / 20 |
| Gemini 2.5 Flash | `gemini-2.5-flash` | 5 | 250,000 | 20 | 0 / 20 |
| Gemini 2.5 Flash Lite | `gemini-2.5-flash-lite` | 10 | 250,000 | 20 | 0 / 20 |
| Gemini 3 Flash | `gemini-3-flash-preview` | 5 | 250,000 | 20 | 0 / 20 |

3.6 Flash is not visible; its account access remains unverified and it is omitted
from this execution cohort. Entries with zero daily allowance are not candidates.
Agents, image generators and text-to-speech endpoints are not alternative visual
inspection classifiers simply because they have quota. The existing complete 3.5
Lite evaluation is reused; the earlier unsuccessful 3.8 trial remains excluded
under the recorded qualification rule. No repeat of that unchanged trial is needed.

Sources checked 25 October 2026: [model catalog](https://ai.google.dev/gemini-api/docs/models),
[2.5 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash),
[2.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-lite),
[3 Flash preview](https://ai.google.dev/gemini-api/docs/models/gemini-3-flash-preview),
[Standard pricing](https://ai.google.dev/gemini-api/docs/pricing),
[REST thinking settings](https://ai.google.dev/gemini-api/docs/generate-content/thinking)
and [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).
Official docs say 2.5 access may be restricted to previously active users; the
screenshot supports trying the displayed allowances, not assuming a successful
generation. All three new model metadata GETs returned HTTP 200 and advertised
generateContent support. Metadata is not inference or proof of available quota.

## Frozen request settings and scope

Version 1 trial configuration/schema and the original complete Lite evidence stay
unchanged. New configuration: [gemini-comparison.v2.json](../configs/gemini-comparison.v2.json),
validated by [trial schema v2](../schemas/gemini-trial.v2.schema.json).

- The exact existing prompt, acceptable normal-fitting reference and first two
  distinct normal-fitting probes are reused. No evaluator labels/masks/test index
  are opened during normal qualification. Original metadata-free RGB PNGs remain
  at 700 × 700, at most 1 MiB each; no resizing or alternate teaching images.
- REST settings differ where the model API requires it: 2.5 Flash/Flash-Lite use
  `thinkingBudget: 0`; 3 Flash preview uses `thinkingLevel: low`. The Lite baseline
  used low thinking. This compares recorded model/configuration combinations;
  it is not an assertion of identical reasoning effort or architecture-only effects.
  No final-test outcome is used to choose those settings.
- One structured decision and concise observation, 2,048 maximum output tokens,
  a 60-second overall request deadline, at most three attempts per picture.
  Qualification permits at most six total submissions and needs two successes with
  reported versions. A normal-only pass establishes request feasibility, not recall.
- A qualified candidate freezes all 115 neutral evaluation members unchanged.
  Maximum 345 submissions across that complete run, including retries. Batches
  permit 1–12 submissions, at most 900 seconds request/wait time; trial invocations
  use 600 seconds. Never convert pending items into terminal failures to finish.
- Request construction, transport, comparison supervisor, preparation/input hashes,
  configuration, reference and qualification identities are bound to the saved
  run. Changes create new identities. Old snapshots and old complete results are
  preserved. Code is checkpointed before authentic execution.

The [existing local-use review](GEMINI_LOCAL_USE.md) covers this same authorized
private, noncommercial Gemini preparation arrangement with the user-confirmed
Swiss/UK region. [Google's terms](https://ai.google.dev/gemini-api/terms) were
checked again; the relevant regional data-use provision remains. This scoped
engineering interpretation does not clear public distribution or grant rights
beyond the dataset licence. Only approved public image pixels and neutral input
text enter requests. No visitor answers, private factory data or credentials enter
the request body or saved evidence. No paid service, billing change, live visitor
inference, grounding, tuning, new provider or publication is enabled.

## Allowance and safe resumption

All comparison trials and evaluations share a per-model submission ledger under
ignored `artifacts/gemini-comparisons/`. Every journaled attempt after the supplied
access snapshot counts, including retry, failure and unknown outcome. A new phase,
run or invocation does not reset the account allowance. At least one daily request
is left as headroom. Failures/unknowns do not refund requests.

Only one request child runs at a time, using the same provider-wide OS lock as the
old runners. Start spacing is at least `max(10 seconds, 120 / verified RPM)` across
trials and evaluations of a model, including a phase/run switch. Provider retry
deadlines are respected across runs. The 16,000-input-token reservation/request is
planning headroom, not a provider-enforced tokenizer limit; missing or excessive
reported successful usage stops the run. Persist the unknown submission before
sending, then save sanitized status/version/usage/timing/response. Unknown results
stop for reconciliation. Access errors stop; quota errors pause without substitution.

The screenshot receipt and three nonsecret access records are under ignored
`artifacts/model-comparison-oct25/`. Their four-hour validity is an internal
freshness limit, not an invented provider expiry. Do not infer current balances
from this historical screenshot later or fabricate access refreshes. Google states
daily quotas reset at midnight Pacific; this runner deliberately needs a fresh
account snapshot to resume across days and does not infer other project usage.
At 20 RPD, 115 first attempts need at least six daily windows before trial/retry
overhead; with one request/day headroom and two trial calls, seven windows may be
needed. There is no scheduled background continuation without an active session.

## Commands

Working folder: the project root. Offline trial preparation, **not inference**:

```powershell
.\.venv\Scripts\python.exe -m pipeline.run_gemini_comparison --package data/metal_nut.inputs.v2 --model gemini-2.5-flash
```

Expected: a zero-submission plan or the existing saved snapshot; no key/network
access. Choose one of the three declared candidate IDs.

With current model-specific nonsecret access evidence, an explicitly live trial:

```powershell
.\.venv\Scripts\python.exe -m pipeline.run_gemini_comparison --package data/metal_nut.inputs.v2 --model gemini-2.5-flash --execute --access artifacts/model-comparison-oct25/gemini-2.5-flash.access.json --budget 6
```

After two qualifying successes, use `--phase evaluation --trial <saved-trial-evidence.json>`
with the same model/access and a bounded `--budget`. This is command syntax;
the actual execution record below owns which commands ran and their outcomes.
Resuming uses saved successes and a matching frozen identity, not a new selection.
Do not modify supervisor/configuration code during a frozen multi-day run without
preserving its executable checkpoint and explicitly creating a new configuration.

## Verification and execution record

The full offline test count and real outcomes are recorded in [progress](PROGRESS.md).
Tests use generated images and fake responses; they never read a real key or call
a provider. Coverage includes all three request settings/allowlisted endpoints,
shared daily headroom, retry/unknown accounting, stale access without automatic
reset, trial-to-evaluation pacing, input/plan tampering, complete membership,
resumption and missing-access refusal. The old trial/evaluation/transport checks
remain in the full regression suite. No dependency or web change is required for
this step; the website still shows only the completed Lite comparison row.

New partial runs cannot be packaged or used for benchmark quality claims. After
complete evaluations, the frozen-configuration packaging path must support the new
version and preserve the five existing challenge IDs; model-aware playback must
be integrated and checked before claiming the whole comparison request is done.
