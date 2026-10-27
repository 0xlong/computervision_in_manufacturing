# Repository contents and upload boundary

Prepared 28 October 2026 for the requested private GitHub repository.
Repository privacy must be verified before uploading; private source storage is
separate from publishing a website or making the repository public.

## Included

| Files | Purpose |
| --- | --- |
| `web/src/`, `web/index.html` | The website and browser calculations. |
| `web/public/evidence/` | The versioned saved results, frozen model settings, 115 display pictures, 93 outlines and original dataset notices required by the local demo. |
| `pipeline/`, `configs/`, `schemas/`, `scripts/` | Repeatable preparation, evaluation, validation and setup. No local credentials are included. |
| `tests/`, `web/tests/`, source unit tests | Software checks and explicitly labelled invented test examples. |
| Package manifests, lockfiles and runtime/configuration files | Recreate the selected software environment. |
| `README.md`, `docs/`, `AGENTS.md` | Visitor overview, technical/evidence records and project working instructions. |
| Shared `.vscode/tasks.json` and `extensions.json` | Optional repeatable editor tasks and extension suggestions. |

The relocated specification in `docs/` and user stories must be tracked together
with the references that use them. Existing documentation and workspace-check
changes were reviewed as part of preparing this first remote snapshot.

## Local only

`.gitignore` excludes credential/configuration files, `done/`, raw `data/`,
`artifacts/`, downloaded models/checkpoints, dependencies, local Node/Python tools,
caches, screenshots/test reports, build output, temporary test folders and
archives. Shared source fixtures and the curated demo evidence are intentional
exceptions to excluding generated or image data.

Do not upload raw provider journals, account-limit screenshots, private prompts,
API keys or personal editor state. The saved public-facing configuration files
are intentional evidence inputs, not local account configuration.

The audit checks tracked history as well as the proposed working files for
forbidden paths, large objects and recognizable credential patterns. It reports
file names/counts, never secret values. Pattern checks cannot prove the absence
of every possible secret. Ignoring a path does not remove it from past commits.

## Data and publication

Retain the included dataset attribution and licence with display assets. Do not
replace them with an unrestricted blanket repository licence. The project keeps
its recorded source limitations. A private backup does not claim public
publication clearance, commercial-use permission, industrial validation or a
hosted release.
