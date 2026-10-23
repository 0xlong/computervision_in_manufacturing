# Free API feasibility — 24 October 2026

Published Gemini documentation supports a short list of image-capable candidates.
Actual project entitlement, quotas, response speed and inspection usefulness are
**not verified**. No model request or image upload was made. The website still
shows the starter page. The user reconfirmed free API tiers only in this session.

One agent on `main`; parent EN-03, supporting US-02/03/06 and Gate 1.
Requirements: API-FREE-001/002, API-INPUT-001, API-OUTPUT-001 and SEC-SECRET-001.
This is discovery evidence, not a completed provider adapter or release gate.

## Published candidate evidence

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
