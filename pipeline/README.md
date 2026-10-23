# Offline evidence pipeline — first contract increment

The pipeline currently validates image manifests. A **manifest** is a list of
images and their origins, splits, labels and display assets. Models, acquisition,
evaluation reports and release bundles are not implemented yet.

## Try the validator

Run these commands in a VS Code PowerShell terminal, working folder
`C:\Users\Longin\Desktop\Projects\computervision_in_manufacturing`.
For a fresh checkout run `powershell -NoProfile -File scripts/setup.ps1` first.

| Command | Purpose | Expected result |
| --- | --- | --- |
| `powershell -NoProfile -File scripts/pipeline.ps1 install` | Install the hashed Windows x64 / Python 3.13 contract lock in `.venv` | Successful install of 18 locked packages; no global changes |
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

This is partial `T-CONTRACT`/`T-DATA` coverage. We have not decoded actual images,
verified measured pixel dimensions, acquired an official archive, established exact
category membership, constructed seeded preparation splits, audited related images,
or validated frontend agreement. The schema's `authentic` flag is a declaration,
not an authenticity certificate. Contract validation does not mark a run or bundle
complete. Challenges, runs, predictions, reports, visitor state and export contracts
will be added with their consumers. Resizing/maps need measured alignment checks
before a new transform is accepted.

Next: use the [official acquisition/discovery record](../docs/DATA_SOURCES.md),
acquire approved data into ignored `data/`, record archive/member hashes and counts,
then implement fixed preparation splits and the label-free inference boundary.
Datasets, checkpoints, generated results, raw provider responses and credentials
stay outside source control. No model/provider SDK is installed by this lock.

## Dependency reproducibility

[requirements-contracts.in](requirements-contracts.in) contains four direct pins:
Pydantic, jsonschema, its RFC3339 date-time helper, and pytest. The
[lock](requirements-contracts.lock) includes every resolved dependency and the
SHA-256 of its selected wheel. This lock targets Windows x64 / CPython 3.13 only;
it must not be presented as a Linux or ML lock.

To intentionally refresh it, download the direct pins and all dependencies with
`pip download --only-binary=:all:` into a new task-specific project cache directory,
using the pinned interpreter and official PyPI. Record each wheel's Name/Version
from `.dist-info/METADATA` and SHA-256; review changes and prove a fresh installation
with `--require-hashes` before committing. Never regenerate the lock automatically
during setup. Provider SDKs and ML dependencies wait for their feasibility tasks.
