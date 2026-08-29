$ErrorActionPreference = 'Stop'

$BuildRoot = [IO.Path]::GetFullPath((Split-Path -Parent $MyInvocation.MyCommand.Path))
$OutputRoot = [IO.Path]::GetFullPath((Join-Path $BuildRoot 'build-output'))
$JobName = 'duncan-complete-id'
$Driver = 'duncan-complete-id.tex'

if (([IO.Path]::GetFullPath((Split-Path -Parent $OutputRoot))) -ne $BuildRoot) {
    throw "Refusing to clean an output directory outside the build closure: $OutputRoot"
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

# Hapus hanya artefak yang dihasilkan oleh job ini agar setiap replay benar-benar bersih.
$GeneratedExtensions = @(
    '.aux', '.bbl', '.bcf', '.blg', '.fls', '.log', '.out', '.pdf',
    '.run.xml', '.toc', '.xdv'
)
foreach ($Extension in $GeneratedExtensions) {
    $Artifact = Join-Path $OutputRoot ($JobName + $Extension)
    if (Test-Path -LiteralPath $Artifact -PathType Leaf) {
        Remove-Item -LiteralPath $Artifact -Force
    }
}

$env:SOURCE_DATE_EPOCH = '1682087756'
$env:FORCE_SOURCE_DATE = '1'
$env:TZ = 'UTC'
$env:LC_ALL = 'C'
$env:LANG = 'C'

$XeLaTeXArgs = @(
    '-interaction=nonstopmode',
    '-halt-on-error',
    '-file-line-error',
    '-no-shell-escape',
    '-disable-installer',
    '-recorder',
    '-synctex=0',
    "-jobname=$JobName",
    "-output-directory=$OutputRoot",
    $Driver
)

Push-Location $BuildRoot
try {
    & xelatex @XeLaTeXArgs
    if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass 1 failed with exit code $LASTEXITCODE" }

    & biber --validate-datamodel --input-directory $OutputRoot --output-directory $OutputRoot $JobName
    if ($LASTEXITCODE -ne 0) { throw "Biber failed with exit code $LASTEXITCODE" }

    & xelatex @XeLaTeXArgs
    if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass 2 failed with exit code $LASTEXITCODE" }

    & xelatex @XeLaTeXArgs
    if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass 3 failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}

Write-Host "Bangunan selesai: $(Join-Path $OutputRoot ($JobName + '.pdf'))"
