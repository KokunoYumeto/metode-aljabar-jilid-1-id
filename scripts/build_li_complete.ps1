[CmdletBinding()]
param(
	[string]$OutputDirectory = "build/li-complete-reader-replay"
)

$ErrorActionPreference = "Stop"
$laneRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$sourceRoot = Join-Path $laneRoot "repo/source"
$driver = "full-reader-id.tex"
$checker = Join-Path $laneRoot "scripts/check_li_complete_translation.py"
$artifact = Join-Path $laneRoot "artifacts/metode-aljabar-jilid-1-id-lengkap.pdf"
$finalLog = Join-Path $laneRoot "qa/LI_COMPLETE_BUILD_FINAL.log"

function Invoke-Checked([string]$Program,[string[]]$Arguments) {
	& $Program @Arguments
	if ($LASTEXITCODE -ne 0) { throw "$Program exited with $LASTEXITCODE" }
}

if (-not (Test-Path -LiteralPath $checker -PathType Leaf)) {
	throw "missing complete-translation gate: $checker"
}
Invoke-Checked "python" @($checker)

$job = "metode-aljabar-jilid-1-id-lengkap"
if ([IO.Path]::IsPathRooted($OutputDirectory)) {
	$outputRoot = [IO.Path]::GetFullPath($OutputDirectory)
} else {
	$outputRoot = [IO.Path]::GetFullPath((Join-Path $laneRoot $OutputDirectory))
}
if (-not $outputRoot.StartsWith($laneRoot + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) {
	throw "output must stay in the task lane"
}
if (Test-Path -LiteralPath $outputRoot) {
	if (@(Get-ChildItem -LiteralPath $outputRoot -Force).Count -ne 0) {
		throw "output directory must be absent or empty"
	}
} else {
	New-Item -ItemType Directory -Path $outputRoot | Out-Null
}

$args = @(
	"-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
	"-file-line-error", "-jobname=$job", "-output-directory=$outputRoot", $driver
)
$oldEpoch = [Environment]::GetEnvironmentVariable("SOURCE_DATE_EPOCH","Process")
$oldForce = [Environment]::GetEnvironmentVariable("FORCE_SOURCE_DATE","Process")
[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH","1787875200","Process")
[Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE","1","Process")
Push-Location $sourceRoot
try {
	Invoke-Checked "xelatex" $args
	Invoke-Checked "biber" @("--input-directory",$outputRoot,"--output-directory",$outputRoot,$job)
	Push-Location $outputRoot
	try {
		if ((Test-Path "$job.idx") -and (Select-String -LiteralPath "$job.idx" -Pattern '^\\indexentry' -Quiet)) {
			Invoke-Checked "makeindex" @("$job.idx")
		}
		if ((Test-Path "sym1.idx") -and (Select-String -LiteralPath "sym1.idx" -Pattern '^\\indexentry' -Quiet)) {
			Invoke-Checked "makeindex" @("sym1.idx")
			$symbol = Join-Path $outputRoot "sym1.ind"
			$text = [IO.File]::ReadAllText($symbol)
			$text = $text.Replace('\item Z_p,','\item $\Z_p$,').Replace('\item F_q,','\item $\F_q$,')
			[IO.File]::WriteAllText($symbol,$text,[Text.UTF8Encoding]::new($false))
		}
	} finally {
		Pop-Location
	}
	Invoke-Checked "xelatex" $args
	Invoke-Checked "xelatex" $args
	Invoke-Checked "xelatex" $args
} finally {
	Pop-Location
	[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH",$oldEpoch,"Process")
	[Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE",$oldForce,"Process")
}

$pdf = Join-Path $outputRoot "$job.pdf"
$log = Join-Path $outputRoot "$job.log"
$logText = [IO.File]::ReadAllText($log)
$forbidden = @(
	'There were undefined references', 'Citation .+ undefined',
	'Please \(re\)run Biber', 'Rerun to get cross-references right',
	'Undefined control sequence', 'Emergency stop', 'Fatal error'
)
foreach ($pattern in $forbidden) {
	if ($logText -match $pattern) { throw "final log contains forbidden diagnostic: $pattern" }
}
[IO.Directory]::CreateDirectory((Split-Path -Parent $artifact)) | Out-Null
[IO.Directory]::CreateDirectory((Split-Path -Parent $finalLog)) | Out-Null
[IO.File]::WriteAllBytes($artifact,[IO.File]::ReadAllBytes($pdf))
[IO.File]::WriteAllBytes($finalLog,[IO.File]::ReadAllBytes($log))
$pages = ((& pdfinfo $artifact | Select-String '^Pages:\s+(\d+)$').Matches.Groups[1].Value)
if (-not $pages) { throw "pdfinfo did not report pages" }
[pscustomobject]@{
	path = $artifact
	pages = [int]$pages
	bytes = (Get-Item -LiteralPath $artifact).Length
	sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $artifact).Hash.ToLowerInvariant()
	log_path = $finalLog
	log_bytes = (Get-Item -LiteralPath $finalLog).Length
	log_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $finalLog).Hash.ToLowerInvariant()
}
