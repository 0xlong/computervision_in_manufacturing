# Free API feasibility — 24 October 2026

## Completed local fastener outcome

The user's Swiss/UK regional answer and the scoped local-use review allowed the
authorized private noncommercial trials. Lite qualified and completed all 115
fastener test images; the local visitor journey and browser checks now work.
See [current verification](FASTENER_VERIFICATION.md) and the
[scoped terms/use conclusion](GEMINI_LOCAL_USE.md). Earlier discovery/blocker notes
below are historical; publication and billing changes remain unauthorized.

## User confirmation and request runner — latest update

The user has now supplied the AI Studio limits screenshot and explicitly confirmed
that the Gemini limits are free. Do not ask them to reconfirm Free tier. The
recorded allowances are 5 RPM / 250,000 input TPM / 20 RPD for 3.8 Flash and
15 RPM / 250,000 input TPM / 500 RPD for 3.5 Flash-Lite. Usage was zero at capture.
This is user-provided account evidence, not an independent login; current remaining
allowance and validity still need to be recorded when executing. The user chose
Gemini only for the next work. The screenshot does not resolve the separate
terms/dataset-use question below.

A bounded serial runner and two real-data **offline plans** now exist. Preparation
does not read the key or send requests. Live generation still requires the saved
access/use evidence contract. See [trial instructions and limits](GEMINI_TRIAL.md).
Older statements below that project quotas are wholly unavailable describe the
earlier discovery stage; no generation or defect-quality result exists yet.

Published Gemini documentation supports a short list of image-capable candidates.
Actual project entitlement, quotas, response speed and inspection usefulness are
**not verified**. No model request or image upload was made. The website still
shows the starter page. The user reconfirmed free API tiers only in this session.

One agent on `main`; parent EN-03, supporting US-02/03/06 and Gate 1.
Requirements: API-FREE-001/002, API-INPUT-001, API-OUTPUT-001 and SEC-SECRET-001.
This is discovery evidence, not a completed provider adapter or release gate.

## Trial recommendation after the user's follow-up

Rechecked 24 October 2026. The user asked the agent to choose suitable free-tier
models before providing API access. This changes the recommendation, not the
permission to spend or the missing project/terms evidence. Research stayed with
one agent in line with the project's current single-agent direction.

**Recommend `gemini-3.8-flash` for the first bounded trial**, with
`gemini-3.5-flash-lite` as the speed-oriented comparison if both have usable
project quotas. This is an engineering choice for experimentation, not a measured
inspection winner or final model freeze. Small defects make output usefulness
worth checking before optimizing response time. We have no authentic inspection
results, measured latencies or demonstrated minimum quality for either model.

| Model | Verified published facts | Recommendation |
| --- | --- | --- |
| `gemini-3.8-flash` | Stable; image input and structured output; Google describes it as its most intelligent Flash model | First trial candidate; stronger general capability is a reason to test, not evidence of better defect detection |
| `gemini-3.5-flash-lite` | Stable; image input and structured output; positioned for low latency/high throughput | Second trial candidate for the speed/usefulness trade-off |
| `gemini-3.6-flash` | Standard free input/output; catalog positions it as the previous Flash generation | Do not expand the initial trial with a previous-generation alternative |
| `gemini-3.1-flash-lite` | Stable; image input/structured output and Standard free input/output | Reserve candidate only if project availability justifies revising the plan; no automatic substitution |

Sources: [3.8 Flash model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash),
[3.5 Flash-Lite model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite),
[3.1 Flash-Lite model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite),
[current model catalog](https://ai.google.dev/gemini-api/docs/models).

The [pricing page](https://ai.google.dev/gemini-api/docs/pricing) lists free input
and output for Standard execution of all four. Choose Standard only in the trial;
free availability of another consumption option must not be inferred. Gemini 4
Argon has no Free tier; exclude it. The catalog restricts older 2.5 models to
previously active users and recommends newer models for new projects. Do not
choose a legacy model based on remembered free-quota tables. Neither public
pricing nor a key proves this project's eligibility or remaining allowance.

The [quota guide](https://ai.google.dev/gemini-api/docs/rate-limits) confirms
project/model-specific limits. The [active-limits page](https://aistudio.google.com/rate-limit)
must show nonzero RPM, input TPM, daily requests and current allowance for the
chosen model. No project-specific numbers are available yet. No login, key
reading, account change or request was attempted during this comparison.

The [current terms](https://ai.google.dev/gemini-api/terms) retain the EEA/UK/Swiss
API Client restriction recorded below. The offline generation/static website use
question and dataset/provider-use suitability remain unresolved. This model
recommendation does not clear those prerequisites. Do not enable billing or send
images to work around them. Configure a key privately only in the later approved
offline environment; never paste it in chat or put it in browser code.

Next: verify nonsecret project access and applicable use, then fix a small trial's
neutral preparation IDs, prompt/references/preprocessing, schema/configuration
hashes, usefulness checks, request/token/output/time budgets and stopping rules.
Include retries in the total allowance. Use no final-test images for selection.
Only authentic samples can establish whether either candidate is useful enough
to proceed to complete evaluation. The saved-answer checker is now available
with synthetic examples; it does not implement provider execution/resume.

## Published candidate evidence

The original two-candidate discovery below is retained for context; the later
recommendation above supersedes its trial priority.

Official pages were read on 24 October 2026 (Europe/Warsaw). These are candidate
endpoint IDs, not selected models or immutable weight versions.

| Candidate | Published capability | Project status |
| --- | --- | --- |
| `gemini-3.5-flash-lite` | Image input, text output and structured output; stable endpoint | First candidate to verify; no request made |
| `gemini-3.1-flash-lite` | Image input, text output and structured output; stable endpoint | Second candidate to verify; no request made |

Sources: [3.5 Flash-Lite model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite),
[3.1 Flash-Lite model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite).
Google describes both as low-latency models; that is a provider description,
not a project measurement or a claim that either detects small defects well.

The [pricing page](https://ai.google.dev/gemini-api/docs/pricing) lists free input
and output for Standard execution of both candidates. This does not establish
the selected project's tier, entitlement or remaining quota. Use no paid fallback,
billing activation, grounding tools or additional provider. OpenAI remains disabled.

[Structured-output documentation](https://ai.google.dev/gemini-api/docs/structured-output)
supports schema-constrained JSON. Our adapter must still validate decisions and
observations locally, and distinguish refusals, invalid responses and transport
failures. A supported capability does not prove this app's implementation works.

## Quota and account access

The [rate-limit guide](https://ai.google.dev/gemini-api/docs/rate-limits) says
limits depend on project/model and are shown in AI Studio. Requests/minute,
input tokens/minute and requests/day are separate limits. Limits apply per project,
not per key; daily request quotas reset at midnight Pacific time. Published limits
are not guaranteed capacity. We have recorded no actual numerical project limits.

The official [active-limits page](https://aistudio.google.com/rate-limit)
redirected the read-only web tool to Google sign-in. No authenticated provider
session is available through the tools used here. No sign-in, key lookup,
credential-file access or account change was attempted. This is the concrete
access blocker, rather than evidence that the user has no account or free access.

Before requests, record the following nonsecret evidence from the approved
project interface. A local project alias is sufficient in public notes.

- Checking date, project alias, Free tier and confirmation that paid execution
  and automatic paid fallback are unavailable.
- Exact candidate model availability, requests/minute, input tokens/minute,
  requests/day, current usage/remaining allowance where shown, and any expiry.
- Any absent or zero limit as a blocker; do not fill gaps from another account,
  an old quota table, a subscription or the user's free-only intention.

The user reconfirmed the spending rule, but supplied no project/tier/quota values.
Never ask for an API key in chat. Secret configuration belongs to a later approved
offline execution step; this discovery task does not need credential values.

## Terms and data suitability still need a recorded conclusion

[Available regions](https://ai.google.dev/gemini-api/docs/available-regions)
includes Poland. Regional availability alone does not prove account eligibility.
The [additional terms](https://ai.google.dev/gemini-api/terms), effective
23 March 2026, require an adult developer and restrict making API Clients
available in the EEA, Switzerland or UK to Paid Services. They separately apply
Paid Services data-use terms to unpaid quota used in those regions; that data-use
exception is not evidence of billing activation or permission for every use.

Our proposed visitor site serves saved files and does not call Gemini. Whether
this offline-generation/static-publication arrangement falls within the API Client
restriction is **unresolved here**; do not claim either blanket free-use clearance
or that a free development experiment is prohibited. Record a provider-supported
conclusion for the actual arrangement before the affected use. Do not activate
billing to resolve uncertainty. This note records terms, not legal clearance.

Outside the regional exception, unpaid-service terms describe product-improvement
use and possible human review of submitted content. Review the applicable data-use
terms together with the dataset licence before uploading images. Existing
[source/licence limitations](DATA_SOURCES.md#licence-and-publication-record)
remain open; a public dataset is not automatically cleared for every provider use.
Never send confidential factory images, visitor answers or visitor rationale.

## Next small tasks

| Task | Dependency and allowed files | Completion check |
| --- | --- | --- |
| Verify project access and applicable terms | Approved project evidence and provider clarification where needed; this note, MODEL_SELECTION.md and PROGRESS.md | Dated nonsecret tier/model/quota record and recorded terms/data suitability, or a precise remaining blocker |
| Specify a bounded trial | Verified access; label-free preparation inputs; a new trial configuration and focused validation code/tests, scoped before edits | Exact neutral IDs, permitted normal references, preprocessing, prompt/schema hashes, request/token/time budgets and stop rules fixed before execution |
| Run the small trial | Validated plan and zero-cost safeguards | Saved authentic decisions/observations, provider version, usage, latency and failures; no final benchmark or quality ranking from this small sample |
| Freeze and evaluate | Qualifying samples, source/split/visibility decisions and versioned run/prediction contracts | All declared test images accounted for; failures/coverage visible; metrics regenerate from saved records |

The trial remains pending; no numerical time target or request allowance is
invented here. Keep one concurrent request, the specification's 60-second timeout
and at most three attempts per image for transient transport/5xx failures.
Quota exhaustion pauses; authentication/entitlement errors stop the provider run.
Persist attempts before advancing. Neutral IDs and clean pixels must remain
separate from labels, masks and evaluator paths. Model-specific image visibility
still needs checking; previous local 256/384px findings do not approve API inputs.

Independent work while account evidence is unavailable: define the provider
response/run contracts and test the adapter's safeguards with labelled synthetic
examples, without network requests. This would be implementation progress, not
authentic API evidence. No extra dependency is justified by this note alone.

## Verification and limits

Checked the candidate pages, pricing, quota guide, regional list, structured-output
guide and additional terms directly. The account page could not be read past
sign-in. Reviewed this note against the specification's free-only, privacy,
authentic-evidence and full-evaluation rules. No model result, speed measurement,
quota value, completed story or release readiness is claimed.
