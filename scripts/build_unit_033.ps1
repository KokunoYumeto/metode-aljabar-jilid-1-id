[CmdletBinding()]
param(
    [string]$OutputDirectory = "build/unit-033-replay"
)

$ErrorActionPreference = "Stop"

$laneRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$sourceRoot = Join-Path $laneRoot "repo/source"
$authority = Join-Path $laneRoot "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
$candidate = Join-Path $laneRoot "build/unit-033-candidate/chapter4-symmetric-groups-id.tex"
$target = Join-Path $sourceRoot "chapter4.tex"

$expectedAuthorityBytes = 154744
$expectedAuthoritySha256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
$sourceStart = 1389
$sourceEnd = 1608
$expectedSourceSliceLineRecords = 220
$expectedSourceSliceBytes = 19076
$expectedSourceSliceSha256 = "c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a"

$expectedCandidateLineRecords = 219
$expectedCandidateBytes = 23099
$expectedCandidateSha256 = "1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76"

# This is the exact anticipated prefix + candidate + authority-suffix identity.
# Recompute it after canonical integration and change these adjacent values only
# if the independently verified integration differs.
$expectedTargetLineRecords = 1893
$expectedTargetBytes = 185920
$expectedTargetSha256 = "a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde"
$targetStart = 1384
$targetEnd = 1602
$boundaryBlankLine = 1603
$nextSentinelLine = 1604

$utf8Strict = [System.Text.UTF8Encoding]::new($false, $true)

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][byte[]]$Bytes)

    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try {
        return [System.BitConverter]::ToString($hasher.ComputeHash($Bytes)).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $hasher.Dispose()
    }
}

function Read-StrictUtf8 {
    param([Parameter(Mandatory = $true)][string]$Path)

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xef -and $bytes[1] -eq 0xbb -and $bytes[2] -eq 0xbf) {
        throw "UTF-8 BOM is forbidden: $Path"
    }
    if ($bytes -contains 13) {
        throw "CR/CRLF line endings are forbidden: $Path"
    }
    [pscustomobject]@{
        Bytes = $bytes
        Text = $utf8Strict.GetString($bytes)
        Sha256 = Get-Sha256 -Bytes $bytes
    }
}

$authorityRecord = Read-StrictUtf8 -Path $authority
if ($authorityRecord.Bytes.Length -ne $expectedAuthorityBytes -or $authorityRecord.Sha256 -ne $expectedAuthoritySha256) {
    throw "Unit 033 authority identity mismatch: bytes=$($authorityRecord.Bytes.Length) sha256=$($authorityRecord.Sha256)"
}
$authorityLines = $authorityRecord.Text.Split("`n")
$sourceSliceLines = $authorityLines[($sourceStart - 1)..($sourceEnd - 1)]
$sourceSliceText = [string]::Join("`n", $sourceSliceLines) + "`n"
$sourceSliceBytes = $utf8Strict.GetBytes($sourceSliceText)
$sourceSliceHash = Get-Sha256 -Bytes $sourceSliceBytes
if (
    $sourceSliceLines.Count -ne $expectedSourceSliceLineRecords -or
    $sourceSliceBytes.Length -ne $expectedSourceSliceBytes -or
    $sourceSliceHash -ne $expectedSourceSliceSha256
) {
    throw "Unit 033 authority slice identity mismatch: records=$($sourceSliceLines.Count) bytes=$($sourceSliceBytes.Length) sha256=$sourceSliceHash"
}
$nextSectionSentinel = $authorityLines[$sourceEnd]
if (
    $sourceSliceLines[-1] -ne "" -or
    -not $nextSectionSentinel.StartsWith('\section{') -or
    -not $nextSectionSentinel.EndsWith('\label{sec:group-limit}')
) {
    throw "Unit 033 authority boundary or Section 4.10 sentinel drifted"
}

$candidateRecord = Read-StrictUtf8 -Path $candidate
if (-not $candidateRecord.Text.EndsWith("`n") -or $candidateRecord.Text.EndsWith("`n`n")) {
    throw "Unit 033 candidate must end in exactly one LF"
}
$candidateLineRecords = ([regex]::Matches($candidateRecord.Text, "`n")).Count
if (
    $candidateLineRecords -ne $expectedCandidateLineRecords -or
    $candidateRecord.Bytes.Length -ne $expectedCandidateBytes -or
    $candidateRecord.Sha256 -ne $expectedCandidateSha256
) {
    throw "Unit 033 candidate identity mismatch: records=$candidateLineRecords bytes=$($candidateRecord.Bytes.Length) sha256=$($candidateRecord.Sha256)"
}

$targetRecord = Read-StrictUtf8 -Path $target
if (-not $targetRecord.Text.EndsWith("`n") -or $targetRecord.Text.EndsWith("`n`n")) {
    throw "Unit 033 canonical target must end in exactly one LF"
}
$targetLineRecords = ([regex]::Matches($targetRecord.Text, "`n")).Count
if (
    $targetLineRecords -ne $expectedTargetLineRecords -or
    $targetRecord.Bytes.Length -ne $expectedTargetBytes -or
    $targetRecord.Sha256 -ne $expectedTargetSha256
) {
    throw "Unit 033 canonical target identity mismatch: records=$targetLineRecords bytes=$($targetRecord.Bytes.Length) sha256=$($targetRecord.Sha256)"
}
$targetLines = $targetRecord.Text.Split("`n")
$targetSpanText = [string]::Join("`n", $targetLines[($targetStart - 1)..($targetEnd - 1)]) + "`n"
$targetSpanBytes = $utf8Strict.GetBytes($targetSpanText)
$targetSpanHash = Get-Sha256 -Bytes $targetSpanBytes
if ($targetSpanBytes.Length -ne $candidateRecord.Bytes.Length -or $targetSpanHash -ne $candidateRecord.Sha256) {
    throw "Unit 033 canonical target span differs byte-for-byte from the admitted candidate"
}
if ($targetLines[$boundaryBlankLine - 1] -ne "") {
    throw "Unit 033 canonical target line 1603 must preserve the blank section boundary"
}
if ($targetLines[$nextSentinelLine - 1] -ne $nextSectionSentinel) {
    throw "Unit 033 canonical target Section 4.10 sentinel drifted"
}

$jobName = "unit-033-bab-4-grup-simetris"
$driverName = "$jobName.tex"
$driver = Join-Path $sourceRoot $driverName
if (-not (Test-Path -LiteralPath $driver -PathType Leaf)) {
    throw "Unit 033 reader driver is not yet present: $driver"
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
        if ((Test-Path -LiteralPath $symbolIndex) -and (Select-String -LiteralPath $symbolIndex -Pattern '^[\\]indexentry' -Quiet)) {
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
$pdfHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $pdf.FullName).Hash.ToLowerInvariant()
$log = Get-Item -LiteralPath (Join-Path $outputRoot "$jobName.log")
$logHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $log.FullName).Hash.ToLowerInvariant()

[pscustomobject]@{
    path = $pdf.FullName
    bytes = $pdf.Length
    sha256 = $pdfHash
    raw_log_path = $log.FullName
    raw_log_bytes = $log.Length
    raw_log_sha256 = $logHash
    authority_slice_lines = "$sourceStart-$sourceEnd"
    authority_slice_bytes = $sourceSliceBytes.Length
    authority_slice_sha256 = $sourceSliceHash
    candidate_path = $candidate
    candidate_line_records = $candidateLineRecords
    candidate_bytes = $candidateRecord.Bytes.Length
    candidate_sha256 = $candidateRecord.Sha256
    canonical_target_bytes = $targetRecord.Bytes.Length
    canonical_target_sha256 = $targetRecord.Sha256
    canonical_span_lines = "$targetStart-$targetEnd"
}
