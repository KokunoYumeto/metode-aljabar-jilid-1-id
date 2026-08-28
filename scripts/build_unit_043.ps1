[CmdletBinding()]
param(
	[string]$OutputDirectory = "build/unit-043-replay",
	[switch]$SkipCandidateCheck
)

$ErrorActionPreference = "Stop"
$laneRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$sourceRoot = Join-Path $laneRoot "repo/source"
$authority = Join-Path $laneRoot "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex"
$candidate = Join-Path $laneRoot "build/unit-043-candidate/chapter5-complete-id.tex"
$checker = Join-Path $laneRoot "build/unit-043-candidate/check_chapter5_complete.py"
$artifact = Join-Path $laneRoot "artifacts/unit-043-bab-5-pengantar-teori-gelanggang-id.pdf"
$finalLog = Join-Path $laneRoot "qa/UNIT_043_BUILD_FINAL.log"
$expectedAuthorityBytes = 122998
$expectedAuthoritySha256 = "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
$expectedCandidateBytes = 156081
$expectedCandidateSha256 = "33a1c65ce1ddea061e02d32a9a250d6db4444eb2251d5b721c8501f95a7f0e3c"
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
if ($a.Bytes.Length -ne $expectedAuthorityBytes -or $a.Sha256 -ne $expectedAuthoritySha256) { throw "Chapter 5 authority identity mismatch" }
$c = Read-StrictUtf8 $candidate
$candidateRecords = ([regex]::Matches($c.Text,"`n")).Count
if (-not $c.Text.EndsWith("`n") -or $c.Text.EndsWith("`n`n") -or $candidateRecords -ne 1382 -or $c.Bytes.Length -ne $expectedCandidateBytes -or $c.Sha256 -ne $expectedCandidateSha256) { throw "Chapter 5 candidate identity mismatch" }

if (-not $SkipCandidateCheck) { Invoke-Checked "python" @($checker) }

$jobName = "unit-043-bab-5-pengantar-teori-gelanggang"
$driverName = "$jobName.tex"
if ([System.IO.Path]::IsPathRooted($OutputDirectory)) { $outputRoot=[System.IO.Path]::GetFullPath($OutputDirectory) }
else { $outputRoot=[System.IO.Path]::GetFullPath((Join-Path $laneRoot $OutputDirectory)) }
if (-not $outputRoot.StartsWith($laneRoot+[System.IO.Path]::DirectorySeparatorChar,[System.StringComparison]::OrdinalIgnoreCase)) { throw "output must remain inside lane" }
if (Test-Path -LiteralPath $outputRoot) {
	if (@(Get-ChildItem -LiteralPath $outputRoot -Force).Count -ne 0) { throw "output must be absent or empty" }
} else { New-Item -ItemType Directory -Path $outputRoot | Out-Null }

$args=@("-no-shell-escape","-interaction=nonstopmode","-halt-on-error","-file-line-error","-jobname=$jobName","-output-directory=$outputRoot",$driverName)
$oldEpoch=[Environment]::GetEnvironmentVariable("SOURCE_DATE_EPOCH","Process")
$oldForce=[Environment]::GetEnvironmentVariable("FORCE_SOURCE_DATE","Process")
$oldInputs=[Environment]::GetEnvironmentVariable("TEXINPUTS","Process")
$candidateRoot = Split-Path -Parent $candidate
[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH","1787875200","Process")
[Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE","1","Process")
[Environment]::SetEnvironmentVariable("TEXINPUTS",$outputRoot+[System.IO.Path]::PathSeparator+$candidateRoot+[System.IO.Path]::PathSeparator+$oldInputs,"Process")
Push-Location $sourceRoot
try {
	Invoke-Checked "xelatex" $args
	Invoke-Checked "biber" @("--input-directory",$outputRoot,"--output-directory",$outputRoot,$jobName)
	Push-Location $outputRoot
	try {
		if (Test-Path "$jobName.idx") { Invoke-Checked "makeindex" @("$jobName.idx") }
		if ((Test-Path "sym1.idx") -and (Select-String -LiteralPath "sym1.idx" -Pattern '^\\indexentry' -Quiet)) {
			Invoke-Checked "makeindex" @("sym1.idx")
			# The frozen source has one raw symbol-index key, Z_p, that truexindy
			# renders mathematically but makeindex emits as invalid text-mode TeX.
			# Repair only that generated index record; source/candidate bytes stay fixed.
			$symbolOutput = Join-Path $outputRoot "sym1.ind"
			$symbolText = [System.IO.File]::ReadAllText($symbolOutput)
			if ([regex]::Matches($symbolText, [regex]::Escape('\item Z_p,')).Count -ne 1) { throw "unexpected Z_p symbol-index repair census" }
			$symbolText = $symbolText.Replace('\item Z_p,', '\item $\Z_p$,')
			[System.IO.File]::WriteAllText($symbolOutput, $symbolText, [System.Text.UTF8Encoding]::new($false))
		}
	} finally { Pop-Location }
	Invoke-Checked "xelatex" $args
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
$logText=[System.IO.File]::ReadAllText($log.FullName)
$forbidden=@('There were undefined references','Citation .+ undefined','Please \(re\)run Biber','Rerun to get cross-references right','Undefined control sequence','Emergency stop','Fatal error')
foreach($pattern in $forbidden){ if($logText -match $pattern){ throw "final log contains forbidden diagnostic: $pattern" } }
[System.IO.Directory]::CreateDirectory((Split-Path -Parent $artifact)) | Out-Null
[System.IO.Directory]::CreateDirectory((Split-Path -Parent $finalLog)) | Out-Null
[System.IO.File]::WriteAllBytes($artifact,[System.IO.File]::ReadAllBytes($pdf.FullName))
[System.IO.File]::WriteAllBytes($finalLog,[System.IO.File]::ReadAllBytes($log.FullName))
$pages = ((& pdfinfo $artifact | Select-String '^Pages:\s+(\d+)$').Matches.Groups[1].Value)
if (-not $pages) { throw "pdfinfo did not report a page count" }
[pscustomobject]@{
	path=$artifact; pages=[int]$pages; bytes=(Get-Item $artifact).Length; sha256=(Get-FileHash -Algorithm SHA256 $artifact).Hash.ToLowerInvariant()
	log_path=$finalLog; log_bytes=(Get-Item $finalLog).Length; log_sha256=(Get-FileHash -Algorithm SHA256 $finalLog).Hash.ToLowerInvariant()
	authority_records=1382; authority_bytes=$a.Bytes.Length; authority_sha256=$a.Sha256
	candidate_records=$candidateRecords; candidate_bytes=$c.Bytes.Length; candidate_sha256=$c.Sha256
}
