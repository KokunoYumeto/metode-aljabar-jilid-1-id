param(
  [string]$OutputDirectory = 'build-output'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$supportRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$componentRoot = [IO.Path]::GetFullPath((Join-Path $supportRoot '..'))
$sourcePath = [IO.Path]::GetFullPath((Join-Path $componentRoot 'source\o013-rute-pembelajar.tex'))
$backendPath = [IO.Path]::GetFullPath((Join-Path $componentRoot 'backend\o013-rute-pembelajar.json'))
$outputRoot = [IO.Path]::GetFullPath((Join-Path $supportRoot $OutputDirectory))
$allowedPrefix = $supportRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar

if (-not $outputRoot.StartsWith($allowedPrefix, [StringComparison]::OrdinalIgnoreCase)) {
  throw "Output directory escapes the original-layer support directory: $outputRoot"
}

$expected = [ordered]@{
  $sourcePath = '776fa0cfd9b9d1e20df691aa19a599aaa527bf8cb37ea4c81234d0f998011974'
  $backendPath = '05eb379f4cad172b6b5cb067845718d9b12b6b469a9b6ff71ba18511721461f8'
}
foreach ($entry in $expected.GetEnumerator()) {
  if (-not (Test-Path -LiteralPath $entry.Key -PathType Leaf)) {
    throw "Pinned input missing: $($entry.Key)"
  }
  $actual = (Get-FileHash -LiteralPath $entry.Key -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -ne $entry.Value) {
    throw "Pinned input mismatch for $($entry.Key): expected $($entry.Value), got $actual"
  }
}

if (-not (Get-Command xelatex -ErrorAction SilentlyContinue)) {
  throw 'Required TeX tool is unavailable: xelatex'
}

if (Test-Path -LiteralPath $outputRoot) {
  Remove-Item -LiteralPath $outputRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $outputRoot | Out-Null

$env:SOURCE_DATE_EPOCH = '1787961600'
$env:FORCE_SOURCE_DATE = '1'
$env:TZ = 'UTC'
$env:LC_ALL = 'C'
$env:MIKTEX_ENABLE_INSTALLER = '0'

$args = @(
  '-interaction=nonstopmode',
  '-halt-on-error',
  '-file-line-error',
  '-no-shell-escape',
  '-synctex=0',
  "-output-directory=$outputRoot",
  $sourcePath
)

& xelatex @args
if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass 1 failed: $LASTEXITCODE" }
& xelatex @args
if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass 2 failed: $LASTEXITCODE" }

$pdf = Join-Path $outputRoot 'o013-rute-pembelajar.pdf'
if (-not (Test-Path -LiteralPath $pdf -PathType Leaf)) {
  throw "Expected PDF missing: $pdf"
}

[pscustomobject]@{
  result = 'PASS'
  pdf = $pdf
  bytes = (Get-Item -LiteralPath $pdf).Length
  sha256 = (Get-FileHash -LiteralPath $pdf -Algorithm SHA256).Hash.ToLowerInvariant()
} | ConvertTo-Json -Compress
