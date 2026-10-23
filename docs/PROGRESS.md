# Progress and next action

Updated: 23 October 2026. This file records project state, not promised implementation success.

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
