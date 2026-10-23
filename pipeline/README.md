# Offline evidence pipeline — contracts and local inventory

The pipeline validates image manifests and checks downloaded fastener archives.
A **manifest** is a list of images and their origins, splits, labels and display
assets. Automatic downloading, models, evaluation reports and release bundles
are not implemented yet. The supplied unpacked fastener folder and draft split pass local checks.
Missing archive details remain explicitly unknown; no repeated download is needed.

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
during setup. Provider SDKs and ML dependencies wait for their feasibility tasks.
