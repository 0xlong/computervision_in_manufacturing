# Fastener preparation draft — 23 October 2026

Current direction (24 October 2026): further local model experiments are
deferred. Prioritize fast, efficient API models with verified free access;
see [model-selection plan](MODEL_SELECTION.md). Earlier local preparation and
measurement records below are preserved, not current assignments.

## Current continuation

The unpacked acquisition is now representable in image-manifest **version 2**.
Version 1 remains unchanged and strict. The new acquisition object distinguishes
an archive from an unpacked directory, user-supplied/unverified context from
operator-declared details, and the checked content fingerprint from an archive hash.
Unknown direct URL, download time and original archive hash stay `null`.
`checked_at` is explicitly a checking time, never a substituted download time.
This records provenance limitations; it does not complete official-source verification.

Automated follow-up measured all 12 recorded preparation-boundary risks, with
same-photo controls and zero new visual examples. It did not establish physical-part
identity. **The original 176/44/115 groups remain provisional and are not frozen.**
See [comparison measurements and limitations](DATA_REVIEW.md#automated-follow-up-of-the-12-recorded-risks).

The real, development-only package is in ignored `data/metal_nut.inputs.v2/`:

- `evaluator/`: v2 labelled image manifest, unchanged original photos/masks and
  retained notices. This is evaluator metadata, never inference input.
- `model-inputs/`: 335 neutral-named RGB PNGs and separate fitting/calibration/
  evaluation indexes. The PNGs preserve source pixels but remove embedded metadata;
  the indexes allow only neutral IDs, neutral paths, dimensions and content hashes.
- `preparation.json`: membership, manifest/index fingerprints and explicit limitations.

Export verified all 335 model images for unchanged RGB pixels, empty metadata,
dimensions, hashes and complete membership. The manifest CLI separately verified
all 428 evaluator image/mask asset hashes. No source image or split changed.
The three indexes contain 176 fitting, 44 calibration and all 115 evaluation images.
Model feasibility reads fitting/calibration only; final-test inference remains pending.

| Current artifact | SHA-256 |
| --- | --- |
| Evaluator v2 image manifest | `5c77a9e478d03ce4b211d655b577b4363cc2853b9900eaef93ebb94f0a1940d5` |
| Fitting input index | `32e34327319987c986f14e7f59d06441f16c115e3a7738620f490b0cb3b793d2` |
| Calibration input index | `fe2732cc3b7f333941335b61b4a672af1694a48d56c06964d66634b9aed7cfad` |
| Evaluation input index | `00bfb7bd04b3f369426e4db8c6d78d69926ef659bf8072d114369c1415d42516` |

Executed in the project root:

```powershell
.\.venv\Scripts\python.exe -m pipeline.prepare_inputs data/downloads/metal_nut --plan data/metal_nut.preparation-plan.v1.json --acquisition data/metal_nut.acquisition.v2.json --output-dir data/metal_nut.inputs.v2
.\.venv\Scripts\python.exe -m pipeline.validate_manifest data/metal_nut.inputs.v2/evaluator/image-manifest.v2.json --asset-root data/metal_nut.inputs.v2/evaluator
```

The acquisition input was explicitly transcribed from the existing user-supplied
source record, retaining its checking timestamp and the three unknown values.
It contains no newly inferred acquisition facts. Choose a new output directory
for a repeat; outputs are not replaced. An interrupted export can leave partial
files and must not be treated as a successful package without `preparation.json`.

The earlier sections below describe the previous draft and the format limitation
that motivated v2. The website remains the starter page; this package is not a
public evidence bundle, final benchmark or model-performance result.
Both specialists have now completed authentic normal-only CPU practice runs using
these preparation inputs. See [measurements and limits](MODEL_FEASIBILITY.md).

The new download in `data/downloads/metal_nut/` passes the file checks. A draft
separates pictures for model practice, threshold setting and final testing.
The website still shows the starter page. No model has been trained.

## Current download

The user supplied this folder in response to the official MVTec download request.
It is already unpacked; no original archive, direct download URL or exact download
time was supplied. The source record retains that context without claiming an
independently verified download receipt or inventing missing values.

The folder contains **430 files / 165,862,477 bytes**: 220 normal training pictures,
22 normal test pictures, 93 anomalous test pictures, 93 masks, `license.txt` and
`readme.txt`. All 428 PNGs passed integrity/full decoding. The 335 photographs are
RGB, 700 × 700. All anomalous pictures have corresponding nonempty binary masks
of the same dimensions. No exact-byte photograph duplicates were found.

All 430 paths, sizes and file identities match the previously inspected
[Hugging Face reference](https://huggingface.co/datasets/MSherbinii/mvtec-ad-metal-nut)
at revision `8db7371c35a94709cbb3e69ac69f80d2716e2f8a`: PNGs by LFS SHA-256 and
notices by Git blob identity. This is a mirror comparison, not proof of official
acquisition. Included notices identify MVTec and CC BY-NC-SA 4.0; the mirror's MIT
card is not used to relicense images.

Ignored local evidence: `data/metal_nut.current-folder-audit.v1.json` and
`data/metal_nut.current-source-record.v1.json`. Current membership fingerprint:
`e0c75a7d552ed53999cba5cf385470976149e8339134771a3097290da3083aa1`.
The previous `data/downloads/mvtec-ad-metal-nut/` and older ignored reports are no
longer present. [Earlier records](DATA_COMPLETENESS.md) describe historical checks;
the agent did not delete or move those inputs. Current checks use the new path.

## Draft preparation groups

| Purpose | Internal name | Pictures |
| --- | --- | ---: |
| Learn normal appearance | fitting | 176 |
| Set the warning threshold using separate normal pictures | calibration | 44 |
| Measure results later; retain all original test pictures | evaluation | 115 |

Neutral IDs follow sorted source-member order. Normal training IDs are sorted,
shuffled using Python `random.Random(42)`, and the first `ceil(n/5)` are calibration.
The exact integer formula is `(n + 4) // 5`. Test pictures are not involved in
choosing preparation membership or thresholds, and none are removed.

Encoded-file SHA-256 and decoded RGB pixel SHA-256 are checked across fitting and
calibration. Pixel hashes cover the ASCII header `RGB:<width>:<height>:` plus
unchanged decoded RGB bytes. Different PNG encodings of an identical picture
cannot silently cross groups: that fails for group-aware review. Evaluation
overlap is reported while retaining test images. The real draft has **zero
exact-pixel overlaps** between preparation groups or between preparation and test.
A first visual pass reviewed 69 similar-picture candidates; physical-object
relationships remain unresolved. See [review findings](DATA_REVIEW.md).

The [canonical schema](../schemas/preparation-plan.v1.schema.json) and Python
relationship checks validate a development-only plan. It is not the release image
manifest, frozen benchmark or label-free inference input. Source paths contain
labels and must remain evaluator metadata.

Saved plan: `data/metal_nut.preparation-plan.v1.json`.

| Fingerprint | SHA-256 |
| --- | --- |
| Complete JSON bytes | `1be285daf202cf1ff0c8bfd977e2a786c24f96e2395822532f9acb7a45803e2e` |
| Fitting IDs | `7bbd9763086b0ecedd8299cd253b46fbe615902d238d78331d9081072e542c3d` |
| Calibration IDs | `77161c006b1d696e13f4240392cad15bc9f922a56b6de443a031941f103428aa` |
| Evaluation IDs | `2c0cb7eafed57f71dd2e4fbe227757dd178b5409daa0c136604e62040ceeccb9` |

ID fingerprints use sorted IDs joined with LF and a final LF. The plan has no
creation timestamp, so unchanged inputs/methods yield identical JSON bytes. Its
input fingerprint includes masks and notices even though only photographs are split.

## Executed commands and checks

Working folder: `C:\Users\Longin\Desktop\Projects\computervision_in_manufacturing`.
These commands **were executed**:

```powershell
.\.venv\Scripts\python.exe -m pipeline.audit_mvtec_ad_directory data/downloads/metal_nut --output data/metal_nut.current-folder-audit.v1.json
.\.venv\Scripts\python.exe -m pipeline.plan_preparation data/downloads/metal_nut --output data/metal_nut.preparation-plan.v1.json
powershell -NoProfile -File scripts/pipeline.ps1 test
```

The first checked 430 files and matched the published category summary. The second
rechecked original bytes before pixel fingerprints and produced the 176/44/115
draft. Neither modifies source images; outputs are never overwritten. For another
run choose a new output filename. The planner refuses a failed real-category
summary and adds no dependency.

**137 tests passed**, including 14 new preparation cases: known seeded membership,
integer rounding, stable order, complete evaluation, re-encoded duplicates, visible
test overlap, modified plans, changed images, safe paths and preserved outputs.
The first run caught an accidental duplicate in the generated test example; the
example was corrected while duplicate checks remained enforced.

## Before freezing a benchmark

This is `development_only`. All 93 real outlines received a visual alignment
review, with no gross geometric mismatch seen and an annotation-extent caveat for
scratch/008. Seven native-resolution details were checked. The 69 related-picture
candidates include 12 unresolved fitting/calibration risks; membership stays a
draft. See [review evidence and limitations](DATA_REVIEW.md). Model-resolution
defect visibility, related-object identification, model compatibility and source
metadata remain work.
The user confirmed the folder is in `data/downloads`; no archive location was
provided. Continue with an explicitly unpacked acquisition record, without another
move/download request. Do not substitute content fingerprints for an archive hash
or a check time for download time.

Image-manifest v1 requires an archive hash and exact acquisition timestamp. It
cannot truthfully represent unpacked-only acquisition yet. Before producing that
manifest, recover those details or version the contract to represent unknown or
declared fields explicitly. Do not weaken v1 or invent values. The draft does not
complete `DATA-SOURCE-001`, all of `DATA-SPLIT-003`, Gate 1 or any user story.

Next: strengthen the 12 preparation-boundary candidate reviews, represent
unpacked acquisition honestly, then produce the validated image manifest and
label-free model inputs. No repeated download, paid/provider call or publication
is needed for this work.


## Picture review completed as a scoped first pass

The [review record](DATA_REVIEW.md) contains the actual command, sheet locations,
input/output fingerprints, all mask coverage and the remaining related-picture
risks. The review tool scans all 55,945 pairs, creates 69 candidates and lays out
all 93 outlines beside their originals. All 42 sheets and seven native-resolution
details were inspected. No source image, preparation member or test image changed.

Current checks: **149 pipeline tests passed** and the workspace check passed.
These prove the tool's tested behavior and input consistency; they do not prove
physical-object independence, exact annotation boundaries or model performance.
The website is unchanged and there are no AI results yet.


Native-size follow-up: all 12 fitting/calibration candidates were also compared
at 700 × 700. No reliable repeated physical-object identity was established;
independence remains unverified. The [supplemental record](DATA_REVIEW.md#native-size-follow-up-of-all-12-preparation-boundary-candidates)
contains the observations and hashes. Next independent implementation: represent
unpacked acquisition honestly, keeping preparation development-only and related-object
risk visible.
