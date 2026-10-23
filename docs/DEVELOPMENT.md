# Minimal development setup — EN-01

Verified on 23 October 2026, Windows x64. This is a runnable development page,
not an inspection journey or model-feasibility result. Gate 1 remains open.

## What is installed

| Tool | Observed / selected | Purpose |
| --- | --- | --- |
| Git | 2.51.2.windows.1 | Local version history |
| VS Code | 1.142.0; `openai.chatgpt` installed | Existing editor and Codex extension |
| System Node / npm | 20.17.0 / 10.8.3 | Existing tools; not used by the web scripts |
| Project Node / npm | 24.22.1 / 11.19.1 | Supported runtime and bundled package installer |
| Python | 3.13.2, Windows x64 | Existing interpreter; project `.venv` uses Python 3.13.x |
| React / React DOM | 19.3.1 / 19.3.1 | Render the development page |
| TypeScript | 7.0.2 | Check source types before building |
| Vite | 8.3.5 | Local server and static build |
| React type definitions | `@types/react` / `@types/react-dom` 19.3.0 | TypeScript's description of React APIs |

Only six direct web packages are needed. Vite handles TSX through its built-in
transform; no React plugin is required for this setup page. We can add development
conveniences when an actual feature needs them. No Python packages, browser-test
downloads, provider SDKs, containers, CI services, or new package managers are needed
for this increment.

A **lockfile**, `web/package-lock.json`, records exact dependency versions and
download integrity hashes, including packages required by the six direct packages.
Commit it whenever dependency changes are intentional. `npm ci` installs that
recorded tree rather than choosing new versions.

## Compatibility evidence

Official documentation and package metadata checked on 23 October 2026:

- [Vite getting started](https://vite.dev/guide/): requires Node 20.19+ or 22.12+;
  the selected Vite package declares `^20.19.0 || >=22.12.0`. Installed system
  Node 20.17.0 does not qualify.
- [Node release status](https://nodejs.org/en/about/previous-releases): Node 24 is
  LTS (long-term support); Node 20 is end of life. Use the pinned project runtime.
- [Node 24.22.1 checksums](https://nodejs.org/dist/v24.22.1/SHASUMS256.txt): the
  Windows x64 ZIP SHA-256 is
  `d2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5`.
  Setup verifies it before extraction.
- The official [npm registry](https://registry.npmjs.org/vite/8.3.5) supplied
  exact package versions and runtime requirements. The lockfile records resolved
  package URLs and integrity hashes; `web/.npmrc` rejects incompatible runtimes.
- [anomalib installation](https://github.com/open-edge-platform/anomalib#installation)
  and [anomalib 2.7.0 metadata](https://pypi.org/pypi/anomalib/2.7.0/json): Python
  `>=3.10`; CPU extra requires torch `>=2.10.0` and torchvision `>=0.25.0`.
- [PyTorch Windows guidance](https://pytorch.org/get-started/locally/) and official
  [torch 2.14.1](https://pypi.org/pypi/torch/2.14.1/json) /
  [torchvision 0.29.1](https://pypi.org/pypi/torchvision/0.29.1/json) metadata:
  both publish CPython 3.13 Windows x64 wheels. Torchvision requires torch
  `>=2.14.0`. This is a candidate combination, not an installed or tested ML lock.
- [Pydantic 2.14.1](https://pypi.org/pypi/pydantic/2.14.1/json) and
  [pytest 9.1.1](https://pypi.org/pypi/pytest/9.1.1/json) declare Python `>=3.10`.
  Add and lock them with the first contract implementation, not in advance.

Metadata compatibility does not prove that the complete ML dependency tree resolves,
imports, or fits this computer. That check belongs to the specialist feasibility
task, before training. No datasets, weights, or provider requests have been acquired.

## Local resources

Read-only inventory: Intel Core i7-6500U at 2.50 GHz, 2 physical cores / 4 logical
processors; 17,031,761,920 bytes RAM (about 15.86 GiB); about 33.1 GiB free on C:
before dependencies finished installing. GPUs reported: AMD Radeon R5 M330 and
Intel HD Graphics 520. No NVIDIA GPU was reported. Plan the first ML experiment
for CPU; GPU acceleration and model memory/performance are unverified.

The restricted command environment denied the first hardware query and network
downloads. Approved read-only hardware queries and package downloads succeeded.
Python's initial pip bootstrap could not write its temporary directory; setup now
uses `.cache/tmp` and repairs an incomplete pip bootstrap. The first type check
caught the CSS import declaration; Vite's standard client types resolved it.
VS Code printed access warnings for its log directory, but returned its version and
extension list. Interactive extension use/sign-in remains unverified.

## Reproduce on this Windows machine

Run these commands in a VS Code PowerShell terminal in
`C:\Users\Longin\Desktop\Projects\computervision_in_manufacturing`.
Prerequisites: Python 3.13.x on PATH, PowerShell, Git, and internet access for setup.

| Command | Purpose | Expected result |
| --- | --- | --- |
| `powershell -NoProfile -File scripts/setup.ps1` | Download checksum-verified Node into `.tools`, create isolated `.venv`, install the web lock | `Setup complete`; no global tool changes |
| `python scripts/check_environment.py` | Check the learning workspace | `PASS workspace checks`; this does not check the app or models |
| `powershell -NoProfile -File scripts/web.ps1 check` | Check TypeScript source | Exit 0, no type errors |
| `powershell -NoProfile -File scripts/web.ps1 build` | Type check and produce static assets | Build completes under `web/dist/` |
| `powershell -NoProfile -File scripts/web.ps1 dev` | Start local development | Server at `http://127.0.0.1:5174/`; Ctrl+C stops it |
| `powershell -NoProfile -File scripts/web.ps1 preview` | Serve the existing production build | Server at `http://127.0.0.1:4173/`; build first |
| `.\.venv\Scripts\python.exe --version` | Check the isolated Python runtime | `Python 3.13.x` |

Port 5173 was already occupied during setup, so this project uses 5174. The strict
port setting reports a conflict instead of silently serving at a different URL.

The web script selects the local Node for its process only and restores PATH
afterward. Running plain `node` in another terminal still uses the existing system
installation. `.tools`, `.venv`, `.cache`, `node_modules`, and `dist` are ignored by Git.
Setup can be rerun; `npm ci` replaces the generated dependency folder from the lock.
It does not recreate an existing Python environment or remove personal files.

Open localhost with VS Code's **Browser: Open Integrated Browser** command
(`workbench.action.browser.open`). Expect **AI Inspection Pilot Lab** and
**The React and TypeScript development page is running.**
This task verifies HTTP serving; visual rendering and interactive browser behavior
remain unverified until that browser action is performed.

There are no application behavior tests yet. Build/type checks verify the toolchain,
not inspection correctness. Add pytest for contracts, Vitest for browser-side logic,
and Playwright for the first meaningful connected journey when those tasks begin.

## Next increment

EN-02 starts artifact contracts and official dataset/licence discovery. Later EN-01
work will lock the Python packages actually used by that task and the specialist
experiment. Model configuration, checkpoints/licences, memory, provider eligibility,
and authentic evidence remain separate Gate 1 work.
