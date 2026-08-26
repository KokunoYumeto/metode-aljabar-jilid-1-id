[CmdletBinding()]
param(
    [string]$OutputDirectory = "build/unit-032-replay"
)

$ErrorActionPreference = "Stop"

$laneRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$sourceRoot = Join-Path $laneRoot "repo/source"
$candidate = Join-Path $laneRoot "build/unit-032-candidate/chapter4-free-groups-id.tex"
$expectedCandidateLineRecords = 280
$expectedCandidateBytes = 27910
$expectedCandidateSha256 = "28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc"

$candidateItem = Get-Item -LiteralPath $candidate
$candidateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $candidate).Hash.ToLowerInvariant()
$utf8Strict = [System.Text.UTF8Encoding]::new($false, $true)
$candidateBytes = [System.IO.File]::ReadAllBytes($candidate)
$candidateText = $utf8Strict.GetString($candidateBytes)
if ($candidateText.Contains("`r")) {
    throw "Unit 032 candidate must use LF-only line endings"
}
if (-not $candidateText.EndsWith("`n") -or $candidateText.EndsWith("`n`n")) {
    throw "Unit 032 candidate must end in exactly one LF"
}
$candidateLineRecords = ([regex]::Matches($candidateText, "`n")).Count
if (
    $candidateLineRecords -ne $expectedCandidateLineRecords -or
    $candidateItem.Length -ne $expectedCandidateBytes -or
    $candidateHash -ne $expectedCandidateSha256
) {
    throw "Unit 032 candidate identity mismatch: records=$candidateLineRecords bytes=$($candidateItem.Length) sha256=$candidateHash"
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

$jobName = "unit-032-bab-4-grup-bebas"
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
[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH", "1787702400", "Process")
[Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE", "1", "Process")

Push-Location $sourceRoot
try {
    Invoke-Checked "xelatex" $xelatexArguments
    Invoke-Checked "biber" @("--input-directory", $outputRoot, "--output-directory", $outputRoot, $jobName)

    Push-Location $outputRoot
    try {
        Invoke-Checked "makeindex" @("$jobName.idx")
        $symbolIndex = Join-Path $outputRoot "sym1.idx"
        if (
            (Test-Path -LiteralPath $symbolIndex) -and
            (Select-String -LiteralPath $symbolIndex -Pattern '^\\indexentry' -Quiet)
        ) {
            Invoke-Checked "makeindex" @("sym1.idx")
        }
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
$pdfHash = Get-FileHash -Algorithm SHA256 -LiteralPath $pdf.FullName
$log = Get-Item -LiteralPath (Join-Path $outputRoot "$jobName.log")
$logHash = Get-FileHash -Algorithm SHA256 -LiteralPath $log.FullName

[pscustomobject]@{
    path = $pdf.FullName
    bytes = $pdf.Length
    sha256 = $pdfHash.Hash.ToLowerInvariant()
    raw_log_path = $log.FullName
    raw_log_bytes = $log.Length
    raw_log_sha256 = $logHash.Hash.ToLowerInvariant()
    candidate_path = $candidateItem.FullName
    candidate_line_records = $candidateLineRecords
    candidate_bytes = $candidateItem.Length
    candidate_sha256 = $candidateHash
}
