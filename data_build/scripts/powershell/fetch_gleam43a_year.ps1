[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet(2020)]
    [int]$Year = 2020,

    [Parameter()]
    [ValidateSet("download", "validate")]
    [string]$Mode = "download",

    [Parameter()]
    [string]$PythonExe,

    [Parameter()]
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $repoRoot = [System.IO.Path]::GetFullPath(
        (Join-Path $PSScriptRoot "..\..\..")
    )
    $PythonExe = Join-Path $repoRoot ".venv-climate\Scripts\python.exe"
}
if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw "Python executable not found: $PythonExe"
}

$fetcher = Join-Path $PSScriptRoot "..\python\fetch_gleam43a_year.py"
$fetcherArgs = @(
    "-B",
    $fetcher,
    "--year",
    [string]$Year,
    "--mode",
    $Mode
)
if ($DryRun) {
    $fetcherArgs += "--dry-run"
}
& $PythonExe @fetcherArgs
if ($LASTEXITCODE -ne 0) {
    throw "GLEAM safe fetch/validation failed for $Year."
}
