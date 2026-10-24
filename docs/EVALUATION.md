# Offline API evaluation

The evaluator counts every declared test image. It makes no network requests,
reads no credentials, and never reruns inference. Current checks use generated
pictures and invented responses only; there are no real model quality results yet.

From the project root, after a **complete evaluation run** has been saved:

```powershell
.\.venv\Scripts\python.exe -m pipeline.evaluate_api --package data/metal_nut.inputs.v2 --evidence artifacts/your-complete-evaluation/evidence.json --out artifacts/your-complete-evaluation/report.json
```

This is command syntax, not an executed real-data evaluation. The two-probe
normal-fitting trial is deliberately rejected: it is not the complete test set.
The output path must be unused; existing reports are preserved.

The file entry point validates the manifest and display/mask files, checks the
clean RGB input files, compares their decoded pixels to the corresponding display
images, and binds manifest/input byte hashes to the saved run. Every evaluation
ID must occur exactly once. A changed model input, wrong category, preparation
image, partial set, unfinished run or unreconciled submission blocks evaluation.

The report preserves fixture/development status. Hashes do not establish provider
authenticity, official acquisition or publication clearance. Promotion to a public
authentic bundle needs its own provenance/security/licence review.

For successful outputs it reports TP/FN/FP/TN, class denominators, recall,
false-positive rate, precision and review count. `uncertain` routes to review.
Separately it reports full-set routing metrics with technical failures routed to
review, coverage and failure reasons. This makes a failing model's additional
review workload visible. Zero-denominator rates/intervals are `null` (display as
N/A). Recall and false-positive rates have 95% Wilson intervals. These intervals
do not cover dataset shift or public-model benchmark contamination.

Output order is deterministic; no generation timestamp is inserted. Provider
observations, local paths and raw response bodies are not copied into the report.
The saved evidence remains the source for real observations and request metadata.
No score curves, calibrated probabilities, heatmaps or sensitivity are invented.

Verification on 24 October 2026: 14 new cases cover hand-counted confusion
matrices, uncertainty and failure routing, zero denominators, known Wilson bounds,
membership/hash/track changes, incomplete and unknown submissions, actual image
pixel mismatches with rebound hashes, deterministic output and overwrite refusal.
No real dataset image was visually opened.
