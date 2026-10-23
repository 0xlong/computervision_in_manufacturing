param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$projectRoot = Split-Path -Parent $PSScriptRoot
$previousTemp = $env:TEMP
$previousTmp = $env:TMP
Push-Location $projectRoot
try {
    if (-not [Environment]::Is64BitOperatingSystem) {
        throw 'This setup supports Windows x64 only.'
    }
    & python -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 13) else 'Python 3.13.x is required.')"
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.13.x before continuing.' }

    New-Item -ItemType Directory -Force -Path '.cache/tmp' | Out-Null
    $env:TEMP = Join-Path $projectRoot '.cache/tmp'
    $env:TMP = $env:TEMP

    $nodeVersion = (Get-Content -LiteralPath '.node-version' -Raw).Trim()
    if ($nodeVersion -ne '24.22.1') { throw 'Update the verified Node checksum before changing .node-version.' }
    $archiveName = "node-v$nodeVersion-win-x64.zip"
    $nodeFolder = Join-Path $projectRoot ".tools/node-v$nodeVersion-win-x64"
    if (-not (Test-Path -LiteralPath (Join-Path $nodeFolder 'node.exe'))) {
        New-Item -ItemType Directory -Force -Path '.cache', '.tools' | Out-Null
        $archivePath = Join-Path $projectRoot ".cache/$archiveName"
        Write-Host "Downloading project-local Node $nodeVersion from nodejs.org..."
        Invoke-WebRequest -UseBasicParsing -Uri "https://nodejs.org/dist/v$nodeVersion/$archiveName" -OutFile $archivePath
        $expectedHash = 'd2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5'
        if ((Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) {
            throw 'Node archive checksum mismatch; nothing was extracted.'
        }
        Expand-Archive -LiteralPath $archivePath -DestinationPath '.tools' -Force
    }

    if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
        & python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Creating the project Python environment failed.' }
    }
    & ./.venv/Scripts/python.exe -c "import importlib.util, sys; raise SystemExit(0 if importlib.util.find_spec('pip') else 1)"
    if ($LASTEXITCODE -ne 0) {
        & ./.venv/Scripts/python.exe -m ensurepip --upgrade --default-pip
        if ($LASTEXITCODE -ne 0) { throw 'Initializing pip in the project Python environment failed.' }
    }
    & ./.venv/Scripts/python.exe -c "import sys; assert sys.version_info[:2] == (3, 13); assert sys.prefix != sys.base_prefix; print('PASS isolated Python ' + sys.version.split()[0])"
    if ($LASTEXITCODE -ne 0) { throw 'The existing .venv is not an isolated Python 3.13 environment.' }

    & "$PSScriptRoot/web.ps1" ci
    if ($LASTEXITCODE -ne 0) { throw 'Installing locked web dependencies failed.' }
    Write-Host 'Setup complete. Run: powershell -NoProfile -File scripts/web.ps1 build'
} finally {
    $env:TEMP = $previousTemp
    $env:TMP = $previousTmp
    Pop-Location
}
