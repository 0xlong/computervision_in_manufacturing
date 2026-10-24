# Progress and next action

Updated: 24 October 2026. This file records project state, not promised implementation success.

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
