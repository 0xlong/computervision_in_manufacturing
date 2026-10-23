param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('ci', 'dev', 'check', 'build', 'preview')]
    [string]$Action
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$nodeVersion = (Get-Content -LiteralPath (Join-Path $projectRoot '.node-version') -Raw).Trim()
$nodeFolder = Join-Path $projectRoot ".tools/node-v$nodeVersion-win-x64"
if (-not (Test-Path -LiteralPath (Join-Path $nodeFolder 'node.exe'))) {
    throw 'Project Node is missing. Run: powershell -NoProfile -File scripts/setup.ps1'
}

$previousPath = $env:PATH
Push-Location (Join-Path $projectRoot 'web')
try {
    # Only this process uses the local runtime; the machine PATH is unchanged.
    $env:PATH = "$nodeFolder;$previousPath"
    if ($Action -eq 'ci') {
        & (Join-Path $nodeFolder 'npm.cmd') ci --cache ../.cache/npm --offline=false --no-fund --fetch-retries=0
    } else {
        & (Join-Path $nodeFolder 'npm.cmd') run $Action
    }
    $result = $LASTEXITCODE
} finally {
    $env:PATH = $previousPath
    Pop-Location
}
exit $result
