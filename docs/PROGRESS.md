# Progress and next action

Updated: 24 October 2026. This file records project state, not promised implementation success.

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
