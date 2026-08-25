[CmdletBinding()]
param(
    [string]$OutputDirectory = "build/unit-029-replay"
)

$ErrorActionPreference = "Stop"

$laneRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$sourceRoot = Join-Path $laneRoot "repo/source"
$target = Join-Path $sourceRoot "chapter4.tex"
$expectedTargetLineRecords = 1896
$expectedTargetBytes = 170663
$expectedTargetSha256 = "8cbd766360a3c7cd214876e297c45de3b8938daa9a3623192efdf1d6ebc766fc"
$spanStart = 665
$spanEnd = 793
$expectedSpanLineRecords = 129
$expectedSpanBytes = 10028
$expectedSpanSha256 = "234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d"

$targetItem = Get-Item -LiteralPath $target
$targetHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash.ToLowerInvariant()
$utf8Strict = [System.Text.UTF8Encoding]::new($false, $true)
$targetBytes = [System.IO.File]::ReadAllBytes($target)
$targetText = $utf8Strict.GetString($targetBytes)
if ($targetText.Contains("`r")) {
    throw "Unit 029 canonical target must use LF-only line endings"
}
$targetLineRecords = ([regex]::Matches($targetText, "`n")).Count
if ($targetLineRecords -ne $expectedTargetLineRecords -or $targetItem.Length -ne $expectedTargetBytes -or $targetHash -ne $expectedTargetSha256) {
    throw "Unit 029 canonical target identity mismatch: records=$targetLineRecords bytes=$($targetItem.Length) sha256=$targetHash"
}
$targetLines = $targetText.Split("`n")
$spanLines = $targetLines[($spanStart - 1)..($spanEnd - 1)]
$spanText = [string]::Join("`n", $spanLines) + "`n"
$spanBytes = [System.Text.Encoding]::UTF8.GetBytes($spanText)
$spanHasher = [System.Security.Cryptography.SHA256]::Create()
try {
    $spanHash = [System.BitConverter]::ToString($spanHasher.ComputeHash($spanBytes)).Replace("-", "").ToLowerInvariant()
}
finally {
    $spanHasher.Dispose()
}
if ($spanLines.Count -ne $expectedSpanLineRecords -or $spanBytes.Length -ne $expectedSpanBytes -or $spanHash -ne $expectedSpanSha256) {
    throw "Unit 029 canonical span identity mismatch: records=$($spanLines.Count) bytes=$($spanBytes.Length) sha256=$spanHash"
}

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

$jobName = "unit-029-bab-4-teorema-sylow"
$driverName = "$jobName.tex"
$xelatexArguments = @(
    "-no-shell-escape",
    "-interaction=nonstopmode",
    "-halt-on-error",
    "-file-line-error",
    "-jobname=$jobName",
    "-output-directory=$outputRoot",
    $driverName
)

$previousSourceDateEpoch = [Environment]::GetEnvironmentVariable("SOURCE_DATE_EPOCH", "Process")
$previousForceSourceDate = [Environment]::GetEnvironmentVariable("FORCE_SOURCE_DATE", "Process")
[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH", "1787616000", "Process")
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
    canonical_target_bytes = $targetItem.Length
    canonical_target_sha256 = $targetHash
    canonical_span_lines = "$spanStart-$spanEnd"
    canonical_span_line_records = $spanLines.Count
    canonical_span_bytes = $spanBytes.Length
    canonical_span_sha256 = $spanHash
}
