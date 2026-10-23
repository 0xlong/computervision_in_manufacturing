# Offline pipeline (not implemented yet)

Use the root `.venv` with Python 3.13.x. Setup creates it with Python's built-in
`venv` tool; no activation or global package installation is needed.

No Python application dependencies are installed in EN-01. EN-02 will introduce
Pydantic and contract tests when artifact validation is implemented. PyTorch and
anomalib will be pinned and installed for the first measured specialist experiment,
after selecting its CPU configuration. Provider SDKs wait until approved free access
is verified. See [development setup](../docs/DEVELOPMENT.md).

Datasets, checkpoints, generated results, caches, and credentials stay outside
source control. Nothing in this folder currently fits or runs a model.
