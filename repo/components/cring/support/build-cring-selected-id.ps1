param(
  [string]$OutputDirectory = 'reader-build'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$candidateRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$outputRoot = [IO.Path]::GetFullPath((Join-Path $candidateRoot $OutputDirectory))
$allowedPrefix = $candidateRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
if (-not $outputRoot.StartsWith($allowedPrefix, [StringComparison]::OrdinalIgnoreCase)) {
  throw "Output directory escapes the CRing candidate root: $outputRoot"
}

$expectedHashes = [ordered]@{
  '..\source-id\01-nakayama.tex' = '6304f3d7767234d3f082eab0147c04ba1bc5037739cae093176db7f29ddaafc8'
  '..\source-id\02-spec-zariski.tex' = 'a814e86a7034550310570bca32488f3b4953e9333ced5249efc4c0facf78139a'
  '..\source-id\03-associated-primary.tex' = '235781e45e240bc41382968c694c295b847e11d2183f5b00915405b3183410b3'
  '..\source-id\04-lying-over-going-up.tex' = 'a7ab9ecfcc9414dba5c7a7cb9f080bdde0be09e7adacfeb55ade40bb3c3b488f'
  '..\source-id\05-nullstellensatz-normalization.tex' = '395287f8152a71c24b27e8b6db6ec8830c16521ec99a100729218b9cfd49a702'
  '..\source-id\06-krull-dimension.tex' = 'd49cf309f3d5d47ab2838741392ce9ebb06ed91b10624bfe106e626f8ab90c36'
  'GFDL-1.2-or-later.tex' = 'c491697410aceabdbc88cd724024b9faac6fe1308db1c732682574b95fab457f'
  'CRING-references.bib' = 'e57221002c0fc62b63de39b0f01c279a85d32f0d4861507570f9fca6d09a3bc5'
}

foreach ($entry in $expectedHashes.GetEnumerator()) {
  $path = [IO.Path]::GetFullPath((Join-Path $candidateRoot $entry.Key))
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
    throw "Pinned input is missing: $($entry.Key)"
  }
  $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -ne $entry.Value) {
    throw "Pinned input hash mismatch for $($entry.Key): expected $($entry.Value), got $actual"
  }
}

foreach ($tool in @('xelatex','bibtex','makeindex')) {
  if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
    throw "Required TeX tool is unavailable: $tool"
  }
}

if (Test-Path -LiteralPath $outputRoot) {
  Remove-Item -LiteralPath $outputRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $outputRoot | Out-Null

$env:SOURCE_DATE_EPOCH = '1288569600'
$env:FORCE_SOURCE_DATE = '1'
$env:TZ = 'UTC'
$env:LC_ALL = 'C'
$env:MIKTEX_ENABLE_INSTALLER = '0'

function Invoke-Checked {
  param(
    [Parameter(Mandatory=$true)][string]$Command,
    [Parameter(Mandatory=$true)][string[]]$Arguments
  )
  $process = Start-Process -FilePath $Command -ArgumentList $Arguments -Wait -PassThru -NoNewWindow
  if ($process.ExitCode -ne 0) {
    throw "$Command failed with exit code $($process.ExitCode)"
  }
}

Push-Location $candidateRoot
try {
  $driver = 'cring-selected-id-reader.tex'
  $stem = Join-Path $outputRoot 'cring-selected-id-reader'
  $latexArguments = @(
    '-interaction=nonstopmode',
    '-halt-on-error',
    '-file-line-error',
    '-no-shell-escape',
    '-synctex=0',
    "-output-directory=$outputRoot",
    $driver
  )

  Invoke-Checked -Command 'xelatex' -Arguments $latexArguments
  Invoke-Checked -Command 'bibtex' -Arguments @($stem)
  Invoke-Checked -Command 'makeindex' -Arguments @("$stem.idx", '-o', "$stem.ind", '-t', "$stem.ilg")
  Invoke-Checked -Command 'xelatex' -Arguments $latexArguments
  Invoke-Checked -Command 'xelatex' -Arguments $latexArguments
}
finally {
  Pop-Location
}

$pdf = Join-Path $outputRoot 'cring-selected-id-reader.pdf'
if (-not (Test-Path -LiteralPath $pdf -PathType Leaf)) {
  throw "Expected PDF was not produced: $pdf"
}

[pscustomobject]@{
  result = 'PASS'
  pdf = $pdf
  bytes = (Get-Item -LiteralPath $pdf).Length
  sha256 = (Get-FileHash -LiteralPath $pdf -Algorithm SHA256).Hash.ToLowerInvariant()
} | ConvertTo-Json -Compress
