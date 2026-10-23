# Working with agents: the practical guide

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

## First parallel round (later, not running now)

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
