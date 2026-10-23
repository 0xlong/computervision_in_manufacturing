param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('install', 'test')]
    [string]$Action
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Project Python is missing. Run: powershell -NoProfile -File scripts/setup.ps1'
}

$previousTemp = $env:TEMP
$previousTmp = $env:TMP
Push-Location $projectRoot
try {
    New-Item -ItemType Directory -Force -Path '.cache/tmp' | Out-Null
    $env:TEMP = Join-Path $projectRoot '.cache/tmp'
    $env:TMP = $env:TEMP
    & $pythonPath -c "import sys; assert sys.version_info[:2] == (3, 13) and sys.platform == 'win32' and sys.maxsize > 2**32 and sys.prefix != sys.base_prefix, 'Contract lock requires isolated Windows x64 Python 3.13'"
    if ($LASTEXITCODE -ne 0) { throw 'Unsupported Python environment for the contract lock.' }
    if ($Action -eq 'install') {
        & $pythonPath -m pip install --index-url https://pypi.org/simple --only-binary=:all: --require-hashes --cache-dir .cache/pip --retries 0 --timeout 15 -r pipeline/requirements-contracts.lock
    } else {
        # Do not auto-load unrelated machine plugins or collect outside our tests.
        & $pythonPath -m pytest -o addopts='' -p no:cacheprovider --disable-plugin-autoload --basetemp .cache/pytest -q tests/pipeline
    }
    $result = $LASTEXITCODE
} finally {
    $env:TEMP = $previousTemp
    $env:TMP = $previousTmp
    Pop-Location
}
exit $result
