"""Read-only learning-workspace check. No installs, network, or secret access."""

from pathlib import Path
import shutil
import subprocess
import sys


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = 0
    print(f"Workspace: {root}")
    print("This checks the workspace, not app/model readiness or Codex sign-in.\n")

    required_files = (
        "AGENTS.md", "README.md", "docs/AI_Inspection_Pilot_Lab_SPEC.md",
        "docs/PROGRESS.md", "docs/WORKFLOW.md", "docs/USER_STORIES.md", ".gitignore",
        ".vscode/tasks.json", ".vscode/extensions.json",
    )
    for name in required_files:
        exists = (root / name).is_file()
        print(f"{'PASS' if exists else 'FAIL'} file: {name}")
        failures += not exists

    for label, candidates, required in (
        ("Git", ("git",), True),
        ("Node", ("node",), True),
        ("npm", ("npm.cmd", "npm"), True),
        ("VS Code command", ("code.cmd", "code"), False),
        ("Codex CLI (optional)", ("codex.cmd", "codex"), False),
    ):
        found = next((shutil.which(name) for name in candidates if shutil.which(name)), None)
        level = "PASS" if found else ("FAIL" if required else "NOTE")
        print(f"{level} tool: {label}{' available' if found else ' not found on PATH'}")
        if required and not found:
            failures += 1

    print(f"PASS Python: {sys.version.split()[0]}")
    git = shutil.which("git")
    if git:
        try:
            result = subprocess.run(
                [git, "rev-parse", "--show-toplevel"], cwd=root,
                text=True, capture_output=True, timeout=10, check=False,
            )
            valid = result.returncode == 0 and Path(result.stdout.strip()).resolve() == root
            print(f"{'PASS' if valid else 'FAIL'} Git repository belongs to this workspace")
            failures += not valid
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"FAIL Git check: {error}")
            failures += 1

    node = shutil.which("node")
    if node:
        try:
            result = subprocess.run(
                [node, "--version"], text=True, capture_output=True,
                timeout=10, check=False,
            )
            if result.returncode == 0:
                print(f"NOTE Node {result.stdout.strip()}: check package compatibility before web setup.")
            else:
                print("FAIL Node was found but did not run successfully")
                failures += 1
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"FAIL Node check: {error}")
            failures += 1

    print("NOTE Python/ML compatibility and free API access are checked during feasibility.")
    print(f"\n{'PASS workspace checks' if not failures else f'FAIL {failures} workspace check(s)'}")
    print("Next: open README.md and ask Codex to continue docs/PROGRESS.md.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
