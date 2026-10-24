# Gemini request runner

The two authentic normal-only trials and selected Lite model's complete fastener
evaluation have now finished. The website has the local inspection-to-brief
journey; see the [current verification](FASTENER_VERIFICATION.md). Offline
preparation still does not produce model answers. The original implementation
and prerequisite notes below are historical where superseded by that record.

## Confirmed account information

On 24 October 2026 the user supplied an AI Studio limits screenshot and explicitly
confirmed that these are free Gemini allowances. Treat this as the user's account
confirmation; do not ask them to reconfirm Free tier. This is not an independent
account login/audit. The screenshot is cropped above the column headings; values
are transcribed using AI Studio's requests/minute, input tokens/minute and
requests/day order, consistent with the preceding discussion.

| Model | Requests/minute | Input tokens/minute | Requests/day | Usage shown |
| --- | ---: | ---: | ---: | --- |
| `gemini-3.8-flash` | 5 | 250,000 | 20 | 0 in each column at capture |
| `gemini-3.5-flash-lite` | 15 | 250,000 | 500 | 0 in each column at capture |

Remaining allowance is time-sensitive. No expiry or authenticated project alias
was visible. Never invent an evidence expiry or a current remaining balance from
an old screenshot. The user chose to stay with Gemini; OpenAI is not part of this
trial. Existing key-metadata access evidence is separate from generation.

## Fixed first trial

[`configs/gemini-trial.v1.json`](../configs/gemini-trial.v1.json) is checked against
[`schemas/gemini-trial.v1.schema.json`](../schemas/gemini-trial.v1.schema.json).
For each candidate the runner selects the first three sorted IDs from the
hash-checked **normal fitting index**: one reference, then two distinct probes.
The same pixels, prompt and probes are used for both candidates. The original
RGB PNGs are sent without resizing, up to 700 pixels/side and 1 MiB/image.
There is no image-viewing step in preparation; zero examples were visually opened.

- Only pixels, a neutral probe ID, the permitted normal reference and the fixed
  inspection instructions enter the request. No source paths, answers, masks,
  evaluator manifest or evaluation index is opened by the runner.
- One request at a time across this runner's live trials; at least 65 seconds
  between starts, including across restart. Provider retry guidance can extend it.
- Two initial requests/model; at most three attempts/probe and six total requests
  per model, including failures and unknown submissions. No automatic fallback.
- Input allowance reservation: 16,000 tokens/request, up to 96,000/model including
  retries. This is a conservative planning allowance for the two bounded images,
  **not a provider-enforced input-token maximum or an exact tokenizer measurement**.
  Reported successful input usage above it, or missing usage, stops the trial.
  Failed requests may not report usage; their full reservation remains counted.
- At most 2,048 output tokens/request, with low thinking. Truncated answers remain
  invalid responses. Six 60-second request deadlines bound supervised request time
  to 360 seconds/model, excluding process cleanup and local preparation/writes.
  Each invocation allows at most 600 seconds for requests plus planned waits;
  longer waits pause instead of blocking. Resuming does not reset attempt budgets.
- This normal-only sample checks request format, response usefulness on normals,
  recorded versions, usage and timing. It cannot establish defect recall, model
  superiority, final image-resolution adequacy or a release benchmark.

## Offline preparation — safe to run now

Working folder: the project root. These commands prepare/validate real-data plans;
they do not read the key, launch a request child, upload images or use API quota:

```powershell
.\.venv\Scripts\python.exe -m pipeline.run_gemini_trial --package data/metal_nut.inputs.v2 --model gemini-3.8-flash
.\.venv\Scripts\python.exe -m pipeline.run_gemini_trial --package data/metal_nut.inputs.v2 --model gemini-3.5-flash-lite
```

Both commands were executed on 24 October 2026. Expected and observed:
`PASS trial offline preparation: 2 probes; 0 saved successes; state=in_progress`.
The deterministic folder under ignored `artifacts/gemini-trials/<run-id>/` contains
`plan.json`, `evidence.json` and an OS lock file. Repeating preparation reuses the
matching snapshot; configuration/image changes create a different run identity.
Request-construction and transport source fingerprints also form part of that
identity, using normalized line endings. Code changes cannot silently reuse an
older request identity. Earlier offline-only snapshots are preserved as superseded
plans if the implementation changes; they contain no attempts.
The snapshot's `in_progress` state means pending work, not inference in progress.

## Live execution and saved records

Live execution adds `--execute --access <nonsecret-access-record.json>` to the
chosen command. This is a usage description, **not a command executed in this task**.
The access record follows the existing `access` definition in
[`api-evidence.v1.schema.json`](../schemas/api-evidence.v1.schema.json): provider,
model, evidence fingerprint, verification/validity times, free execution and paid
disablement confirmations, terms/data-use conclusion, model quotas and current
remaining requests. It contains no key. Validation checks claims, not their truth.
No live-ready access record has been manufactured by this implementation.

The supervisor journals a possible unknown submission and flushes it to disk
**before** launching a child. The child loads only the named local Gemini key,
uses the fixed Google HTTPS endpoint, sends a POST with header authentication,
and returns allowlisted sanitized fields. Redirects, inherited proxies, tools,
search grounding, SDK retries, billing changes and provider/model substitution
are absent. The parent kills a request child at 60 seconds, including response
reading; a socket timeout alone would not enforce that overall deadline.

Successful snapshots are never rerun. Transient transport/5xx/timeouts have bounded
retry/backoff. A refusal and malformed/truncated output are separate terminal
failures. Authentication/permission errors stop the run. HTTP 429 pauses it;
Retry-After/Google RetryInfo are respected. Without a known quota window it waits
at least 24 hours, a conservative pause rather than an asserted provider reset.
Unknown outcomes after a crash stop for reconciliation and are never auto-retried.
There is no automatic reconciliation command yet; preserve the records.
Timeout retries may repeat a request still running remotely; the runner cannot
cancel remote generation or guarantee exactly-once execution.

Raw response bodies are hashed, not retained. Validated decisions/observations,
model versions, input/output usage (including reported thought tokens), timings
and failure classifications are retained in the evidence schema.
The schema's latency field records supervised request time capped at its
60-second deadline; process cleanup beyond that deadline is not represented as
network latency. It is not a complete end-to-end pipeline timing measurement.
Keys, headers, raw error messages and local paths are not stored in the snapshot. Publication
still needs a separate evidence/security review. OS locks prevent concurrent live
instances of this runner, but cannot coordinate other applications using the key
or changes to account usage. Ordinary power loss/filesystem failures remain
possible despite fsync/atomic replacement; corrupt snapshots fail closed.

## Original use prerequisite and next-work record (historical)

The scoped private local-use conclusion is now recorded in
[GEMINI_LOCAL_USE.md](GEMINI_LOCAL_USE.md). The following describes the original
runner-implementation checkpoint, before the user's regional answer and trial.

The existing [terms/data-use investigation](API_FEASIBILITY.md#terms-and-data-suitability-still-need-a-recorded-conclusion)
is unresolved for submitting these licensed images and publishing saved results.
Free-tier confirmation resolves account spending eligibility; it does not itself
resolve dataset/provider-use conditions. The access contract deliberately keeps
`terms_and_data_use_verified` separate. This task did not weaken that requirement
or upload images. Continue that investigation without asking the user to reconfirm
the account. Then execute these bounded preparation trials, inspect their genuine
outputs, and qualify/freeze configurations before final evaluation.

Sources checked for this implementation: [generateContent REST](https://ai.google.dev/api/generate-content),
[structured output](https://ai.google.dev/gemini-api/docs/structured-output),
[thinking settings](https://ai.google.dev/gemini-api/docs/generate-content/thinking),
[rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), and
[provider terms](https://ai.google.dev/gemini-api/terms).
