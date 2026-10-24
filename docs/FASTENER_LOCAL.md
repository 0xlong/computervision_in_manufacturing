# Local fastener inspection

The website now has the inspection-to-brief controls: five judgments, answer-gated
reveal, image zoom, dataset outlines, genuine saved model observations when the
local authentic bundle is installed, complete-set counters, workload assumptions,
a pilot decision and a deterministic Markdown download. Progress stays in the
browser. Reset-current/reset-all ask first and replace only this app's state.

Current verification and authentic-evaluation completion are in
[PROGRESS.md](PROGRESS.md#fastener-completion-goal--completed-locally). A fixture browser
pass checks software behavior, not AI quality. The default app has no synthetic
fallback: missing evidence shows a recovery message.

## Run locally

Working folder: `C:\Users\Longin\Desktop\Projects\computervision_in_manufacturing`.

```powershell
powershell -NoProfile -File scripts/web.ps1 dev
```

Purpose: start the website. Expected URL: **http://127.0.0.1:5174/**.
In VS Code use **Browser: Open Integrated Browser**
(`workbench.action.browser.open`) and enter that URL. Stop with Ctrl+C in the
server terminal. The automated browser suite uses its own port 4175.

Click **Try it**, choose **Looks fine** or **Needs checking**, then **Reveal AI
assessment**. Move forward and back: your revealed answer stays fixed. **Next**
returns to the new picture so you can make another call.

Open **Results** for three plain-language counts. **Detailed results** holds the
full statistics; **Explore a workday & download a brief** opens workload assumptions,
a decision and the download. **Where the results come from** holds source records.
To start over, open **About this demo & reset progress** and confirm a reset.
No visitor action sends a prompt, answer or rationale to Gemini.

## Evidence preparation

The [trial](GEMINI_TRIAL.md), [local-use review](GEMINI_LOCAL_USE.md) and
[frozen evaluation](GEMINI_EVALUATION.md) document the genuine offline provider
work. A complete run must account for every one of the 115 selected public test
images; failures are retained and separately routed to human review.

From the project root, after that complete run exists:

```powershell
.\.venv\Scripts\python.exe -m pipeline.public_bundle --package data/metal_nut.inputs.v2 --evidence artifacts/gemini-evaluations/eval-flash-lite-46e242a298f20b6f/evidence.json --out web/public/evidence
```

This is the packaging command, not another inference run. It checks manifest and
image bytes, complete membership and all metrics before copying five teaching
images, three masks, original notices, saved structured results and frozen
instructions/reference/settings. Bundle v2 indexes that configuration download;
the earlier v1 contract is preserved. Choose
an unused output folder for a different bundle; the command preserves existing
output. Source/model/configuration changes create new identities. The local bundle
retains development status and source limitations; recorded_live describes the
audited local workflow, not cryptographic provider attestation or release approval.

The committed five-image manifest is curated **after** complete evaluation: two
normal and three anomalous examples from distinct defect groups, preferring real
misses/normal reviews when available. This does not change the complete benchmark
or establish superiority. API sensitivity and heatmaps are unavailable. With one
qualifying run the UI explains that model comparison is unavailable.

## Checks

Run from the project root:

```powershell
powershell -NoProfile -File scripts/web.ps1 test
powershell -NoProfile -File scripts/web.ps1 build
powershell -NoProfile -File scripts/web.ps1 test:browser
powershell -NoProfile -File scripts/pipeline.ps1 test
```

Expected: passing unit/browser/pipeline checks and a static build under `web/dist/`.
Browser tests require the pinned Chromium downloaded into `.cache/playwright`;
on a fresh machine use the local Node/npm environment from DEVELOPMENT.md and
`playwright install chromium` with `PLAYWRIGHT_BROWSERS_PATH` set to that directory.
No browser test makes provider calls. Fixtures are visibly marked, served only by
test interception, and checked by Python and browser validators against the same
Draft 2020-12 schemas. Browser failures retain a trace under `web/test-results/`.

## Scope and limits

This goal covers the **local fastener** journey. The optional surface track,
publication and remote host checks remain outside this milestone. No paid calls,
billing changes or deployment. Images are public manufacturing proxies, not site
data. Original acquisition receipts and physical-object/session independence
remain unverified. General-purpose models may have encountered the benchmark.
The development banner, evidence notes and export preserve these limitations.
Scenario costs are editable illustrations; human-review capacity and correctness
are assumptions, not measured savings or production approval.
