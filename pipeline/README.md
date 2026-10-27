# Offline evidence pipeline — contracts and local inventory

Current direction (24 October 2026): local PaDiM/PatchCore experiments are deferred.
Keep these tools and saved outputs as historical work; the next task is
[API-first efficient-model selection](../docs/MODEL_SELECTION.md).

The pipeline validates image manifests and checks downloaded fastener archives.
A **manifest** is a list of images and their origins, splits, labels and display
assets. Automatic downloading, models, evaluation reports and release bundles
are not implemented yet. The supplied unpacked fastener folder and draft split pass local checks.
Missing archive details remain explicitly unknown; no repeated download is needed.

## Check saved AI answers using made-up examples

The API answer checker now validates saved decisions and request history. This
works offline; a provider adapter, durable request journal and real AI results
are still pending. The website still shows the starter page.

From the project-root VS Code PowerShell terminal, run:

```powershell
.\.venv\Scripts\python.exe -m pipeline.api_contracts tests/fixtures/api-evidence.fixture.json
```

Purpose: check six invented records (three decisions, refusal, malformed answer,
timeout). Expect `PASS API evidence contract (fixture): 6 image records` and a
statement that authenticity, access, image bytes, frontend agreement and quality
remain unverified. No key, image upload or provider call is involved.

The authoritative [API evidence schema](../schemas/api-evidence.v1.schema.json)
defines the response object, development run, attempts, predictions and nonsecret
access-evidence shape. Python's `ApiEvidence` delegates field checking to that
schema, adding identity, chronology, retry and completion checks. See the
[behavior tests](../tests/pipeline/test_api_contracts.py).

- `looks_acceptable`, `needs_review` and `uncertain` are successful categorical
  answers; uncertainty routes to review. No heatmap, probability or adjustable
  sensitivity is claimed.
- Prediction statuses follow specification section 8.2. Quota pauses and pending
  images are separate execution states and prevent completion. Unknown outcomes
  require reconciliation, not automatic retry. Authentication/entitlement stops
  the run; only transient transport/5xx/timeouts and quota recovery permit retry,
  within three total attempts and recorded backoff/retry guidance.
- Every declared image has a record, including pending work. Request fingerprints
  bind run/model, hashes and image bytes. Changed configuration cannot reuse an
  old prediction. Successful saved records are available for a future runner to
  reuse; persistence/resume and crash recovery are not implemented by validation.
- Attempts retain timestamps, measured latency, nullable usage and reported model
  version (unknown stays null), status/reason, raw-response SHA-256 and validated
  response only on success. No raw exceptions, HTTP headers or raw error text are
  retained. `sanitized_result` redacts known supplied secrets and common private
  path/credential markers in observations. Arbitrary secret detection and public
  release review remain separate work; untrusted observation text still needs safe
  rendering. A hash is not a copy of a response or proof of authenticity.
- `check_access` refuses absent/stale/false evidence, other providers/models and
  budgets reaching quota limits. Its returned serial settings leave headroom.
  These are pure offline checks of caller-supplied claims, not account verification
  or a running throttle. A future adapter must enforce time/request/token budgets,
  concurrency, actual usage, zero spend and durable writes before advancing.

The schema is development-only; it is not the final release bundle contract.
An eventual provider integration must classify real provider envelopes/refusals
and supply actual metadata. The frontend does not consume these records yet.
No full T-API/T-CONTRACT or release gate is claimed from these offline checks.

## Check the locally configured Gemini key

The user configured `gemini_api_key` in the root `.env`. Keep the value private;
the offline checker consumes only that assignment (or `GEMINI_API_KEY`) without
printing it or evaluating the file as shell code. It accepts an unquoted value or
one pair of ordinary quotes. It rejects empty/repeated assignments, multiline
values and shell expressions. No dotenv dependency or global setup is required.
Do not rename the key for this project or put it in frontend code.

In the project-root VS Code PowerShell terminal:

```powershell
.\.venv\Scripts\python.exe -m pipeline.check_gemini_metadata
```

Purpose: check that the one configured value can be loaded. Expect
`PASS local Gemini key configuration; value hidden.` This default makes no network
request and does not establish authentication, free access or model quality.

The following **read-only check was run successfully on 24 October 2026**:

```powershell
.\.venv\Scripts\python.exe -m pipeline.check_gemini_metadata --metadata
```

It makes at most two sequential GETs for the declared trial candidates, with a
15-second socket timeout and a 64 KiB response limit. It uses the fixed Google
HTTPS endpoint with the key in a header, no request body, no redirects, inherited
proxy, retry, alternate provider or generation request. Only allowlisted
model/status/capability fields reach output. Authentication/permission/quota or
connection errors stop the probe; raw responses, error messages and headers are
never printed or saved. TLS verification stays enabled. This timeout is not a
strict overall trial deadline; no inference runner is implemented by this tool.

Both `gemini-3.8-flash` and `gemini-3.5-flash-lite` returned HTTP 200 and advertised
`generateContent`. This confirms metadata access with the configured key,
**not** remaining free quota, inspection quality, a successful inspection,
or clearance of applicable usage conditions. No images/prompts were submitted.
Do not use a generation request to discover whether the project is billed.

Actual model quotas and project tier still need the approved AI Studio interface.
Open [active rate limits](https://aistudio.google.com/rate-limit) with VS Code's
**Browser: Open Integrated Browser** (`workbench.action.browser.open`). Select the
project linked to this key and record only nonsecret tier, RPM, input TPM, RPD,
remaining allowance and expiry where shown. An authenticated VS Code browser
was unavailable to the agent during this check. See the
[access/use findings](../docs/API_FEASIBILITY.md#configured-key-and-read-only-metadata-check).

## Try the validator

Run these commands in a VS Code PowerShell terminal, working folder
`C:\Users\Longin\Desktop\Projects\computervision_in_manufacturing`.
For a fresh checkout run `powershell -NoProfile -File scripts/setup.ps1` first.

| Command | Purpose | Expected result |
| --- | --- | --- |
| `powershell -NoProfile -File scripts/pipeline.ps1 install` | Install the hashed Windows x64 / Python 3.13 contract/inventory lock in `.venv` | Successful install of 19 locked packages; no global changes |
| `powershell -NoProfile -File scripts/pipeline.ps1 test` | Run manifest behavior tests, without network/model calls | All tests pass; exit 0 |
| `.\.venv\Scripts\python.exe -m pipeline.validate_manifest tests/fixtures/image-manifest.fixture.json` | Check the committed synthetic metadata example | `PASS manifest contract`, explicitly labelled `fixture`, with asset/evidence limitations |

The [fixture](../tests/fixtures/image-manifest.fixture.json) contains invented
metadata and placeholder hashes, with no image files. It teaches/tests the format;
it is never a release or prediction. It intentionally fails asset checking.

For a manifest you have actually acquired, add `--asset-root <asset-directory>` to
the validation command. Replace the placeholder with the directory containing the
manifest's relative display/mask paths. This checks file existence, root containment
and SHA-256. A **hash** is a fingerprint of file bytes: changing the file changes
its fingerprint. Hash agreement alone does not prove who created a file.

The CLI exits 1 for invalid data and reports the failing field or asset check.
It does not print raw invalid values or private local paths. It reports known
exact-byte test contamination without removing any test member.

## Inventory a downloaded fastener archive

First follow [the personal download step](../docs/DATA_SOURCES.md#your-download-step--mvtec-ad).
Do not send personal details to the agent. The agent will run the inventory after
the local archive, public source URL and download time are available.

The following is a **template, not a command already executed on official data**.
In the project-root VS Code PowerShell terminal, replace all placeholders with
the real local archive, public HTTPS download URL and actual UTC acquisition time:

```powershell
.\.venv\Scripts\python.exe -m pipeline.inventory_mvtec_ad data/downloads/ACTUAL-ARCHIVE.tar.xz --source-url "https://PUBLIC-DOWNLOAD-HOST/ACTUAL-ARCHIVE.tar.xz" --acquired-at "YYYY-MM-DDTHH:MM:SSZ" --output data/metal_nut.inventory.json
```

Purpose: read the selected category without unpacking anything and save a new local
inventory report. Expected result: `PASS local inventory (acquired)` with measured
counts, followed by its evidence limits. Failure exits 1 with no successful report;
an existing output is never overwritten. Choose a new filename for a repeat run.
For generated test archives use `--evidence-status fixture`. Do not label those
examples as acquired data.

Reports retain archive/member fingerprints, supplied source/time, published licence,
decoded PNG sizes/modes and corresponding defect masks. No resize/orientation change
is applied. Matching dimensions do not certify visual alignment. Unrecognized image
layout, missing/orphan/empty/nonbinary masks, corrupt PNGs, links, unsafe paths and
case collisions fail. Initial limits: 100,000 members, 50 GiB total declared unpacked
bytes, 64 MiB per selected file and 25 million pixels per image. Limits may be
revised only after checking an actual official archive; they are not data measurements.

The checker scans all archive headers, decodes only `metal_nut`, and records other
selected/root-level files without executing their contents. They remain in the
original archive for licence review. It supports root-level `metal_nut/` and
category-only layouts; it does not guess unfamiliar enclosing folder names. Paths
and labels in this report are evaluator metadata, never provider inputs. No source
authenticity, complete official membership, preparation splits, duplicate audit,
release readiness or AI accuracy is established by this command alone.

## One contract, two kinds of checks

```text
Manifest JSON
   -> JSON Schema: required fields, types, versions, permitted paths/splits
   -> Python checks: unique identities, split separation, matching dimensions
   -> optional file checks: existence, containment, hashes
```

[JSON Schema](../schemas/image-manifest.v1.schema.json) is the field contract
source. `pipeline/contracts.py` uses `jsonschema` Draft 2020-12, with required
date-time format checking. The Pydantic `ImageManifest` is a thin envelope around
that same validator; it does not independently redeclare the fields. Use
`read_manifest(Path(...))` for file input: it also rejects duplicate JSON keys and
nonfinite numbers. `.root` contains evaluator metadata, including labels and
label-bearing source members; it must never be passed directly to a provider.
Label-free inference inputs will get a separate adapter/contract before execution.
Pydantic's generic `model_json_schema()` output is not the artifact contract;
consumers must read the canonical schema file.

Current identity transforms preserve encoded bytes and dimensions. Image IDs are
neutral `img-000001` style identifiers. `official_split` normalizes AD's `test`
to `test_public`; `source_member` retains the real archive-relative member name.
AD calibration comes from training; AD2 calibration comes from validation.
Fitting/calibration/evaluation must each be nonempty. Repeated source-byte hashes
across fitting/calibration are rejected; evaluation overlap is visibly reported.
Repeated asset paths are rejected case-insensitively for Windows reproducibility.

## Limits and next work

This is partial `T-CONTRACT`/`T-DATA` coverage. The tools decode both generated test images and the user-supplied
fastener photographs. Current local counts, dimensions, draft splits and the scoped
visual review are recorded in [data preparation](../docs/DATA_PREPARATION.md).
Original archive acquisition, exhaustive related-object identification, model-resolution
visibility and frontend agreement remain unverified. The schema's `authentic` flag is a declaration,
not an authenticity certificate. Contract validation does not mark a run or bundle
complete. Challenges, runs, predictions, reports, visitor state and export contracts
will be added with their consumers. Resizing/maps need measured alignment checks
before a new transform is accepted.

## Check an unpacked fastener directory

Use `pipeline.audit_mvtec_ad_directory` when pictures are already unpacked. It
reuses the PNG, path and mask checks above, hashes every category file, reports
exact-byte image duplicates, and compares counts/dimensions with the official
paper's Table 1. It records unknown URL/time/archive fields as `null` and labels
the source unverified; it does not invent archive provenance from a folder name
or the parent application's Git history.

The [local completeness record](../docs/DATA_COMPLETENESS.md#reproduce-the-check)
contains the actual executed command and result. For repeat checks choose a new
output filename. Exit 0 means local integrity and published-summary checks passed;
it does not certify official file identity. A summary mismatch writes a diagnostic
report and exits 1. Corrupt/missing images or mask pairing failures exit 1 without
a successful report. Links/junctions are rejected; private/configuration paths
are excluded without reading contents and prevent a summary match.

Current work uses the existing unpacked data and draft preparation plan; see
[preparation](../docs/DATA_PREPARATION.md). Next: resolve related-image risks and
represent unpacked acquisition honestly, then build the label-free inference boundary.
Datasets, checkpoints, generated results, raw provider responses and credentials
stay outside source control. No model/provider SDK is installed by this lock.

## Propose preparation groups

`pipeline.plan_preparation` checks the real unpacked category, rechecks photograph
bytes, hashes decoded RGB pixels and makes a deterministic **development-only**
preparation plan. The [schema](../schemas/preparation-plan.v1.schema.json) is its
canonical field contract; Python checks identity, seeded membership, nonempty
groups and duplicate separation. It sorts neutral training IDs, shuffles with
seed 42 and holds out `ceil(n/5)` for calibration. Every official test image remains
evaluation. Identical pixel content crossing preparation groups fails for review;
test overlap is reported without deleting members. Related-image review remains
pending. This does not produce the release image manifest or inference inputs.

See [executed commands, results and limits](../docs/DATA_PREPARATION.md#executed-commands-and-checks).
Existing outputs are never overwritten; use a new filename for a repeat run.
No model is trained, no input image changes and no dependency is added.

## Review related pictures and defect outlines

`pipeline.review_preparation` re-audits the existing category and requires the saved
plan to match the current source membership and image pixels. It scans all picture
pairs using small grayscale copies and writes a documented shortlist, source/mask
fingerprints and side-by-side PNG sheets. No dependency, source image, preparation
membership or provider input is changed. The JSON is an internal review aid, not a
release contract or an automatic visual verdict.

From the project-root VS Code terminal, this is a **repeat-run example**; choose a
new output directory because previous reviews are preserved:

```powershell
.\.venv\Scripts\python.exe -m pipeline.review_preparation data/downloads/metal_nut --plan data/metal_nut.preparation-plan.v1.json --output-dir data/metal_nut.review.NEXT
```

Expected: 69 related-picture candidates and 93 masks for the unchanged real draft,
followed by `Visual review is pending`. A human/agent must actually inspect the
sheets and record decisions separately. Output within the source category, stale
plans and existing review directories are refused. Failed writing can leave an
incomplete directory; only a completed `review.json` identifies a generated set.
The report records pending decisions even when a separate visual record exists.
See [actual review findings and limitations](../docs/DATA_REVIEW.md).

## Dependency reproducibility

[requirements-contracts.in](requirements-contracts.in) contains five direct pins:
Pydantic, jsonschema, its RFC3339 date-time helper, pytest, and Pillow. The
[lock](requirements-contracts.lock) includes every resolved dependency and the
SHA-256 of its selected wheel. This lock targets Windows x64 / CPython 3.13 only;
it must not be presented as a Linux or ML lock. Pillow 13.0.0 is the sole added
package for image decoding; official PyPI metadata declares Python >=3.11, a
CPython 3.13 Windows x64 wheel, no mandatory dependencies, and MIT-CMU licensing.
Sources checked 23 October 2026: [Pillow metadata](https://pypi.org/pypi/Pillow/13.0.0/json),
[Pillow image verification/loading](https://pillow.readthedocs.io/en/stable/reference/Image.html),
[Python streaming TAR reader](https://docs.python.org/3.13/library/tarfile.html).
The inventory checks integrity immediately after opening, then reopens and calls
`load()` for pixel decoding; EXIF inspection must happen after integrity checking.

To intentionally refresh it, download the direct pins and all dependencies with
`pip download --only-binary=:all:` into a new task-specific project cache directory,
using the pinned interpreter and official PyPI. Record each wheel's Name/Version
from `.dist-info/METADATA` and SHA-256; review changes and prove a fresh installation
with `--require-hashes` before committing. Never regenerate the lock automatically
during setup. Provider SDKs wait for their feasibility tasks.

## Honest unpacked provenance and answer-free model inputs

Image-manifest v1 remains supported without changes. V2 replaces the dataset's
mandatory archive receipt with an explicit `acquisition` object. `kind` selects
`archive` or `unpacked_directory`; an archive still requires URL/time/hash. The
unpacked route allows unknown URL/time/archive hash as `null`, requires a separate
content-membership hash, checking time, assurance and context, and never certifies
official acquisition. Both versions use the same identity-asset relationship checks.

From the project root, the current real-data commands are documented in
[data preparation](../docs/DATA_PREPARATION.md#current-continuation). `python -m
pipeline.prepare_inputs --help` describes the exporter, which refuses existing
output or output within source data, checks current plan/audit agreement, and
creates separate `evaluator/` and `model-inputs/` directories. A failed run can
leave partial output; use only a completed package with its summary.

`model-inputs/{fitting,calibration,evaluation}.json` follows
[`model-inputs.v1.schema.json`](../schemas/model-inputs.v1.schema.json). Python
also checks unique ID/path pairs, contained paths, bytes, decoded dimensions,
single-frame RGB and absence of metadata. Inference receives only these records
and clean image pixels. It must not open evaluator manifests, masks, source paths
or notes. References must come from fitting inputs only. These development inputs
do not authorize test tuning or claim a frozen benchmark.

`python -m pipeline.compare_related --help` describes the automated follow-up.
It reconstructs the saved shortlist, searches bounded rigid alignment and records
native-size detail measurements and same-photo controls. It views no images,
changes no membership, confirms no object identity and cannot freeze unresolved
groups. See [actual findings](../docs/DATA_REVIEW.md#automated-follow-up-of-the-12-recorded-risks).

## Local CPU model feasibility

Use the separate `.venv-models` environment through `scripts/models.ps1 install`
or `check`; this does not alter the data-checker environment. The pinned Windows
x64 / Python 3.13 lock uses binary packages except source-only FrEIA, built with
the pinned setuptools tool. `check` verifies dependency consistency and imports,
not fitting or inference.

`python -m pipeline.smoke_specialist --help` describes the actual sample runner.
It requires a local hash-pinned official checkpoint, the approved answer-free
fitting/calibration indexes and a new output directory. It never reads evaluation
inputs or evaluator metadata, never downloads weights and never calls a provider.
Started/failed runs remain recorded and are not successful evidence. See
[the executed commands, real results and remaining limits](../docs/MODEL_FEASIBILITY.md).

For a bounded full-normal-fitting check, use `python -m pipeline.profile_specialist
--help` in `.venv-models`. It derives a configuration using every approved fitting
ID and one normal calibration probe. Windows caps committed process memory at
up to 3 GiB and worker wall time at up to 600 seconds; the supervisor checks free
RAM before launching and refuses execution without an attached resource limit.
Outputs require a new directory below ignored `artifacts/`. No evaluation index,
labels or masks are read. A successful probe measures resources, not defect
quality or final resolution suitability. See [resource findings and exact commands](../docs/MODEL_RESOURCES.md).
