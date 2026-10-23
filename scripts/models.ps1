param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('install', 'check')]
    [string]$Action
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv-models/Scripts/python.exe'
$previousTemp = $env:TEMP
$previousTmp = $env:TMP
Push-Location $projectRoot
try {
    New-Item -ItemType Directory -Force -Path '.cache/tmp' | Out-Null
    $env:TEMP = Join-Path $projectRoot '.cache/tmp'
    $env:TMP = $env:TEMP
    if ($Action -eq 'install') {
        if (-not (Test-Path -LiteralPath $pythonPath)) {
            python -m venv .venv-models --without-pip
            if ($LASTEXITCODE -ne 0) { throw 'Cannot create model environment.' }
        }
        & $pythonPath -c "import sys; assert sys.version_info[:2] == (3, 13) and sys.platform == 'win32' and sys.maxsize > 2**32 and sys.prefix != sys.base_prefix"
        if ($LASTEXITCODE -ne 0) { throw 'Model lock requires isolated Windows x64 Python 3.13.' }
        & $pythonPath -m ensurepip --upgrade
        if ($LASTEXITCODE -ne 0) { throw 'Cannot bootstrap model installer.' }
        & $pythonPath -m pip install --index-url https://pypi.org/simple --require-hashes --only-binary=:all: --cache-dir .cache/pip -r pipeline/requirements-models-build.lock
        if ($LASTEXITCODE -ne 0) { throw 'Cannot install pinned source-build tool.' }
        & $pythonPath -m pip install --index-url https://pypi.org/simple --require-hashes --no-deps --no-build-isolation --only-binary=:all: --no-binary=freia --cache-dir .cache/pip -r pipeline/requirements-models.lock
        if ($LASTEXITCODE -ne 0) { throw 'Cannot install locked CPU packages.' }
    }
    if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Run scripts/models.ps1 install first.' }
    & $pythonPath -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Model dependencies are inconsistent.' }
    & $pythonPath -c "import torch, torchvision; from anomalib.models.image.padim.torch_model import PadimModel; from anomalib.models.image.patchcore.torch_model import PatchcoreModel; print('PASS model imports; not a fitting/inference check. torch=' + torch.__version__)"
    $result = $LASTEXITCODE
} finally {
    $env:TEMP = $previousTemp
    $env:TMP = $previousTmp
    Pop-Location
}
exit $result
