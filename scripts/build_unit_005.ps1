[CmdletBinding()]
param(
    [string]$OutputDirectory = "build/unit-005-replay"
)

$ErrorActionPreference = "Stop"

$laneRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$sourceRoot = Join-Path $laneRoot "repo/source"

if ([System.IO.Path]::IsPathRooted($OutputDirectory)) {
    $outputRoot = [System.IO.Path]::GetFullPath($OutputDirectory)
}
else {
    $outputRoot = [System.IO.Path]::GetFullPath((Join-Path $laneRoot $OutputDirectory))
}

if (-not $outputRoot.StartsWith($laneRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Output directory must remain inside the edition root: $laneRoot"
}

if (Test-Path -LiteralPath $outputRoot) {
    $existing = @(Get-ChildItem -LiteralPath $outputRoot -Force)
    if ($existing.Count -ne 0) {
        throw "Output directory must be absent or empty for a clean build: $outputRoot"
    }
}
else {
    New-Item -ItemType Directory -Path $outputRoot | Out-Null
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Program,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Program exited with code $LASTEXITCODE"
    }
}

$jobName = "unit-005-bab-1-kardinal"
$xelatexArguments = @(
    "-no-shell-escape",
    "-interaction=nonstopmode",
    "-halt-on-error",
    "-file-line-error",
    "-output-directory=$outputRoot",
    "$jobName.tex"
)

$previousSourceDateEpoch = [Environment]::GetEnvironmentVariable("SOURCE_DATE_EPOCH", "Process")
$previousForceSourceDate = [Environment]::GetEnvironmentVariable("FORCE_SOURCE_DATE", "Process")
[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH", "1787356800", "Process")
[Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE", "1", "Process")

Push-Location $sourceRoot
try {
    Invoke-Checked "xelatex" $xelatexArguments
    Invoke-Checked "biber" @("--input-directory", $outputRoot, "--output-directory", $outputRoot, $jobName)

    Push-Location $outputRoot
    try {
        Invoke-Checked "makeindex" @("$jobName.idx")
        Invoke-Checked "makeindex" @("sym1.idx")
    }
    finally {
        Pop-Location
    }

    Invoke-Checked "xelatex" $xelatexArguments
    Invoke-Checked "xelatex" $xelatexArguments
    Invoke-Checked "xelatex" $xelatexArguments
}
finally {
    Pop-Location
    [Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH", $previousSourceDateEpoch, "Process")
    [Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE", $previousForceSourceDate, "Process")
}

$pdf = Get-Item -LiteralPath (Join-Path $outputRoot "$jobName.pdf")
$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $pdf.FullName

[pscustomobject]@{
    path = $pdf.FullName
    bytes = $pdf.Length
    sha256 = $hash.Hash.ToLowerInvariant()
}
