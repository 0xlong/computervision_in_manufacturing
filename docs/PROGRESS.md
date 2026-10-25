# Progress and next action

Updated: 25 October 2026. This file records project state, not promised implementation success.

## Aligned inspection grid and consistent controls (25 October 2026)

Status: Verified locally; focused checkpoint. One
coordinator on `main`, no workers. Parent: user's minimal UI refinement,
US-02/03/08/09; FR-REVEAL-001/002, NFR-ACCESS-001, NFR-LAYOUT-001. Dependencies:
current persistent-score cards and reference-tile outline. Allowed: Watch, shared
styles, Watch browser checks and only this new progress section.

Tasks/acceptance: (1) align the uncropped photograph and three closed assessment
cards in a four-column desktop grid and a two-by-two tablet grid; retain compact
single-column cards on phones; (2) unify button shape, sizing and interaction
states, align toolbar controls, and move model explanations inside their cards;
(3) check 320/360/768/1440 px, keyboard, expanding details/outline, all journeys,
unchanged benchmark/visitor data; (4) bounded visual review and focused checkpoint.

Implemented: one shared grid for the photograph and all three assessment cards,
with 16 px gaps and aligned edges. At 1440 px, all four cells measure **288 x
288 px**, with matching top/bottom edges. Tablet layout is two-by-two with equal
square cells; phones stack the full photograph and compact cards to avoid empty
space. The image remains uncropped at Fit; zoom and the real reference outline
remain available. Expanded explanations/counts grow naturally rather than clipping
or shrinking text; exact square alignment applies to the closed default view.

Moved Why AI said this inside each model card, grouped with its score/footer.
Footer dividers align with the reference control. Scores stay visible throughout
playback and still update only when the reference appears. No duplicate text or
navigation was added. Kept the existing forest green, backgrounds and status
colors. Shared buttons use an 8 px radius, consistent border/type/hover/focus
states and a 44 px minimum height. Zoom buttons use a compact 36 px variant.
Play remains the filled primary action; other actions are quieter outlines.
The speed control and filter align, including wrapped labels at 320 px.

Design references: W3C's [target-size guidance](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
and [reflow guidance](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html).
The exact grid, spacing and button appearance are project design choices, not a
claim of a universal visual standard or complete WCAG conformance.

Checks: production TypeScript/build pass. All **27 browser cases pass across the
full run and focused rerun** (23 passed in the full 3.9-minute run; four responsive
cases passed in a 28.5-second rerun). Four initial layout checks used a broad
selector matching both newly grouped disclosure sections; targeted the direct
Score details child and reran all four widths. No requirement/threshold weakened.
The initial four-width visual pass also passed before the footer alignment polish.

New geometry checks verify equal photograph/card dimensions and top edges on
desktop, two-by-two placement at 768 px, persistent scores, aligned speed/filter
heights, 8 px control radii, controls at least 44 px high, keyboard outline/details,
visible focus, no page overflow and no automated WCAG-tagged violations at
**320/360/768/1440 px**. The complete 115-picture and 26-picture filtered checks
retain Gemini **98/115** and Gemma **89/115**; visitor answers, refresh, replay,
reset/export, uncertainty/failure cases and reference-mask recovery pass.
The shared button changes also passed Try it and Results journeys/layouts.

The previously failed startup check passed this run at **2425.8549 ms** under the
unchanged 10 Mbps / 100 ms RTT profile, fetching one challenge photograph.
Earlier slower results remain recorded below; the cause of timing variability
has not been established, and this UI work is not claimed as a performance fix.

Fresh single-agent review checked semantic grouping/order, natural expansion,
closed-view image readability/alignment, consistent interaction states, reveal
gating, unchanged calculations/evidence and preserved visitor state. Public data,
provider code, dependencies and calculation/playback/state modules are unchanged;
pipeline/pure-calculation tests were not repeated.

Visual sample: three grid-preview appearances of the same first photograph
(one distinct source picture), plus two controls-only crops. No other source
pictures visually opened; all-set checks are automated, not a full visual review.
[Grid and control screenshots/measurements](../artifacts/aligned-watch/),
[startup measurement](../artifacts/browser-verification/startup.json).

Remaining limits: native VS Code browser access, native devices, Safari and a
screen-reader audit remain unverified; actual browser checks use Chromium
156.0.8078.4. Next: refresh http://127.0.0.1:5174/ in **Browser: Open Integrated
Browser** (`workbench.action.browser.open`), choose Watch AI Inspect and Play;
try expanding a model explanation and showing the reference outline.
No model evaluations, provider calls, deployment or publication work. Checkpoint
scope: three UI/test files plus only this new progress section. Unrelated earlier
documentation/setup changes remain preserved and excluded.

## Cleaner Watch screen and reference-tile outline (25 October 2026)

Status: UI verified locally; startup speed target remains unmet in this session.
One coordinator on
`main`, no workers. Parent: user-requested UI iteration, US-02/03/06/08/09,
FR-REVEAL-001/003, NFR-ACCESS-001, NFR-LAYOUT-001. Dependencies: current persistent
model cards and existing verified reference masks. Allowed: Watch, Picture, App,
styles, Watch browser checks and only this new progress section.

Tasks and acceptance checks: (1) extend the dataset-reference tile with its own
outline toggle, gated until reference reveal and scoped to the current picture;
(2) remove the Watch subtitle, visible playback-status row and About this playback,
and hide the global background/footer on Watch while retaining them elsewhere;
(3) verify outline lazy loading/toggling/recovery, persistent scores, full/filtered
playback, visitor-state preservation, keyboard and 360/768/1440 px layouts;
(4) review the diff and save a focused checkpoint excluding unrelated edits.

Implemented: the reference tile extends to the same height as the model cards
and contains **Show/Hide reference outline** in its lower section. The toggle is
available only after the reference appears and only for pictures with a mask. It
loads the authentic mask on demand, and resets when the picture/replay changes.
The button and its explanatory line are removed from beneath the Watch picture;
the separate visitor challenge keeps its existing outline controls.

Removed the Watch subtitle and About this playback section, and suppressed the
global Public-data demo bar and About this demo/reset footer while watching.
Attribution, source limitations and reset remain available on the other screens.
The picture/stage status and keyboard instructions are available to assistive
technology without taking visible space. Controls, model explanations, persistent
scores, real error recovery and fixture notices remain available.

Verification: TypeScript/production build passed; **25 of 26 browser cases passed**
in the full run (8.3 min). This includes all functional checks: the complete
115-picture run and 26-picture filter, unchanged final Gemini **98/115** and Gemma
**89/115**, retained visitor judgments/refresh/reset/export, genuine challenge
outline, timers, keyboard and 360/768/1440 px accessibility/layout checks. New
checks verify no visible subtitle/status/background/footer, equal reference/model
card height, an outline toggle inside the reference tile and none below the
picture, keyboard show/hide/focus, no page overflow, and no automated WCAG-tagged
violations. A separate generated fixture checks lazy mask requests, a missing
mask/retry, a normal picture without an outline, and correct reset/identity on the
next defective picture. Fixture results are not AI evaluation evidence.

**Remaining failed check:** startup under 10 Mbps / 100 ms RTT measured
**3000.1245 ms**, above the unchanged `<3000 ms` target. An isolated rerun measured
**3425.3614 ms**, so this is not marked passed. Inspected its network trace: all
five local requests returned HTTP 200, with one challenge photograph fetched;
no full-corpus startup load. The cause of the timing increase and whether it is a
regression remain unresolved; no threshold, test or requirement was weakened.
No further performance implementation was added to this UI iteration.

Fresh single-agent review checked outline gating/current-picture identity,
default Picture behavior, reference versus AI attribution, persistent scores,
screen-reader status, source/attribution availability on other screens, and the
focused diff. Public evidence, calculations/playback state, data, dependencies and
provider code are unchanged. Pipeline/pure-calculation tests were not repeated.
Visually inspected two card-only screenshots (360/1440 px), zero source pictures;
tablet layout checked automatically. This is not a dataset visual review.

Native VS Code browser access remains unverified as previously recorded; actual
checks use production Chromium 156.0.8078.4 on port 4175. No native-device, Safari
or screen-reader audit is claimed. Next: try Watch AI Inspect on
http://127.0.0.1:5174/ using **Browser: Open Integrated Browser**
(`workbench.action.browser.open`), then Play and Show reference outline inside the
reference tile. A separate follow-up should investigate the startup timing.
No model evaluations, provider calls, publication or deployment work resumed.
Checkpoint scope: five UI/test files and only this new progress section; earlier
unrelated documentation/setup edits remain preserved and excluded.

## Keep playback scores visible between pictures (25 October 2026)

Status: Verified locally; focused checkpoint. One coordinator
on `main`, no workers. Follow-up to the accepted card layout; US-02/03/08/09,
FR-REVEAL-001/002, NFR-ACCESS-001, NFR-LAYOUT-001. Dependencies: existing card
footer and unchanged playback counters. Allowed: Watch/assessment components,
playback browser checks/helpers, and only this new progress section.

Small tasks: keep model names/scores and the dataset-reference heading visible;
hide only unrevealed answers/explanations; check automatic next-picture changes,
navigation, full/filtered scores, keyboard and 360/768/1440 px layouts; review and
save a focused checkpoint excluding unrelated edits. Acceptance: both model
scores remain visible at every picture/model stage, update only on reference,
and answers still reveal Gemini, Gemma, then dataset reference.

Implemented: persistent Gemini/Gemma card headings and score footers, plus a
persistent dataset-reference heading. Only each answer/status and its explanation
are hidden until that stage. Reserved explanation space avoids moving the other
model card when an explanation becomes available. Existing colors, collapsed score
details, reference-gated counting and all calculation/state/evidence files remain
unchanged. The default visitor cards retain their existing behavior.

Verification: all **25 production browser cases pass across the full run and
focused rerun**. Full run: 21 passed; four newly edited checks had test-setup
mistakes (one undefined before-snapshot, three absolute screen-coordinate checks
affected by image controls/keyboard scrolling). Corrected the snapshot placement
and compared score position within its card; retained visible-score, reveal-order,
overflow, keyboard, focus and accessibility requirements. All eight Watch cases
then passed in 29.6 s. Production TypeScript/build passed on both runs.

The full 115-picture check now explicitly verifies both scores remain visible at
each new picture and model decisions remain hidden until their stage. The
26-picture filtered ending retains Gemini 98/115 and Gemma 89/115; visitor answers,
refresh, replay, failures, uncertain/unavailable cases and the separate challenge
pass. At 360/768/1440 px, checks verify persistent scores, stable placement within
cards, keyboard expansion/focus, no page overflow and no automated WCAG-tagged
violations. Fresh single-agent diff review checked default visitor behavior,
neutral pending cards, hidden answer accessibility, reference gating and unchanged
evidence/calculations. No pipeline or pure-calculation tests were repeated: those
modules were unchanged. No source photographs were visually opened in this step;
the previously accepted card styling was reused, with automated layout checks.

Limitations: native VS Code browser access remains unverified as recorded in the
preceding step; checks use local production Chromium. No native-device, Safari or
screen-reader audit is claimed. Open http://127.0.0.1:5174/ using **Browser: Open
Integrated Browser** (`workbench.action.browser.open`), then Watch AI Inspect and
Play: both model names and scores remain visible as each new picture starts.
No model evaluations, provider calls, dependencies or deployment work. Only four
UI/test files and this new section are included; earlier unrelated edits remain
preserved and excluded. Next: user tries the continuous score display.

## Running scores inside model cards (25 October 2026)

Status: Done locally. One coordinator on `main`, no workers. User-requested UI
refinement; US-02/03/08/09, FR-REVEAL-001/002, FR-COMPARE-001/002,
NFR-ACCESS-001, NFR-LAYOUT-001. Dependencies: existing complete saved evaluations
and sequential playback. No model evaluations or deployment work resumed.

| Task | Allowed files / dependency | Acceptance check | Result |
| --- | --- | --- | --- |
| Fit running scores inside model cards | Watch, shared assessment component and styles; existing counts | Correct-so-far count directly beneath assessment, equal treatment, no duplicate bottom panel; extra counts collapsed | Verified |
| Verify affected journeys and layouts | Existing web checks/helpers; implementation complete | Reference-gated updates counted once, full/filtered scores, visitor persistence, keyboard, 360/768/1440 px | Verified |
| Review and focused checkpoint | This new progress section + six named UI/test files only | Authentic evidence/calculations unchanged; unrelated documentation/setup edits excluded | Reviewed; focused checkpoint |

Each model now has a small **Correct so far** count (correct / references viewed)
inside its assessment card, visible as that model is revealed. Counts still update
once when the dataset reference appears. The separate bottom totals panel is
removed. Defects flagged/missed, good parts flagged and unsure/unavailable counts
remain under each card's **Score details**. Before reference reveal, assessments
stay neutral; opening score details retains focus/open state when the reference
appears. The visitor challenge retains its existing cards and answers.

Checks run: `scripts/web.ps1 test` - **49 unit tests pass**;
`scripts/web.ps1 test:browser` - **25 production Chromium checks pass (3.9 min)**,
including a new production build/TypeScript check. The first restricted unit run
could not start a helper (`spawn EPERM`); permitted local process access passed.
No test or requirement was weakened.

The complete playback check verifies 230 genuine saved decisions and both models'
counters/denominators across all 115 references. The 26-picture filtered ending
retains complete-set scores: Gemini **98/115**, Gemma **89/115**. Single-model
fixtures separately verify unsure/unavailable answers stay outside correct counts.
Visitor judgments survive watching, replay and refresh; the five-answer challenge,
Results/export/reset and failure recovery pass. No external request/page error in
the genuine full run. No automated WCAG-tagged violation or page overflow in the
responsive checks. New checks confirm scores fit inside their cards below the
assessment, equal model widths, keyboard expansion/focus and reference gating.

Fresh single-agent diff review checked default visitor-card behavior, stable card
identity/focus at reveal, hidden unrevealed cards, retained categorical arithmetic,
full/filtered denominators, and removal of unused totals styles. Public evidence,
playback/calculation/state modules, datasets, dependencies and provider code are
unchanged. Backend tests were not repeated because no backend code changed.

Visually inspected **two card-only screenshots** (360 and 1440 px), **zero source
photographs**; tablet layout checked automatically. This is not a dataset visual
review. Native VS Code browser control failed because its native pipe is
unavailable; it remains unverified. Chromium **156.0.8078.4** exercised production
preview port 4175. No native-device, Safari or screen-reader audit is claimed.
Local dev URL http://127.0.0.1:5174/ returned HTTP 200. To view in VS Code use
**Browser: Open Integrated Browser** (`workbench.action.browser.open`).

The first final progress update failed on Windows' default text encoding and
temporarily emptied this file. Restored the complete pre-task file from the
existing workspace snapshot, verified exact normalized bytes against its saved
blob, and used a focused patch for this section. No prior progress was lost.

Next: refresh the local site, choose Watch AI Inspect, then Play. Look beneath
each model's assessment for its score; expand Score details if wanted.
[Card-only screenshots and layout records](../artifacts/card-scores/),
[full-run evidence](../artifacts/sequential-playback/full-run.json),
[filtered-run evidence](../artifacts/sequential-playback/filtered-run.json).
Existing unrelated documentation/setup changes remain preserved and excluded;
only this new section is included from this mixed progress file.

## Complete sequential playback and simpler navigation (25 October 2026)

Status: Done locally. One coordinator on `main`, no workers. User's clarified
request supersedes the five-picture Watch scope below; the visitor challenge
remains five pictures. Parent US-02/03/06/08/09; T-EVIDENCE/JOURNEY/ACCESS/CONTRACT.

| Task | Dependencies and acceptance check | Allowed files | Status |
| --- | --- | --- | --- |
| Package all 115 viewable references | Existing neutral prepared assets + complete unchanged saved bundle; exact IDs/labels/hashes/dimensions and aligned masks; no inference | New playback catalog/schema/builder and checks, public catalog/assets | Done |
| Sequential model reveals | Catalog contract; picture → first model → second model → reference, all cards together; count once only after reference | Watch, playback, assessment/comparison helpers and checks | Done |
| Minimal navigation and text | Top navigation exposes Try it / Watch / Results; no duplicate mode switch or single-model playback selector, concise controls | App, styles, dashboard and browser checks | Done |
| Verify complete journey and checkpoint | Full 115 and filtered ends, score invariance, visitor preservation, keyboard, loading/errors, phone/desktop, bounded visual review | Web/pipeline tests, local guide/verification, this section | Verified; focused Git checkpoint |

Preserved bundle identity, both saved evaluations, challenge IDs, visitor judgments
and unrelated uncommitted user edits. Added a separate versioned playback catalog
so existing saved judgments do not reset just to make all evaluated images viewable.
All 115 image and 93 mask hashes/dimensions pass automated checks; no exhaustive
visual inspection. Images load individually, with no full-corpus startup request.
No paid requests, dependencies, publication or remote changes.

The complete player shows 115 pictures, both models in fixed order and all three
cards together after the reference. Running correct/flag/miss/good-flag counts are
categorical, with unsure/unavailable separate. The filter covers all **26** genuine
different answers, including Gemma's unsure result. Final scores remain Gemini
98/115 (85.2%) and Gemma 89/115 (77.4%); model evidence/report bytes are unchanged.
Top tabs replace the duplicate mode row; the single-model playback selector is
removed. Further text is collapsed under About this playback / How scores are counted.

**49 web unit tests** and TypeScript/production build pass. All **25 browser cases**
pass across the full run and the isolated timing rerun. The full-run case checks
230 saved decisions, every reference/counter update across 115 pictures, stopping,
replay reset and visitor-state preservation/refresh. The filtered case checks all
26, score invariance, review/replay and honest watched counts when skipping ahead.
Single-model/no-match fixtures, unsure/unavailable/missing timing, catalog/image
failures, exact pause/speed behavior, top-tab/visibility pauses, keyboard, reduced
motion and 360/768/1440 px layouts pass. No automated WCAG-tagged violations or
page overflow in the responsive scans, and no external requests/page errors in
the full run. The visibility check is synthetic, not a native VS Code tab audit.

**496 offline pipeline cases** pass across the regression and focused rerun:
495 passed in the full suite; one fake-run setup hit Windows WinError 5 while
replacing a temporary evidence file, then passed unchanged in a fresh test folder.
The file-check suite contended with browser timing: the page-load check measured
3.095 s against the unchanged <3 s target. Repeating it alone passed at **2.074 s**,
10 Mbps / 100 ms RTT, fetching one challenge image. No thresholds or checks weakened.
The new packaging tests include changed-input preflight and preservation of public
files; the full asset audit verifies all catalog images/masks without inference.

Earlier corrections: imported the generated fixture dependency explicitly; copied
the sixth test image's metadata before changing its ID (avoiding alias duplicates);
made Viewing time an explicit label/control pair. Updated the old genuine-bundle
test from a v1-only assumption to the exact configuration version for each run
family, retaining hash/frozen-plan validation. Replaced obsolete five-picture/
single-model player tests with complete sequential journeys; the visitor challenge
retains its existing checks. Fresh single-agent review checked reveal order and
reference gating, neutral pre-reference cards, timer cleanup, stable full/filter
IDs, categorical versus routing totals, catalog validation and saved visitor state.

Viewed **two player screenshots**, desktop and phone, showing the same first image
(two displayed examples / one distinct source picture). No additional source
photographs viewed. Native VS Code browser remains unavailable/unverified; actual
browser Chromium 156.0.8078.4, production preview 4175. Existing user edits remain
excluded. Next: user refreshes the local site and tries Watch AI Inspect → Play;
remaining model evaluations/surfaces/publication clearance stay separate work.

[Guide](FASTENER_LOCAL.md#watch-all-115-saved-results),
[verification and packaging command](FASTENER_VERIFICATION.md#complete-sequential-playback--25-october-2026),
[full run](../artifacts/sequential-playback/full-run.json),
[filtered run](../artifacts/sequential-playback/filtered-run.json).

## Playback totals, different answers and final dashboard (25 October 2026)

Status: Done locally. Owner: one coordinator on `main`; no workers.
Parent: user's additional required features; US-03/06/08/09,
FR-COMPARE-001/002, T-EVIDENCE/ACCESS/JOURNEY. Existing user edits preserved.
Allowed: playback/dashboard components, pure calculations, styles and web tests;
local guide/verification and this progress section. Dependencies: existing validated
two-model bundle, five viewable teaching pictures and complete 115-picture records.

| Task | Dependency / observable completion check | Status |
| --- | --- | --- |
| Separate categorical counts | Saved decisions + reference labels; unsure/failures excluded from correct/flag/miss totals, every revealed picture counted once/model | Done |
| Different-answers playback | Stable challenge IDs; matching count, show-all, empty case and paused filter changes without score/judgment changes | Done; 2 of 5 genuine matches |
| End comparison dashboard | Full-set categorical calculations; equal cards, class denominators, timing, review/replay actions and distinct watched counts | Done |
| Verify and checkpoint | Independent evidence recount, full/filtered endings, uncertainty/failures, keyboard, 360/768/1440 layout, visitor preservation, build and diff review | Verified; focused Git checkpoint |

Scope: filtering applies to the five packaged/viewable pictures. Complete benchmark
scores always cover all 115 saved records, including the one genuine Gemma unsure
answer; routing metrics are not categorical correctness. No new inference, evidence
changes, dependencies, publication or remote operations are required.

Correctness independently verified from reference labels and final successful
responses: Gemini **98/115 (85.2%)**, 81 categorical defect flags, 12/93 misses,
5/22 good flags, 0 unsure/unavailable; Gemma **89/115 (77.4%)**, 72 categorical defect
flags, 20/93 misses, 5/22 good flags, 1 unsure and 0 unavailable. Gemma's routing
TP=73 includes that unsure answer; the dashboard deliberately does not reuse it.
Recorded median attempt times: 4.9563224 s (116 attempts) and 6.0602535 s (115).

**36 web unit tests**, TypeScript/production build and **28 production Chromium
checks pass**. Six new browser cases cover full/filtered endings and invariant
scores, both models' counters, replay reset, review actions, keyboard focus return,
visitor judgments, equal cards at 360/768/1440 px, and labelled fixture
uncertain/unavailable/missing-time/empty-filter cases. No automated WCAG-tagged
violations, page overflow, page errors or external requests in new checks.
The first test invocation hit Windows sandbox process restrictions; permitted
local execution passed. An initial new unit assertion guessed the challenge order
from prediction order; corrected to the actual stable challenge IDs. The first
new browser helper advanced two fake-clock stages in one call before React could
render; it now checks each stage separately. No app checks/requirements weakened.

Fresh single-agent review checked categorical versus routing arithmetic, complete
class denominators (including failures), stable filtered picture identities,
end timing, focus, timer cleanup, replay and visitor-state separation. Visually
reviewed **two dashboard-only crops** (desktop and phone), **zero source
photographs**; no broader visual review claimed. Native VS Code browser remains
unavailable/unverified; actual checks use Chromium 156.0.8078.4. Saved public
evidence is byte-unchanged. Backend code did not change, so pipeline tests were
not repeated. Older uncommitted documentation/setup edits remain excluded.

Try Different answers only → Play → Watch again. The filtered end states 2 watched
pictures while the cards still show the complete 115-picture scores. Next: user
tries the local experience; remaining model evaluations, surface track and release
clearance are separate later tasks. [Guide](FASTENER_LOCAL.md#watch-the-five-saved-results),
[verification](FASTENER_VERIFICATION.md#playback-dashboard--25-october-2026),
[independent browser audit](../artifacts/comparison-dashboard/evidence-and-endings.json).

## Additional free candidates and quota-display correction (25 October 2026)

**Current state: the local website compares two genuine complete 115-image runs:
the preserved Gemini 3.5 Flash-Lite baseline and Gemma 4 26B. Locally verified.**

Owner: one coordinator on `main`, no workers; user requested genuine free-model
comparison, then supplied additional limits and confirmed all other models unused
today. Parent EN-03 / US-03/06/09; API-FREE/INPUT/OUTPUT/RUN/QUOTA/RETRY/AUDIT and
T-CONTRACT/ACCESS. Baseline `075dbcb`. Allowed: new isolated Gemma config/schema/
probe/evaluator/tests, versioned public configuration, comparison guides and this
section. Do not edit frozen Gemini runners.

| Task | Dependencies / observable completion check | Result |
| --- | --- | --- |
| Correct peak/current usage interpretation | User clarification and first-party source; preserve original receipts | Documented; limits numerators are peaks, not today's balance |
| Prepare small Gemma trials | Exact hosted IDs/image support/free pricing, user zero-use reply, same normal pixels/prompt | Frozen request checkpoint `e38a8a4`; both passed strict image/JSON trials |
| Verify and checkpoint request path | Generated offline checks; 16K TPM protected, no changed frozen campaigns | 465 pipeline tests pass; 12 new tests, no network/key access |
| Run and inspect real normal trials | Frozen checkpoint/current access; at most 3 submissions/model | Done: 2 successes/model, four total submissions, zero retries |
| Prepare complete 26B evaluation | Same 115 pictures/prompt/reference; rolling shared TPM, quota/error/resume checks, versioned public configuration | Verified; full 480-test regression plus final 16-case evaluator rerun pass |
| Complete real 26B evaluation | Frozen checkpoint `9cfd7b1`, usable user-confirmed access, bounded serial batches | Done: 115 answers / 115 submissions; zero retries/failures, one unsure |
| Integrate and verify genuine comparison | Complete evidence only; baseline/assets/labels unchanged, model-specific player/visitor separation | Done: two real rows, 481 pipeline / 32 web / 22 production browser checks pass |

The earlier multi-model section below interpreted the first limits screenshot's
numerators as today's usage. That was incorrect. [Google support](https://discuss.ai.google.dev/t/rpd-is-not-being-reset/145704/3)
explains default peak usage over 90 days. Historical receipts/access/evidence are
preserved; an append-only local correction identifies the mistaken fields. The
19 actual locally journaled submissions/model are real; the earlier “one left”
was an internal allocation deduction, not a verified provider balance. Do not
reuse those historical access records. Existing three runs remain 17/115 each,
98 pending. Their saved responses and complete 3.5 Lite evidence stay unchanged.

Gemma screenshot caps: **30 RPM, 16K input TPM, 14.4K RPD/model**. The explicit reply
“all other models 0” to the current-usage question is recorded separately from the
peak display. It is user-confirmed access evidence, not an independent account
audit. Existing Free-tier and Swiss/UK private-local-use confirmation stands; no
repeated billing or regional question. Robotics ER 2 is a possible later candidate;
Live/embedding/generation endpoints are not selected here.

The isolated trial reuses normal-fitting reference/two probes, unchanged PNGs and
prompt, minimal thinking and the same strict JSON contract. Reserve 4,096 input
tokens/request, 12,288 total trial budget below 16,000 TPM, 60-second start spacing,
60-second hard request deadline, at most 3 total submissions/model. Journal before
send; stop on unknown/missing/excess usage, pause quota, no paid/format fallback.
New source/config/input identities protect existing multi-day Gemini campaigns.
Full Gemma evaluation/packaging needs a new frozen token-aware configuration; the
old evaluator's 16K/request reservation is incompatible with a 16K TPM cap.

Verification: the initial restricted pytest process could not create temporary
folders; the permitted offline rerun worked. A fake quota response lacked its
required retry window and was corrected; no checks weakened. **465 pipeline tests
pass** (12 new Gemma cases). Code/configuration reviewed again against token,
retry, deadline, privacy and evidence boundaries. No web code changed, so earlier
web/browser checks were not repeated. No source photographs visually opened.
The first full-run test was slow because it repeatedly loaded/validated the entire
ledger. It now reads once under the provider-wide lock and updates each journaled
attempt in memory; every snapshot is still durable. The diagnostic Windows stack
dump ended with an access violation; the ordinary suite rerun passed. A generated
unknown-outcome example was corrected to put interruption last, respecting the
existing prohibition on continuing after interruption. **480 pipeline tests pass**
after evaluation/packaging additions. The final 16-case evaluator rerun also passes,
including a new heavy-token window-expiry case and a minimum timer sleep to prevent
rounding stalls. It covers a complete fake 115-picture run, repeat/resume, shared
allowance, unknown/quota/auth/timeout/usage cases and frozen configuration v3.
The final complete pipeline suite passes **481 tests**. No checks weakened. No paid
requests, billing changes, dependencies, publication or remote changes.
Earlier uncommitted files remain preserved and excluded from these checkpoints.

[Trial settings, sources and next step](GEMMA_TRIAL.md),
[corrected previous run record](GEMINI_COMPARISON_RUNS.md).
Authentic trials: `probe-gemma-4-26b-a4b-it-5fa2077031b1` and
`probe-gemma-4-31b-it-f11b607b6934`, each 2/2 successful versioned answers,
`looks_acceptable` on both normal probes. Request seconds 6.471/7.404 versus
28.726/28.795; each reports 615 input tokens and 31–36 output tokens. Start gaps
at least 60 seconds. This qualifies request feasibility, not defect accuracy.
The trial audit verifies old evidence, frozen sources and public bundle unchanged.
No source photographs opened. Ignored audit/access files:
`artifacts/additional-models-oct25/`; saved Gemma plans/evidence:
`artifacts/gemma-probes/` and next `artifacts/gemma-evaluations/`. Four-hour access
freshness is internal, not provider expiry. 31B is qualified but not fully evaluated.

Full 26B evaluation: `eval-gemma-7292d2441bcfd2c1`, 115/115 valid structured answers,
115 submissions, zero retries/terminal failures/unknowns. One unsure anomalous part
is routed for checking, not called a successful categorical prediction. Independent
recount: 73/93 defects routed to review (72 categorical flags plus one unsure),
20 missed, 5/22 normal flagged, 17 normal passed, 78/115 total routed. Median recorded
attempt 6.060 s. Baseline remains 12/93 missed, 5/22 normal flagged, zero unsure,
median 4.956 s, 86/115 review. It has fewer misses and lower request time on this
dataset; no universal winner or significance claim. Model/configuration settings
differ as recorded, without final-test tuning.

Minimum full-evaluation start gap including phase/batch boundaries: 10.010 s;
maximum reserved rolling input window: 7,171 < 16,000. Total shared Gemma calls:
119, including both two-picture trials. A real partial Gemma run was rejected
before packaging output creation. All original Gemini evidence and frozen request
sources remained byte-identical. No new Gemini generations in this milestone.
The complete-set audit checks exact 115 IDs/pixel hashes/prompt/reference/schema
against baseline and independently recounts outcomes from labels/saved answers.

New bundle `fasteners-92538e3ac8f7cbfa` adds one genuine completed model. Baseline
evidence/report, five teaching IDs/labels/image/mask bytes, notices and original
public configuration are identical. Full old public copy preserved under
`artifacts/additional-models-oct25/baseline-public/`. Existing evidence-change
handling restarts an older saved browser challenge once; within the new bundle,
model/mode changes preserve visitor judgments. Only App's provider-specific wording
changed to saved responses; title/colors/layout/footer behavior are unchanged.

**32 web unit checks**, TypeScript/build and **22 production Chromium checks pass**.
The first browser run found one old test assuming a single configuration-download
link. It now verifies every exact model file and SHA-256; full rerun passes. New
real Gemma playback checks all five saved decisions/observations/counters, final
stop, selected-model identity, same-picture paused model switch, cleared counts and
unchanged visitor answers/reveals/image. Fixture edge cases remain explicitly
labelled. No external browser requests/page errors, no page overflow or automated
WCAG-tagged violations in responsive scans. Viewed two UI crops (desktop comparison,
phone controls), **zero source photographs**. Chromium 156.0.8078.4; native VS Code
browser unavailable/unverified, tab visibility simulated as documented. Automated
browser uses production preview 4175; use local guide for VS Code on 5174.

[Complete 26B audit](../artifacts/additional-models-oct25/complete-26b-audit.json),
[integration audit](../artifacts/additional-models-oct25/bundle-integration.json),
[genuine browser playback](../artifacts/additional-models-oct25/genuine-playback-browser.json).
Next: further genuine full evaluations (31B and remaining 98/model for three Gemini
campaigns) with usable current access; do not rank partial runs or fabricate access
refreshes. No evaluator/background schedule remains. Surface track and source/
publication clearance are separate later work. Earlier user changes remain intact.

## Multi-model free-tier runner and first batches (25 October 2026)

**Current state: three new models qualified; each has 17/115 saved test assessments
and is paused at daily allowance headroom. Full comparison remains unfinished.**

Owner: one coordinator on `main`; no workers. Parent EN-03 / US-03/06/09 and the
user's free-model comparison request; API-FREE/INPUT/OUTPUT/RUN/QUOTA/RETRY/AUDIT,
DATA-FREEZE/TEST and T-CONTRACT/ACCESS. Baseline `acf2288`. Allowed: versioned
comparison configs/schemas, request/evaluation/package tools and tests, model-aware
player/checks, run/verification guides and this section. Preserve earlier user edits.

| Task | Dependency / observable completion check | Result |
| --- | --- | --- |
| Record access and add runner | Actual screenshot caps/usage; bounded label-free requests, shared daily ledger and cross-phase spacing | Done; request checkpoint `dc432fb` |
| Qualify new candidates | Two successful normal-fitting probes/model with real metadata, versions, usage and observed-appearance text | Done: 2.5 Flash, 2.5 Flash-Lite, 3 Flash preview; six generation submissions, no retries |
| Start frozen complete-set evaluation | Same 115 IDs/pixels/prompt/reference; persist before send, reuse success, pause before allowance cap | Each at 17/115, 98 pending; later quota windows needed |
| Prepare packaging and playback | v1 output unchanged; v2 settings, same five IDs; selected-model cards/counters, same picture, paused reset and unchanged visitor answers | Verified; checkpoints `ae355fd`, `59f1eb0`; genuine combined bundle awaits complete runs |

The user's headed Free-tier screenshot records 3.5 Lite 15 RPM / 250K input TPM /
500 RPD (118 used), 3.8 Flash 5 / 250K / 20 (4 used), 2.5 Flash 5 / 250K / 20,
2.5 Lite 10 / 250K / 20 and 3 Flash 5 / 250K / 20 (last three zero used). Capture
time/project ID are unknown. This is user-supplied account evidence, not an independent
billing audit. 3.6 is absent; zero-quota, agent/image/TTS entries are excluded. All
three new metadata GETs returned HTTP 200/generateContent. Reuse the completed 3.5
Lite evaluation; preserve the old unsuccessful 3.8 trial. No repeated Free-tier
confirmation was requested. Current official capability/terms sources were checked.

The v2 configuration keeps the original clean RGB pixels, prompt and normal-fitting
reference/probes. REST thinking is budget 0 on 2.5 and low level on 3 Flash; these
are explicit model/configuration combinations, not identical reasoning effort.
No test-result tuning. Trial times: 2.925/3.712 s, 3.038/2.259 s and 20.854/14.439 s,
respectively. Both normal probes were acceptable for each model. This demonstrates
request feasibility, not defect recall or superiority. Existing Swiss/UK private
noncommercial local-use conclusion remains scoped to preparation, not publication.

Final first-day audit: **17/115 successful responses, 98 pending and zero terminal
failures/retries per new model**. Each used 2 trial + 17 evaluation requests, **19/model
and 57 total generation submissions** (three metadata GETs are separate), then paused
with one snapshot request as headroom. No unknown outcome remains. Observed minimum
start gaps across phases: 24.066 / 12.047 / 24.069 seconds, meeting 24/12/24 minimums.
All 115 input identities, prompt and normal reference match the baseline; its saved
evidence fingerprint and public bytes are unchanged. A real partial run was rejected
by the bundle builder before output creation. No partial defect benchmark was computed.
The genuine website still has only the complete 3.5 Lite row; fixtures are not a second
real model. Model-aware controls appear only when multiple completed runs are packaged.

Checks: **453 offline pipeline tests**, **32 web unit tests**, TypeScript/build and
**21 production Chromium checks pass**. Two focused comparison cases also pass after
adding the 360 px multi-model control scan. Cases cover new settings/endpoints,
quota/retry/unknown accounting, stale access, phase pacing, input/plan tampering,
no repeated successes, v1 compatibility, preserved teaching IDs and selected-model
counter/judgment separation. Initial generated fixture fingerprints/timestamps and
one fixture import were corrected without weakening checks. Fresh single-agent
reviews tightened phase pacing/output-link handling and checked packaging/player
state. Viewed only one labelled fixture-controls crop: **zero source photographs**.
No page overflow or automated WCAG-tagged violations in the mobile control scan.
VS Code integrated-browser UI remains unverified; actual browser is Chromium
156.0.8078.4. The prior dev server was not running when checked; the local guide has
the start command. No paid access, billing change, new dependency or publication.

[Run guide, limits, sources and resume syntax](GEMINI_COMPARISON_RUNS.md),
[execution audit](../artifacts/model-comparison-oct25/execution-audit.json),
[player verification](FASTENER_VERIFICATION.md#model-aware-playback-readiness--25-october-2026).
Ignored plans/evidence: `artifacts/gemini-comparisons/`; nonsecret receipt/access/audit:
`artifacts/model-comparison-oct25/`. Four-hour access freshness is an internal limit,
not a provider expiry. Do not fabricate refreshed access or infer current balances.
Next: resume the remaining 98/model in later quota windows with actual current
remaining usage and a new nonsecret access record; no background schedule exists.
Then regenerate full metrics, package the same five pictures and verify the combined
genuine comparison. Earlier uncommitted work remains preserved and excluded from
these commits; only this section/update date is staged from mixed PROGRESS.md.

## Model comparison — display ready; additional evaluations pending (24 October 2026)

The user now wants several free API models compared on the inspection task, with a
clear evaluation table. This is the current priority. Owner: one coordinator on
`main`, no workers; parent US-03/02/06/09, FR-COMPARE-001/002, T-EVIDENCE/T-ACCESS.
Baseline: `62a08ff`. The new request is not complete until additional genuine full
runs exist. Existing uncommitted documentation/setup work is preserved.

| Task | Allowed files | Dependencies / observable completion check | Status |
| --- | --- | --- | --- |
| Compare existing saved results | ModelComparison/Lab/styles and checks, local guide/verification, model-selection/comparison notes, this section | Existing validated bundle; real denominators/timing, multiple labelled fixture rows, selected model preserves judgments, responsive/keyboard/browser checks | Done locally |
| Prepare additional eligible models | Versioned comparison config/runner/package validation and tests; scope in MODEL_COMPARISON.md | Selected candidate IDs, documented model capability and free access; preserve old config/evidence identities, identical test membership and bounded preparation qualification | Pending; existing evaluation/packaging are Lite-specific |
| Obtain authentic full evaluations | Bounded offline runner and ignored new run records | Current model quotas/remaining allowance and qualifying frozen configuration; all 115 IDs end in success or terminal failure, no rerun of old successes | Awaiting preparation and current account information |
| Integrate model comparison | New immutable evidence bundle, table/visitor/playback model integration and checks | At least two genuine complete runs; honest coverage/errors, same-image comparison, model-specific playback counters, no changed reference labels | Pending new evaluations |

What changed: Results now has a comparison table with one row per complete saved
run. It shows defects missed, good parts flagged, AI answers, no answer, unsure,
median request time and parts sent for checking. Selecting a model drives existing
details/workday/brief selections without changing judgments/reveals/picture identity.
The sole genuine row is Flash-Lite: 12/93 missed, 5/22 normal flagged, 115/115 answers,
zero unavailable/unsure, median 4.96 s across 116 timed attempts and 86/115 checks.
No fabricated second result or universal-best claim appears. Detailed uncertainty,
failure routing, timing coverage and denominator explanations remain available.

Official model/pricing sources were checked. Shortlist: reuse existing 3.5 Flash-Lite;
consider 3.6 Flash; retain 3.8 Flash's unsuccessful normal-fitting trial honestly.
Image capability and published free pricing do not prove actual quota. Existing
Free-tier confirmation stands; requested only current 3.8/3.6 RPM, input TPM, RPD
and remaining daily usage via AI Studio. With the recorded 3.8 20-RPD allowance,
115 first attempts require at least six daily windows before trial/retry overhead.
No new provider generation/image upload was made. Additional providers need their
own verified access and reviewed content-use terms before any uploads.

Checks: **31 web unit tests**, TypeScript/production build and **21 production
Chromium checks pass**. Genuine baseline values/timing, single-model disclosure,
labelled two-model fixture selection, missing timing, uncertainty and technical
failures pass. Prior answers/reveals/image remain unchanged when selecting models.
360/768/1440 px table scans: zero automated WCAG-tagged violations and no page
overflow; keyboard mobile scrolling/Enter selection and desktop column fit pass.
All original inspection/playback/export/reset/privacy checks pass. No external
visitor requests or page errors in the real table check. Pipeline/schema/config,
fixtures, dependency manifests and saved public evidence are unchanged, so pipeline
checks were not rerun. Documentation links/fences and staged whitespace pass.

Fresh single-agent review checked the diff, all-attempt median, missing timings,
class denominators, failure/uncertainty honesty and actual completion status.
Viewed desktop/phone table crops: **zero source photographs**. Actual browser:
Chromium 156.0.8078.4 on Windows. VS Code integrated-browser UI remains unverified;
use http://127.0.0.1:5174/ with Browser: Open Integrated Browser
(`workbench.action.browser.open`), then Results → Compare models.
No provider calls, paid access, publication, dependency or remote changes occurred.
Only this new section is staged from the mixed progress file; earlier edits remain.

[Comparison plan / sources / next work](MODEL_COMPARISON.md),
[verification](FASTENER_VERIFICATION.md#model-comparison-display--first-milestone),
[local guide](FASTENER_LOCAL.md). Ignored records/screenshots:
`artifacts/model-comparison/`. Checkpoint: Add saved-model comparison table and record evaluation plan.
Next: obtain the requested model quota/remaining-usage information, then prepare
and qualify additional configurations before serial complete-set evaluation.
The table is working software; the second-model evaluation is not yet evidence.

## Watch AI Inspect — five-picture playback (24 October 2026)

Status: **Done locally; stop after this scope.** Owner: one coordinator on `main`,
no workers. Parent US-02/06/09 plus the explicit playback request; FR-REVEAL,
T-EVIDENCE, T-ACCESS and SEC-PRIVACY-001. Baseline UI checkpoint: `a42abc8`.

The website now offers Try it yourself and Watch AI Inspect. Watching replays the
five existing pictures and genuine saved AI answers, with equally prominent AI /
dataset cards and no visitor-answer card. It starts paused, retains stages and
remaining time across pauses/speed changes, waits for pictures, recovers from errors,
pauses on mode/hidden-tab changes, and stops after picture five. Restart clears only
playback state/counts. Visitor judgments, reveal gates and stored progress are unchanged.
The manufacturing title/colors and absent footer are preserved.

| Milestone | Allowed files | Dependencies and observable completion check | Result |
| --- | --- | --- | --- |
| 1: staged playback | App/shared assessment/playback/styles and focused checks | Existing five packaged pictures and saved run; picture → AI → reference, Play/Pause, independent judgments, stop at end | Done; checkpoint `c65e709` |
| 2: controls and recovery | Picture/playback and focused checks | M1; Previous/Next/Restart pause, adjustable viewing time, loading/Retry, mode/tab freeze | Done; checkpoint `0d0a33a` |
| 3: counts and accessibility | App/playback/styles/checks, local guide/verification, this section | M2; count unique revealed references, separate unsure/failures, keyboard/reduced motion, responsive browser checks, fresh diff review and commit | Done; final checkpoint: Verify playback counts controls and accessibility |

Normal viewing is three seconds per picture, one second per stage; fast is 1.5
seconds and slow six. Loading adds time. The mode says Saved AI results and
explicitly distinguishes viewing time from AI processing speed. Five-picture totals:
**2 defects flagged / 1 defect missed / 2 good parts flagged**, five references
shown, zero unsure/unavailable. Revisits never double-count. Unknown answers are
separate from categorical counts and need human checking. These curated counts
remain separate from the complete 115-image benchmark. Only one qualifying model;
new models/configurations need separate genuine evaluation and remain future work.

Verification: **30 web unit checks**, TypeScript/production build and **19 production
Chromium checks pass**. All nine new playback checks pass, alongside every existing
journey check. Cases cover fractional-stage pause/resume, active speed changes,
loading/Retry, genuine five-picture values/observations, end/Restart, repeat visits,
separate uncertain/refusal/invalid fixtures and unchanged visitor storage. At
360/768/1440 px: no horizontal overflow, equal comparison-card dimensions, zero
automated WCAG-tagged violations; keyboard and reduced-motion checks pass. No
external/non-GET visitor requests or page errors. Startup: 1928.69 ms under the
recorded 10 Mbps / 100 ms RTT profile, one photograph; scenario p95 35.00 ms;
compressed JS+CSS 127,762 bytes. Offline pipeline files/data did not change; the
historical 437-test pipeline result was not rerun.

Fresh single-agent review checked requirements, timer cleanup, evidence integrity,
counts, state separation and the diff. Visual review covered desktop/phone before
and after compacting controls/help and placing cards beside the picture on wide
screens: **one distinct source photograph (`img-000071`)**. The header no longer
marks Try it active during playback. Windows spawn EPERM required normal local
process access. Two existing multi-scan tests needed a 90-second overall timeout;
assertions and performance thresholds were preserved. The accessible speed label
and deterministic test clock were corrected during verification.

[Full verification and limits](FASTENER_VERIFICATION.md#watch-ai-inspect--five-picture-playback)
and [how to try it](FASTENER_LOCAL.md#watch-the-five-saved-results) record controls,
screenshots and ignored browser outputs. Browser: Chromium 156.0.8078.4 on Windows.
Tab-visibility verification uses synthetic hidden/visible events. Native VS Code UI
control is unavailable; integrated-browser UI remains unverified. Local server
returned HTTP 200 at http://127.0.0.1:5174/; open with Browser: Open Integrated Browser
(`workbench.action.browser.open`), then Watch AI Inspect → Play.

Saved evidence, labels, benchmark membership, fixtures, schemas and dependency
manifests are unchanged against `a42abc8`. No provider requests, paid access,
publication or remote changes. Source/licensing, factory-use, screen-reader,
cross-browser, second-track and remote-host limits remain. Earlier uncommitted work,
including the specification move and documentation/setup edits, is preserved and
excluded from these commits. Only this new section is staged from the mixed progress
file. Next: user can try the saved playback; no further implementation in this goal.

## Clear answer comparison (24 October 2026)

Owner: one coordinator on `main`; no workers. Parent US-02/09; FR-REVEAL-001–003,
FR-INSPECT-002/004 and T-ACCESS. Depends on genuine saved answers and fixed
visitor judgments. Allowed: App/styles, browser checks, verification and this section.
Task: equally sized Your answer / AI assessment / Dataset reference cards with
consistent decision wording, clear agreement/mismatch text, icons and contrast;
compact aligned rows on mobile. Keep unsure/failure outcomes distinct and source
labels explicit. Keep observations available without crowding the comparison.
Completion: saved and fixture agreement/error cases, gating/persistence, responsive
keyboard/accessibility checks, bounded screenshots, diff review and focused commit.
Status: Done locally. Three equal desktop cards now compare Your answer, AI
assessment and Dataset reference using the same Looks fine / Needs checking
wording, large answers and visible status text/icons. Green means matching the
reference, amber a mismatch; neither color replaces the written status. Mobile
uses aligned compact rows. An agreement heading distinguishes matching answers
from matching the reference, including when visitor and AI agree but are wrong.
Uncertain and unavailable AI outputs stay neutral, not matches or misses.
Dataset labels remain explicitly labelled, not presented as factory disposition.
Saved observations/identity/time are unchanged under Why AI said this (or failure
details). Reveal gating, fixed judgments, stored progress and exports are unchanged.

Checks: TypeScript/production build and all 10 production Chromium checks pass.
Genuine cases assert real misses, false alarms and correct agreement; generated
fixture cases assert disagreement, both answers wrong, uncertainty and unavailable
responses. Opened explanations match the verbatim saved observations. At
360/768/1440 px the genuine comparison has no horizontal overflow or automated
WCAG-tagged violations. Desktop/tablet card top edges, widths and heights match;
existing keyboard focus, reveal, refresh/reset, error/export/privacy checks pass.
Latest startup: 1945.66 ms; scenario p95: 34.90 ms;
gzip JS+CSS: 125,678 bytes. No pipeline/calculation files changed or tests rerun.

Fresh single-agent diff review covered categorical/unknown outcomes, colour plus
text/icon cues, explicit dataset labels, evidence honesty and unchanged state.
Viewed desktop/phone comparison crops; zero source photographs visually inspected.
Screenshot review caught an old reference margin shrinking the third card; removed
that unused style, added geometry assertions and reran all browser checks.
[Verification](FASTENER_VERIFICATION.md#clear-answer-comparison) records screenshots.
VS Code UI remains unverified after the earlier helper failure; actual checks use
Chromium. Existing http://127.0.0.1:5174/ returned HTTP 200. Open with Browser:
Open Integrated Browser (`workbench.action.browser.open`).

Focused checkpoint: Make visitor AI and reference answers easy to compare. Preserve
all earlier uncommitted work; stage only this new progress section. No provider
request, paid access, dependency, publication or remote change. Next: visitor
feedback on the comparison; playback remains a proposal. No screen-reader trial,
recruiter study or complete accessibility certification is claimed.

## Clear manufacturing title and no footer (24 October 2026)

Owner: one coordinator on `main`; no workers. Parent US-01/09, FR-START-001,
T-ACCESS and DATA-LICENCE-001. Dependency: working saved-results journey.
Allowed: App, index HTML, styles, existing authentic browser checks, verification
record and this section. Preserve all earlier uncommitted work.
Task: make manufacturing/computer vision immediately visible, remove the footer,
keep attribution/source/licence inside About this demo. Preserve the short
picture/choice/reveal flow. Playback is still a proposal, outside this small edit.
Completion: build and relevant browser checks; visible title/no footer, accessible
credits, both entry paths, responsive scans and bounded screenshot review; commit.
Status: Done locally. The heading, loading screen and browser tab now say
AI Visual Inspection for Manufacturing; header says Manufacturing / AI Inspection.
One short subtitle names computer vision and quality control. Removed the footer
and its CSS; moved unchanged attribution/licence/source links into shared About
this demo. Both entry paths and the picture/choice/reveal flow are unchanged.

Checks: TypeScript/production build and all 10 production Chromium checks pass.
Existing opening check verifies browser/visible titles, absent footer, credits
hidden until About is opened, then accessible source/licence links. Natural keyboard
order, closed/expanded scans and layouts at 360/768/1440 px pass with no automated
accessibility violations or horizontal overflow. Full genuine and fixture journeys,
state/reset/export, failures and privacy checks pass. Latest startup:
2011.87 ms; scenario p95: 37.40 ms; JS+CSS gzip:
125,233 bytes. Pure calculation/pipeline tests were not rerun for text/layout edits.
Fresh single-agent diff review checked short copy, attribution preservation and
scope. Viewed only desktop/phone landing screenshots: zero dataset examples.
See [verification](FASTENER_VERIFICATION.md#manufacturing-title-and-footer-removal).
VS Code UI remains unverified after the previously recorded helper failure;
actual checks use Chromium. Use http://127.0.0.1:5174/ with Browser: Open Integrated
Browser (`workbench.action.browser.open`); click the header brand for the opening.

Focused checkpoint: Clarify manufacturing title and remove footer. Preserve all
earlier uncommitted work; only this progress section is staged. No new inference,
dependency, billing, publishing or remote modification. Next product proposal is
saved-result automatic playback with pause/speed controls; it is not implemented
or authorized as part of this title/footer edit. No job-offer matching or recruiter
user study is claimed.

## Visitor simplicity — picture, choice, reveal (24 October 2026)

Owner: single coordinator on `main`; no workers. Parent US-01/02/03/04/05/08/09.
Dependencies: saved 115-image evaluation, existing browser state/calculations and
completed first opening-page iteration. Preserve all earlier uncommitted work.
Allowed: App/Lab/Picture/styles, browser checks, local guide, verification record and this section.
Task: make the challenge a single-column picture/choice/reveal flow; shorten
visitor-facing labels as explicitly requested; keep judgement-before-reveal and
locked revealed answers. Show three plain-language saved-result counts, with
statistics, scenario/export and source/reset controls in accessible disclosures.
Completion: genuine and fixture browser journeys, both entry paths, keyboard,
closed/expanded responsive accessibility checks, truthful failure/denominator
handling, unchanged deterministic export; bounded screenshot review; focused commit.
Status: Done locally. The default path is picture -> Looks fine / Needs checking
-> Reveal AI assessment. The shorter wording is the user's explicit refinement
of the specification's longer button labels; answer semantics are unchanged.
One column, no repeated side-panel instructions; revealed choices become fixed
text, with Your answer, Dataset reference and AI assessment clearly separated.
Saved observations stay verbatim; short takeaways distinguish misses, flags,
normal agreement, uncertainty and unavailable assessments. Focus moves to reveal;
Next restores the new picture/title rather than leaving visitors down the page.

Results lead with genuine counts: 81/93 defective flagged, 12/93 missed,
5/22 normal flagged; 115 assessed, zero unavailable, 86/115 total checks.
Details retain class denominators, failures, policy and both metric sets. Native
closed disclosures hold statistics, workday/export, source records and reset.
Removed duplicate notices, single-option challenge selector and unavailable-track
banner from the main path. Fixture warnings/attribution remain; source limitations,
capability limits and reset confirmations remain accessible. No result or contract
changed. The local guide now uses the actual labels and disclosure locations.

Verification: 27 web unit checks, TypeScript/production build and all 10 production
Chromium checks pass. Genuine five-picture reveal checks compare the visible saved
observation to the bundle and verify the real miss on image 2. Both entry paths,
Next focus/scroll, answer preservation, deterministic brief/configuration downloads,
refresh/reset, invalid inputs, broken assets/storage and visitor privacy pass.
At 360/768/1440 px, closed and expanded results have no horizontal overflow and
zero WCAG-tagged scan violations. Fixture checks preserve unavailable-response
counts separately from successful detections (3 assessed / 3 unavailable).
Startup: 1965.19 ms at 10 Mbps/100 ms RTT; scenario p95:
38.20 ms; compressed JS+CSS: 125,307 bytes. No pipeline change;
the earlier 437 pipeline pass was not rerun for this UI task.

Fresh single-agent review checked requirements, diff, genuine/fixture truth,
denominators, uncertainty/failures, disclosures, focus and state preservation.
Visually reviewed desktop challenge/reveal plus desktop/phone result screenshots;
re-viewed the corrected takeaway. Two distinct real dataset examples inspected,
not a full dataset review. [Verification](FASTENER_VERIFICATION.md#picture-choice-reveal)
records screenshots and limits. Actual browser is Chromium; VS Code integrated
browser remains unverified following the earlier native-helper failure. Existing
http://127.0.0.1:5174/ returned HTTP 200; use Browser: Open Integrated Browser
(`workbench.action.browser.open`). Click the brand to return to the opening.

Focused checkpoint: Simplify picture choice reveal and saved results. Preserve
all earlier uncommitted edits; stage only this progress section. No provider call,
paid access, publication, remote change or new dependency. Next: have the visitor
try the shorter flow and use their feedback to choose the next small improvement.
No recruiter user study, screen-reader trial or full accessibility certification
is claimed.

## Visitor simplicity — first improvement (24 October 2026)

Owner: one coordinator on `main`; no workers. Existing uncommitted work is
preserved. Parent US-01 / US-09; FR-START-001, T-JOURNEY and T-ACCESS.

Task: simplify the first-time visitor's opening page into one column, with a
plain-language purpose, one primary start action, a direct results action and
keyboard-accessible optional background. Keep public-data/prototype and factory
limitations visible; preserve authentic/fixture distinctions and all saved results.
Dependencies: completed local fastener journey and existing 115-image bundle.
Allowed files: `web/src/App.tsx`, `web/src/style.css`, browser checks,
`docs/FASTENER_VERIFICATION.md` and this new progress section only.
Completion: production browser checks show both entry paths work, optional details
open with keyboard, focus moves into content, layout fits 360/768/1440 px and
accessibility scans pass. Review the actual screenshots and commit focused files.
Status: Done locally. Replaced the two-column introduction and route card with a
single column, plain-language purpose and two entry buttons. Duplicate home
navigation/reset controls are absent; background is under native About this demo
disclosure. Reset controls remain available inside the challenge and results.
Public-data/prototype and factory-performance limits stay visible; fixture warning
stays prominent. No result, dataset, bundle, dependency or storage contract changed.

Checks: 27 web unit checks, TypeScript/production build and all 10 production
Chromium checks pass. The new authentic opening-page check covers both entry
paths, natural keyboard tab order, Enter/Space disclosure operation, content focus,
and closed/expanded accessibility scans at 360/768/1440 px (zero violations and
no horizontal overflow). The opening page fetches zero dataset pictures.
Existing reveal, export, refresh, reset, error and privacy checks still pass.
First usable challenge: 2079.77 ms at 10 Mbps/100 ms RTT; scenario p95: 40.10 ms.
Restricted child-process EPERM prevented initial startup; unchanged checks passed
with normal local process access. No checks or requirements were weakened.

Fresh single-agent diff review checked the start requirement, both real entry
paths, truthful saved/fixture evidence, unchanged results and reversible navigation.
Viewed three actual screenshots: 1440 px opening, 360 px opening and expanded
background. Zero dataset examples were visually inspected in this task; this is
layout review, not a dataset review or recruiter user study. Existing real-image
journey checks ran automatically. See [verification](FASTENER_VERIFICATION.md#visitor-simplicity--first-iteration).

VS Code Computer Use initialization succeeded but both app-list calls failed:
native pipe unavailable, OS error 2. Integrated-browser UI remains unverified;
actual Chromium is recorded. The running dev server returned HTTP 200 at
http://127.0.0.1:5174/. Use Browser: Open Integrated Browser
(`workbench.action.browser.open`) in VS Code to try it.

Focused checkpoint: Simplify the visitor opening page. Only this new progress
section is staged, leaving all earlier uncommitted progress/spec/workspace edits
untouched. No Gemini call, paid access, publication or remote modification.
Next separate milestone: simplify the results page into a short plain-language
summary with detailed statistics and assumptions available on demand.

## Fastener completion goal — completed locally

Completed 24 October 2026. The user's local fastener definition of done is met:
the complete visitor journey uses authentic saved Gemini evidence, relevant checks
pass, and production-browser verification is recorded. Nothing was published.
This current section supersedes older starter-page/next-action notes below.

Owner: one coordinator on `main`; no workers. Earlier unrelated working-tree edits,
including the specification move and documentation/workspace changes, are preserved.

| Milestone | Requirement / scope | Outcome and checkpoint |
| --- | --- | --- |
| Count complete-set evidence | EN-03; policy, coverage, failures and uncertainty; evaluator/tests/guide | Done; `a2e738c`; 14 new cases, 413 combined cases at that stage |
| Qualify and freeze free Gemini execution | EN-03/API safeguards; runner, generated tests, use/selection records | Done; `917f867`; two authentic normal trials, nine new runner checks; Lite selected, Flash excluded |
| Build visitor journey | US-01–06/08/09 fastener scope; shared schemas, web UI, calculations, storage/export, fixtures and tests | Done; `b53c1d0`; five answers, gated reveal/zoom, fixed answers, evidence lab, scenario, decision/brief and confirmed resets |
| Complete genuine test membership and package | DATA-TEST/FREEZE, T-EVIDENCE/CONTRACT/LICENCE; public fastener assets/configuration and offline checks | Done; 115/115 successful; 116 submissions including one recovered server 5xx; v2 bundle with original notices and downloadable frozen instructions/reference/settings |
| Verify local completion | T-JOURNEY/POLICY/SCENARIO/EXPORT/ACCESS/PERF/SECURITY; final tests, bounded visual review and records | Done; 437 offline pipeline, 27 web unit and 9 production Chromium checks; static build and workspace/doc checks |

Current bundle: `fasteners-f0b61a212fefce56`; run `eval-flash-lite-46e242a298f20b6f`.
Policy results: **12 missed / 93 anomalous**, **5 reviewed / 22 normal**;
86 total reviews, 115 successful outputs, zero terminal failures. All attempts,
reported aliases, usage, hashes and structured observations are retained. These
are public benchmark results, not factory validation. The five teaching examples
were curated after complete evaluation; no benchmark member or prompt was changed.
Only one model qualified; comparison, API heatmaps and sensitivity are explicitly
unavailable. No model result is fabricated or supplied by a fixture fallback.

Latest verification: all **437 pipeline tests pass** (140.18 s), **27 web units
pass**, and **nine production browser checks pass** (1.1 min). The authentic
journey includes deterministic repeated brief downloads, frozen configuration
download, refresh, reset and no external/non-GET visitor requests. Automated
accessibility/layout checks at 360/768/1440 px report zero violations. First usable
challenge: **1984.78 ms** at 10 Mbps / 100 ms RTT;
100 scenario edits: **40.00 ms p95**. Startup fetched
one photograph. Build size and machine/browser details are in the verification
record. A Windows test-file replace lock passed on an unchanged isolated rerun
and a subsequent complete suite; no persistence rule/check was weakened.

Fresh single-agent review checked exact membership/byte/pixel identities,
success versus failure routing, fixed policy, per-image gating, invalid inputs,
safe deterministic export, original notices, configuration hashes, missing-data
recovery and visitor-state privacy. Screenshot review found/fixed active-button
hover contrast and reduced reference tint; the corrected real-outline state was
rescanned and viewed. **Two distinct real examples** were visually inspected,
not the full dataset. Browser screenshots/downloads/timing JSON remain under
ignored `artifacts/browser-verification/` and can be regenerated without inference.

The native VS Code Computer Use helper was unavailable after prescribed retries;
VS Code integrated-browser UI remains unverified. The recorded browser evidence
is actual Chromium. Local server started and evidence checked at
**http://127.0.0.1:5174/**; use **Browser: Open Integrated Browser**
(`workbench.action.browser.open`) to try it in VS Code.

The user's Free-tier/key authorization remains accepted. Lite used 118 requests
including trials; Flash used four. Paid fallback, billing activation, other
providers, publication and remote changes were not used. The scoped Swiss/UK
noncommercial-use review is recorded, not a general publication clearance or
independent billing audit. Unknown source download receipts, related-object
independence and public-model contamination remain disclosed; local evidence keeps
development status. Optional surfaces, complete release/publication clearance,
full accessibility audit and authorized VPS/load checks remain future scope.

Try next: answer/reveal image 1, return to it, then use Evidence & pilot to change
capacity and download a brief. No additional inference is needed for this goal.
See [local guide](FASTENER_LOCAL.md), [complete verification](FASTENER_VERIFICATION.md),
[selection/execution bounds](GEMINI_EVALUATION.md) and [local-use review](GEMINI_LOCAL_USE.md).

## Gemini runner and user-confirmed free limits — latest continuation

The user explicitly confirmed the screenshot's Gemini limits are free and asked
to build. Accept that account confirmation; do not ask again. Stay with Gemini.
Recorded 3.8 Flash: 5 RPM / 250,000 input TPM / 20 RPD; 3.5 Flash-Lite:
15 RPM / 250,000 input TPM / 500 RPD. Screenshot showed zero usage at capture.
This is user-supplied evidence, not a fresh authenticated account audit. No key
contents were read/displayed during this task. Earlier edits remain preserved.

Owner: single coordinator on `main`; parent EN-03, supports US-02/03/06 and
API-INPUT/OUTPUT/RUN/QUOTA/RETRY/AUDIT. Shared saved-answer schema stays unchanged.

| Task | Dependencies and allowed files | Observable check | Status |
| --- | --- | --- | --- |
| Build serial Gemini transport and durable runner | Existing API contract, clean fitting inputs, current official REST docs; new runner/transport, bounded config/schema and generated tests | Fixed host/header POST, process deadline, bounded retries, quota pause, access stop, pre-submit journal, restart reuse and unknown-outcome refusal | Done; 64 new offline tests pass within the full suite |
| Prepare a small first trial | Existing normal-only package and hash checks; new trial guide, scoped API/model notes and this progress section | Same reference/two probes across models; exact request/prompt/image identities, budgets; no evaluation reads or network | Both real-data offline plans prepared; zero successes/attempts |
| Verify combined pipeline and review | Existing full offline suite, workspace/docs/diff checks | Existing preparation/contracts stay valid; scope/evidence claims reviewed | Done; 399 offline tests, workspace checks, 49 local documentation links/anchors/fences and whitespace checks passed |
| Execute authentic trial | Free account confirmation accepted; current allowance and separate terms/data-use evidence before sending | Saved authentic structured answers, versions, timings, usage/failures within frozen bounds | Pending use prerequisite; not executed |

Built `pipeline/run_gemini_trial.py` and `pipeline/gemini_transport.py`,
`configs/gemini-trial.v1.json`, `schemas/gemini-trial.v1.schema.json` and generated
integration/transport tests. No dependency, source picture, data split, frontend,
remote infrastructure or billing change. Zero real images were visually opened.
The website remains the starter page. No genuine AI assessment has been produced.

The runner selects one reference and two probes from hash-checked normal fitting
data only. No evaluator/test index is read. A single child owns a request; a hard
60-second process timeout includes response reads. Requests start at least 65 s
apart; a live-provider OS lock prevents concurrent instances. At most six requests
per model including retries, with 16,000 planned input tokens/request and 2,048
output-token cap. Unknown submissions are flushed before sending; successful
records are reused; quota pauses and auth stops persist. Failed/unknown attempts
remain visible. See [complete bounds, commands and limitations](GEMINI_TRIAL.md).

Verification: 64 new offline tests and all 399 pipeline tests pass, including a real generated child
killed at the deadline, exclusive OS locking, fake HTTP/structured outputs, disk
failure before submission, crash/restart refusal, retry/backoff, quota recovery,
stale access, changed pixels, request-code fingerprints and default offline CLI. The first restricted run hit
the known pytest temporary-folder permission failure; unchanged tests passed with
normal local file access. Fresh review corrected retry guidance on terminal HTTP
errors and unknown block-reason classification before the passing focused suite.
Final review also bound request-construction/transport source fingerprints to run
identity, followed by the final full 399-test pass (31.69 s). Timing is explicitly
deadline-capped, not represented as complete end-to-end pipeline latency.
Both candidate offline commands passed using the actual normal-input package;
no key access, generation or upload occurred.
Superseded offline-only snapshots created before the source-fingerprint addition
remain preserved with no attempts; current plans include implementation hashes.

Checkpoint scope includes the previously pending metadata checker and its tests,
unchanged, because the new transport reuses that fixed-host/key-loader module.
Other earlier mixed documentation/specification/workspace edits remain excluded.
This checkout is not a clean release snapshot; existing spec relocation remains
pending and the website has not been browser-tested in this backend-only task.

Next: investigate the remaining licensed-data/
provider-use condition independently, without asking for Free tier again. Do not
manufacture `terms_and_data_use_verified` or a live access record. Once recorded,
run the fixed trial, then qualify/freeze inputs/models, evaluate complete test
membership and connect the five-picture challenge. All app stories/Gate 1 remain
incomplete. Older next-action sections below are historical where they conflict.

## Saved API answer contract — 24 October 2026

Owner: one agent on `main`; parent EN-03, supports US-02/03/06 and Gate 1.
Earlier uncommitted documentation/specification changes are preserved.

| Task | Dependency / allowed files | Completion check | Status |
| --- | --- | --- | --- |
| Define saved API answers and run identity | Canonical JSON Schema approach and existing contract environment; new API schema, pipeline validator/safeguard module, generated fixture/tests, pipeline guide, this section | Three decisions, distinct failures, consistent run/image/hash identities, strict JSON, bounded attempts, sanitized output and missing entitlement/quota refusal tested offline | Done for offline contract scope |
| Recommend free candidates before API setup | User follow-up; official Google model/catalog/pricing/quota/terms pages; API_FEASIBILITY.md, MODEL_SELECTION.md, this section | Concrete trial recommendation, supported free/capability claims, unmeasured quality and actual access/use limits explicit | Done; recommend 3.8 Flash first and 3.5 Flash-Lite comparison |
| Verify project access/use | Nonsecret authenticated evidence and applicable terms/data suitability; API feasibility/selection/progress notes | Actual Free tier/model quotas and recorded use conclusion before requests | Blocked on project evidence and applicable-use conclusion; no requests |

Scope: no network/provider adapter or live request, no new dependencies, no image
viewing, final evaluation, frontend or remote changes. The contract and pure
safeguard checks are a foundation, not proof of a working request runner,
account entitlement, real AI quality or frontend agreement.

Built `schemas/api-evidence.v1.schema.json`, schema-backed `pipeline/api_contracts.py`
and an explicitly synthetic six-image record fixture. Every declared image has an
execution record. The three valid decisions remain distinct from refusals,
invalid responses, timeouts, provider failures and unknown outcomes. Pending and
quota-paused work prevents completion. Run/image/configuration/schema fingerprints,
attempt order, retry bounds/guidance, serial chronology and stop conditions are
checked. The allowlisted result helper hashes raw responses, keeps valid outputs
and redacts supplied secrets/common credential/path markers. Preflight refuses
missing/stale/incorrect access claims and budgets reaching verified quotas.

Verification: **93 focused contract tests passed; all 308 pipeline tests passed**.
The restricted first run encountered the known pytest temporary-folder permission
problem; unchanged tests passed with normal local file access. Fixture CLI passed,
workspace checks passed (setup only), 26 scoped local documentation links/anchors
and code fences passed, and diff whitespace passed. Fresh single-agent review
checked specification sections 7/8, identities, evidence limits, failure routing,
sanitization and candidate-versus-measured claims; it added serial stop/overlap
and unsanitized-observation rejection before the final checks. No frontend/browser
check was needed because the website remains the starter page. Zero real images
were viewed or uploaded; no inference, new dependency, paid/remote change occurred.

The user's follow-up asked for model advice before providing access. Rechecked
official Google sources: recommend `gemini-3.8-flash` as the first trial candidate
and `gemini-3.5-flash-lite` for speed comparison, subject to actual free quotas and
use clearance. Both have published Standard free input/output and image/structured
output support. This is a trial recommendation, not a defect-quality finding or
final selection. [Comparison and sources](API_FEASIBILITY.md#trial-recommendation-after-the-users-follow-up).

Limits: no provider-envelope classification, enforced runtime timeout/throttle,
durable request journal/restart recovery, complete evaluation, bundle or frontend
contract consumer exists yet. JSON validity cannot authenticate user-supplied
access claims, manifest/configuration hashes or outputs. Sanitization is not a
general secret detector or approval to publish. T-API/T-CONTRACT and Gate 1 remain
incomplete. Exact commands, fields and limitations: [pipeline guide](../pipeline/README.md#check-saved-ai-answers-using-made-up-examples).

Handoff: focused checkpoint includes only the API schema/module/fixture/tests,
pipeline-guide addition, recommendation edits and this new progress section.
Earlier mixed documentation/spec/workspace edits remain preserved and excluded.

Next: verify nonsecret project/model tier/quotas and applicable terms/data use;
configure credentials privately in an approved offline environment, never in chat.
Then build the durable serial adapter and fix a bounded preparation-only trial
plan (IDs, references, prompt, preprocessing, quality checks, request/token/output/
time limits and stop rules) before any call. Final-test inference and website
connection follow qualifying authentic samples and the remaining freeze decisions.
The earlier next-step notes below are historical where they conflict with this section.

## Free API discovery and continuation — 24 October 2026

One agent on `main`, as requested. Read AGENTS.md, README and the docs records;
checked working changes against starting checkpoint `71d0fdf` (24 October,
00:51 Europe/Warsaw). Earlier documentation/spec relocation edits are preserved.
The user reconfirmed free API tiers only; this is the spending rule, not actual
project entitlement or quota evidence.

Since that checkpoint, the working copy contains the specification move to
`docs/` and version 2.1 changes, the new user-story backlog, updated learner/task
guidance, accumulated data/progress notes and the workspace check's new paths.
These are largely earlier unsaved documentation changes. The existing modified
script checks workspace files; it does not add an inspection feature.
No application/pipeline model code, dependency or frontend changed in this task.

Parent EN-03; supports US-02/03/06, Gate 1 and API-FREE-001/002.

| Task | Dependencies / allowed files | Acceptance check | Status |
| --- | --- | --- | --- |
| Check published free API candidates | Official sources; API_FEASIBILITY.md, MODEL_SELECTION.md and this new progress section | Dated candidate image/structured-output/pricing/terms/quota evidence; no model call or secret access | Done; two published candidates, neither selected |
| Verify actual project and applicable use | Approved nonsecret account evidence and terms/data suitability; same documentation files | Free execution and exact model quota evidenced; unresolved use restrictions recorded | Blocked on authenticated project tier/limits and applicable terms/data suitability |
| Define response/run contracts with synthetic checks | Existing canonical-schema approach; scope schemas/pipeline/tests in the next task | Valid decisions and distinct failures, quota/entitlement refusal and sanitized records tested without network | Ready independent implementation task |
| Plan and measure a short real trial | Verified access/use and input/response safeguards | Exact IDs/configuration and request/token/time limits fixed before execution; authentic outputs saved | Pending prerequisites |

[API_FEASIBILITY.md](API_FEASIBILITY.md) records official model capabilities,
published Standard free-tier pricing, project-specific quota rules, regional terms
and exact missing evidence. The active-quota page redirected to sign-in; no
authenticated provider interface was available through the tools used. No API key
or credential file was accessed. Public pricing is not account-specific clearance.
The website still shows the starter page; no authentic API output exists yet.

Verification: workspace check passed (workspace readiness only), 37 local
documentation links/anchors and code fences passed, and working diff whitespace
passed. Fresh review by the same agent checked primary-source support, candidate
versus measured claims, account/terms blockers and preservation of earlier edits.
No app/model tests or browser checks were rerun for this documentation-only task.
The focused checkpoint covers the new feasibility note, selection-plan update and
only this new progress section; earlier mixed-file changes remain unsaved.
Gate 1 and all application stories remain incomplete. No real images were visually opened,
uploaded or scored. No billing, paid calls, publication or remote changes occurred.

Next: implement the small response/run contract and offline safeguard checks while
project evidence is pending; verify access/use before a bounded authentic trial.
Later steps remain complete evaluation, the connected fastener journey, the
surface track, and release checks. Earlier next-step notes are historical where
they conflict with this section or the API-first direction below.

## Current direction: fast, efficient models — 24 October 2026

The user changed the plan because local experiments take too long. Prefer API
models and include only candidates that pass bounded time/resource and evidence
checks. Further PaDiM/PatchCore work is deferred. Two local specialists are no
longer mandatory. No exact API model or speed winner has been selected.

Owner: one agent on `main`, as requested; no workers or worktrees. Parent EN-03,
supporting US-02/03/06 and Gate 1. Earlier working-tree edits are preserved.
The [specification](AI_Inspection_Pilot_Lab_SPEC.md) is revised to version 2.1;
[model selection](MODEL_SELECTION.md) records the current plan and limitations.

| Task | Dependencies / allowed files | Acceptance check | Status |
| --- | --- | --- | --- |
| Update model direction | User's explicit instruction; specification, backlog, learner/workflow/pipeline guides, model/preparation records and this section | Remove mandatory two-specialist fitting; retain zero-spend, authentic evidence and complete evaluation; API speed/access stay unverified; historical results retained | Done; documentation and saved-record checks below |
| Verify free API feasibility | Current official sources and actual approved project entitlement; provider/model-selection docs only initially | Dated model/vision/terms/quota evidence or precise access blocker; no paid, unverified or visitor-triggered calls | Next ready task; no provider call started |
| Plan a small API trial | Verified free access and label-free inputs; detailed allowed files set when ready | Exact IDs, time/request budget, stopping conditions and validation fixed before requests | Pending access evidence |

The website still shows the starter page. API outputs will use real categorical
decisions/observations, with no invented heatmap or adjustable API sensitivity.
Comparison requires two qualifying runs; otherwise explicitly show its
unavailability. Exact models/count and acceptable time budgets are feasibility
outputs. Gemini remains the first route; OpenAI stays disabled without verified
zero-cost entitlement. Additional providers, paid calls, billing, publishing and
remote changes are not authorized by this direction change.

Completed local attempt, retained as history: the separate 384px candidate changes
only picture size. Two known source/resized pairs were viewed (four displayed
examples); the spot stays clear and scratch detail remains softened. PaDiM used
all 176 fitting images and one normal probe, finishing in 90.385 s supervised wall
time at 2.924 GiB peak committed memory, about 78 MiB below the cap. PatchCore
was automatically stopped at 600.013 s while fitting; no completed fit or probe
output exists for that attempt. Its peak committed memory was 2.456 GiB; this is
a timeout, not proof of memory exhaustion. No retry or further local experiment
was started. See [preserved findings](LARGER_RESOLUTION.md).

No final-test inference, calibration threshold, split change or final resolution
approval occurred. Original 256px evidence and provisional 176/44/115 membership
remain preserved. Preparation/source/licence risks remain open. The planned
broader independent source/map audit and test rerun were not executed after the
user redirected work to docs. No pipeline code, dependency or frontend changed.

Verification: checked the final saved profiles, worker snapshots, pinned candidate
and output fingerprints; checked documentation links, requirement references,
code fences, current-direction consistency and whitespace. These checks do not
establish API access/speed, model quality or a passing release gate. Earlier test
results remain historical. All stories and Gate 1 remain incomplete.

Fresh single-agent review checked the revised requirements, API-only capability
claims, unchanged spending/privacy/evaluation boundaries, timeout reporting and
historical-next-step labels. A focused checkpoint saves the new selection plan,
local findings/configuration, clean guide edits and only the new scoped notes
from mixed files. The earlier specification relocation, story file and other
mixed documentation changes remain in the working copy; this is not a clean
release snapshot.

Next: verify current Gemini free access and model suitability, then record a short
trial plan before any API request. Do not resume local resolution/fitting work or
run a full benchmark as the next step. Earlier next-action sections below are
historical and superseded where they conflict with this decision.

## Full-fitting resource check — 24 October 2026

Owner: one agent on `main`, as requested; no delegation or worktrees. Parent
EN-03, supporting US-06 and Gate 1 resource feasibility. Earlier working edits
are preserved. This is a development resource probe, never final evaluation.

| Task | Dependencies / allowed files | Acceptance check | Status |
| --- | --- | --- | --- |
| Bound full-normal-fitting runs | Existing locked CPU environment, pinned checkpoint and provisional answer-free inputs; `pipeline/profile_specialist.py`, `pipeline/smoke_specialist.py`, focused tests and model/pipeline/progress/learner docs | OS memory cap and timeout tested with generated processes; all 176 fitting IDs used; only one normal calibration probe; limits, time, memory, hashes and failures retained; no evaluation input or changed membership | Verified resource probes; final resolution remains open |

Plan: run models sequentially at the unchanged 256px development candidate,
two CPU threads, at most 3 GiB committed process memory and 600 seconds each.
Require free physical RAM of the cap plus 1 GiB before launch. Refuse execution
if the Windows limit cannot be attached to the actual interpreter. Started,
failed and timed-out evidence stays distinct from success; choose new output
directories. No dependencies, provider calls, downloads, visual image review,
threshold selection, benchmark freeze or website changes are needed.

Initial safeguard checks: 22 focused tests passed, including real Windows memory
allocation denial, timeout cleanup of the actual interpreter, missing-limit
refusal, all-fitting membership and incomplete-result handling. The restricted
run hit the known project temporary-folder permission issue; unchanged tests
passed with normal local permissions. Measured 6.21 GiB available physical RAM
before the first model run.

Both real probes succeeded sequentially at 256px. PaDiM fitted all 176 normal
pictures in 43.127 s (1.463 GiB peak physical working set; 1.826 GiB committed).
PatchCore fitted them in 187.379 s (1.303 GiB working set; 1.585 GiB committed;
1802×384 coreset bank). Each scored only normal calibration `img-000118` and
saved its own finite float32 1×1×256×256 map. No final-test image was scored,
threshold set, split changed or resolution approved. Other routine checks
overlapped portions of these feasibility samples; no controlled speed comparison
or model-quality claim is supported. Zero real images/maps were visually opened.

Final verification: **215 pipeline tests passed**, including 21 new resource
cases and real Windows checks for memory denial, timeout, abrupt-supervisor-exit
cleanup and missing-job refusal. Workspace check passed. Independently rechecked
all fitting/calibration assets, exact membership/settings, checkpoint/features,
map hashes/shape/finite values/mapping, report fingerprints and bounds, without
repeating inference. Fresh review by the same agent checked requirements,
actual-interpreter limits, leakage boundaries, preservation and evidence claims.
No frontend changed; website remains the starter page and browser checks were
not repeated. Commands, exact measurements, hashes and limits:
[MODEL_RESOURCES.md](MODEL_RESOURCES.md).

Handoff: focused checkpoint contains
the runner, scoped smoke-report changes, new tests, model/pipeline guides and
only this new progress section. Earlier mixed documentation/spec/workspace edits
remain preserved and excluded. Generated artifacts/data stay ignored; no provider
request, paid call, remote change or publication occurred.

Next ready work: assess a larger picture-size candidate with bounded resources
to address the recorded fine-scratch detail loss before selecting final
resolution. Explicitly settle related-object/split risk before freezing;
do not repeat the completed 256px full-fitting check without new cause. Gate 1
and all user stories remain incomplete. Earlier continuation sections below
retain their historical next-step statements.

## Current milestone: learning workspace

- [x] Write the application development specification.
- [x] Initialize local Git on `main`.
- [x] Add agent teaching rules, beginner entry guide, and worktree explanation.
- [x] Add a repeatable environment check and VS Code tasks.
- [x] Verify the workspace check, VS Code JSON, and documentation links/code fences.

Verification: `python scripts/check_environment.py` passed. Both VS Code JSON files parse, local documentation links resolve, and code fences are balanced. App/model execution and interactive Codex sign-in remain unverified. The setup is ready to save as the first local Git checkpoint; Git history is authoritative for whether that commit exists.

## Observed tools

Git 2.51.2; Node 20.17.0; npm 10.8.3; Python 3.13.2; VS Code 1.142.0; Codex CLI 0.161.0. The VS Code extension `openai.chatgpt` is installed. These are setup-time observations, not pinned application requirements.

The restricted setup environment reported access warnings from Codex's temporary-directory handling and VS Code's log directory while printing versions. Installation was detected; interactive authentication, extension operation, and browser UI have not been verified by this setup.

## Next small task: foundation feasibility

**Goal:** prove the selected tools/data can support one authentic inspection flow before building many screens.

**Agent does:** verify current frontend runtime requirements and Python/ML compatibility, propose/install the smallest project-scoped dependencies, establish data contracts, and prepare a small real-data/model experiment in the order defined by specification Gate 1. Record exact versions and measurements. Do not assume the observed Node/Python versions are suitable for all new packages.

**Your role:** open the folder and Codex, optionally run the environment check, and ask the agent to continue. Configure required provider access yourself through an approved mechanism when genuinely needed; never paste keys into chat.

**Done when:** a documented reproducible setup and validated authentic sample evidence satisfy Gate 1. A blank webpage or test fixture does not prove model feasibility.

## Later milestones

- [ ] Gate 1: feasibility, compatible pinned runtimes/dependencies, schemas, real sample evidence.
- [ ] Gate 2: one connected fastener inspection-to-export journey.
- [ ] Gate 3: complete evaluated comparison and surface track.
- [ ] Gate 4: verified release package and deployment instructions.

No workers, paid calls, public repository, remote deployment, app dependencies, or model runs have been started by the workspace setup. Parallel tasks begin after stable contracts and a shared committed foundation exist.

## Handoff convention

After each completed task, record its outcome, relevant checks/results, known limitations, and next action here. Keep this file short; Git records the detailed file history. A blocked check stays visible rather than being marked complete.

## EN-02-T05b — related-picture and outline review (23 October 2026)

I built a local picture-review tool and inspected 69 similar-picture candidates
and all 93 defect outlines. No gross wrong-image, rotation or shifted-outline
problem was seen. Seven full-size details were checked; scratch/008 has visible
abrasion beyond parts of its annotation. The website still shows the starter page;
no AI has been trained. Existing source pictures and the 176/44/115 draft remain
unchanged. No repeated download is needed.

Owner: one agent on `main`; no workers. Parent EN-02, supporting future US-06.
Requirements: `DATA-SPLIT-003`, `DATA-TRANSFORM-001`, partial `T-DATA`.
Dependencies: existing draft and unchanged local dataset.
Allowed/changed files: `pipeline/review_preparation.py`, its tests,
`pipeline/README.md`, `docs/DATA_REVIEW.md`, `docs/DATA_PREPARATION.md`, this file;
ignored local outputs. No dependencies, source data or schemas were changed.

| Small task | Completion check | Result |
| --- | --- | --- |
| Recheck inputs and generate related-picture candidates | Current files match saved plan; deterministic documented shortlist and local sheets | Verified: 430 files, 55,945 pairs, 69 candidates |
| Inspect real image/outline pairs | All 93 pairs covered; original beside overlay; concerns recorded by ID | Verified scoped pass: 24 mask sheets and 7 native details |
| Verify and record the review | Relevant tests; fresh single-agent diff/evidence review; focused checkpoint; limits explicit | 149 tests and workspace check passed; review record complete |

The shortlist includes all 48 pairs with thumbnail mean absolute difference <= 6
and the closest 12 across each split boundary (69 unique candidates). All 18 pair
sheets were viewed. Similar poses do not establish physical-part/session identity;
12 fitting/calibration candidates remain unresolved. No related groups were invented
and no test member was removed. The draft must not be frozen as a completed
related-image audit. Next: stronger native-detail/registration review of those 12,
then honest unpacked-acquisition representation and label-free model inputs.
Model-resolution RGB visibility still needs a measured feasibility check.

Evidence: [review findings](DATA_REVIEW.md), [preparation state](DATA_PREPARATION.md).
Ignored final output: `data/metal_nut.review.v3/`; generated report and separate
per-pair/per-mask visual decisions have recorded hashes. Its 42 sheets are
byte-identical to the actually viewed v2 set. Earlier failed v1 output is incomplete
and is not evidence. Input membership and saved plan fingerprints are unchanged.
Original archive URL/time/hash remain unknown; v1 release provenance was not weakened.
Gate 1 and all stories remain incomplete.

Checks: 149 pipeline cases passed (137 existing plus 12 review cases). Tests verify
coordinate rendering, invalid masks, stable shortlist/output bytes, source integrity,
complete mask coverage, stale-plan/image/mask rejection, containment/output preservation
and pending-review claims. Real visual observations are separate from those generated
fixtures. The restricted run first failed on known Windows test-folder permissions;
normal local access resolved that. The first tool run/tests found normal images have
`mask: null`; corrected the new tool to skip them. No test/requirement was weakened.
Workspace and edited-document link/fence/whitespace checks passed. Web checks were
not repeated because frontend/tooling files are unchanged; no browser journey was
claimed. Fresh single-agent review checked scope, source preservation, evidence
limits and the remaining preparation risks.

Handoff: focused checkpoint on `main` contains the review code/tests, pipeline/data
guides and this new progress section. Earlier user/agent edits, specification move,
README/workflow/workspace-check changes and earlier progress text remain preserved
in the working tree; only this new progress section is staged from that mixed file.
No workers, provider calls, publication, paid service or remote changes occurred.

## Image-viewing preference — 23 October 2026

The user requested a firm limit after excessive image viewing. The standing rule
in AGENTS.md now requires automated checks first, normally 1–3 visual examples and
a maximum of 5 per task, including examples within contact sheets. Larger visual
reviews require an explicit user request. General picture-checking instructions
do not authorize exhaustive viewing. Record the actual sample and uncertainty.
This documentation change does not change the website, data or application code.
Checked the exact added text and whitespace; application tests are unnecessary.
