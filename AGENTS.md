# Working agreement for coding agents

## Read first

- This project is both real software development and an educational journey for a junior developer using AI coding agents for the first time.
- Read `AI_Inspection_Pilot_Lab_SPEC.md` before implementation; it owns product requirements. Read `docs/PROGRESS.md` to find the current step and `README.md` for the learner's entry point.
- Use VS Code with the Codex extension as the default. CLI sessions in ordinary PowerShell terminals are optional. Keep tooling small; introduce a tool only when a current task needs it.

## Teach while delivering

- Explain in plain English. Define a new technical term once using a concrete example from this app. Keep explanations short and practical.
- Before a meaningful step, state: **What we are doing**, **why it matters**, **what the agent will do**, and **your role**. Distinguish actions for the user from actions already performed by the agent.
- After the step, state: **What was created/changed** (clickable files), **how it was checked**, **what you can try** (exact command or UI action and expected result), and **what happens next**.
- For a command the user should run, give the working folder, the command, its purpose, and the expected result. Never present an example command as already executed.
- Use a short ASCII/Mermaid diagram when architecture, dependencies, or parallel tasks are hard to follow in prose. Explain every box in familiar language. Skip diagrams for trivial changes.
- Invite small learning actions at useful milestones: inspect a diff, run a check, try a button, or explain a trade-off. These are optional learning opportunities, not approval gates for ordinary work.
- Continue routine authorized work autonomously. Ask only for consequential product choices, missing access, or actions outside existing authority. If the user explicitly requests one-step-at-a-time guidance, give one action and wait for their result.
- When a check fails, explain the symptom and next diagnostic action simply. Fix and rerun relevant checks; do not weaken checks or requirements to appear finished.

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
