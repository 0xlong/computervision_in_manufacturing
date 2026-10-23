# Fastener picture and outline review — 23 October 2026

I checked 69 similar-picture candidates and all 93 real defect outlines. The
outlines sit on the expected picture regions; no obvious wrong-image, rotation or
translation problem was seen. Some scratch boundaries are faint or only partly
annotated. Similar views do not establish which pictures show the same physical
nut. The preparation groups remain a draft. No images or split memberships changed,
and the website still shows the starter page. There are no trained-model results.

## Scope and reproducible inputs

One agent on `main`; EN-02-T05b, supporting `DATA-SPLIT-003`,
`DATA-TRANSFORM-001` and partial `T-DATA`. This is a visual data-quality review,
not an annotation accuracy score, completed leakage audit or frozen benchmark.
No remote access, download, upload, dependency installation or model/provider call.

The tool re-audited the existing `data/downloads/metal_nut` and rebuilt the saved
plan in memory. Full equality with that plan is required before creating sheets.
All 430 files and their membership still match the previous local fingerprint:
`e0c75a7d552ed53999cba5cf385470976149e8339134771a3097290da3083aa1`.
Plan file SHA-256 remains
`1be285daf202cf1ff0c8bfd977e2a786c24f96e2395822532f9acb7a45803e2e`.
The 176 fitting, 44 calibration and all 115 evaluation members are unchanged.
Original archive/source receipt details remain unknown; none were inferred.

Working folder: project root. This command **was executed**:

```powershell
.\.venv\Scripts\python.exe -m pipeline.review_preparation data/downloads/metal_nut --plan data/metal_nut.preparation-plan.v1.json --output-dir data/metal_nut.review.v3
```

Expected and observed: 69 candidates, 93 masks, 42 PNG sheets (18 related-picture
sheets and 24 outline sheets). Generated JSON intentionally says visual decisions
are pending. Actual visual decisions are recorded separately, after inspection.
All 42 final sheets have the same SHA-256 as the v2 sheets actually viewed. Seven
supplemental native-resolution comparisons were also inspected and copied into v3.
They use `overlay(original, mask)` without resizing, original left and overlay right,
on a 1405 × 730 white canvas with a 30-pixel caption; source panels are 700 × 700.
Their individual hashes are retained in the decision record.

Local ignored evidence:

- `data/metal_nut.review.v3/review.json`: generated candidate/mask inventory and sheet hashes.
- `data/metal_nut.review.v3/visual-decisions.v1.json`: all 69 pair decisions, all 93 outline observations, supplementary hashes and remaining limits.
- `data/metal_nut.review.v3/related-001.png` through `related-018.png`.
- `data/metal_nut.review.v3/masks-001.png` through `masks-024.png`.
- Seven `detail-img-*.png` files for the native-resolution checks below.

| Evidence file | SHA-256 |
| --- | --- |
| Final generated review | `24ef57b88aeb52764d660e7d495c0f3a73c4030e09e23fc00ad7fde623d03c7d` |
| Visual decisions | `2d8b2594ea36693096a8936e8421977e1b1756b7fc40bebd08afc82b74652904` |

These are internal evaluator records containing labels, not inference inputs or
public bundle contracts. Outputs refuse existing directories and locations within
the source category. A failed generation can leave partial files: v1 is an
incomplete failed attempt and must not be used. v2 is the first successfully viewed
set; v3 records the final method description and matches its sheet bytes.

## Similar-picture review

Pillow 13.0.0 converts each original RGB image to grayscale and resizes to 32 × 32
using LANCZOS, without rotation/cropping/registration. All **55,945** unordered pairs
of 335 pictures are scored by mean absolute grayscale difference on a 0–255 scale.
The exploratory review shortlist contains every pair at distance <= 6 (48 pairs),
plus the closest 12 pairs for each distinct split boundary. Ties use sorted neutral
IDs. The union is 69 pairs. This threshold limits an exploratory visual review; it
is not a calibrated duplicate detector or model operating threshold.

| Candidate membership | Pairs visually inspected |
| --- | ---: |
| Fitting / fitting | 29 |
| Calibration / calibration | 2 |
| Evaluation / evaluation | 2 |
| Fitting / calibration | 12 |
| Fitting / evaluation | 12 |
| Calibration / evaluation | 12 |

All P001–P069 were viewed in side-by-side 350-pixel panels. Many have almost the
same pose/outline, while surface rings, highlights, texture or visible defects
differ. No pair is declared a confirmed repeated photograph or independently
identified physical-object group from this view alone. This does **not** establish
that the objects are different: physical-object/session identity is unresolved.

The exact-byte and decoded-pixel checks still find zero identical-content overlaps.
The thumbnail search can miss rotation, crop, small shifts, lighting changes and
other related views. No acquisition-session or physical-part IDs are available in
the current records. Neither similar orientation nor file-number proximity is
sufficient to invent those identities.

These are the specific fitting/calibration risks to follow up before freezing:

| Pair | Calibration source | Fitting source | Observation |
| --- | --- | --- | --- |
| P008 | `train/good/104.png` | `train/good/107.png` | Similar pose; physical identity unresolved |
| P009 | `train/good/016.png` | `train/good/127.png` | Similar pose; physical identity unresolved |
| P019 | `train/good/195.png` | `train/good/023.png` | Similar pose; physical identity unresolved |
| P039 | `train/good/003.png` | `train/good/041.png` | Similar pose; physical identity unresolved |
| P045 | `train/good/192.png` | `train/good/023.png` | Similar pose; physical identity unresolved |
| P049 | `train/good/005.png` | `train/good/122.png` | Similar pose; physical identity unresolved |
| P051 | `train/good/101.png` | `train/good/122.png` | Similar pose; physical identity unresolved |
| P054 | `train/good/182.png` | `train/good/190.png` | Similar pose; physical identity unresolved |
| P055 | `train/good/115.png` | `train/good/110.png` | Similar pose; physical identity unresolved |
| P056 | `train/good/030.png` | `train/good/040.png` | Similar pose; physical identity unresolved |
| P058 | `train/good/003.png` | `train/good/032.png` | Similar pose; physical identity unresolved |
| P059 | `train/good/104.png` | `train/good/204.png` | Similar pose; physical identity unresolved |

No member was moved or deleted. In particular, all official test images stay in
evaluation regardless of similarity. The test/preparation candidates are disclosed
in the decision record; contamination is not ruled out. A stronger follow-up should
compare registered native-resolution surface details and record only defensible
related groups. Confirmed preparation groups must stay together in a newly
versioned proposal, with the seed-42/20% requirement resolved explicitly if affected.
The present schema still truthfully calls related-image review pending; it was not
weakened to accept an unverified split. Do not mark `DATA-SPLIT-003` complete.

## Outline coverage and observations

All sheets retain an unmarked original beside its reference overlay. Photographs
are LANCZOS-resized to 350 × 350; binary masks use NEAREST with the same full-frame
mapping (scale 0.5, no crop/padding/rotation). A 25% pink fill and yellow inner edge
are derived directly from the dataset mask. No AI detection is displayed. These
are local review derivatives, not proposed release assets or model preprocessing.

| Source members covered (inclusive) | Neutral IDs | Count | Observation |
| --- | --- | ---: | --- |
| `test/bent/000.png`–`024.png` | img-000001–img-000025 | 25 | Masks follow folded tabs, including fragments and fine streaks. |
| `test/color/000.png`–`021.png` | img-000026–img-000047 | 22 | Masks follow spots/strokes; exact pigment boundaries are approximate. |
| `test/flip/000.png`–`022.png` | img-000048–img-000070 | 23 | Whole-object face masks follow silhouette and exclude the hole; different semantic scope from local damage. |
| `test/scratch/000.png`–`022.png` | img-000093–img-000115 | 23 | Masks lie on visible abrasion/scratch regions; faint boundary completeness is not certified. |

The intervening img-000071–img-000092 are the 22 normal test images; they correctly
have no defect mask. Every anomalous image is covered exactly once by the visual
record. No gross wrong-image, geometric offset or rotation mismatch was observed
in this pass. This is a visual assessment, not pixel-perfect annotation certification.

Native 700 × 700 side-by-side checks:

- `img-000026` / color/000: small dark spot; mask corresponds to the spot.
- `img-000030` / color/004: thin curved stroke beside the hole; mask follows it.
- `img-000029` / color/003: separate small spots; separate mask regions correspond.
- `img-000027` / color/001: thin line on the upper-right face; mask follows it.
- `img-000016` / bent/015: main folded tab and faint streaks below it are present; do not discard small disconnected annotation regions.
- `img-000101` / scratch/008: mask is on the abrasion, but parts of the visible light band extend beyond the polygon. Retain the source annotation and disclose this extent caveat; no source correction was made.
- `img-000113` / scratch/020: subtle fine scratches are visible inside the marked lower-face area; native detail is more informative than the overview.

The smallest complete mask contains 2,135 source pixels (color/000). Nearest-neighbour
mask resizing leaves at least 284 pixels at 256², 642 at 384² and 1,139 at 512²
across the 93 masks. None disappears in those mask checks. **These counts do not
prove RGB defect visibility, retention of every tiny component, or model detection.**
No model input resolution is selected here. Candidate preprocessing still needs
visual RGB comparisons and actual specialist feasibility measurements before freeze.

## Verification and next work

Executed `powershell -NoProfile -File scripts/pipeline.ps1 test`: **149 passed**,
including 12 new review-tool cases (parametrized). Checks cover known overlay
coordinates, invalid masks, deterministic shortlist/order and sheet bytes, full mask
membership, unchanged input bytes, output preservation/containment, stale image/mask/
plan rejection and explicit pending-review CLI claims. They use generated fixtures;
they cannot certify real mask quality. The real-sheet visual review above supplies
separate evidence. The initial restricted run failed on Windows temporary-folder
permissions; unchanged checks ran with normal local file access. The first actual
run/tests caught normal images having `mask: null`; the new tool was corrected to
skip them, preserving the original audit meaning. No check was weakened.

The workspace checker passed; it establishes only workspace readiness. Web checks
were not repeated because no web code/tooling changed. A fresh single-agent review
read the final code/tests and findings against source preservation, test membership,
coordinate mappings, leakage claims and unknown source details. Documentation and
whitespace checks are recorded in progress.

Next: strengthen the 12 preparation-boundary candidate reviews before any split
freeze; represent the unpacked acquisition honestly in a versioned manifest
contract; then prepare label-free model inputs and test candidate RGB resolutions.
These follow-ups need no repeated download. Gate 1 and all app stories remain open.
