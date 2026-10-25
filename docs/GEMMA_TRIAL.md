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
responses only. Real execution outcomes will be appended after the frozen request
checkpoint; no provider requests have been made for this Gemma configuration yet.

A full Gemma evaluation needs a separately frozen token-aware evaluator and
packaging configuration: the existing Gemini evaluator reserves 16,000 tokens per
request and cannot safely be reused unchanged against a 16,000 TPM limit. Do not
change frozen campaign files to bypass this check. Only complete genuine 115-image
runs can produce benchmark rows. The existing website still has its sole complete
Gemini 3.5 Flash-Lite result.
