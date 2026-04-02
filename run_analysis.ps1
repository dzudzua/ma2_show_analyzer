param(
    [string]$InputDir = "exports",
    [string]$OutputDir = "out",
    [string]$Glob = "*.xml",
    [switch]$Recursive
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$resolvedInput = Join-Path $projectRoot $InputDir
$resolvedOutput = Join-Path $projectRoot $OutputDir

if (-not (Test-Path -LiteralPath $resolvedInput)) {
    throw "Input folder not found: $resolvedInput"
}

$args = @(
    (Join-Path $projectRoot "run_analysis.py"),
    "analyze",
    "--input", $resolvedInput,
    "--output", $resolvedOutput,
    "--glob", $Glob
)

if ($Recursive) {
    $args += "--recursive"
}

Write-Host "Running analysis..."
Write-Host "Input:  $resolvedInput"
Write-Host "Output: $resolvedOutput"

python @args

if ($LASTEXITCODE -ne 0) {
    throw "Analysis failed with exit code $LASTEXITCODE"
}

Write-Host "Analysis complete."
Write-Host "Open: $resolvedOutput"
