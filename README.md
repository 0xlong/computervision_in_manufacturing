# AI Inspection Pilot Lab

A public-data inspection game and model-comparison lab. We are building it with coding agents while learning practical software engineering.

**Current state:** the specification and learning workspace exist. There is no runnable web application, trained model, or evaluated API integration yet. See [current progress](docs/PROGRESS.md).

## Start here in VS Code

1. Open this project folder in VS Code: **File → Open Folder**.
2. Open this README and select **Open Preview** to read it comfortably.
3. Open the Codex sidebar. If hidden, open the Command Palette (`Ctrl+Shift+P`) and search **Codex: Open Codex Sidebar**. Sign in yourself if prompted; never paste credentials into chat.
4. Open **Terminal → New Terminal**. This is a PowerShell terminal: a place to run commands and see their results.
5. In the project root, run:

   ```powershell
   python scripts/check_environment.py
   ```

   It checks installed tools and required workspace files without installing anything, inspecting credentials, or making model calls. Expect `PASS` for the workspace checks. Version notes are information, not proof that future application packages are compatible.

6. In Codex, use this starting message:

   > Read AGENTS.md and docs/PROGRESS.md. Continue the next small task. Explain it simply: what you will do, why, my role, how we will check it, and what happens next. Do routine work autonomously and keep the progress file current. Before installing app dependencies, verify the runtime versions and show the smallest setup needed.

**Your role:** understand the next outcome, try working milestones, and make product choices. **Agent's role:** inspect, implement, test, diagnose, document, and explain routine engineering work. You do not need to approve each file edit.

## Everyday controls

| What you want | What to do |
| --- | --- |
| See the current task | Open `docs/PROGRESS.md`. |
| Check the workspace | Run `python scripts/check_environment.py`, or **Terminal → Run Task → Learning: check environment**. |
| See files changed since the last checkpoint | Open VS Code **Source Control**, or run `git status --short`. |
| Understand a change | Click a changed file in Source Control; ask Codex to explain the diff in plain English. |
| Inspect recent saved checkpoints | Run `git log --oneline -5`. |
| Slow down the teaching | Tell Codex: “Give me one action at a time and wait for my result.” |
| Continue with fewer interruptions | Tell Codex: “Continue routine work; explain each milestone and ask only for consequential decisions or missing access.” |

Do not run `npm install` yet: there is no package manifest. Web/ML dependencies and their checks will be added during the next foundation steps.

## Extension or terminal?

Use the **Codex extension** by default: code, changes, explanations, and terminals stay visible in one place. The **Codex CLI** is an alternative interface, not a required second system.

To try the CLI, open a new terminal **in the project folder** and run `codex` (or `codex.cmd` if PowerShell blocks the `.ps1` launcher). Give it the same starting message above. Choose the directory/permission scope deliberately; do not disable safeguards to bypass a setup problem.

Use one editing agent in a checkout at a time. If the extension is editing the project, do not start another editor-agent in that same folder. Read-only review can be separate.

**No tmux is needed.** Use named VS Code terminals such as `checks`, `web-server` (later), and `worker-ui` (later). A terminal keeps a command session visible; a Git worktree isolates a worker's files. They solve different problems. Closing a terminal may stop its process; this setup is not an unattended job scheduler.

## How we will build

```text
Specification → one small task → build → check → fix
                                      ↑         |
                                      +---------+
                    → review → save checkpoint → next task
```

Parallel agents come after shared setup and data contracts are ready. Read the short [workflow and worktree guide](docs/WORKFLOW.md) when we reach that point.

## Project map

| File | Purpose |
| --- | --- |
| `AI_Inspection_Pilot_Lab_SPEC.md` | What the application must do and how completion is verified. |
| `AGENTS.md` | How agents should work and teach in this repository. |
| `docs/PROGRESS.md` | Current step, evidence, next task, and blockers. |
| `docs/WORKFLOW.md` | Simple task loop, parallel work example, and handoff procedure. |
| `scripts/check_environment.py` | Repeatable, read-only workspace check. |

## Official Codex references

- [VS Code / IDE extension](https://learn.chatgpt.com/docs/codex/ide)
- [Codex CLI](https://learn.chatgpt.com/docs/cli)
- [Project instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

Codex account usage and the application's Gemini/OpenAI API entitlement are separate concerns. Having Codex installed does not verify free application API access.
