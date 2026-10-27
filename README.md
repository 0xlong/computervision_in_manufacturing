# AI Inspection Pilot Lab

**An interactive demo of how AI could support visual quality checks in manufacturing.**

Inspect five metal parts yourself, compare your decisions with two AI models, and
explore what missed defects and extra checks could mean for a working day.

This is a working local portfolio prototype using public images and genuine saved
AI responses. It demonstrates an evaluation approach; it does not establish
factory readiness or measured business savings.

## What you can try

| View | What it shows |
| --- | --- |
| **Try it** | Judge five parts, then reveal the AI assessments and dataset answers. |
| **Watch AI Inspect** | Watch both models' saved answers across all 115 test pictures. |
| **Results** | Compare missed defects, unnecessary flags, answer coverage and recorded request times in a table and charts. |
| **Workday & brief** | Change volume, review capacity and cost assumptions, then download a short pilot brief. Available under Results. |
| **Architecture** | Follow an interactive diagram showing how the software and saved evidence fit together. |

Your challenge answers stay in your browser. Exploring the website makes no AI
requests and requires no API key, account or image upload. The demo displays
previously recorded results; it does not inspect new production pictures.

## What the evaluation found

Both models were evaluated on the same **115 public test pictures**: 93 defective
parts and 22 good parts. All 115 pictures have a saved assessment from each model.

| Model | Correct decisions | Defects missed / 93 | Good parts flagged / 22 | Unsure answers |
| --- | --- | --- | --- | --- |
| Gemini 3.5 Flash-Lite | 98 / 115 (85.2%) | 12 | 5 | 0 |
| Gemma 4 26B | 89 / 115 (77.4%) | 20 | 5 | 1 |

An unsure answer is sent for human checking and is not counted as correct. These
figures describe this test set only. The five-picture challenge is a curated
teaching example, not a separate measure of human or AI performance.

[Evaluation and verification records](docs/FASTENER_VERIFICATION.md) explain the
counts, recorded timings and limitations.

## Why this matters for a manufacturing team

A useful inspection pilot needs more than an accuracy score. This demo connects
model errors with review workload and makes the assumptions visible. It helps a
team discuss what to test, where a person should check a result, and what evidence
is still needed before using a system at a real site.

For technical reviewers, the project includes reproducible calculations, saved
model settings, evidence checks and automated browser tests. The website uses
React and TypeScript; Python prepares and checks the saved evidence. AI coding
agents assisted development, with checks and limitations recorded in the project.

## Run locally in VS Code

Open the project folder in VS Code and choose **Terminal → New Terminal**.
Run these commands from the project root on Windows:

```powershell
# First run only: install the project's local tools and web packages.
powershell -NoProfile -File scripts/setup.ps1

# Start the website.
powershell -NoProfile -File scripts/web.ps1 dev
```

Setup requires Python 3.13 on PATH and internet access. Expect `Setup complete`,
then a local server at **http://127.0.0.1:5174/**. The repository includes the saved
results and display pictures, so trying the website needs no new model calls.

In VS Code, press **Ctrl+Shift+P**, select **Browser: Open Integrated Browser**,
and enter that address. Keep the terminal running; press **Ctrl+C** to stop.

[Development setup](docs/DEVELOPMENT.md) covers installation details and check
commands. [The local guide](docs/FASTENER_LOCAL.md) provides a longer walkthrough;
older dated UI descriptions may show controls that have since changed.

## Scope and limitations

- Current working track: fasteners, using MVTec AD's `metal_nut` pictures. The
  metal-surface track and further model evaluations remain future work.
- These are public benchmark pictures, not private factory or customer data.
  Original acquisition records and independence of related physical parts remain
  incomplete; public models may also have encountered the benchmark before.
- Workday and cost projections use editable assumptions. They are not measured
  savings, staffing recommendations or production approval.
- Local Chromium checks cover inspection, saved progress, comparison, export,
  responsive layouts and automated accessibility. Native devices, other browsers
  and screen-reader behavior have not received a full audit.
- No hosted demo or production deployment is provided by this repository.

Dataset pictures and outlines retain their supplied **CC BY-NC-SA 4.0** notices.
See the [dataset source](https://www.mvtec.com/research-teaching/datasets/mvtec-ad),
[included licence](web/public/evidence/notices/license.txt), and
[source/provenance record](docs/DATA_SOURCES.md). No affiliation with a manufacturer
or dataset provider is implied.

## Further reading

- [Project requirements](docs/AI_Inspection_Pilot_Lab_SPEC.md)
- [Current progress and recorded checks](docs/PROGRESS.md)
- [What belongs in this repository](docs/REPOSITORY_CONTENTS.md)
- [Data preparation and evaluation tools](pipeline/README.md)
