[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("assets", "grid", "phenology", "era_daily", "era_baseline", "spei", "gleam_daily", "gleam_baseline", "events", "aggregate", "export", "validate", "all")]
    [string]$Stage,
    [string]$RunId,
    [switch]$Resume,
    [int]$PilotCells,
    [string]$Years,
    [ValidateSet("pilot", "full")]
    [string]$HashMode,
    [string]$PythonExe = ".\.venv-climate\Scripts\python.exe",
    [string]$Config = ".\data_build\config\climate_stress_panel_v1.yaml",
    [string]$ClimateStressManualPath,
    [string]$ProjectDataRoot,
    [string]$Era5Root,
    [string]$DailyTempRoot,
    [string]$GleamRoot,
    [string]$ChmSpeiRoot,
    [string]$PhenologyRoot,
    [string]$ClimateStressOutputRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$environmentBindings = @(
    @{ Name = "CLIMATE_STRESS_MANUAL_PATH"; Value = $ClimateStressManualPath },
    @{ Name = "PROJECT_DATA_ROOT"; Value = $ProjectDataRoot },
    @{ Name = "ERA5_ROOT"; Value = $Era5Root },
    @{ Name = "DAILY_TEMP_ROOT"; Value = $DailyTempRoot },
    @{ Name = "GLEAM_ROOT"; Value = $GleamRoot },
    @{ Name = "CHM_SPEI_ROOT"; Value = $ChmSpeiRoot },
    @{ Name = "PHENOLOGY_ROOT"; Value = $PhenologyRoot },
    @{ Name = "CLIMATE_STRESS_OUTPUT_ROOT"; Value = $ClimateStressOutputRoot }
)

foreach ($binding in $environmentBindings) {
    if (-not [string]::IsNullOrWhiteSpace([string]$binding.Value)) {
        [Environment]::SetEnvironmentVariable(
            [string]$binding.Name,
            [string]$binding.Value,
            [EnvironmentVariableTarget]::Process
        )
    }
}

$missing = @(
    foreach ($binding in $environmentBindings) {
        $value = [Environment]::GetEnvironmentVariable(
            [string]$binding.Name,
            [EnvironmentVariableTarget]::Process
        )
        if ([string]::IsNullOrWhiteSpace($value)) {
            [string]$binding.Name
        }
    }
)
if ($missing.Count -gt 0) {
    throw "Missing required session environment variables: $($missing -join ', ')"
}

$arguments = @(
    ".\data_build\scripts\python\build_climate_stress_panel.py",
    "--config", $Config,
    "--stage", $Stage
)
if (-not [string]::IsNullOrWhiteSpace($RunId)) {
    $arguments += @("--run-id", $RunId)
}
if ($Resume) {
    $arguments += "--resume"
}
if ($PilotCells -gt 0) {
    $arguments += @("--pilot-cells", [string]$PilotCells)
}
if (-not [string]::IsNullOrWhiteSpace($Years)) {
    $arguments += @("--years", $Years)
}
if (-not [string]::IsNullOrWhiteSpace($HashMode)) {
    $arguments += @("--hash-mode", $HashMode)
}

& $PythonExe @arguments
exit $LASTEXITCODE
