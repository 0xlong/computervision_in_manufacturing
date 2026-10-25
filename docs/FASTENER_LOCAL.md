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
No visitor action sends a prompt, answer or rationale to an AI provider.

**Compare models** shows one row per completed saved model evaluation on the same
test pictures. Select a model's row to use its detailed results and workday/brief
calculations. The table shows missed defects, good parts flagged, answer coverage,
unavailable/unsure answers, median recorded request time and total checks. On small
screens scroll the table sideways; Tab to its border and use arrow keys when using
a keyboard. Open **How to read the table** for counting/timing explanations.
There are now two genuine complete results: Gemini 3.5 Flash-Lite and Gemma 4 26B,
each on all 115 pictures. Three other Gemini evaluations remain partial; Gemma 31B
has only its normal-picture trial. They are not shown as completed comparisons.
The evidence update has a new version, so an older saved challenge restarts once
under the app's existing evidence-change rule. Model switches keep answers within
the current version.

<a id="watch-the-five-saved-results"></a>

## Watch all 115 saved results

Choose **Watch AI Inspect** on the opening page or in the top navigation. It starts
paused. For every picture, playback reveals:

1. The picture alone.
2. Gemini 3.5 Flash-Lite's saved assessment.
3. Gemma 4 26B's saved assessment, keeping the first visible.
4. The dataset reference, with all three cards visible together.

The reference reveal updates each model's totals once. Both models always appear;
there is no playback model selector. Your own five-picture challenge and its saved
judgments stay separate. The underlying genuine evidence bundle is unchanged, so
this update does not reset saved visitor judgments.

Use **Play/Pause**, **Previous**, **Next**, **Restart**, and **Viewing time**.
Fast, Normal and Slow show each picture for 2, 4 or 8 seconds, split equally across
its four stages. This is viewing time, not measured AI processing time. Image
loading adds time. Pause retains the remaining fraction of the current stage.
Moving between top tabs or hiding the browser tab pauses playback; it never
resumes by itself. Pictures load one at a time, not all 115 at startup.

**Different answers only (26)** plays all 26 pictures where the saved answer
categories differ. This includes unsure and unavailable categories. **Show all
pictures** returns to the complete 115. Changing the filter pauses at its first
picture and clears only playback counters. Empty selections have a Show all path.

After the last reference's viewing time, playback stops and opens the comparison
dashboard. It always scores the complete 115-picture benchmark, with all 93 defective
and 22 good pictures in the respective error denominators. It states how many
references you actually viewed, including when filtered or when pictures were
skipped. Correct decisions are categorical matches; unsure/unavailable answers do
not count as correct. Genuine correctness remains Gemini 98/115 (85.2%) versus
Gemma 89/115 (77.4%), with Gemma's one unsure answer separate.

**Watch again** starts the current selection paused with cleared playback counters.
**Review pictures** starts all 115; **Review different answers** starts the 26
matches. Each model has separate running counts for correct decisions, defects
flagged, defects missed, good parts flagged, unsure and unavailable answers.
Filtering never changes the benchmark scores or your challenge judgments.

Try **Watch AI Inspect → Play** and watch both model cards appear before the
reference. For a shorter run, choose **Different answers only (26)** first.

The top navigation is the single place to switch between **Try it**, **Watch AI
Inspect**, and **Results**. Extra explanations live under **About this playback**;
score definitions live under **How scores are counted** on the dashboard.

Keyboard: focus the playback area, then Space to play/pause, arrows to change
pictures, Home to restart, End to jump to the last picture, Esc to pause. Buttons
work with Tab and Enter. Zoomed-picture arrows scroll the picture. No animated
reveals or automatic scrolling. Completion focuses the dashboard heading;
review/replay returns focus to the playback area.

Missing/changed images offer **Retry picture**. A missing, corrupt or mismatched
playback catalog offers **Retry playback**, without inventing a shorter run.
Playback is held in memory during tab changes and restarts paused on refresh;
your challenge keeps its normal browser storage behavior. No visitor action calls
an AI provider or sends visitor judgments off the browser.

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
