[CmdletBinding()]
param(
    [string]$OutputDirectory = "build/unit-034-replay"
)

$ErrorActionPreference = "Stop"

$laneRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$sourceRoot = Join-Path $laneRoot "repo/source"
$authority = Join-Path $laneRoot "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
$candidate = Join-Path $laneRoot "build/unit-034-candidate/chapter4-group-limits-completions-id.tex"
$target = Join-Path $sourceRoot "chapter4.tex"

$expectedAuthorityBytes = 154744
$expectedAuthoritySha256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
$sourceStart = 1609
$sourceEnd = 1744
$expectedSourceSliceLineRecords = 136
$expectedSourceSliceBytes = 15005
$expectedSourceSliceSha256 = "9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab"

$expectedCandidateLineRecords = 135
$expectedCandidateBytes = 19019
$expectedCandidateSha256 = "8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62"

# This is the exact anticipated prefix + candidate + authority-suffix identity.
# Recompute it after canonical integration and change these adjacent values only
# if the independently verified integration differs.
$expectedTargetLineRecords = 1893
$expectedTargetBytes = 189935
$expectedTargetSha256 = "37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569"
$targetStart = 1604
$targetEnd = 1738
$boundaryBlankLine = 1739
$nextSentinelLine = 1740

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
    throw "Unit 034 authority identity mismatch: bytes=$($authorityRecord.Bytes.Length) sha256=$($authorityRecord.Sha256)"
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
    throw "Unit 034 authority slice identity mismatch: records=$($sourceSliceLines.Count) bytes=$($sourceSliceBytes.Length) sha256=$sourceSliceHash"
}
$nextSectionSentinel = $authorityLines[$sourceEnd]
if (
    $sourceSliceLines[-1] -ne "" -or
    -not $nextSectionSentinel.StartsWith('\section{') -or
    -not $nextSectionSentinel.EndsWith('\label{sec:group-in-cat}')
) {
    throw "Unit 034 authority boundary or Section 4.11 sentinel drifted"
}

$candidateRecord = Read-StrictUtf8 -Path $candidate
if (-not $candidateRecord.Text.EndsWith("`n") -or $candidateRecord.Text.EndsWith("`n`n")) {
    throw "Unit 034 candidate must end in exactly one LF"
}
$candidateLineRecords = ([regex]::Matches($candidateRecord.Text, "`n")).Count
if (
    $candidateLineRecords -ne $expectedCandidateLineRecords -or
    $candidateRecord.Bytes.Length -ne $expectedCandidateBytes -or
    $candidateRecord.Sha256 -ne $expectedCandidateSha256
) {
    throw "Unit 034 candidate identity mismatch: records=$candidateLineRecords bytes=$($candidateRecord.Bytes.Length) sha256=$($candidateRecord.Sha256)"
}

$targetRecord = Read-StrictUtf8 -Path $target
if (-not $targetRecord.Text.EndsWith("`n") -or $targetRecord.Text.EndsWith("`n`n")) {
    throw "Unit 034 canonical target must end in exactly one LF"
}
$targetLineRecords = ([regex]::Matches($targetRecord.Text, "`n")).Count
if (
    $targetLineRecords -ne $expectedTargetLineRecords -or
    $targetRecord.Bytes.Length -ne $expectedTargetBytes -or
    $targetRecord.Sha256 -ne $expectedTargetSha256
) {
    throw "Unit 034 canonical target identity mismatch: records=$targetLineRecords bytes=$($targetRecord.Bytes.Length) sha256=$($targetRecord.Sha256)"
}
$targetLines = $targetRecord.Text.Split("`n")
$targetSpanText = [string]::Join("`n", $targetLines[($targetStart - 1)..($targetEnd - 1)]) + "`n"
$targetSpanBytes = $utf8Strict.GetBytes($targetSpanText)
$targetSpanHash = Get-Sha256 -Bytes $targetSpanBytes
if ($targetSpanBytes.Length -ne $candidateRecord.Bytes.Length -or $targetSpanHash -ne $candidateRecord.Sha256) {
    throw "Unit 034 canonical target span differs byte-for-byte from the admitted candidate"
}
if ($targetLines[$boundaryBlankLine - 1] -ne "") {
    throw "Unit 034 canonical target line 1739 must preserve the blank section boundary"
}
if ($targetLines[$nextSentinelLine - 1] -ne $nextSectionSentinel) {
    throw "Unit 034 canonical target Section 4.11 sentinel drifted"
}

$jobName = "unit-034-bab-4-limit-dan-kompletisasi-grup"
$driverName = "$jobName.tex"
$driver = Join-Path $sourceRoot $driverName
if (-not (Test-Path -LiteralPath $driver -PathType Leaf)) {
    throw "Unit 034 reader driver is not yet present: $driver"
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

$canonicalSpanName = "unit-034-canonical-span.tex"
$canonicalSpanPath = Join-Path $outputRoot $canonicalSpanName
[System.IO.File]::WriteAllBytes($canonicalSpanPath, $targetSpanBytes)
$canonicalSpanRecord = Read-StrictUtf8 -Path $canonicalSpanPath
if (
    $canonicalSpanRecord.Bytes.Length -ne $candidateRecord.Bytes.Length -or
    $canonicalSpanRecord.Sha256 -ne $candidateRecord.Sha256
) {
    throw "Generated Unit 034 canonical span differs from the admitted target/candidate identity"
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
$previousTexInputs = [Environment]::GetEnvironmentVariable("TEXINPUTS", "Process")
[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH", "1787788800", "Process")
[Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE", "1", "Process")
[Environment]::SetEnvironmentVariable("TEXINPUTS", $outputRoot + [System.IO.Path]::PathSeparator + $previousTexInputs, "Process")

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
    [Environment]::SetEnvironmentVariable("TEXINPUTS", $previousTexInputs, "Process")
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
    canonical_span_path = $canonicalSpanPath
    canonical_span_bytes = $canonicalSpanRecord.Bytes.Length
    canonical_span_sha256 = $canonicalSpanRecord.Sha256
}
