# Fastener experience — local verification

Verified 24 October 2026 (Europe/Warsaw). The complete **local fastener** journey
works with genuine saved Gemini answers: start, inspect five pictures, reveal,
explore full-set evidence, change assumptions, decide, download a Markdown brief,
refresh and reset. No publication or remote deployment occurred.

The default page uses [the genuine local bundle](../web/public/evidence/bundle.json),
not a fixture. Test examples are separate and visibly labelled. Use the
[local guide](FASTENER_LOCAL.md) to run or try it.

## Playback dashboard — 25 October 2026

The five-picture player now counts both genuine models separately after each
reference reveal, with unique picture counting across revisits. Unsure and
unavailable answers remain outside categorical flags/misses. The Different answers
filter finds 2/5 selected pictures using answer categories, not observation text.
Filter changes pause and clear playback counters. Show all recovers from an empty
filter; one-model evidence disables comparison filtering.

After the final reference has had its viewing time, playback stops and replaces
the image with a complete-benchmark dashboard. Equal model cards sit side by side
at desktop/tablet widths and stack on phones. Three simple bars show correctness,
misses and good flags, with symbols/text and denominators alongside color.
Review pictures, Review different answers and Watch again all start paused;
Watch again retains the filter and clears counters. Focus moves to the dashboard
heading at completion and returns to the playback area after review/replay.

The dashboard always uses every saved benchmark member; it never uses filtered
playback totals or review-routing TP/TN as categorical correctness. Independent
fixed unit expectations and a separately written browser recount check:

| Complete 115-picture evidence | Gemini 3.5 Flash-Lite | Gemma 4 26B |
| --- | --- | --- |
| Correct categorical decisions | 98/115 (85.2%) | 89/115 (77.4%) |
| Categorical defects flagged | 81 | 72 |
| Defects missed / all defective pictures | 12/93 | 20/93 |
| Good parts flagged / all good pictures | 5/22 | 5/22 |
| Unsure / all pictures | 0/115 | 1/115 |
| Unavailable / all pictures | 0/115 | 0/115 |
| Median recorded attempt time | 4.9563224 s | 6.0602535 s |
| Timed attempts, including retries/failures | 116/116 | 115/115 |

Gemma's unsure anomalous answer routes to review and produces routing TP=73;
only its 72 categorical defect flags plus 17 categorical normal passes count
as correct. A labelled six-record fixture verifies correctness 0/6, errors 1/3
in each class, unsure 1/6, unavailable 3/6 and missing request times. This proves
failure-class denominators use the full set, not only successful answers.

Verification: **36 unit tests**, TypeScript/production build and **28 production
Chromium browser tests pass**. The browser recount also checks bar proportions,
full and filtered endings, unchanged full cards, unique reveals across revisits,
cleared/paused replay, all review actions and exact visitor-storage preservation.
Keyboard checks cover Tab/Enter actions, visible focus, completion heading focus
and return to the playback area. Dashboard scans at 360/768/1440 px find no
page overflow or automated WCAG 2.2-tagged violations; cards have equal dimensions.
Existing inspection, reveal, refresh, reset, export, timing and error checks pass.

The first restricted unit invocation could not spawn its runner; permitted local
execution worked. Initial new test assumptions about challenge ordering and
two-stage fake-clock advancement were corrected against actual IDs and render
boundaries; no requirements weakened. Fresh single-agent diff review covered
arithmetic, identity, timers, focus, full versus filtered scope and saved judgments.
Manual visual review used **two dashboard-only screenshots**, desktop and phone;
**zero source photographs**. Automation and these bounded visual samples do not
establish screen-reader, cross-browser or native VS Code browser verification.
Actual browser: Chromium 156.0.8078.4 on Windows, production preview port 4175.
The native VS Code integrated browser is unavailable through these tools. To try it,
use http://127.0.0.1:5174/ and **Browser: Open Integrated Browser**
(`workbench.action.browser.open`); [start command and expected behavior](FASTENER_LOCAL.md).

Records: [independent evidence/endings audit](../artifacts/comparison-dashboard/evidence-and-endings.json),
[desktop dashboard](../artifacts/comparison-dashboard/dashboard-1440.png),
[phone dashboard](../artifacts/comparison-dashboard/dashboard-360.png),
[tablet dashboard](../artifacts/comparison-dashboard/dashboard-768.png),
[phone layout/accessibility](../artifacts/comparison-dashboard/layout-360.json).
Ignored audit images/JSON regenerate with the browser suite. Public evidence,
images, labels, configuration and bundle identity remain unchanged. No pipeline
code, dependencies, inference, publication or remote infrastructure changed.
Older verification sections below record earlier milestones.

## Measured evidence

**Latest 25 October update:** the local bundle is now
`fasteners-92538e3ac8f7cbfa`, with two genuine completed 115-picture runs. The
24 October single-model checkpoint below is preserved as history. Gemini baseline:
12/93 defects missed, 5/22 good parts flagged, 115/115 answers, zero unsure, median
4.96 s over 116 attempts. Gemma 26B: 20/93 missed, 5/22 good parts flagged,
115/115 answers, one unsure, median 6.06 s over 115 attempts, zero retries/failures.
The unsure anomalous part is routed to review; it is not a categorical prediction.
Complete-set routing totals are 86 versus 78, including unsure and failures.

The two-model table uses actual evidence; the same five teaching IDs/labels/assets,
baseline report/evidence, notices and original frozen configuration bytes are
preserved. A prior public copy remains under ignored
`artifacts/additional-models-oct25/baseline-public/`. Details and independent audit:
[Gemma record](GEMMA_TRIAL.md). No unfinished model or fixture enters real metrics.

**481 pipeline tests**, **32 web unit tests**, TypeScript/production build pass.
The genuine browser comparison and all five Gemma playback stages/counts pass in
the first full run. It found an old test assuming one configuration download;
the corrected test checks each model's exact file identity and SHA-256. The final
**22-case production Chromium rerun passes**. This is test repair, not weakened checks.
Native VS Code browser control remains unavailable; actual checks use production
Chromium. No new source photographs are visually opened for this milestone.
The existing evidence-change rule restarts an older saved challenge once; browser
checks verify model/mode switches preserve answers within this new bundle.

The genuine comparison check verifies every row's class totals, answer coverage,
unsure count, measured timing and review workload; fixed independent baseline
assertions remain. The genuine Gemma journey selects its row with the keyboard,
replays all five references, checks actual saved observations/decisions and
running counts, then changes models at the final picture: paused, same picture,
zero new-model totals and unchanged visitor judgments/reveals/selected image.
No page errors or external browser requests were recorded. Both frozen
configuration downloads match their model identity and recorded SHA-256.

Responsive table scans at 360/768/1440 px and real multi-model playback at 360 px
have no page overflow or automated WCAG-tagged violations. The desktop table and
360 px controls were visually checked as **two UI crops, zero source photographs**;
this is bounded visual review, not a full accessibility or dataset visual audit.
Actual browser: Chromium 156.0.8078.4. Hidden-tab behavior remains a synthetic
document visibility check; native VS Code tab behavior remains unverified.
[Genuine playback evidence](../artifacts/additional-models-oct25/genuine-playback-browser.json),
[comparison evidence](../artifacts/model-comparison/verification.json).
No evaluator or background schedule remains running; nothing was published.

- Bundle schema version: 2; identity: `fasteners-f0b61a212fefce56`.
- Run: `eval-flash-lite-46e242a298f20b6f`; provider/reported version: Gemini / `gemini-3.5-flash-lite`.
  The reported name is an alias, not an immutable model-weights identifier.
- Complete evaluation: **115/115 attempted and successful**, 0 terminal failures.
  116 submissions include one recorded transient server 5xx, followed by a
  successful retry. No image was dropped or converted from pending to failure.
- Anomalous: **81 routed to review, 12 missed / 93**. Normal: **5 sent to review,
  17 accepted / 22**. Reviews: **86/115**. Routing recall 87.10%; false-positive
  rate 22.73%. These are public-benchmark observations, not site performance.
- Both successful-output and full-set routing metrics, denominators, Wilson
  intervals, usage, reported versions and all attempts remain available. With
  no terminal failures the two confusion matrices happen to agree.
- The website explains that only one model qualified. Flash's normal-only trial
  produced one success and one probe timing out after three attempts. Lite's two
  trial responses were valid in 6.048/5.144 seconds; they did not establish defect
  recall. No test labels or outcomes were used to change the frozen prompt.
- Evaluation request-time median was 4.956 s. The 116 supervised request times
  total 628.759 s. The execution window was 11:39:08.968–12:07:23.989 UTC and
  includes deliberate waiting/development between batches, not just inference.

The [frozen configuration download](../web/public/evidence/configurations/eval-flash-lite-46e242a298f20b6f.json)
retains the actual prompt, neutral fitting reference, original RGB image settings,
source fingerprints, complete neutral test index and effective execution limits.
Its hash is indexed in the bundle and exported brief. Inherited trial-only fields
are explicitly distinguished from the complete-evaluation supervisor's limits.
Bundle v2 adds this required configuration asset; v1 is preserved and rejected by
the v2 loader. Earlier local bundle metadata is preserved under ignored artifacts.

## Checks and browser evidence

- **437 pipeline tests**, **27 web unit tests**, TypeScript/static build, and
  **9 production Chromium browser checks** pass. No check sends a provider request.
- Browser: Chromium 156.0.8078.4, Windows on the recorded development laptop.
  Browser automation uses Playwright with the pinned project runtime.
- The authentic five-picture journey verifies hidden-before-answer evidence,
  fixed revealed answers, backward navigation, refresh, scenario edits,
  deterministic repeated brief downloads, frozen configuration download, reset
  confirmation and preservation of unrelated browser storage.
- Generated fixture journeys also check corrupt/missing evidence, missing images,
  invalid assumptions, blocked storage, safe text rendering and keyboard actions.
- At **360, 768 and 1440 px**: no page-level horizontal scrolling; automated
  WCAG-tagged scans report **0 violations**. Real reveal/outline hover is scanned
  as well as challenge/lab views. This is not a claim of complete WCAG certification.
- Across 100 actual browser scenario edits, p95 update time was
  **40.00 ms**, below the 100 ms target. The measurement
  includes two animation frames to allow the visible result to settle.
- Fresh production-preview context, **10 Mbps / 100 ms RTT**: first usable challenge
  **1984.78 ms**, below 3 seconds. Only one photograph
  was requested; startup did not fetch the full image corpus. This is one local
  browser measurement, not remote-host performance.
- Compressed built JS+CSS: **125,300 bytes** (122.36 KiB),
  below 500 KiB. The local evidence directory contains only five photographs,
  three masks, original notices, structured evidence and frozen configuration.
- No external visitor requests, no non-GET visitor requests and no page errors
  were observed. Visitor rationale/decisions stayed local. No credentials, headers,
  raw provider errors or absolute machine paths are in the public package.

Records: [journey](../artifacts/browser-verification/journey.json),
[startup](../artifacts/browser-verification/startup.json),
[verified brief](../artifacts/browser-verification/verified-pilot-brief.md).
Screenshots: [landing](../artifacts/browser-verification/landing-1440.png),
[original](../artifacts/browser-verification/inspect-original-1440.png),
[revealed outline](../artifacts/browser-verification/reveal-outline-1440.png),
[360 px lab](../artifacts/browser-verification/lab-360.png),
[768 px lab](../artifacts/browser-verification/lab-768.png),
[1440 px lab](../artifacts/browser-verification/lab-1440.png).
These ignored local verification outputs are regenerated by browser checks.

## Bounded visual review and corrections

The agent viewed the landing, original photograph, revealed reference and mobile
lab screenshots. **Two distinct real dataset examples** were visually inspected:
`img-000071` and `img-000050`. No full-dataset visual review is claimed. The
reference overlay followed the second example's whole-object annotation; the
original remains available with the overlay off. Sample review cannot establish
alignment or small-defect visibility for every image. Existing broader source
review findings remain historical and were not repeated.

Screenshot review caught white text on a pale hover state for the active outline
button. The active hover now stays dark, with readable white text; overlay opacity
was reduced so the photograph remains readable. The corrected screenshot was
viewed and a real-outline accessibility scan was added. Earlier checks also caught
scenario/report integration and error-label issues; both were fixed and rerun.
One final offline run encountered a Windows temporary-file replace lock. The
unchanged failed case passed in a fresh test folder, followed by a complete pass;
no persistence rule or check was weakened and no genuine result was rerun.

Git's whitespace check passes for edited code and documentation. The unchanged
third-party licence/readme retain three original whitespace diagnostics; their
exact byte hashes are verified instead of reformatting the legal notices.

VS Code's native Computer Use helper failed after initialize/retry/reset/retry.
**VS Code integrated-browser UI remains unverified.** The recorded checks and
screenshots are actual Chromium verification, not a claim of VS Code inspection.
Open http://127.0.0.1:5174/ with **Browser: Open Integrated Browser**
(`workbench.action.browser.open`) to try it in VS Code. A local dev server was
started on that address; its static evidence endpoint was checked independently.

## Remaining limits and scope

The [local-use review](GEMINI_LOCAL_USE.md) records the confirmed Swiss/UK region,
user-confirmed Free access/quotas and scoped private noncommercial interpretation.
Lite used 118 submissions including its two trial calls; Flash used four trial
submissions. No paid fallback, billing change, other provider, publication or
remote infrastructure change occurred. Account evidence is user supplied, not an
independent billing audit. Configuration/byte hashes are integrity evidence, not
cryptographic provider attestation.

Source download URL/time/archive receipt and physical-object/session independence
remain unverified and are disclosed in the page and brief. Public benchmark
contamination cannot be excluded. Original licence/readme bytes are retained and
protected from Git line-ending conversion. Source code does not relicense dataset
assets. The optional surface track, publication clearance, full accessibility
audit, cross-browser coverage and authorized VPS/load/deployment checks remain
outside this local fastener milestone. Do not describe the whole two-track release
or factory readiness as complete.

## Visitor simplicity — first iteration

Verified 24 October 2026 after the original local-completion milestone. This
continuation supersedes the earlier opening-page layout and latest browser timing
measurements above; the saved evaluation and its 115 results are unchanged.

The opening now uses one column: a short purpose, Start the inspection and See
the results. Native About this demo details hold background and source limits.
Duplicate navigation and reset actions are absent on the opening; reset remains
available within the challenge/results. The public-data label, learning-demo
limit, fixture warning where applicable, dataset attribution and licence remain.
The results/challenge screens have not been redesigned in this iteration.

- **27 web unit checks**, TypeScript/production build and **10 production Chromium
  checks pass**. Pipeline code/data did not change; the earlier 437 pipeline pass
  is historical evidence and was not rerun for this UI-only step.
- The new genuine-bundle check verifies both entry paths, natural keyboard order,
  disclosure Enter/Space operation, and focus on content after navigation.
- Closed and expanded opening at **360/768/1440 px**: no horizontal overflow;
  automated WCAG-tagged scans report **zero violations**. Existing real-image,
  fixture, persistence/reset, export and privacy browser checks still pass.
- Opening fetches **zero photographs**. First usable challenge under the existing
  10 Mbps / 100 ms RTT profile: **2079.77 ms**;
  one photograph requested. Scenario edits: **40.10 ms p95**.
  Compressed built JS+CSS: **125,097 bytes**. These are local measurements.
- Initial restricted checks could not launch child processes (spawn EPERM).
  Identical checks passed with normal local process access.
- Fresh single-agent review covered requirements, diff, evidence honesty and
  unchanged saved results. Viewed desktop, phone and expanded-background
  screenshots. **Zero dataset examples visually inspected** in this task.
  This is a bounded layout review, not a user study or full accessibility audit.

New records: [opening checks](../artifacts/ui-simplification/opening-checks.json),
[desktop](../artifacts/ui-simplification/opening-1440.png),
[phone](../artifacts/ui-simplification/opening-360.png),
[tablet](../artifacts/ui-simplification/opening-768.png),
[expanded background](../artifacts/ui-simplification/opening-about-expanded.png).
Records/screenshots remain ignored local outputs. Existing browser-verification
journey/startup records were regenerated; the two-picture manual-review count in
that older journey record belongs to the original completion review above.

VS Code's helper initialized, but two app-list attempts reported native pipe
unavailable (OS error 2). Integrated-browser UI remains unverified. Actual checks
ran in Chromium 156.0.8078.4. The existing dev server returned HTTP 200 at
http://127.0.0.1:5174/. Open it using **Browser: Open Integrated Browser**
(`workbench.action.browser.open`). Returning visitors can click the Inspection
brand to see the new opening without clearing their progress.

No Gemini/provider requests, paid access, publication or remote changes occurred.
Next: simplify the results page so visitors see the key trade-off before detailed
metrics and scenario inputs. Recruiter/hiring-manager usability remains unmeasured.

## Picture choice reveal

Verified 24 October 2026. This second simplicity iteration supersedes earlier
visitor-facing labels/layout and browser measurements; the genuine 115-image
bundle, all source bytes, contracts and evaluation results remain unchanged.

The default challenge is one column: picture, Looks fine / Needs checking, Reveal
AI assessment. No AI answer/reference is shown before reveal. After reveal, the
original choice becomes fixed text and the visitor sees Your answer, Dataset
reference and AI assessment. Saved model observations are verbatim. Short factual
takeaways expose real flags/misses; uncertainty and failed assessments stay distinct.
Keyboard focus follows reveal; Next returns focus/scroll to the new picture title.

The results opening contains three counts: 81/93 defective parts flagged, 12/93
missed, 5/22 normal parts flagged, plus 115 assessed / zero unavailable and 86/115
sent for checking. Detailed results, workday/export, Where the results come from,
and About this demo & reset progress are native disclosures. Full statistics,
class denominators, source/capability limits, original notices, scenario assumptions,
reset confirmation and deterministic export remain available. The brief/calculations
and storage format are unchanged. The user's shorter labels supersede the original
button wording, preserving its meaning. Fixture warnings remain visible.

- **27 web unit checks**, TypeScript/production build and all **10 production
  Chromium checks pass**. Existing offline pipeline checks were not rerun; this
  task changes no pipeline/schema/data files.
- Genuine and fixture five-answer journeys, gated reveal, fixed restored answers,
  zoom/outline, both entry paths, reveal/Next keyboard focus, deterministic repeated
  brief downloads, frozen configuration download and resets pass. The real miss on
  image 2 is asserted. Visible saved observations match the genuine bundle.
- New plain-language summary assertions cover real counts and a fixture with three
  successful / three unavailable responses, preserving the distinction between
  successful AI detection and failure-driven human review.
- At **360/768/1440 px**, opening and closed/expanded results have no horizontal
  overflow and **zero automated WCAG-tagged scan violations**. Existing challenge,
  real-outline and error/state checks still pass. No page errors or external/non-GET
  visitor requests were observed in the complete authentic journey.
- Local startup under 10 Mbps / 100 ms RTT: **1965.19 ms**, one
  photograph. 100 scenario edits: **38.20 ms p95**. Compressed JS+CSS:
  **125,307 bytes**. Opening fetches no photographs. These are local measurements.

Fresh single-agent review covered the requirement/diff, honest denominators,
uncertainty/failure handling, unmodified observations, state/export and disclosures.
Visually reviewed desktop original, desktop outline/reveal, desktop results and
phone results; re-viewed the final reveal takeaway. **Two distinct real examples**
(`img-000071`, `img-000050`) inspected. No full-dataset visual review, nontechnical
visitor study, screen-reader trial or full accessibility certification is claimed.

Current screenshots: [challenge](../artifacts/browser-verification/inspect-original-1440.png),
[reveal](../artifacts/browser-verification/reveal-outline-1440.png),
[desktop results](../artifacts/ui-iteration-two/results-1440.png),
[phone results](../artifacts/ui-iteration-two/results-360.png),
[tablet results](../artifacts/ui-iteration-two/results-768.png).
The [journey record](../artifacts/browser-verification/journey.json) and
[startup record](../artifacts/browser-verification/startup.json) are regenerated
ignored outputs. The journey now records screenshot subjects rather than
hard-coding a manual-review count; this document owns the visual sample record.

Actual checks use Chromium 156.0.8078.4. VS Code integrated-browser UI remains
unverified following the earlier native-pipe failure; no new native UI inspection
is claimed. Existing http://127.0.0.1:5174/ returned HTTP 200. Open it in VS Code
with **Browser: Open Integrated Browser** (`workbench.action.browser.open`). Click
the Inspection brand for the opening if an earlier screen is restored. The
[local guide](FASTENER_LOCAL.md) has the current steps.

No new Gemini/provider requests, paid access, publication, dependency or remote
changes. Next iteration should use visitor feedback on this shorter flow.

## Manufacturing title and footer removal

Verified 24 October 2026. Visible title, loading title and browser tab now identify
**AI Visual Inspection for Manufacturing**. Header: Manufacturing / AI Inspection.
Subtitle: Computer vision for quality control. Try five parts. No footer remains;
unchanged dataset attribution, source and licence links are inside the shared
About this demo disclosure. This supersedes earlier title/footer screenshots.
Saved evidence, inspection flow, calculations and export content are unchanged.

TypeScript/production build and all **10 production Chromium checks pass**. The
existing opening check verifies both titles, absent footer and keyboard-accessible
credits after opening About. At 360/768/1440 px, closed/expanded opening scans have
zero automated WCAG-tagged violations and no horizontal overflow. Complete genuine
and fixture journeys, reset/storage, error handling, export and privacy still pass.
Latest local startup: **2011.87 ms**; scenario p95: **37.40 ms**;
compressed JS+CSS: **125,233 bytes**. Earlier unit/pipeline results were not rerun
for this text/layout-only change. Browser records were regenerated.

Fresh single-agent review checked diff/scope, copy and preserved attribution.
Viewed [desktop](../artifacts/ui-simplification/opening-1440.png) and
[phone](../artifacts/ui-simplification/opening-360.png) screenshots; **zero dataset
examples** visually inspected. [Opening checks](../artifacts/ui-simplification/opening-checks.json)
record keyboard/scan results. This is not a recruiter study or accessibility
certification. No job offer was inspected or exact job-fit claim made.

VS Code integrated-browser UI remains unverified following the earlier helper
failure; actual verification uses Chromium 156.0.8078.4. Open
http://127.0.0.1:5174/ with **Browser: Open Integrated Browser**
(`workbench.action.browser.open`) and click the header brand for the opening.
No new inference, dependency, paid access, publication or remote change. The
proposed saved-result playback mode remains a future, unimplemented idea.

## Clear answer comparison

Verified 24 October 2026. Reveal now groups **Your answer / AI assessment /
Dataset reference** into three equal desktop cards and compact aligned mobile
rows. Decision wording is consistent (Looks fine / Needs checking). Text and
symbols expose reference matches, misses and false alarms alongside contrast
and colour. A headline states whether visitor and AI agree, explicitly warning
when both agree but differ from the reference. Unsure and unavailable assessments
are neutral and require human checking; neither becomes a successful prediction.
Dataset labels remain explicit; these are learning references, not factory approval.
Verbatim saved observations/model/timing remain under Why AI said this. No new
prediction, state contract, scenario calculation or export change was introduced.

TypeScript/production build and all **10 production Chromium checks pass**. Genuine
cases assert three card identities/values, real miss, false alarm and correct
agreement. Fixture cases cover disagreement, both answers wrong, uncertainty,
refusal and invalid output. Explanation disclosure opens to the exact saved text.
At **360/768/1440 px**, real revealed comparisons have no horizontal overflow and
**zero automated WCAG-tagged violations**; desktop/tablet geometry checks assert
equal top positions, widths and heights. Existing gating/locked judgment, focus,
zoom, state/reset, error handling, export/configuration downloads and privacy pass.
Latest local startup: **1945.66 ms**; scenario p95: **34.90 ms**;
compressed JS+CSS: **125,678 bytes**. Offline pipeline/pure calculation checks were
not rerun: those files did not change. Browser records were regenerated.

Fresh single-agent review checked diff, honest outcomes, labels, accessible status
cues and preserved evidence/state. Visually reviewed [desktop comparison](../artifacts/ui-comparison/comparison-1440.png)
and [phone comparison](../artifacts/ui-comparison/comparison-360.png); re-viewed
corrected desktop. [Tablet comparison](../artifacts/ui-comparison/comparison-768.png)
is also recorded. **Zero source photographs visually opened**; crops contain
answer UI only. An obsolete reference margin initially made one card shorter;
screenshot review caught it, the style was removed and geometry assertions plus
the full browser suite reran successfully. No accessibility certification,
screen-reader trial or nontechnical visitor study is claimed.

VS Code integrated-browser UI remains unverified after the earlier helper failure;
actual checks use Chromium 156.0.8078.4. Existing http://127.0.0.1:5174/ returned
HTTP 200. Open it using **Browser: Open Integrated Browser**
(`workbench.action.browser.open`), answer a picture, then reveal.
Saved results and 115-image evaluation remain unchanged. No new provider requests,
paid access, dependencies, publication or remote changes. Playback remains a proposal.

## Watch AI Inspect — five-picture playback

Verified 24 October 2026. This supersedes the earlier statements that playback is
only a proposal. The existing **Try it yourself** journey and the new **Watch AI
Inspect** mode have separate state. Playback is labelled **Saved AI results** and
uses only the five already packaged pictures and the one qualifying Gemini run.
Saved observations, labels, membership, configuration and model results are unchanged.

Playback starts paused. Each loaded picture has three equal viewing stages: picture,
AI assessment, dataset reference. Normal viewing time totals three seconds; fast
and slow total 1.5 and six seconds. This is viewing time, not measured AI latency.
Play/Pause retains the current stage and unfinished fraction. Changing speed keeps
that fraction. Previous/Next pause and start the selected picture at its first stage.
Restart clears playback counts and returns to picture one, paused. Mode switches
and hidden tabs pause; returning never resumes automatically. Playback stops after
the fifth reference's viewing time. Missing/changed/undecodable pictures have Retry;
the timer waits for successful integrity, dimensions and decode checks.

The equally prominent AI/reference cards reuse the same decision wording, explicit
status text and symbols alongside color. There is no Your answer in playback.
Wide screens place picture and cards together; smaller screens stack them. Keyboard
help is a disclosure. Space, arrow keys, Home and Escape work from the playback
area; native button/select and zoomed-picture keyboard behavior remain available.
There are no reveal animations, moving timers or automatic scrolling, including
under reduced motion. Playback lives in memory; refresh returns to the ordinary
stored visitor screen, and a newly opened playback starts paused at picture one.

### Counts and evidence integrity

Each picture counts once when its reference is revealed. Seen-picture membership
survives backward navigation, pause and speed changes; Restart clears it. Genuine
five-picture totals: **2 defects flagged, 1 defect missed, 2 good parts flagged**;
five references shown, zero unsure and zero unavailable. These are curated playback
counts, separately labelled from the unchanged complete **115-image** benchmark.
Successful `uncertain` responses and technical failures appear separately and never
inflate the three categorical counts. Both require human checking; these playback
counts do not replace the full benchmark's routing metrics.

`git diff a42abc8 -- web/public/evidence tests/fixtures schemas web/package.json
web/package-lock.json` is empty. Bundle SHA-256 remains
`d880f82e321b36847ddd84a6607f74dcd994e1280b574e44e003ca7d0d5f39b5`.
No new provider request, model/configuration, confidence score, sensitivity control,
dependency, paid access, publication or remote modification was introduced.
Further models/configurations require separate genuine evaluation. Playback remains
bounded to these five pictures.

### Local checks and bounded visual review

- **30 web unit checks**, TypeScript/production build and **19 production Chromium
  browser checks pass**, including nine new playback checks. Offline pipeline
  code/data did not change; its earlier 437 passing checks were not rerun.
- Genuine browser playback checks every saved answer/reference and verbatim
  observation, stage order, count timing, final totals, backward replay without
  double-counting, stop-at-end and Restart. Pauses and active speed changes are
  checked at partial-stage boundaries with a deterministic paused test clock.
- Mode switching preserves visitor storage byte-for-byte, including a preexisting
  unrevealed answer. Unanswered challenge evidence stays gated. Hidden/visible
  tab events are exercised through synthetic `document.hidden` and
  `visibilitychange`; this is not a native VS Code tab-switch observation.
- Delayed image responses start no viewing timer. Missing-image recovery pauses,
  disables Play, retries successfully and stays paused. Separate labelled fixtures
  check unsure, refusal and invalid-response cards/counts; fixtures are not AI evidence.
- At **360/768/1440 px**, keyboard and reduced-motion checks pass, both cards have
  equal dimensions, no page-level horizontal overflow occurs, and automated
  WCAG-tagged scans report **zero violations**. On desktop, both cards are asserted
  beside the photograph and inside the first 1000 px of viewport height. No active
  animations are present. This is not a screen-reader trial or WCAG certification.
- Existing authentic/fixture challenge, fixed answers, storage/reset, export,
  configuration download, errors, responsive scans and privacy checks pass.
  Playback and the complete authentic journey have no page errors, external visitor
  requests or non-GET visitor requests. Visitor decisions are never submitted.
- Latest recorded local startup under 10 Mbps / 100 ms RTT: **1928.69 ms**, one
  photograph requested. Scenario updates: **35.00 ms p95** across 100 edits.
  Compressed production JS+CSS: **127,762 bytes**, below 500 KiB. These are local
  Chromium measurements, not provider-speed or remote-host measurements.

Fresh single-agent review covered requirements, timer cleanup, unique counts,
separate judgments, uncertainty/failure honesty, preserved evidence and the diff.
Viewed desktop/phone playback screenshots before and after the layout correction:
**one distinct source photograph, `img-000071`**, throughout. Automated screenshots
elsewhere are not additional manually inspected examples. No dataset-wide visual
review or visitor study was performed. Review moved verbose keyboard help into a
disclosure, shortened speed labels and placed picture/cards together on wide
screens; corrected the header's active-page marker while watching.

Initial restricted test launches failed with Windows spawn EPERM; identical checks
ran with normal local process access. Two existing multi-scan browser tests hit
their 30-second overall timeout, so their overall limits are now 90 seconds while
all assertions and performance targets remain unchanged. Test development also
caught a long accessible select label and an advancing test clock; the label and
test setup were corrected, with real saved answers left untouched.

Records: [playback](../artifacts/watch-ai/playback.json),
[phone keyboard/accessibility](../artifacts/watch-ai/accessibility-360.json),
[tablet](../artifacts/watch-ai/accessibility-768.json),
[desktop](../artifacts/watch-ai/accessibility-1440.json).
Screenshots: [desktop](../artifacts/watch-ai/playback-1440.png),
[phone](../artifacts/watch-ai/playback-360.png),
[tablet](../artifacts/watch-ai/playback-768.png).
Outputs remain ignored local verification artifacts, regenerated by the browser suite.
Browser: Chromium **156.0.8078.4** on Windows.

VS Code native UI control is unavailable in this session; integrated-browser UI
remains unverified after the previously recorded helper failure. Actual verification
uses Chromium. The local server returned HTTP 200 at http://127.0.0.1:5174/.
In VS Code use **Browser: Open Integrated Browser** (`workbench.action.browser.open`),
then choose Watch AI Inspect and Play. The [local guide](FASTENER_LOCAL.md#watch-the-five-saved-results)
records all controls. Existing provenance/licensing, contamination and factory-use
limits remain. This completes the requested local playback scope, not publication,
the surface track or the entire two-track release.

## Model comparison display — first milestone

Verified 24 October 2026. Results now contains a comparison table populated only
from complete validated saved runs on the same pictures and labels. It currently
shows **one genuine model**, Gemini 3.5 Flash-Lite, not a completed multi-model
evaluation. The user's new comparison goal and remaining candidate/access work
are recorded in [MODEL_COMPARISON.md](MODEL_COMPARISON.md).

The real row shows 12/93 defects missed, 5/22 good parts flagged, 115/115 AI answers,
0/115 no answer, 0/115 unsure and 86/115 sent for checking. Median recorded request
time is **4.96 seconds**, derived from all 116 attempts, including the recovered
server error. Each row shows timing coverage; absent times remain Unavailable,
not zero. Failed requests remain separate from successful AI assessments. The
counting guide explains uncertainty, class denominators, failure-driven review
and the distinction between request time and saved-playback viewing time.

Selecting a saved model changes its detailed results and workday/brief inputs
without changing visitor judgments or image identity. The existing detail and
frozen-configuration downloads remain available. The results page is wider on
desktop so all table columns fit; smaller screens have a keyboard-focusable
horizontal table scroll area, without page-level horizontal overflow. Current
colors, manufacturing title, absent footer and both inspection modes are preserved.

- **31 web unit checks**, TypeScript/production build and **21 production Chromium
  browser checks pass**. Two new browser cases check the genuine table and clearly
  labelled two-model fixture selection. Existing inspection/playback, reset,
  export, privacy, loading and error checks still pass.
- Genuine values are asserted against the saved complete run; no unsupported
  Flash row or fake result is displayed. Generated fixture checks cover unequal
  successful-class denominators, three unavailable responses, uncertainty, missing
  timings and model selection while preserving prior answers/reveals/image.
- At **360/768/1440 px**, table scans report zero automated WCAG-tagged violations
  and no page overflow. Keyboard scrolling works on mobile, selection works with
  Enter and desktop table columns fit without internal scrolling. No page errors
  or external visitor requests occurred in the genuine comparison check.
- Fresh single-agent diff review checked all-attempt timing, missing measurements,
  uncertainty/failure semantics, complete-set membership validation, honest single
  model status and unchanged evidence. Viewed desktop/phone table crops only:
  **zero source photographs** inspected for this task. This is bounded UI review,
  not complete accessibility certification or a user study.

Records: [verification](../artifacts/model-comparison/verification.json),
[desktop](../artifacts/model-comparison/comparison-1440.png),
[phone](../artifacts/model-comparison/comparison-360.png),
[tablet](../artifacts/model-comparison/comparison-768.png). Ignored outputs are
regenerated by the browser suite. Actual browser: Chromium 156.0.8078.4 on Windows;
VS Code integrated-browser UI remains unverified because native UI control is
unavailable. Use http://127.0.0.1:5174/ with Browser: Open Integrated Browser
(`workbench.action.browser.open`) and open Results.

Saved bundle, predictions, labels, membership, schemas, fixtures and dependency
manifests are unchanged from `62a08ff`. Offline pipeline code did not change, so
its earlier checks were not rerun. No new inference/provider request, image upload,
paid access, publication or remote change occurred. Remaining: verify current
candidate quotas/remaining allowance, prepare model-specific execution, obtain
genuine complete additional evaluations and integrate them before calling the
model comparison complete. Existing source/publication limits still apply.

## Model-aware playback readiness — 25 October 2026

The saved-result player now follows the selected model. With multiple complete
saved runs, a Saved model selector appears. Switching models preserves the current
playback picture, pauses at its first stage and clears counts. Restart preserves
the chosen model. Counters and cards read that model's actual saved responses;
visitor answers/reveals and challenge image identity remain unchanged. A model
selected in Results is used when entering playback. Existing one-model behavior
is preserved; no extra selector is shown for the current genuine single-model bundle.

**32 web unit checks**, TypeScript/production build and all **21 production
Chromium checks pass**. The extended labelled two-model fixture journey checks
Results-to-playback selection, switching from a revealed second picture while
playing, same-picture pause/reset, cleared counters and unchanged visitor storage.
A focused rerun of both comparison browser checks additionally verifies zero
automated WCAG-tagged violations and no page overflow with the multi-model controls
at 360 px. A unit case gives the models different normal-part decisions and checks
that their false-alarm counts stay separate. Every existing genuine and fixture
inspection/playback/export/reset/privacy journey still passes.

Fresh single-agent diff review checked model identity, synchronized selection,
instant model-change reset, timer/load restart, preserved judgments and the honest
one-real-model boundary. Viewed only the [phone controls crop](../artifacts/model-comparison-oct25/player-controls-fixture-360.png),
which uses labelled synthetic fixture model names. **Zero source photographs**
were visually opened in this task. This is bounded UI review, not full accessibility
certification. Actual browser: Chromium 156.0.8078.4 on Windows; VS Code integrated
browser remains unverified because native control is unavailable. The prior dev
server was not running when checked; the [local guide](FASTENER_LOCAL.md) has its
start command. Automated checks used their own production preview on port 4175.

The [new free-tier run record](GEMINI_COMPARISON_RUNS.md) owns authentic qualification
and partial full-set progress. Both new trial/evaluation request settings and future
configuration packaging are checked by **453 offline pipeline tests**. The genuine
website still shows only the completed 115-image Lite baseline. The two-model
fixture check does not establish a second complete real evaluation, and no partial
run is packaged. Existing source/licensing, provider terms, factory-use, cross-browser
and publication limits remain. No paid access, new dependency or publication.
