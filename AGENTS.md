# Working agreement for coding agents

## Read first

- This project is both real software development and an educational journey for a junior developer using AI coding agents for the first time.
- Read `docs/AI_Inspection_Pilot_Lab_SPEC.md` before implementation; it owns product requirements. Read `docs/PROGRESS.md` to find the current step and `README.md` for the learner's entry point.
- When planning implementation, read `docs/USER_STORIES.md`; break the next ready story/enabler into small tasks with acceptance checks and dependencies using `docs/WORKFLOW.md`. Keep assignments/results in `docs/PROGRESS.md`; user stories do not replace the specification.
- Use VS Code with the Codex extension as the default. CLI sessions in ordinary PowerShell terminals are optional. Keep tooling small; introduce a tool only when a current task needs it.

## Teach while delivering

- The user's standing preference is simple, everyday language in every reply, including progress updates and final answers. Assume a beginner who is learning software development. Start with what the work actually does, using familiar words: for example, "I built a data checker."
- Explain the practical result before technical names. Introduce a technical term only when needed, and explain it with an example from this app. Keep task IDs, package versions, file inventories and detailed test evidence in linked documentation unless the user asks for them or they are needed to act.
- Before a meaningful step, briefly explain what we are doing, why it matters, what the agent will do, and the user's role. Say "You don't need to do anything now" when no action is needed. Distinguish suggested user actions from work already performed.
- After the step, explain **what I built/changed**, **what you can see or use now**, **why it matters**, **how I checked it**, and **what happens next**. Include one clear thing to try when useful. Put clickable file links after the plain-language explanation.
- For work behind the scenes, say what changed on the website, including when it still shows the same starter page. Distinguish working features, test examples and real AI results explicitly. Describe what the passing checks prove and what remains unverified.
- Keep explanations short and concrete. Use a few short paragraphs or simple bullets; include a table or long technical breakdown only when it helps the user understand or act. Keep precise engineering detail in the project records without making it the main explanation.
- For a command the user should run, give the working folder, the command, its purpose, and the expected result. Never present an example command as already executed.
- Use a short ASCII/Mermaid diagram when architecture, dependencies, or parallel tasks are hard to follow in prose. Explain every box in familiar language. Skip diagrams for trivial changes.
- Continue routine authorized work autonomously. Ask only for consequential product choices, missing access, or actions outside existing authority. If the user explicitly requests one-step-at-a-time guidance, give one action and wait for their result.
- When a check fails, explain the symptom and next diagnostic action simply. Fix and rerun relevant checks; do not weaken checks or requirements to appear finished.

Example of the expected language: "I built a data checker. It checks the image
information for mistakes before we use it with AI. The website still shows the
starter page. I tested that the checker catches missing files and incorrect
information. Next, I'll get the real fastener images and check them."

## Image viewing and token use

- Use automated checks for dataset-wide validation. View only a few examples to understand the data or investigate a specific problem: normally 1–3, with a maximum of 5 examples per task. Every example in a contact sheet counts toward that limit; splitting views across tool calls does not reset it.
- A general request to check pictures or outlines does not authorize exhaustive viewing. Review a larger visual sample only when the user explicitly requests it.
- Reuse existing findings and stop viewing once the specific question is answered. Record the sample size and remaining uncertainty; never describe a small visual sample as a full visual review.

## Development loop

1. Inspect the actual state and select one small, useful task from `docs/PROGRESS.md`.
2. Identify its requirement, allowed files, dependencies, and observable completion check.
3. Explain the step, implement it, and run relevant checks. Use current official documentation for unfamiliar/time-sensitive interfaces.
4. Review the diff against the requirement; use a fresh review for meaningful milestones. A green test suite alone does not prove usability or evidence integrity.
5. Update `docs/PROGRESS.md` with evidence, limitations, and the next action. Save a focused Git checkpoint when the task is verified; stage named files, not an indiscriminate repository-wide add.
6. Report the result in the teaching format above and continue ready work within scope.

## Git and parallel work

- Start with one coordinator. Parallelize only independent tasks with stable shared contracts and clearly owned files; consult `docs/WORKFLOW.md` for the procedure.
- Each parallel worker gets its own branch and worktree. A terminal tab alone does not isolate files. Confirm folder and branch before edits.
- The coordinator owns shared schemas, dependency manifests/lockfiles, root configuration, progress tracking, and integration. Workers report a required shared change rather than independently changing the contract.
- Give each worker a task, allowed files, completion check, and handoff expectation. Each handoff includes branch/commit, changed files, checks, and remaining problems.
- Integrate one branch at a time, inspect the diff, run relevant checks, and then verify the combined app. Resolve ordinary conflicts without involving the learner in every Git operation.
- Worktrees share Git metadata and are not security sandboxes. Keep generated data/output directories distinct or explicitly read-only; use separate dev-server ports. Verify clean/merged state before removing a worktree.
- Keep merges in the coordinator's checkout, not in worker checkouts. Preserve user changes and never reset, force-push, or discard work to simplify integration.

## Boundaries and evidence

- Follow the specification's free-tier-only, privacy, licensing, and authentic-evidence requirements. Do not make paid calls, enable billing, publish, or modify remote infrastructure without applicable authorization.
- Exclude `done/`, `.env` files, credentials, tokens, and similar secrets from searches/access. Document required variable names without reading their values. Do not copy secrets into worktrees.
- Use VS Code's integrated browser for websites/localhost. If unavailable, give the URL and `Browser: Open Integrated Browser` (`workbench.action.browser.open`) and say what remains unverified.
- `python scripts/check_environment.py` checks the development workspace only. It does not establish that models, provider access, app tests, or deployment work.
- Do not introduce application dependencies, CI services, agent orchestration frameworks, Docker, WSL, or tmux just for completeness. Add the smallest justified piece when needed.
