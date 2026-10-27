# User stories — AI Inspection Pilot Lab

Status: backlog defined; no application story is implemented or verified yet.

The [development specification](AI_Inspection_Pilot_Lab_SPEC.md) is authoritative. These stories explain the user outcomes behind its requirements. They do not replace its detailed formulas, data contracts, security rules, or release gates.

Current direction (24 October 2026): prioritize fast, efficient API models. Local
PaDiM/PatchCore experiments are deferred, not story prerequisites. Exact models
and count depend on verified free access and bounded measurements. Comparison
requires two qualifying runs; unsupported sensitivity/maps remain unavailable.
See [model-selection plan](MODEL_SELECTION.md).

## How to read this backlog

- A **story** describes something useful a person can accomplish.
- **Acceptance criteria** are observable conditions showing that the story works.
- A **technical task** is a small piece of implementation needed for a story.
- An **enabler** is necessary engineering work, such as preparing data, that does not by itself complete a user journey.

Stories can be delivered in smaller increments. Each increment must name the criteria it covers; partial work does not mark the whole story done. `Backlog` means not started, not technically ready to start. The coordinator checks prerequisites before assigning tasks.

Use [PROGRESS.md](PROGRESS.md) for current assignments and evidence. Keep these IDs stable. See [WORKFLOW.md](WORKFLOW.md#turning-a-story-into-tasks) for a worked task breakdown.

## Story index

| Story | Outcome | Status | Prerequisites |
| --- | --- | --- | --- |
| US-01 | Start and complete an inspection challenge | Backlog | EN-01, EN-02, authentic evidence from EN-03 for the delivered increment |
| US-02 | Understand my answer and the AI assessment | Backlog | US-01 answer flow, matching evidence from EN-03 |
| US-03 | Compare models and sensitivity | Backlog | Shared evaluation bundle from EN-03; reveal components may be reused |
| US-04 | Explore workload and assumed cost | Backlog | US-03 policy/routing outputs; calculation logic can start earlier |
| US-05 | Decide and export a pilot brief | Backlog | Evidence, selected policy, and scenario state from US-03/US-04 |
| US-06 | Inspect the evidence behind the comparison | Backlog | Provenance and reports from EN-02/EN-03 |
| US-07 | Explore a second component type | Backlog | Working first-track flow and second-track evidence |
| US-08 | Keep or reset my progress | Backlog | Shared state contract from EN-02 and a basic US-01 answer flow |
| US-09 | Use the app across devices and recover from errors | Backlog | Applies throughout; final checks need integrated journeys |

These are dependency relationships, not a requirement to finish one entire story before touching another. Once shared contracts exist, independent parts can run in parallel in separate worktrees.

## US-01 — Start and complete an inspection challenge

**As a first-time visitor, I want to inspect five components so that I can experience the inspection task before seeing AI judgments.**

Requirements: `FR-START-001`, `FR-INSPECT-001`, `FR-INSPECT-002`, `FR-INSPECT-003`.

Acceptance criteria:

- I can start the fastener challenge or go directly to the lab without an account, upload, API key, or configuration.
- The opening explains the task and identifies it as a public-data prototype.
- The challenge shows five versioned examples, an understandable progress indicator, and usable image zoom.
- I can choose `Looks acceptable` or `Needs further inspection`; optional region marking does not prevent completion.
- Model/reference answers remain hidden until I submit my answer for that image.
- I can navigate backward without losing answers.
- The challenge uses the declared two-normal/three-anomalous curated selection and discloses that it is not representative factory prevalence.

Verification: `T-JOURNEY`; record the browser journey and relevant image/challenge manifest checks.

## US-02 — Understand my answer and the AI assessment

**As a visitor, I want to compare my decision with model evidence and the dataset reference so that I understand what was detected or missed.**

Requirements: `FR-INSPECT-004`, `FR-REVEAL-001`, `FR-REVEAL-002`, `FR-REVEAL-003`, `FR-SUMMARY-001`.

Acceptance criteria:

- After answering, I can reveal evidence for that same image, and my original answer stays fixed until reset.
- My answer, each model's assessment, and the dataset reference are distinctly labelled.
- I can inspect one model and compare two when two qualifying runs exist, while keeping the original readable. With fewer than two, comparison is explicitly unavailable.
- Any included specialist shows its own authentic maps/scores; APIs show actual structured decisions/observations. Local specialists are optional.
- Missing capabilities or failed assessments are identified honestly; an API is not given an invented heatmap.
- The explanation makes clear that an anomaly score is not automatically a defect probability, severity, or root cause.
- My challenge summary shows raw counts without claiming five examples establish human/AI superiority.

Verification: `T-JOURNEY`, `T-EVIDENCE`.

## US-03 — Compare models and sensitivity

**As a quality leader, I want to compare missed defects, unnecessary flags, and review workload so that I can assess model and operating-policy trade-offs.**

Requirements: `FR-COMPARE-001`, `FR-COMPARE-002`, `FR-POLICY-001`, `FR-POLICY-002`; specification section 9.

Acceptance criteria:

- When at least two models qualify, they are compared within one category on the complete declared public evaluation membership. With fewer than two, single-model evidence remains available and comparison is explicitly unavailable.
- Misses, false alarms, review counts, class denominators, coverage, and failures are visible.
- Successful-output metrics and full-set routing metrics remain distinct; failures routed to review are counted and labelled.
- Changing models or supported policies preserves the selected track/image and challenge progress.
- If a specialist is included, its sensitivity maps a calibration target to that run's threshold and shows achieved evaluation rates separately.
- The published default remains distinguishable from visitor exploration.
- APIs use their fixed decision policy; unsupported adjustable sensitivity is explicitly unavailable and changing UI controls makes no provider request.
- OpenAI is shown only with real, verified results when the specification's zero-cost conditions are met; its absence does not block the required baseline.

Verification: `T-EVIDENCE`, `T-POLICY`, `T-FREEZE`, `T-CONTRACT`.

## US-04 — Explore workload and assumed cost

**As a quality leader, I want to change volume, defect prevalence, review capacity, and cost assumptions so that I can understand the possible operational consequences.**

Requirements: `FR-SCENARIO-001`, `FR-SCENARIO-002`; specification section 9.3.

Acceptance criteria:

- All specified scenario inputs are editable and labelled with units and illustrative defaults.
- The app calculates expected misses, reviews, review minutes/cost, capacity excess, and illustrative total cost using the specification's formulas.
- Review workload counts all routed flags, including true positives and declared technical-failure routing.
- Invalid inputs receive clear messages and suspend dependent projections/export; valid zero/boundary values work.
- Measured rates remain separate from assumed site conditions, and rounding affects display only.
- Capacity excess is explained as a warning; results are not presented as measured savings or production validation.

Verification: `T-SCENARIO`, `T-POLICY`.

## US-05 — Decide and export a pilot brief

**As a visitor, I want to record my conclusion and download the evidence and assumptions so that I can discuss a possible pilot with others.**

Requirements: `FR-DECIDE-001`, `FR-EXPORT-001`, `FR-EXPORT-002`, `SEC-RENDER-001`, `SEC-PRIVACY-001`.

Acceptance criteria:

- I can choose one of the three specified pilot decisions and optionally add rationale.
- The downloaded Markdown includes the selected track/run/model/policy, evidence and coverage, assumptions, projections, rationale, limitations, attribution, and pilot prerequisites.
- Its content matches the current validated state and is deterministic for identical inputs.
- Export does not call a provider or transmit my state.
- Untrusted text is handled safely; unsupported or invalid dependent evidence does not produce a misleading brief.

Verification: `T-EXPORT`, `T-SECURITY`.

## US-06 — Inspect the evidence behind the comparison

**As an AI engineer, I want to inspect data, configuration, calibration, and evaluation provenance so that I can judge the credibility and limitations of the results.**

Requirements: `DATA-SOURCE-001`, `DATA-SPLIT-001`, `DATA-SPLIT-002`, `DATA-SPLIT-003`, `DATA-TRANSFORM-001`, `DATA-FREEZE-001`, `DATA-TEST-001`, `DATA-LICENCE-001`, `API-AUDIT-001`; specification sections 6–9.

Acceptance criteria:

- Evidence identifies its dataset/category, exact evaluation membership/hash, run/model configuration, preparation split, calibration, and genuine output capabilities.
- Prompt/reference/preprocessing differences and provider version/run date are available where relevant.
- Coverage and failure reporting account for every declared evaluation image; difficult or failed images are not silently removed.
- Published metrics can be regenerated from saved manifests/predictions without repeating inference or provider requests.
- Attribution and transformation notices accompany distributed assets; dataset and source-code licences remain distinct.
- The UI/export state the GIS-proxy limitation, small-sample/uncertainty limitations, and public-model contamination risk.
- Public evidence contains no credentials, secret-bearing logs, or private local paths.

Verification: `T-DATA`, `T-FREEZE`, `T-LICENCE`, `T-API`, `T-CONTRACT`, `T-SECURITY`.

## US-07 — Explore a second component type

**As a visitor, I want to switch from fasteners to metal surfaces so that I can explore another GIS-relevant manufacturing proxy without mixing the evidence.**

Requirements: `FR-TRACK-001`, `FR-COMPARE-002`; specification sections 3 and 8.3.

Acceptance criteria:

- Fasteners are the default, with a clearly discoverable optional metal-surface track.
- The second track provides the same inspection-to-export journey using its own authentic images/results.
- Track switching preserves each track's progress, policy/model selection, and scenario inputs independently.
- Thresholds, scores, metrics, references, and exports never mix categories.
- The UI explains both tracks' relationship to GIS manufacturing as proxies rather than validated factory use cases.

Verification: `T-JOURNEY`, `T-EVIDENCE`, `T-EXPORT`, `T-CONTRACT`.

## US-08 — Keep or reset my progress

**As a visitor, I want my progress to survive a refresh and to be able to reset it so that I can finish later or try again.**

Requirements: specification section 8.3, `SEC-PRIVACY-001`, `NFR-ERROR-001`.

Acceptance criteria:

- Refreshing restores valid answers, reveal progress, selections, and assumptions for the correct evidence bundle and track.
- Reset-current-track and reset-all require confirmation and affect only the application's own stored state.
- Corrupt/unsupported saved state offers an understandable fresh-start/reset path.
- Evidence-dependent selections invalidated by a bundle update receive a visible explanation.
- When local storage is unavailable, the app remains usable in memory and explains that progress will not persist.
- No account is required and visitor state remains local.

Verification: `T-JOURNEY`, `T-CONTRACT`, `T-SECURITY`.

## US-09 — Use the app across devices and recover from errors

**As a visitor using a keyboard, small screen, or unreliable connection, I want usable controls and clear recovery paths so that I can complete the experience.**

Requirements: `NFR-ACCESS-001`, `NFR-LAYOUT-001`, `NFR-PERF-001`, `NFR-PERF-002`, `NFR-ERROR-001`.

Acceptance criteria:

- Core journeys work with keyboard controls, visible focus, text labels, and non-colour status cues.
- Image controls, layouts, and comparisons remain usable at the specification's tested widths.
- Missing images/results and incompatible/corrupt bundles produce clear messages and relevant recovery actions.
- Actions depending on unavailable evidence are disabled rather than showing invented results.
- Assets are loaded progressively; the release is checked against the documented performance targets.
- Automated checks and manual accessibility/visual review are recorded; automation alone is not claimed as complete accessibility verification.

Verification: `T-ACCESS`, `T-PERF`, `T-CONTRACT`.

## Engineering enablers

These are technical work items, not fictional end-user stories. Split them into small tasks when their turn arrives.

| ID | Outcome | Specification coverage | Verification |
| --- | --- | --- | --- |
| EN-01 | Compatible reproducible project tools, dependencies, and test commands | Sections 5 and 11; Gate 1 | Recorded versions/locks, clean setup, relevant build/check commands |
| EN-02 | Validated contracts, official data/manifests, separate preparation/test splits, coordinate alignment | Section 8; all `DATA-*` requirements | T-DATA, T-CONTRACT, T-LICENCE |
| EN-03 | Bounded selection of fast, efficient models (API-first), authentic predictions, supported policies, complete reports and public bundle; local specialists deferred | Section 9; `DATA-FREEZE-001`, `DATA-TEST-001`, all `API-*` requirements, `SEC-SECRET-001` | T-FREEZE, T-POLICY, T-API, T-CONTRACT, T-SECURITY |
| EN-04 | Verified release/deployment package, caching, rollback, target-host checks when authorized | Section 14; `NFR-LOAD-001`, `OPS-CACHE-001` | T-RELEASE, T-PERF, T-SECURITY |

## Definition of done

A story is done only when all its acceptance criteria have relevant verification evidence, the integrated journey works, applicable accessibility/security checks pass, and documentation/progress are current. Mark coverage honestly: UI built with fixtures is development progress, not authentic model evaluation. Required release evidence follows the specification's gates. Optional region marking and optional OpenAI support do not become mandatory simply because tasks exist for them.

Use `Backlog`, `In progress`, `Blocked`, or `Done`. A blocked item records the specific missing prerequisite and what can continue independently. Do not change a story's meaning just to mark it complete.
