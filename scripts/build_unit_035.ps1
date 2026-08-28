[CmdletBinding()]
param([string]$OutputDirectory = "build/unit-035-replay")

$ErrorActionPreference = "Stop"
$laneRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$sourceRoot = Join-Path $laneRoot "repo/source"
$authority = Join-Path $laneRoot "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
$candidate = Join-Path $laneRoot "build/unit-035-candidate/chapter4-groups-in-categories-and-exercises-id.tex"
$target = Join-Path $sourceRoot "chapter4.tex"
$expectedAuthorityBytes = 154744
$expectedAuthoritySha256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
$sourceStart = 1745
$sourceEnd = 1898
$expectedSourceSliceLineRecords = 154
$expectedSourceSliceBytes = 14398
$expectedSourceSliceSha256 = "f841860520d4ab35dc82354f288bc295c4681f9faffc8f5a645c92a3af1dd287"
$expectedCandidateLineRecords = 154
$expectedCandidateBytes = 18089
$expectedCandidateSha256 = "5d9bf6e5c9c17c83821f1bba63078f4d28e3836428f4557e0727ee5b1046c2ca"
$expectedTargetLineRecords = 1893
$expectedTargetBytes = 193626
$expectedTargetSha256 = "2b682d67292e4c439ccc9f6d46f72d3d0eb7cb5bf8b3a3a5999210c45ef547c5"
$targetStart = 1740
$targetEnd = 1893
$utf8Strict = [System.Text.UTF8Encoding]::new($false, $true)

function Get-Sha256([byte[]]$Bytes) {
	$hasher = [System.Security.Cryptography.SHA256]::Create()
	try { [System.BitConverter]::ToString($hasher.ComputeHash($Bytes)).Replace("-", "").ToLowerInvariant() }
	finally { $hasher.Dispose() }
}
function Read-StrictUtf8([string]$Path) {
	$bytes = [System.IO.File]::ReadAllBytes($Path)
	if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xef -and $bytes[1] -eq 0xbb -and $bytes[2] -eq 0xbf) { throw "UTF-8 BOM forbidden: $Path" }
	if ($bytes -contains 13) { throw "CR/CRLF forbidden: $Path" }
	[pscustomobject]@{Bytes=$bytes; Text=$utf8Strict.GetString($bytes); Sha256=Get-Sha256 $bytes}
}
function Invoke-Checked([string]$Program,[string[]]$Arguments) {
	& $Program @Arguments
	if ($LASTEXITCODE -ne 0) { throw "$Program exited with code $LASTEXITCODE" }
}

$a = Read-StrictUtf8 $authority
if ($a.Bytes.Length -ne $expectedAuthorityBytes -or $a.Sha256 -ne $expectedAuthoritySha256) { throw "authority identity mismatch" }
$aLines = $a.Text.Split("`n")
$sliceLines = $aLines[($sourceStart-1)..($sourceEnd-1)]
$sliceText = [string]::Join("`n",$sliceLines) + "`n"
$sliceBytes = $utf8Strict.GetBytes($sliceText)
$sliceHash = Get-Sha256 $sliceBytes
if ($sliceLines.Count -ne $expectedSourceSliceLineRecords -or $sliceBytes.Length -ne $expectedSourceSliceBytes -or $sliceHash -ne $expectedSourceSliceSha256) { throw "authority slice identity mismatch" }
if (-not $sliceLines[0].EndsWith('\label{sec:group-in-cat}') -or $sliceLines[-1] -ne '\end{Exercises}') { throw "authority boundary drift" }

$c = Read-StrictUtf8 $candidate
$cRecords = ([regex]::Matches($c.Text,"`n")).Count
if (-not $c.Text.EndsWith("`n") -or $c.Text.EndsWith("`n`n") -or $cRecords -ne $expectedCandidateLineRecords -or $c.Bytes.Length -ne $expectedCandidateBytes -or $c.Sha256 -ne $expectedCandidateSha256) { throw "candidate identity mismatch" }

$t = Read-StrictUtf8 $target
$tRecords = ([regex]::Matches($t.Text,"`n")).Count
if ($tRecords -ne $expectedTargetLineRecords -or $t.Bytes.Length -ne $expectedTargetBytes -or $t.Sha256 -ne $expectedTargetSha256) { throw "canonical target identity mismatch" }
$tLines = $t.Text.Split("`n")
$spanText = [string]::Join("`n",$tLines[($targetStart-1)..($targetEnd-1)]) + "`n"
$spanBytes = $utf8Strict.GetBytes($spanText)
$spanHash = Get-Sha256 $spanBytes
if ($spanBytes.Length -ne $c.Bytes.Length -or $spanHash -ne $c.Sha256) { throw "canonical span differs from candidate" }

$jobName = "unit-035-bab-4-grup-dalam-kategori-dan-latihan"
$driverName = "$jobName.tex"
if ([System.IO.Path]::IsPathRooted($OutputDirectory)) { $outputRoot=[System.IO.Path]::GetFullPath($OutputDirectory) }
else { $outputRoot=[System.IO.Path]::GetFullPath((Join-Path $laneRoot $OutputDirectory)) }
if (-not $outputRoot.StartsWith($laneRoot+[System.IO.Path]::DirectorySeparatorChar,[System.StringComparison]::OrdinalIgnoreCase)) { throw "output must remain inside lane" }
if (Test-Path -LiteralPath $outputRoot) {
	if (@(Get-ChildItem -LiteralPath $outputRoot -Force).Count -ne 0) { throw "output must be absent or empty" }
} else { New-Item -ItemType Directory -Path $outputRoot | Out-Null }
$spanPath=Join-Path $outputRoot "unit-035-canonical-span.tex"
[System.IO.File]::WriteAllBytes($spanPath,$spanBytes)

$args=@("-no-shell-escape","-interaction=nonstopmode","-halt-on-error","-file-line-error","-jobname=$jobName","-output-directory=$outputRoot",$driverName)
$oldEpoch=[Environment]::GetEnvironmentVariable("SOURCE_DATE_EPOCH","Process")
$oldForce=[Environment]::GetEnvironmentVariable("FORCE_SOURCE_DATE","Process")
$oldInputs=[Environment]::GetEnvironmentVariable("TEXINPUTS","Process")
[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH","1787875200","Process")
[Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE","1","Process")
[Environment]::SetEnvironmentVariable("TEXINPUTS",$outputRoot+[System.IO.Path]::PathSeparator+$oldInputs,"Process")
Push-Location $sourceRoot
try {
	Invoke-Checked "xelatex" $args
	Invoke-Checked "biber" @("--input-directory",$outputRoot,"--output-directory",$outputRoot,$jobName)
	Push-Location $outputRoot
	try {
		if (Test-Path "$jobName.idx") { Invoke-Checked "makeindex" @("$jobName.idx") }
		if ((Test-Path "sym1.idx") -and (Select-String -LiteralPath "sym1.idx" -Pattern '^\\indexentry' -Quiet)) { Invoke-Checked "makeindex" @("sym1.idx") }
	} finally { Pop-Location }
	Invoke-Checked "xelatex" $args
	Invoke-Checked "xelatex" $args
} finally {
	Pop-Location
	[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH",$oldEpoch,"Process")
	[Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE",$oldForce,"Process")
	[Environment]::SetEnvironmentVariable("TEXINPUTS",$oldInputs,"Process")
}

$pdf=Get-Item -LiteralPath (Join-Path $outputRoot "$jobName.pdf")
$log=Get-Item -LiteralPath (Join-Path $outputRoot "$jobName.log")
[pscustomobject]@{
	path=$pdf.FullName; bytes=$pdf.Length; sha256=(Get-FileHash -Algorithm SHA256 $pdf.FullName).Hash.ToLowerInvariant()
	raw_log_path=$log.FullName; raw_log_bytes=$log.Length; raw_log_sha256=(Get-FileHash -Algorithm SHA256 $log.FullName).Hash.ToLowerInvariant()
	authority_slice_lines="$sourceStart-$sourceEnd"; authority_slice_bytes=$sliceBytes.Length; authority_slice_sha256=$sliceHash
	candidate_bytes=$c.Bytes.Length; candidate_sha256=$c.Sha256; canonical_target_bytes=$t.Bytes.Length; canonical_target_sha256=$t.Sha256
	canonical_span_lines="$targetStart-$targetEnd"; canonical_span_bytes=$spanBytes.Length; canonical_span_sha256=$spanHash
}
