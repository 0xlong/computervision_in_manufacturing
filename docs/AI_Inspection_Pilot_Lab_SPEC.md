# AI Inspection Pilot Lab — Software Development Specification

> Version: 2.1 · Updated: 24 October 2026 (Europe/Warsaw)
> Status: development baseline; implementation and evaluation are not yet verified.
> Audience: implementing engineers, coding agents, and reviewers.

## 1. Authority and conventions

This document is the source of truth for application development. It incorporates the accepted product decisions and supersedes conflicting proposals in earlier briefs and conversation summaries. Later explicit instructions from the project author take precedence.

**MUST** identifies a release requirement. **SHOULD** identifies an engineering default that may change with documented evidence. **MAY** identifies optional work. Requirement IDs remain stable; retired IDs are not reused. Record changes affecting scope, spending, evidence validity, or publication in the decision register. Resolve ordinary implementation details without reopening settled product decisions.

This is a specification of intended behavior, not evidence of completed training, evaluation, deployment, industrial validation, or factory access. Numerical targets are acceptance targets until measured. Each mandatory requirement is associated with acceptance evidence in section 12.

## 2. Purpose, audiences, and scope

### 2.1 Purpose and positioning

AI Inspection Pilot Lab is a publicly hosted, interactive personal portfolio project demonstrating how to evaluate inspection AI, explain errors, explore operational trade-offs, and propose a bounded pilot with human review.

The manufacturing context is high-voltage gas-insulated switchgear (GIS), motivated by the GE Vernova Site AI Leader opportunity at Oberentfelden. Public fastener and metal-surface images are **proxies for relevant manufacturing tasks**, not actual site images or validated GIS defect criteria. No affiliation, sponsorship, private-data access, production deployment, or enterprise integration is implied.

The central question is: **Could AI assist this inspection task, and what evidence would be needed before a real-site pilot?**

### 2.2 Audiences and outcomes

| Audience | Successful outcome |
| --- | --- |
| Recruiter or first-time visitor | Starts immediately and completes a short inspection challenge. |
| Site or quality leader | Understands missed defects, unnecessary reviews, workload assumptions, and pilot prerequisites. |
| AI engineer | Can inspect provenance, reproduce metrics, and understand preparation and evaluation differences. |
| Nontechnical participant | Can explain why greater sensitivity can increase both detection and review workload. |

The main story should fit an approximately two-minute demonstration. Detailed evidence remains available on demand. This is an interaction-design goal, not a measured completion-time claim.

### 2.3 First-release scope

- A default five-image fastener challenge and an optional five-image metal-surface track.
- Authentic saved results from fast, resource-efficient models selected through feasibility checks; API models are the preferred direction. Two local specialists are no longer required.
- Optional OpenAI results when sufficient zero-cost API entitlement is verified.
- Model/reference reveal, category-specific comparison, supported sensitivity controls, workload/cost scenarios, and deterministic Markdown pilot-brief export.
- Browser-only progress, reset, responsive and accessible presentation, reproducible evidence, and a deployment package for the existing VPS.

### 2.4 Exclusions

Accounts, uploads, cameras, hardware integration, visitor-triggered inference/training, leaderboards, centrally stored visitor feedback, databases, live provider services, ensembles, chat/RAG, generated root-cause reports, and AMP/APM integration are outside this release. APM and AMP 2.0 are not assumed to be the same system. Publication and remote deployment are separate operations.

## 3. Accepted decisions and engineering defaults

| Topic | Baseline |
| --- | --- |
| Runtime | Static website serving authentic saved results; policy/scenario calculations run in the browser. |
| Host target | Existing Infomaniak VPS, 2 CPUs and 4 GB RAM. OS, available disk, existing workloads, and access remain discovery tasks. |
| Fastener track | `fasteners`: MVTec AD `metal_nut`; default entry point. |
| Surface track | `metal_surfaces`: MVTec AD2 `sheet_metal`; publicly annotated test subset only. |
| Dataset purpose | Personal noncommercial showcase; preserve dataset-specific CC BY-NC-SA 4.0 obligations and verify publication suitability. |
| Model selection | API-first; include only models that meet recorded preparation-time, response-time and resource budgets while providing useful authentic inspection evidence. PaDiM/PatchCore experiments are deferred, optional historical work. |
| Providers | Gemini baseline; OpenAI conditional on verified zero-cost entitlement. No other hosted provider. |
| Spending | Zero paid API spend. Preparation may span multiple days within free quotas. |
| Evaluation | Complete selected public test sets, not a small showcase-only benchmark. |
| Frontend | React, TypeScript, Vite; static build. |
| Offline pipeline | Python; PyTorch/anomalib where compatible; Pydantic for artifact validation. |
| Tests | pytest, Vitest, Playwright. |
| Progress/export | Local browser state, no accounts, deterministic Markdown export. |
| Language | English UI and documentation. |

Pin compatible package versions, checkpoints, provider IDs, and preprocessing during feasibility and before final evaluation. Record the exact resolved configurations in lockfiles and run metadata. Provider aliases are not immutable versions. Missing models must not be silently substituted or simulated.

## 4. User journeys and functional requirements

### 4.1 Start and challenge

| ID | Requirement |
| --- | --- |
| FR-START-001 | The landing screen MUST explain the task, show a concise public-data/prototype label, and provide Start and direct-to-lab actions without login, uploads, keys, or configuration. |
| FR-TRACK-001 | Fasteners MUST be the default track. Visitors MUST be able to switch to surfaces; each track retains its own progress, model, policy, and scenario. |
| FR-INSPECT-001 | Each challenge MUST show five versioned examples with progress, image zoom, and `Looks acceptable` / `Needs further inspection` actions. Optional region marking MUST NOT block completion. |
| FR-INSPECT-002 | Model outputs and reference annotations MUST remain hidden until that image has an answer. Recording an answer unlocks reveal; backward navigation MUST preserve decisions. |
| FR-INSPECT-003 | Each challenge MUST use a committed manifest containing two normal and three anomalous evaluated images. Curated selection and its rationale MUST be disclosed. |
| FR-INSPECT-004 | Once revealed, the original answer MUST remain fixed until that track is reset. Public labels are a learning mechanism, not a secure examination system. |

Select teaching examples after evaluation without changing benchmark membership. Include authentic misses or false alarms when available; do not manufacture errors or promise particular mistakes will exist.

### 4.2 Reveal and comparison

| ID | Requirement |
| --- | --- |
| FR-REVEAL-001 | Reveal MUST distinguish visitor judgment, model assessment, and dataset reference using labels as well as visual styling. |
| FR-REVEAL-002 | Visitors MUST be able to view one selected model and compare two on the same image when two qualifying runs exist. Original imagery MUST remain readable. If fewer than two qualify, explain that model comparison is unavailable; never invent a second result. |
| FR-REVEAL-003 | If a specialist is included, its evidence MUST use that run's score/map. API evidence MUST show its real structured decision and concise observations. Unsupported heatmaps or sensitivity MUST be explicitly unavailable. |
| FR-SUMMARY-001 | Challenge results MUST show raw correct/incorrect counts against reference labels without claiming that five examples establish human or model superiority. |
| FR-COMPARE-001 | The lab MUST compare the complete declared evaluation set within one category, showing misses, false alarms, review count, denominators, coverage, and failures. |
| FR-COMPARE-002 | Model/policy changes MUST preserve track and image identity without restarting the challenge. |
| FR-POLICY-001 | If a specialist is included, its sensitivity MUST map a normal-calibration false-alarm target to a separate threshold per run. The selected target and achieved evaluation rates MUST be labelled separately. |
| FR-POLICY-002 | APIs MUST initially use a fixed categorical policy. `uncertain` routes to review. A sensitivity control MUST NOT imply calibrated API confidence or change the prompt. |

Anomaly scores indicate unusual appearance relative to normal preparation examples, not defect probability, severity, or root cause. Heatmap scales are model-specific. Fixed benchmark results and visitor exploration must remain distinguishable.

### 4.3 Scenario, decision, and export

| ID | Requirement |
| --- | --- |
| FR-SCENARIO-001 | Visitors MUST be able to edit daily volume, assumed prevalence, review minutes, available review capacity, missed-defect cost, and review cost/minute. Defaults MUST be labelled illustrative. |
| FR-SCENARIO-002 | The site MUST display expected misses, reviews, review time, capacity excess, and illustrative total cost using section 9. |
| FR-DECIDE-001 | Visitors MUST be able to choose `Pilot with human review`, `Collect more evidence`, or `Revise the approach`, plus optional rationale. No choice is an automatically validated recommendation. |
| FR-EXPORT-001 | Markdown export MUST contain track/dataset/run identities, model/policy, measured evidence and coverage, assumptions, projections, decision/rationale, limitations, attribution, and pilot prerequisites. |
| FR-EXPORT-002 | Identical structured state and evidence MUST produce identical export content. Export MUST require neither an LLM nor transmission of visitor state. |

The pilot prerequisite checklist includes representative site images, a quality owner, approved data access, agreed defect/disposition definitions, acceptance criteria, sufficient review capacity, and human oversight.

## 5. System architecture and module boundaries

```text
Official datasets
  -> acquisition, checksums, and fixed manifests
  -> free-tier API execution (optional specialist fitting/calibration only if selected)
  -> prediction records, evaluation, and provenance
  -> validated versioned public bundle
  -> static React website
  -> browser calculations, local state, and Markdown export
```

Offline ML dependencies and provider credentials do not belong in the visitor-serving process.

| Module | Responsibility and boundary |
| --- | --- |
| Data preparation | Acquires and validates images, splits, transformations, and challenge membership; produces manifests. |
| Optional specialist runner | Deferred unless a fast, efficient local candidate is selected; fits/loads one declared configuration and emits authentic outputs from permitted preparation data. |
| Provider adapter | Builds label-free requests, validates responses, enforces entitlement/quota policy; never consumes test labels/masks. |
| Evaluation | Reads labels separately, calibrates thresholds, computes metrics, coverage, uncertainty, and failure routing. |
| Bundle builder | Packages approved public evidence and attribution; rejects inconsistent artifacts. |
| Frontend loader | Validates index/contracts and lazy-loads selected evidence. |
| Policy/scenario engine | Pure threshold, routing, metric, and workload functions; no network/persistence side effects. |
| Visitor state | Versioned track-specific judgments/settings, without credentials or identity. |
| Brief builder | Deterministic Markdown from validated evidence and state; no provider call. |

Recommended layout: `web/`, `pipeline/`, `schemas/`, `configs/`, and `tests/`. Generated datasets, checkpoints, caches, raw provider responses, and build output stay outside source control by default. Small labelled fixtures support tests; authentic release evidence has separate paths and provenance.

Use JSON Schema Draft 2020-12 as the artifact contract source. Validate contracts in Python and the frontend; contract tests must establish agreement with Pydantic models. Avoid divergent, independently maintained representations of the same contract.

## 6. Data preparation and provenance

| ID | Requirement |
| --- | --- |
| DATA-SOURCE-001 | Acquire data from official sources; record URL, date, licence, archive/content hashes, and exact category membership. |
| DATA-SPLIT-001 | Preserve official test membership. Specialist fitting and API reference selection MUST use only permitted normal fitting data. Calibration MUST be separate from final test data. |
| DATA-SPLIT-002 | For MVTec AD, reserve 20% of official normal training images for calibration using seed 42 and stable sorted-ID shuffling. For AD2, use official normal validation data. Record exact IDs and reject empty fitting/calibration sets. |
| DATA-SPLIT-003 | Keep identifiable duplicate/related images together within preparation splits. Report overlap risk; do not silently delete official test images. Disclose identified test contamination. |
| DATA-TRANSFORM-001 | Record orientation, resizing, padding/cropping, normalization, dimensions, and coordinate mappings. Maps/masks MUST align with displayed images. |
| DATA-FREEZE-001 | Freeze manifest hashes, prompts, references, model configuration, preprocessing, and calibration before final evaluation. Changes create a new run. |
| DATA-TEST-001 | Evaluate every image in each declared public test set. AD2 private test data and withheld labels MUST NOT be dependencies. |
| DATA-LICENCE-001 | Distributed assets MUST retain required attribution, licence notices, modification descriptions, and applicable redistribution terms. Source-code licensing MUST NOT imply relicensing dataset images. |

Use a shared base image representation where practical. Disclose necessary model-specific transformations and differences in normal-reference access. Inspect small-defect visibility during feasibility and freeze resolution before final evaluation; source-image resolution alone does not establish model visibility after downsampling.

For any selected specialist, run configuration must identify checkpoint hash, feature selection, applicable model parameters, input resolution, and image-score reduction rule. API configurations instead identify the provider/model/version, prompt, permitted references and image preprocessing. These are measured feasibility outputs, not assumed performance guarantees. Deferred PaDiM/PatchCore settings are not requirements for an API run.

## 7. API execution and zero-spend controls

Gemini free access is the required API route. OpenAI stays disabled until suitable zero-cost entitlement is verified. A ChatGPT subscription or account usage ceiling is not proof of free API credits. Retain dated entitlement/terms evidence without secrets.

| ID | Requirement |
| --- | --- |
| API-FREE-001 | Paid requests, credit purchases, billing activation, and paid fallback MUST remain disabled. Verify that the selected project/model is eligible for free execution before running it; unverified entitlement blocks that provider. |
| API-FREE-002 | Obtain actual project/model quotas through the approved provider interface. Record limits and expiry where applicable instead of assuming universal free request counts. |
| API-INPUT-001 | Send image pixels, neutral IDs, and permitted normal references only. Exclude label-bearing paths, masks, test labels, visitor answers, and other model predictions. |
| API-OUTPUT-001 | Validate a decision of `looks_acceptable`, `needs_review`, or `uncertain`, plus concise observed evidence. Refusals, malformed output, and transport errors MUST have separate failure statuses. |
| API-RUN-001 | Persist attempts/results before advancing. Resume by run/image/request fingerprint and reuse successful records. |
| API-QUOTA-001 | Start with one concurrent request and throttle below verified limits. Quota exhaustion MUST pause until the permitted retry window, without provider or billing-tier substitution. |
| API-RETRY-001 | Use a 60-second request timeout and at most three attempts/image for transient transport/5xx failures, with backoff and provider retry guidance. Authentication/entitlement errors stop the provider run. Refusal/schema failures remain recorded terminal outcomes. |
| API-AUDIT-001 | Retain sanitized metadata, prompt/reference hashes, model/version, timestamps, usage, attempts, statuses, and responses. Redact credentials and authorization headers. |

A crash after submission but before persistence may leave the outcome unknown. Record it and reconcile or explicitly record any repeat attempt. Do not claim exactly-once execution without provider support.

Preparation may span multiple days. A terminal failure is an attempted image, not a successful inspection. Public benchmark contamination cannot be excluded for general-purpose models and must appear in limitations. The public site makes no provider calls.

## 8. Artifact contracts and visitor state

### 8.1 Shared conventions

Artifacts use UTF-8 JSON, UTC ISO 8601 timestamps, finite numbers, explicit units, validated relative asset paths, SHA-256 hashes, and `null` for undefined metrics. Display a zero-denominator metric as `N/A`, not zero. IDs are unique within their declared scope. Public artifacts must not expose private local paths.

Each public artifact carries integer `schema_version`. Unsupported versions produce an actionable error, never a fabricated fallback prediction.

### 8.2 Minimum contracts

| Contract | Minimum content and invariants |
| --- | --- |
| Track | `track_id`, title, dataset/category, manifest reference/hash, challenge image IDs, available run IDs, attribution reference. |
| Image manifest entry | Image/track ID, split, source hash, original dimensions, display asset, label, optional mask/hash, transformation record. Inference reads label-free inputs separately. |
| Model run | Run/track ID, model/provider identity and reported version, configuration and split hashes, preparation/reference/prompt hashes, package/checkpoint versions, score meaning, capabilities, calibration, timestamps. |
| Prediction | Run/image identity, status, attempts/timings, nullable score/map/API decision/observation, sanitized error details. Status/capabilities determine required outputs. |
| Evaluation report | Run/manifest hashes, expected/attempted/succeeded/failed counts, failure breakdown, default policy, successful-output metrics, full-set routing metrics, uncertainty, timings/resources. |
| Bundle index | Schema/bundle version, creation time, track/run references, asset hashes, licence/source references, evidence status. |
| Visitor state | State/bundle version, active track, per-track answers/reveal state, selected image/model/policy, scenario, pilot decision, rationale. |
| Export input | Validated evidence snapshot and selections sufficient to reproduce the displayed brief. |

Prediction statuses are `success`, `refusal`, `invalid_response`, `timeout`, `provider_error`, or `unknown_outcome`. Pending/quota-paused items are execution state and prevent a completed-run declaration. A valid API `uncertain` result is a successful response, not a transport failure.

### 8.3 Persistence and navigation

- Use the application-specific localStorage key `ai-inspection-pilot-lab:v1`. The release has no visitor tracking or third-party analytics.
- Keep each track's state independent. Never transfer judgments, thresholds, or scores between categories.
- Persist after meaningful changes and validate on restoration. Bundle changes invalidate evidence-dependent selections with a visible explanation.
- Corrupt/unsupported state offers reset and a fresh start. Storage unavailability permits in-memory use with a progress-persistence notice.
- Offer reset-current-track and reset-all actions with confirmation. Delete only application-owned state.
- Use one static application entry route. Optional query parameters may select a valid track but cannot override stored judgments or evidence.

## 9. Evaluation, policies, and scenario calculations

### 9.1 Operating policy

For specialists, `score > threshold` means review. Select the threshold from ascending normal-calibration scores at one-based rank `ceil((1 - alpha) * n)`, where `alpha` is the target normal false-alarm rate and `n` is calibration size. Preserve score ties. Actual achieved rates need not equal the target.

Initial targets are 1%, 2%, 5%, 10%, and 20%; the immutable benchmark default is 5%. Store each run's thresholds and calibration provenance. This is operating-policy calibration, not probability calibration.

For APIs, `needs_review` and `uncertain` route to review. `looks_acceptable` does not. Technical failures also route to review in operational projections, with their reason visible. API suspicion ratings and adjustable API thresholds are deferred.

### 9.2 Metrics and failure treatment

For successful outputs calculate TP, FN, FP, TN, recall `TP/(TP+FN)`, false-positive rate `FP/(FP+TN)`, precision `TP/(TP+FP)`, and review count `TP+FP`. Show class denominators and coverage. A valid API uncertainty result follows the review policy.

Separately compute full-set **routing metrics**, including technical failures sent to review. These describe the workflow rather than successful model predictions. Show technical-review counts separately so a failing model cannot appear strong merely by reviewing everything. Successful-output performance must always accompany coverage; do not silently compare only the intersection of successful images.

Use full-set routing recall/false-positive rate for workload scenarios, visibly including the failure-to-review assumption. Suppress unsupported comparisons when necessary denominators are absent. Do not invent a winner ranking.

Report AUROC/AUPRC only for genuine numerical scores; do not fabricate a curve from categorical API decisions. Pixel metrics are optional and restricted to aligned, authentic maps. Use 95% Wilson intervals for recall and false-positive rates, with raw counts and a note that they do not capture dataset shift or benchmark contamination.

Distinguish preparation time, specialist inference, provider round-trip latency, and saved-result rendering. Record hardware, peak memory, failures, and preparation duration where measured. Cached rendering time is not inference speed.

### 9.3 Scenario formulas and input rules

Let `N` be components/day, `p` assumed defective proportion, `r` routing recall, `f` routing false-positive rate, `m` minutes/review, `a` available review minutes/day, `c` currency units/review minute, and `d` currency units/missed defect.

```text
caught = N * p * r
missed = N * p * (1 - r)
unnecessary_reviews = N * (1 - p) * f
reviews = caught + unnecessary_reviews
review_minutes = reviews * m
review_cost = review_minutes * c
illustrative_total_cost = review_cost + missed * d
capacity_excess_minutes = max(0, review_minutes - a)
```

Illustrative initial inputs: `N=1000`, `p=0.01`, `m=2`, `a=240`, `c=1`, `d=100`, using editable EUR costs. These are not site measurements. Both tracks start with these assumptions but preserve edits independently.

Require finite nonnegative inputs, integer `N`, and `0 <= p <= 1`. Fractional minutes/costs and zero capacity/cost are valid. Invalid inputs show inline errors and suspend dependent projections/export. Preserve precision internally and round only for display.

Assumptions: every flag is reviewed, human review resolves flags correctly, and each missed defect incurs the entered average cost. Capacity excess is a warning, not a queue simulation or estimate of additional escapes. Do not claim measured savings, optimal staffing, or production approval from this scenario.

## 10. Reliability, accessibility, performance, and security

| ID | Requirement or acceptance target |
| --- | --- |
| NFR-ACCESS-001 | Target WCAG 2.2 AA for implemented journeys: keyboard actions, focus, labels, non-colour status cues, contrast, image controls, and accessible status/errors. Manual checks MUST supplement automation. |
| NFR-LAYOUT-001 | Verify 360, 768, and 1440 px widths. Core controls/evidence MUST remain usable without page-level horizontal scrolling; comparisons may stack. |
| NFR-PERF-001 | Lazy-load track evidence, full images, and maps. Initial compressed JS/CSS SHOULD remain below 500 KiB, excluding selected images. Startup MUST NOT fetch the complete image corpus. |
| NFR-PERF-002 | With assets loaded on a recorded laptop/browser, policy/scenario updates SHOULD finish within 100 ms p95 across 100 changes. Target first usable challenge within 3 seconds under a documented 10 Mbps/100 ms RTT profile. |
| NFR-LOAD-001 | On the authorized target host, exercise 10 concurrent visitors for 5 minutes and record latency/errors/memory and existing-service impact. Targets: under 1% failed requests, p95 static responses under 1 second. Resolve material regressions before release. |
| NFR-ERROR-001 | Missing/corrupt bundles, missing assets, and unsupported schema versions MUST have explicit messages and recovery actions where applicable. Disable actions dependent on unavailable evidence. |
| SEC-SECRET-001 | Credentials MUST remain in the approved offline execution environment. Public artifacts/browser code MUST contain no keys, authorization headers, or secret-bearing logs. |
| SEC-RENDER-001 | Treat provider text/rationale as untrusted text. Bound rationale to 2,000 characters; validate asset paths; escape/quote exported content to prevent executable HTML injection. |
| SEC-PRIVACY-001 | Visitor decisions and rationale MUST remain local and MUST NOT be transmitted to a server or model provider. |
| OPS-CACHE-001 | Versioned immutable assets MUST use long-lived caching; entry HTML/index MUST revalidate. A release MUST NOT mix old metadata with new assets. |

Workspace restrictions apply: exclude `done/`, credential/token files, `.env` files, and similar secrets from searches/access. Document required variable names without values and do not discover unrelated credentials. Use VS Code's integrated browser when available; otherwise state the limitation and provide the URL with `Browser: Open Integrated Browser`, rather than claiming inspection.

## 11. Development workflow and maintenance

- Separate web, pipeline, contracts, and pure calculations. Build complete vertical slices before adding abstractions.
- Establish supported runtimes, compatible dependency locks, and checkpoint licences during feasibility using current official documentation.
- Document reproducible acquisition, manifest, fitting, API execution/resume, evaluation, bundle, local development, test, and build commands. Implementation README/CLI help owns exact command syntax.
- Changes include relevant behavior/evidence checks and review of requirement compliance, leakage, capability claims, and secret exposure.
- Routine CI runs schema checks, pure-function tests, type checks/build, and a fixture-based browser journey. It does not download full datasets, train models, or call providers.
- Full-data/provider checks are explicit and resumable. Saved run IDs/configuration allow metric regeneration without repeated inference.
- Record material configuration/schema changes. Incompatible contracts increment schema versions. Browser-state changes use tested migration or a visible reset.
- Public source preparation includes setup, locks, test instructions, attribution, provenance, limitations, and release/deployment procedures. Publication remains separately authorized.

## 12. Verification and requirements traceability

Check IDs identify acceptance evidence, not a requirement to create one test function per row. Combine cases where that improves clarity.

| Check | Requirements covered | Required evidence |
| --- | --- | --- |
| T-JOURNEY | FR-START-001, FR-TRACK-001, FR-INSPECT-001–004, FR-SUMMARY-001 | Start without setup; five answers; gated reveal; fixed revealed answers; navigation, both tracks, progress, and reset. |
| T-EVIDENCE | FR-REVEAL-001–003, FR-COMPARE-001–002 | Same-image comparison; correct model/reference overlays; unavailable capabilities; full membership, coverage, and failures. |
| T-POLICY | FR-POLICY-001–002 | Known score sets, rank/tie handling, immutable default versus exploration, categorical uncertainty, no prompt changes. |
| T-SCENARIO | FR-SCENARIO-001–002 | Known confusion matrices; prevalence 0/1; zero denominators; invalid/nonfinite inputs; capacity; true-positive review cost; failure routing. |
| T-EXPORT | FR-DECIDE-001, FR-EXPORT-001–002 | Matching evidence/assumptions, deterministic content, escaped text, and no external request. |
| T-DATA | DATA-SOURCE-001, DATA-SPLIT-001–003, DATA-TRANSFORM-001 | Hashes/membership, fitting/calibration separation, duplicate audit, aligned masks/maps, official split preservation. |
| T-FREEZE | DATA-FREEZE-001, DATA-TEST-001 | Frozen configurations, every expected image accounted for, no private AD2 dependency, metrics regenerated from saved records. |
| T-LICENCE | DATA-LICENCE-001 | Assets mapped to source/licence, attribution, modification notices, and recorded publication suitability. |
| T-API | API-FREE-001–002, API-INPUT-001, API-OUTPUT-001, API-RUN-001, API-QUOTA-001, API-RETRY-001, API-AUDIT-001 | Mocked entitlement/quota/failure cases, label-free inputs, restart recovery, attempts, timeout/retry limits, sanitized logs. |
| T-CONTRACT | Section 8, NFR-ERROR-001 | Reject corrupt/unsupported artifacts, unsafe paths, missing IDs; verify Python/frontend agreement and state restoration/reset. |
| T-ACCESS | NFR-ACCESS-001, NFR-LAYOUT-001 | Automated scan plus manual keyboard, focus, contrast, image controls, responsive layouts, status/errors. |
| T-PERF | NFR-PERF-001–002, NFR-LOAD-001 | Build transfer size, lazy loading, documented browser timings, actual-host load evidence. |
| T-SECURITY | SEC-SECRET-001, SEC-RENDER-001, SEC-PRIVACY-001 | Inspect release/logs; untrusted-string cases; verify visitor-state network behavior. |
| T-RELEASE | OPS-CACHE-001, sections 11 and 14 | Clean build, complete bundle validation, activation/rollback procedure, existing-service checks. |

Artifact validation rejects duplicate IDs, missing assets, invalid values, inconsistent hashes, cross-track references, contradictory capabilities, and unaccounted evaluation members. Fixtures remain explicitly labelled test/development inputs. Release evidence identifies authentic runs and cannot substitute fixture predictions.

## 13. Development stages and completion gates

### Gate 1 — Feasibility and contracts

Prioritize free-provider eligibility/terms and short, bounded API feasibility checks. Verify official data/licences, compatible dependencies, model-specific small-defect visibility, validated contracts and exact manifests. Record concrete response-time, total-preparation-time and resource budgets before model trials; select only candidates that meet them and provide useful authentic outputs. Do not assume API access is faster or free without evidence. Local fitting experiments are deferred and are not a prerequisite.

**Complete when:** selected-model sample records pass applicable contract/alignment checks; preparation splits are fixed; free API feasibility or a precise blocker is recorded; measured latency/resource findings and exact configuration candidates exist. Final model IDs and count are settled from this evidence, rather than requiring two local specialists. A provider blocker does not authorize paid execution or another provider. Spending/provider constraints remain fixed.

### Gate 2 — Complete fastener vertical slice

Deliver inspect-to-export with authentic fastener evidence, pure calculations, state persistence, and error states. Partial bundles are visibly development-only.

**Complete when:** T-JOURNEY, T-POLICY, T-SCENARIO, T-EXPORT, and applicable contract checks pass, with manual visual review. A fixture-only site does not pass.

### Gate 3 — Complete evidence and both tracks

Freeze the selected efficient model configurations, execute Gemini within verified free quotas, finish the public test membership for every selected run, and deliver both tracks. Include comparison wherever at least two qualifying models have authentic results; otherwise disclose its unavailability. Add OpenAI only with verified zero-cost access and complete recorded evaluation. Local specialists are optional and deferred, not a gate requirement.

**Complete when:** every required run accounts for every declared image as success or terminal failure; no items remain pending; metrics/coverage/failures regenerate; both tracks work; complete provenance exists. OpenAI absence does not block the gate; Gemini absence does. Failures must remain visible and cannot be described as successful inspections.

### Gate 4 — Release package

Complete accessibility, responsive presentation, performance/security checks, documentation, attribution, screenshots, and deployment/rollback instructions.

**Complete when:** applicable section 12 checks pass; claims match artifacts; the clean-session demonstration works; limitations are recorded. Host-specific checks remain explicitly unverified until authorized access exists. A local package may be complete before deployment, but unmeasured host readiness cannot be claimed.

## 14. Deployment and operation

Prepare a static build with an immutable, versioned evidence bundle. Deployment instructions first inventory the OS, web server, domains/TLS, disk, existing services, and available CPU/RAM. Select compatible configuration from observed facts; do not assume sole use of the host.

Stage a separate release directory, verify index/assets/hashes and a browser smoke journey, then activate atomically through the existing serving arrangement. Retain the previous release for rollback. Do not overwrite shared server configuration wholesale.

After activation verify HTTPS, caching, entry page, both tracks, images/maps, state restore/reset, export, and existing-service availability. Run the defined load profile when authorized. Basic server logs provide operational visibility without collecting visitor decisions.

Restore the previous release for an invalid bundle or broken deployment and record the cause. Evidence updates create new run/bundle versions; published history is not overwritten under the same identity. Actual deployment, public repository publication, and remote changes require separate authorization from this document-writing task.

## 15. Decision register and remaining discovery

### 15.1 Settled product decisions

| Decision | Resolution |
| --- | --- |
| Delivery | Saved authentic results; no live inference in this release. |
| Spending | Free-tier calls only; no paid fallback. |
| Providers | Gemini baseline; OpenAI conditional on verified free entitlement; no Claude. |
| Data direction | GIS-relevant fastener and sheet-metal proxies replace PCB1. |
| Licence purpose | Personal noncommercial showcase; retain restrictions and verify distribution suitability. |
| Visitor experience | Default fastener challenge; optional separate surface track. |
| Evaluation | Complete selected public test sets, even across multiple days. |
| Model speed and efficiency — revised 24 October 2026 | Prefer API models and retain only candidates that pass bounded speed/resource and evidence checks. The earlier mandatory two-specialist plan is superseded; local PaDiM/PatchCore work is deferred. Exact API IDs and model count remain feasibility outputs. |

### 15.2 Discovery tasks, not unanswered product questions

| Unknown | Resolution evidence | Gate |
| --- | --- | --- |
| Local compute/disk | Hardware/runtime inventory, sample fitting and inference measurements | 1 |
| Exact category/split counts | Acquired official manifests and checksums | 1 |
| Preprocessing and memory | Small-defect review, repeatable sample runs, peak memory | 1 |
| Dependencies/checkpoints/licences | Pinned environment, hashes, licence inventory | 1 |
| Provider IDs, quotas, eligibility, terms | Dated official sources and approved project entitlement verification | 1 |
| Performance/failures | Frozen complete evaluation artifacts | 3 |
| Assets and browser timing | Production build measurements | 4 |
| VPS environment/coexistence | Authorized host inventory and checks | Deployment |

Do not present missing facts as measurements. If a required condition fails, finish independent work, identify the blocked gate, and provide a concrete adjustment for review.

### 15.3 Background-source availability

The workspace initially contained only this specification. Previously referenced CV, job offer, APM brochure, and historical briefs are background provenance, not available development dependencies. Do not claim local verification of those missing documents. Development must be possible from this document, acquired public data, and official technical sources.

## 16. Authoritative references

Verify time-sensitive provider facts again before execution. Documentation establishes published capability/terms, not account-specific free entitlement.

- [MVTec AD: data, annotations, and licence](https://www.mvtec.com/research-teaching/datasets/mvtec-ad).
- [MVTec AD2: public/private evaluation and licence](https://www.mvtec.com/research-teaching/datasets/mvtec-ad-2).
- [MVTec AD2 paper](https://arxiv.org/abs/2503.21622).
- [PaDiM documentation](https://anomalib.readthedocs.io/en/latest/markdown/guides/reference/models/image/padim.html).
- [PatchCore documentation](https://anomalib.readthedocs.io/en/latest/markdown/guides/reference/models/image/patchcore.html).
- [Original PatchCore implementation](https://github.com/amazon-science/patchcore-inspection).
- [Gemini pricing and free-tier availability](https://ai.google.dev/gemini-api/docs/pricing).
- [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).
- [Gemini API terms](https://ai.google.dev/gemini-api/terms).
- [Gemini supported regions](https://ai.google.dev/gemini-api/docs/available-regions).
- [OpenAI API pricing](https://developers.openai.com/api/docs/pricing).
- [OpenAI API limits and usage tiers](https://developers.openai.com/api/docs/guides/rate-limits).
- [OpenAI API quickstart](https://developers.openai.com/api/docs/quickstart).

These sources support public proxy selection, not actual-GIS validation. Licence suitability, provider terms, and evidence provenance remain explicit release prerequisites.
