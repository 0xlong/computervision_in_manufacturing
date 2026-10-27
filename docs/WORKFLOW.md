# Working with agents: the practical guide

Current direction (24 October 2026): use one agent for fast, efficient model
selection, starting with API free-access verification and a short bounded trial
plan. Further local PaDiM/PatchCore experiments are deferred. The earlier local
preparation sequence below is historical where it conflicts with this update.
See [model-selection plan](MODEL_SELECTION.md).

## One task at a time

For each task, the agent explains the goal and your role, builds a small change, runs relevant checks, reviews it, saves a checkpoint, and records progress. You can inspect the files or run the same check. The agent continues routine work unless you request step-by-step pauses.

All explanations follow the [plain-language rules](../AGENTS.md#teach-while-delivering).
First explain what was built and what you can see or use now. Keep engineering
details in linked files so the main explanation stays easy to follow.

Use this small task card in chat or the progress file; no issue-tracking service is required:

```text
Task: Record an answer before showing the model result
Owner: challenge worker
Depends on: agreed image/result format
Allowed files: challenge components and their tests
Done when: a browser check proves reveal is blocked before answering
Handoff: branch, commit, changed files, checks, known gaps
```

Choose tasks by outcomes, not vague instructions such as “do the frontend.” Shared setup and contracts must exist before dependent work runs in parallel.

## Turning a story into tasks

Read [USER_STORIES.md](USER_STORIES.md) for user outcomes and acceptance criteria. Technical enablers can be separate tasks. We use Markdown first, so no tracker account is needed.

Example: **US-01 — Start and complete an inspection challenge**. After the shared data/state contracts are ready, the coordinator inspects the code and can propose this breakdown. These tasks are examples, not started assignments:

| Example task | Work and completion check | Dependency |
| --- | --- | --- |
| US-01-T01: Build image/answer controls | Render the agreed image input, zoom, two answer buttons, and keyboard labels; verify component behavior. | Shared contract and web setup |
| US-01-T02: Build answer/progress logic | Record answers by track/image and preserve them during navigation; test known state transitions. | Shared contract and web setup |
| US-01-T03: Connect the challenge | Wire controls to state, load the five declared image IDs, implement answer-before-reveal, and check the complete flow. | T01 and T02 |
| US-01-T04: Verify story acceptance | Run browser checks, review actual imagery and failure behavior, and record which US-01 criteria pass. | T03 and authentic evidence |

T01 and T02 can run in separate worktrees if their file ownership is distinct. T03 joins them; T04 checks the integrated result. Each builder includes its own tests, and story verification is additional evidence. Persistence/reset belong to US-08 and need integration checks with this story.

```text
Shared contracts + working tool setup
           /                 \
      T01: controls      T02: answer logic
           \                 /
             T03: connect
                   |
             T04: verify
                   |
       US-01 done only if every criterion passes
```

For each real task, the agent records the parent story, goal, dependency, allowed files, completion check, owner, and status in the current progress file. The final handoff adds branch/commit, actual checks/results, and known gaps. Create detailed tasks just before their story is ready; later implementation choices can depend on what the earlier work teaches us.

Your role is to judge whether the story describes something useful and try its working journey. The agent chooses ordinary implementation steps, checks dependencies, and proposes parallel tasks with clear boundaries. You do not need to invent every technical ticket.

## First parallel round (later, not running now)

**Readiness check — 24 October 2026:** use one agent for the current API-access
and efficient-model selection sequence. Basic tools and image contracts exist, but final
preparation groups, input resolution and the run/result/state formats needed by
the app are not settled. These connected steps do not currently justify several
builders. Independent reading or review could run separately, but the current
instruction is one agent. No workers or worktrees have been started.

The first useful pair can be challenge controls and answer-state logic once their
shared state format exists, as in the example above. Before assigning them, save
the shared starting point, preserve/resolve existing uncommitted work, give each
worker separate files and a check, and confirm how their changes will join. A
worktree supplies a separate folder; the coordinator still checks that the pieces
work together. This advice is based on the project's current dependencies, not a
requirement to finish every foundation task before any independent work.

```text
                     Coordinator
                  shared starting point
                    /      |      \
                   /       |       \
          Challenge     Calculations     Data preparation
          worktree      worktree         worktree
          answers/UI    costs/reviews    images/manifests
                   \       |       /
                    \      |      /
                  Coordinator merges one at a time
                    → checks the combined app
                    → shows you a working milestone
```

- A **branch** records one line of changes.
- A **worktree** is a separate project folder on a branch. Workers cannot overwrite each other's working files there, but shared assumptions can still disagree.
- A **commit** is a saved checkpoint. A **merge** combines branch changes.
- A **conflict** means Git needs a decision about overlapping changes; the coordinator handles routine conflicts and reruns checks.

The coordinator owns shared schemas, configuration, dependency/lockfiles, and integration. Workers own their agreed files. Do not assign two workers the same shared setup task.

## Example commands: not executed by this guide

These are for the coordinator after the shared foundation is committed on `main`, there are no uncommitted changes, and worker tasks are ready. Run from the main project folder. The sibling folders require a permitted writable location; if unavailable, choose an approved location instead.

```powershell
git status --short
git worktree add -b feature/challenge ../inspection-challenge main
git worktree add -b feature/calculations ../inspection-calculations main
git worktree add -b feature/data ../inspection-data main
git worktree list
```

Expected result: three new folders, each on its own branch, listed by the final command. No agents start just because folders were created.

Open each worker folder in a separate VS Code window (**File → New Window → Open Folder**) and use its Codex extension, or open a named terminal, change to the worker folder, and launch `codex`. Before editing, check:

```powershell
git rev-parse --show-toplevel
git branch --show-current
```

The first command identifies the folder. The second identifies the branch. Each worker receives the task card and reads `AGENTS.md` in its worktree. Each environment installs its own required dependencies when needed; ignored dependency folders are not automatically copied. Keep generated output separate and use different ports for simultaneous web servers.

At completion, the worker commits only its task files and reports the commit/check results. In the coordinator checkout, integrate one branch:

```powershell
git merge feature/calculations
```

Review it and run its relevant checks before integrating another branch. Then run the combined app journey. Do not mark the whole feature done just because each worker passed its own checks.

After verifying integration and clean worker state, remove the finished folder with `git worktree remove <path>`. Do not force removal to bypass uncommitted changes. Future tasks should start from the latest verified shared version.

## Your part at a milestone

The agent should tell you exactly what to open or run, what you should see, and what feedback helps. Example: “Try answering image 1, reveal it, move to image 2, and go back. Your first answer should remain visible.”

Tell the agent what you observed. It diagnoses and fixes failures. You decide user-facing trade-offs; you do not need to debug every implementation detail yourself.
