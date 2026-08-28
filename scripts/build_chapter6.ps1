[CmdletBinding()]
param(
	[string]$OutputDirectory = "build/chapter6-reader-replay",
	[switch]$SkipCandidateCheck
)

$ErrorActionPreference = "Stop"
$laneRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$sourceRoot = Join-Path $laneRoot "repo/source"
$authority = Join-Path $laneRoot "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter6.tex"
$candidate = Join-Path $laneRoot "build/chapter6-batch-candidate/chapter6-complete-id.tex"
$checker = Join-Path $laneRoot "build/chapter6-batch-candidate/check_chapter6_complete.py"
$readerSourceBuilder = Join-Path $laneRoot "scripts/prepare_chapter6_reader_source.py"
$target = Join-Path $sourceRoot "chapter6.tex"
$readerSource = Join-Path $laneRoot "build/chapter6-reader-source/chapter6-reader-reflow.tex"
$artifact = Join-Path $laneRoot "artifacts/unit-044-bab-6-modul-id.pdf"
$finalLog = Join-Path $laneRoot "qa/CHAPTER_6_BUILD_FINAL.log"
$authorityBytes = 160950
$authoritySha = "c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49"
$candidateBytes = 193563
$candidateSha = "15c09af18eeab6ce1a4c5a4cb69b1b3a42bc2422b015f21f77ccfbb3c94f7e14"
$utf8Strict = [Text.UTF8Encoding]::new($false,$true)

function Get-Sha256([byte[]]$Bytes) {
	$h=[Security.Cryptography.SHA256]::Create()
	try{[BitConverter]::ToString($h.ComputeHash($Bytes)).Replace("-","").ToLowerInvariant()}
	finally{$h.Dispose()}
}
function Read-Strict([string]$Path) {
	$b=[IO.File]::ReadAllBytes($Path)
	if($b.Length-ge 3 -and $b[0]-eq 0xef -and $b[1]-eq 0xbb -and $b[2]-eq 0xbf){throw "BOM forbidden: $Path"}
	if($b -contains 13){throw "CR/CRLF forbidden: $Path"}
	[pscustomobject]@{Bytes=$b;Text=$utf8Strict.GetString($b);Sha256=Get-Sha256 $b}
}
function Invoke-Checked([string]$Program,[string[]]$Arguments){
	& $Program @Arguments
	if($LASTEXITCODE-ne 0){throw "$Program exited with $LASTEXITCODE"}
}

$a=Read-Strict $authority
$c=Read-Strict $candidate
$t=Read-Strict $target
if($a.Bytes.Length-ne $authorityBytes -or $a.Sha256-ne $authoritySha){throw "authority identity mismatch"}
if($c.Bytes.Length-ne $candidateBytes -or $c.Sha256-ne $candidateSha){throw "candidate identity mismatch"}
if($t.Sha256-ne $candidateSha){throw "canonical Chapter 6 is not candidate-identical"}
if(-not $SkipCandidateCheck){Invoke-Checked "python" @($checker)}
Invoke-Checked "python" @($readerSourceBuilder)
$reader=Read-Strict $readerSource
if($reader.Text.Split("`n").Count-1-ne 1994){throw "reader-only Chapter 6 record count mismatch"}

$job="unit-044-bab-6-modul-id"
$driver="chapter-6-reader.tex"
if([IO.Path]::IsPathRooted($OutputDirectory)){$outputRoot=[IO.Path]::GetFullPath($OutputDirectory)}
else{$outputRoot=[IO.Path]::GetFullPath((Join-Path $laneRoot $OutputDirectory))}
if(-not $outputRoot.StartsWith($laneRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw "output must stay in lane"}
if(Test-Path -LiteralPath $outputRoot){if(@(Get-ChildItem -LiteralPath $outputRoot -Force).Count-ne 0){throw "output must be absent or empty"}}
else{New-Item -ItemType Directory -Path $outputRoot|Out-Null}

$args=@("-no-shell-escape","-interaction=nonstopmode","-halt-on-error","-file-line-error","-jobname=$job","-output-directory=$outputRoot",$driver)
$oldEpoch=[Environment]::GetEnvironmentVariable("SOURCE_DATE_EPOCH","Process")
$oldForce=[Environment]::GetEnvironmentVariable("FORCE_SOURCE_DATE","Process")
[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH","1787875200","Process")
[Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE","1","Process")
Push-Location $sourceRoot
try{
	Invoke-Checked "xelatex" $args
	Invoke-Checked "biber" @("--input-directory",$outputRoot,"--output-directory",$outputRoot,$job)
	Push-Location $outputRoot
	try{
		if(Test-Path "$job.idx"){Invoke-Checked "makeindex" @("$job.idx")}
		if((Test-Path "sym1.idx") -and (Select-String -LiteralPath "sym1.idx" -Pattern '^\\indexentry' -Quiet)){
			Invoke-Checked "makeindex" @("sym1.idx")
			$symbol=Join-Path $outputRoot "sym1.ind"
			$text=[IO.File]::ReadAllText($symbol)
			$text=$text.Replace('\item Z_p,','\item $\Z_p$,').Replace('\item F_q,','\item $\F_q$,')
			[IO.File]::WriteAllText($symbol,$text,[Text.UTF8Encoding]::new($false))
		}
	}finally{Pop-Location}
	Invoke-Checked "xelatex" $args
	Invoke-Checked "xelatex" $args
	Invoke-Checked "xelatex" $args
}finally{
	Pop-Location
	[Environment]::SetEnvironmentVariable("SOURCE_DATE_EPOCH",$oldEpoch,"Process")
	[Environment]::SetEnvironmentVariable("FORCE_SOURCE_DATE",$oldForce,"Process")
}

$pdf=Join-Path $outputRoot "$job.pdf"
$log=Join-Path $outputRoot "$job.log"
$logText=[IO.File]::ReadAllText($log)
$forbidden=@('There were undefined references','Citation .+ undefined','Please \(re\)run Biber','Rerun to get cross-references right','Undefined control sequence','Emergency stop','Fatal error')
foreach($pattern in $forbidden){if($logText-match $pattern){throw "final log contains forbidden diagnostic: $pattern"}}
[IO.Directory]::CreateDirectory((Split-Path -Parent $artifact))|Out-Null
[IO.Directory]::CreateDirectory((Split-Path -Parent $finalLog))|Out-Null
[IO.File]::WriteAllBytes($artifact,[IO.File]::ReadAllBytes($pdf))
[IO.File]::WriteAllBytes($finalLog,[IO.File]::ReadAllBytes($log))
$pages=((& pdfinfo $artifact|Select-String '^Pages:\s+(\d+)$').Matches.Groups[1].Value)
if(-not $pages){throw "pdfinfo did not report pages"}
[pscustomobject]@{
	path=$artifact;pages=[int]$pages;bytes=(Get-Item $artifact).Length;sha256=(Get-FileHash -Algorithm SHA256 $artifact).Hash.ToLowerInvariant()
	log_path=$finalLog;log_bytes=(Get-Item $finalLog).Length;log_sha256=(Get-FileHash -Algorithm SHA256 $finalLog).Hash.ToLowerInvariant()
	authority_records=1994;authority_bytes=$a.Bytes.Length;authority_sha256=$a.Sha256
	candidate_records=1994;candidate_bytes=$c.Bytes.Length;candidate_sha256=$c.Sha256
	reader_source_records=1994;reader_source_bytes=$reader.Bytes.Length;reader_source_sha256=$reader.Sha256
}
