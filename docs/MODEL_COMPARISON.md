# Comparing inspection models

25 October update: the user's actual free-tier screenshot supports 2.5 Flash,
2.5 Flash-Lite and 3 Flash preview as new candidates; 3.6 is absent. All three new
normal-fitting trials qualified. The quota-aware runner and frozen-configuration
packaging and model-aware playback are implemented. Each new model has 17/115
saved test assessments and is paused at daily headroom; 98/model remain. See the
[current run/allowance record](GEMINI_COMPARISON_RUNS.md). The initial shortlist and
staged-delivery notes below describe the earlier 24 October planning checkpoint.

Later 25 October update: the user's second screenshot also includes Gemma 4 26B
and 31B (30 RPM / 16K input TPM / 14.4K RPD each). Both passed the two-normal-image
feasibility trial; neither has a complete defect benchmark yet. The faster 26B is
the next full evaluation, using an isolated token-aware runner. See the
[isolated Gemma trial](GEMMA_TRIAL.md). The limits page's numerators are **peaks**,
not current consumption; the previous interpretation and claimed remaining one
are corrected in the run record above. The user separately confirmed zero use for
the other models in reply to the current-usage question. Existing genuine results
are preserved; no comparison winner can be declared from unfinished runs.

Updated 24 October 2026. The user now wants several free API models evaluated on
the same inspection task, with a clear comparison table. This takes priority over
starting the surface track. It expands the earlier single-qualifying-model outcome;
it does not turn preliminary trials into full evaluations or authorize paid access.

## What the comparison means

First compare the complete existing **115-image fastener test set**: 93 anomalous,
22 normal. Keep the images, labels and membership unchanged. Reuse the completed
Flash-Lite run without resubmitting its requests. For each new configuration, fix
the prompt, normal-fitting reference, RGB pixels, response format, decision policy
and execution bounds before evaluation. Do not adjust instructions using final-test
answers. A changed configuration is a new recorded run, never a rewritten result.

The comparison table shows missed defects, good parts flagged, AI answers, no
answer, unsure, median request time and all parts sent for checking. Each count
has its own denominator. Selecting a row changes the detailed model results and
workload/brief inputs while preserving visitor judgments and picture identity.
The table only uses completed, validated saved runs on matching pictures/labels.
Candidates without a completed run stay in this preparation record, not in the
website's benchmark table with invented values.

There is no supported universal winner. Compare fewer misses, fewer false alarms,
coverage and request times together. The full detailed metrics retain class
denominators, uncertainty intervals and failure routing. Unsure is a successful
structured answer sent for checking; technical failures are not successful model
predictions. Neither a small trial nor five curated pictures proves inspection
quality or factory performance. Keep surface-category comparisons separate later.

## Initial evidence and shortlist — 24 October

| Model | Genuine evidence now | Next prerequisite |
| --- | --- | --- |
| `gemini-3.5-flash-lite` | Complete 115-image run: 12/93 defects missed; 5/22 normal flagged; 115/115 successful; 0 terminal failures; 86/115 routed to review | Reuse unchanged as baseline |
| `gemini-3.8-flash` | Earlier normal-fitting trial: one success; another probe timed out after three attempts. No full-set defect-performance result | Current remaining quota; an explicitly recorded qualifying preparation configuration before full evaluation; preserve the unsuccessful trial |
| `gemini-3.6-flash` | Official image/structured-output support and published Standard free tier; no project trial or quota evidence yet | Account model availability, actual free limits/remaining allowance, bounded normal-fitting trial and qualification |

Official Google sources checked 24 October 2026:

- [Model catalog](https://ai.google.dev/gemini-api/docs/models) lists the exact
  model identifiers. Do not infer model names from conversational version examples.
- [3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash) and
  [3.6 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash) document
  image input and structured output. The former explicitly supports low/medium/high
  thinking; minimal is unsupported. Do not silently apply minimal thinking to it.
- [Pricing](https://ai.google.dev/gemini-api/docs/pricing) lists Standard free
  input/output for these candidates and the existing Lite baseline. Published free
  pricing does not establish account eligibility, quotas or remaining allowance.
- [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) distinguishes
  account/project limits. The user's existing Free-tier confirmation is retained;
  it is not necessary to ask for that confirmation again.

Previously confirmed limits: 3.8 Flash **5 RPM / 250,000 input TPM / 20 RPD**;
3.5 Flash-Lite **15 RPM / 250,000 input TPM / 500 RPD**. No current remaining balance
is inferred. At 20 RPD, 115 first attempts alone take at least six daily quota
windows; retries and trial calls increase the allowance needed. A multi-day run is
acceptable; no quota upgrade or paid fallback is implied. The existing candidate's
timeouts remain evidence, rather than being removed to create a favorable table.

Other free API providers may be investigated under the user's broader request.
Do not send images to a new provider until its image capability, content-use terms,
account free access, actual quotas and credential mechanism are established. Keep
the present Gemini route first because it already has a reviewed local-use setup.
Never equate a free chat application or subscription with free API entitlement.

## Staged delivery and execution boundary

1. **Comparison display:** show all existing validated complete runs with honest
   denominators, separate failures/unsure responses and recorded request timing.
   Verify real baseline values and clearly labelled multi-run test cases. No new
   inference is necessary for this step.
2. **New candidate preparation:** add a versioned comparison configuration and
   generalize the currently Lite-specific evaluation/configuration packaging path.
   Preserve old supervisors/configuration identities and successful run snapshots.
   Validate exact request settings and same-test membership with generated tests.
3. **Authentic evaluation:** after model-specific access/remaining allowance is
   available, run bounded qualification and then serial resumable batches. Freeze
   each qualifying configuration first, stop on quota/access/unknown-outcome issues,
   retain failed attempts and never resubmit saved successes. Complete every member
   as success or a recorded terminal failure before displaying benchmark metrics.
4. **Integrate and verify:** package new immutable evidence while keeping the same
   five teaching-picture IDs; preserve old bundles and record the new identity.
   Verify table rows, same-image model comparison, visitor-state behavior and the
   playback model behavior before claiming multi-model completion. Model switching
   in playback must reset/identify model-specific counters and pause appropriately;
   the current five-picture player still uses the first saved run.

The earlier requirement for bounded, useful authentic preparation evidence is not
waived. Any policy change to include a model that fails qualification must be an
explicit recorded decision, rather than silently weakening checks. Changes to a
configuration cannot retroactively relabel its earlier failed trial as successful.

At this checkpoint no new image upload/provider generation was made. The only
current genuine full evaluation remains Flash-Lite. The comparison display can be
ready before a second model has been evaluated. Current access information requested:
3.8/3.6 RPM, input TPM, RPD and remaining daily usage from the selected AI Studio
project; no key, private account data or repeated Free-tier confirmation is requested.

## Reading request time

The website derives the median from every available saved `latency_ms`, including
retries and failed attempts. It shows how many attempts have a measurement. Missing
times are not zero, and an entirely missing set displays Unavailable. Supervisor
deadlines/process handling remain as documented in [the evaluation record](GEMINI_EVALUATION.md).
This is recorded request time, excluding deliberate waits between requests, not
time-to-complete the entire campaign or the playback's viewing time. Different run
dates/provider load and mutable aliases limit speed comparisons. Reported versions
and frozen settings remain accessible in the saved evidence.

## Verification and current limitation

See [progress](PROGRESS.md) for the actual check results and current missing access.
Browser outputs for this step are under ignored `artifacts/model-comparison/`.
Two-model fixture cases test interface behavior only and are visibly labelled as
invented test examples; they never become real benchmark results. No universal-best
claim, fabricated second result, paid access, publication or deployment is made.
