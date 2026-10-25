# Additional free models — 25 October 2026

The user's free-model comparison request now includes the second account limits
screenshot. Start with a small normal-picture feasibility trial for **Gemma 4
26B and 31B**, before any full defect evaluation. Existing Gemini campaigns,
saved predictions, labels, test membership and the public website stay unchanged.

## Candidate and quota evidence

| Displayed model | Exact hosted API ID | RPM cap | Input TPM cap | RPD cap | Scope now |
| --- | --- | ---: | ---: | ---: | --- |
| Gemma 4 26B | `gemma-4-26b-a4b-it` | 30 | 16,000 | 14,400 | Two normal-fitting probes |
| Gemma 4 31B | `gemma-4-31b-it` | 30 | 16,000 | 14,400 | Two normal-fitting probes |
| Gemini Robotics ER 2 Preview | `gemini-robotics-er-2-preview` | 5 | 250,000 | 20 | Possible later candidate; no requests here |

Caps are user-supplied account evidence, not an independent billing audit. The
user explicitly replied “all other models 0” to the question about today's Gemma
usage. Record that as a separate confirmation, **not an inference from the limits
page**. The page numerators show peaks: [Google support](https://discuss.ai.google.dev/t/rpd-is-not-being-reset/145704/3)
explains the default 90-day window. The chart icon opens usage charts; it is not a
quality rating. Historical Gemini receipts/access files are preserved with an
append-only interpretation correction under `artifacts/additional-models-oct25/`.

Sources checked 25 October:

- [Hosted Gemma API guide](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api)
  documents both exact IDs, image understanding and `minimal` thinking disabled
  versus `high` enabled. This proves documented capability, not success with our
  two-image JSON request. Hosted response-schema support is tested, not assumed.
- [Pricing](https://ai.google.dev/gemini-api/docs/pricing) lists Gemma 4 input/output
  free of charge and no paid tier. Existing Free-tier confirmation stands.
- [Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4) describes
  image/text input. A model's licence does not grant rights to dataset pictures.
- [Robotics guide](https://ai.google.dev/gemini-api/docs/robotics-overview) documents
  ER 2 image input. Its smaller daily cap makes it a lower priority here.
- [Existing scoped local-use review](GEMINI_LOCAL_USE.md) applies to the same
  private offline Gemini API preparation, with user-confirmed Swiss/UK regional
  data-use treatment. No visitor API access, publication, billing or private data.

Embedding models turn inputs into vectors rather than the required inspection
answer. Audio, music, video and image-generation endpoints are not first choices
for this still-picture comparison. Some Live endpoints can accept images, but
need a different streaming setup; an “Unlimited” request field does not establish
unlimited free computation or remove token limits. Zero-cap entries are excluded.

## Frozen small trial

[Configuration](../configs/gemma-trial.v1.json), [schema](../schemas/gemma-trial.v1.schema.json)
and [isolated runner](../pipeline/probe_gemma.py) reuse the exact original prompt,
one normal-fitting reference and two distinct normal-fitting probes. There is no
test-index/label/mask access during this step. Existing RGB PNGs are unchanged.
Use `thinkingLevel: minimal`, the same strict three-decision JSON schema, 2,048
maximum output tokens and the existing sanitized response contract.

At most **three total generation submissions per model**, including retries;
two successes with reported versions are needed for qualification. One serial
request child, 60-second hard deadline, 60-second minimum start spacing and
600-second invocation limit. Plan 4,096 input tokens/request; the complete trial
reservation is 12,288, below the supplied 16,000 TPM. This is planning headroom,
not an exact tokenizer measurement. Missing/excessive successful input usage stops
advancement. All submitted attempts consume budget; journal before sending.
Authentication stops; quota pauses; unknown outcomes stop for reconciliation.
No unsupported-format fallback, new model substitution or paid fallback.

New files isolate these settings from the three frozen Gemini campaigns. Source,
configuration and input hashes bind the plan. Completed/stopped trials are not
resubmitted. A new configuration requires a new recorded trial; never rewrite old
evidence to make it qualify. Current nonsecret access records expire after four
hours by internal policy, not a provider expiry.

Working folder: project root. Offline preparation command (no inference/key access):

```powershell
.\.venv\Scripts\python.exe -m pipeline.probe_gemma --package data/metal_nut.inputs.v2 --model gemma-4-26b-a4b-it
```

Expected: zero submissions and a saved plan, or the existing saved snapshot.
For an actual trial, the agent adds `--execute --access <current-nonsecret-record>`.
Both candidates run separately. This is normal-fitting feasibility, **not defect
accuracy**, a full benchmark or a website comparison result.

## Verification and results

Offline checks cover normal-only pixels/prompt/identity, minimal thinking, strict
token-budget preflight, pre-send journal, 60-second pacing, usage overshoot stops,
unknown/quota/retry bounds, no repeated completed successes, fixed-host allowlist,
sanitized errors and missing-access refusal. They use generated pictures and fake
responses only. The request path was frozen at checkpoint `e38a8a4` before the
following authentic executions.

| Model | Saved normal-trial ID | Valid answers / submissions | Request seconds |
| --- | --- | --- | --- |
| Gemma 26B | `probe-gemma-4-26b-a4b-it-5fa2077031b1` | 2 / 2 | 6.471 / 7.404 |
| Gemma 31B | `probe-gemma-4-31b-it-f11b607b6934` | 2 / 2 | 28.726 / 28.795 |

Both models returned `looks_acceptable` on both normal-fitting probes, with their
reported model versions, 615 input tokens/request and 31–36 output tokens. No
retries, refusals, quota events or unknown outcomes occurred. Start gaps were at
least 60 seconds. Four total genuine generation submissions. This demonstrates
image/strict-JSON request feasibility, **not defect accuracy or a winner**.
[Local execution audit](../artifacts/additional-models-oct25/trial-execution-audit.json)
also verifies earlier Gemini evidence, frozen source and public bundle byte hashes
unchanged. No source photograph was visually opened.

## Complete-set evaluation preparation

The [new isolated evaluator](../pipeline/run_gemma_evaluation.py) preserves all 115
test IDs/pixels, the exact prompt, normal reference, strict JSON contract and minimal
thinking from the qualifying trial. Source and execution policy are frozen in its
identity. It does not change the old Gemini evaluator, which reserves 16,000 input
tokens/request and is incompatible with this 16,000 TPM cap.

Each batch allows 1–12 submissions and 900 seconds including waits; a run allows
345 submissions and three attempts/picture. All local Gemma trials/evaluations
conservatively share the supplied 30 RPM / 16K input TPM / 14.4K RPD caps, even if
the provider's separate allowances would be larger. Count all journaled attempts
since the user's access confirmation, including failures/unknowns, and leave one
daily request headroom. Never infer a daily reset. Stop before stale access.

Before each request, reserve 4,096 input tokens in a rolling 60-second window,
counting known successful input usage and reserving 4,096 for failed/unknown
attempts. Wait until usage plus the incoming reservation is **below** the verified
input TPM. Start spacing is at least `max(10 seconds, 120 / RPM)`, including model,
phase and batch changes. Respect retry deadlines. Missing/excess usage stops;
unknown outcomes anywhere in the shared Gemma ledger stop for reconciliation.
Hold the provider-wide lock through each batch, load the saved ledger once, then
update it for each new journaled submission. Every snapshot is persisted before
and after sending; completed successes are reused across invocations.

Public frozen configuration version 3 records these limits and Gemma settings;
versions 1 and 2 remain compatible. Pending evaluations cannot be packaged.
Only complete genuine runs can produce benchmark rows. Gemma 26B is now complete
and packaged alongside the unchanged Gemini 3.5 Flash-Lite baseline; 31B remains
qualified but has no defect evaluation yet. This priority uses normal-preparation timings,
not final-test labels or outcomes. No new Gemini requests are authorized by a
Gemma batch, and no paid fallback or publication occurs.

## Complete genuine 26B evaluation and local integration

Frozen evaluator checkpoint: `9cfd7b1`. Run: `eval-gemma-7292d2441bcfd2c1`.
**115/115 successful structured answers, 115 submissions, zero retries/failures**;
one answer is `uncertain`, a valid response needing human checking rather than a
categorical success. It is an anomalous part and counts as routed to review.

| Complete model/configuration | Defects missed | Good parts flagged | Unsure | Median recorded attempt |
| --- | --- | --- | --- | --- |
| Gemini 3.5 Flash-Lite, low thinking | 12 / 93 | 5 / 22 | 0 / 115 answers | 4.96 s |
| Gemma 4 26B, minimal thinking | 20 / 93 | 5 / 22 | 1 / 115 answers | 6.06 s |

Gemma routes 73 anomalous parts to checking (72 categorical flags plus one unsure)
and 5 normal parts, 78/115 total. The baseline routes 86/115. Fewer checks alone
does not mean better: Gemma misses eight more labelled defects here. The baseline
has fewer misses, equal normal flags and faster median requests on this dataset;
this is not a universal model ranking or a statistical significance claim. Both
use the same 115 pixels/labels, prompt and normal reference, with documented
different thinking settings. This public benchmark may occur in model training.

[Complete evaluation audit](../artifacts/additional-models-oct25/complete-26b-audit.json)
independently recounts the confusion totals from saved answers/reference labels.
All original Gemini evidence/source hashes were unchanged before integration.
Minimum full-evaluation start gap across phases/batches: **10.010 seconds**;
maximum reserved rolling input window: **7,171**, below 16,000. Total shared Gemma
submissions: **119** (four normal trials plus 115 evaluation), zero unknowns.
No new Gemini generations occurred during this Gemma milestone.

Local public bundle: **`fasteners-92538e3ac8f7cbfa`**, two complete genuine rows.
[Integration audit](../artifacts/additional-models-oct25/bundle-integration.json)
verifies the original baseline evidence/report, five teaching IDs/labels/image/mask
bytes, notices and baseline frozen configuration all identical. A full prior copy
is preserved at `artifacts/additional-models-oct25/baseline-public/`. Only the
combined bundle and one new Gemma configuration are installed. A real pending
Gemma run was rejected by packaging before output creation. Nothing is published.
Existing browser progress follows the app's bundle-change restart rule once;
switching models/modes within this bundle must preserve visitor answers.

Checks: **481 offline pipeline tests**, **32 web unit tests**, TypeScript and
production build pass. Browser outcomes and the exact local-use steps are in
[verification](FASTENER_VERIFICATION.md) and [local guide](FASTENER_LOCAL.md).
Next candidates: the qualified 31B trial needs its own full run; the three earlier
Gemini campaigns still need 98 pictures each in usable quota windows. Their partial
results remain excluded from the website. No background evaluator remains.
