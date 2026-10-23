# Progress and next action

Updated: 23 October 2026. This file records project state, not promised implementation success.

## Current milestone: learning workspace

- [x] Write the application development specification.
- [x] Initialize local Git on `main`.
- [x] Add agent teaching rules, beginner entry guide, and worktree explanation.
- [x] Add a repeatable environment check and VS Code tasks.
- [x] Verify the workspace check, VS Code JSON, and documentation links/code fences.

Verification: `python scripts/check_environment.py` passed. Both VS Code JSON files parse, local documentation links resolve, and code fences are balanced. App/model execution and interactive Codex sign-in remain unverified. The setup is ready to save as the first local Git checkpoint; Git history is authoritative for whether that commit exists.

## Observed tools

Git 2.51.2; Node 20.17.0; npm 10.8.3; Python 3.13.2; VS Code 1.142.0; Codex CLI 0.161.0. The VS Code extension `openai.chatgpt` is installed. These are setup-time observations, not pinned application requirements.

The restricted setup environment reported access warnings from Codex's temporary-directory handling and VS Code's log directory while printing versions. Installation was detected; interactive authentication, extension operation, and browser UI have not been verified by this setup.

## Next small task: foundation feasibility

**Goal:** prove the selected tools/data can support one authentic inspection flow before building many screens.

**Agent does:** verify current frontend runtime requirements and Python/ML compatibility, propose/install the smallest project-scoped dependencies, establish data contracts, and prepare a small real-data/model experiment in the order defined by specification Gate 1. Record exact versions and measurements. Do not assume the observed Node/Python versions are suitable for all new packages.

**Your role:** open the folder and Codex, optionally run the environment check, and ask the agent to continue. Configure required provider access yourself through an approved mechanism when genuinely needed; never paste keys into chat.

**Done when:** a documented reproducible setup and validated authentic sample evidence satisfy Gate 1. A blank webpage or test fixture does not prove model feasibility.

## Later milestones

- [ ] Gate 1: feasibility, compatible pinned runtimes/dependencies, schemas, real sample evidence.
- [ ] Gate 2: one connected fastener inspection-to-export journey.
- [ ] Gate 3: complete evaluated comparison and surface track.
- [ ] Gate 4: verified release package and deployment instructions.

No workers, paid calls, public repository, remote deployment, app dependencies, or model runs have been started by the workspace setup. Parallel tasks begin after stable contracts and a shared committed foundation exist.

## Handoff convention

After each completed task, record its outcome, relevant checks/results, known limitations, and next action here. Keep this file short; Git records the detailed file history. A blocked check stays visible rather than being marked complete.
