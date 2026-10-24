# Fastener experience — local verification

Verified 24 October 2026 (Europe/Warsaw). The complete **local fastener** journey
works with genuine saved Gemini answers: start, inspect five pictures, reveal,
explore full-set evidence, change assumptions, decide, download a Markdown brief,
refresh and reset. No publication or remote deployment occurred.

The default page uses [the genuine local bundle](../web/public/evidence/bundle.json),
not a fixture. Test examples are separate and visibly labelled. Use the
[local guide](FASTENER_LOCAL.md) to run or try it.

## Measured evidence

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
