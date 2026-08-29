[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$stageRoot = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'publication/o013-aggregate-1.0.0'))
$expectedStageRoot = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'publication/o013-aggregate-1.0.0'))
if ($stageRoot -ne $expectedStageRoot) {
    throw "Refusing unexpected staging path: $stageRoot"
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$fixedZipTime = [System.DateTimeOffset]::new(1980, 1, 1, 0, 0, 0, [System.TimeSpan]::Zero)

$outputNames = @(
    '01_metode-aljabar-jilid-1-id-lengkap.pdf',
    '02_catatan-teori-representasi-duncan-id.pdf',
    '03_pilihan-aljabar-komutatif-cring-id.pdf',
    '04_o013-rute-pembelajar-dan-penguasaan-id.pdf',
    '05_o013-sumber-backend-1.0.0.zip',
    'LICENSES.md',
    'o013-aggregate-manifest.schema.json',
    'o013-aggregate-manifest.json',
    'SHA256SUMS.txt'
)

function Write-Utf8NoBomLf {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )
    $normalized = $Text -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($Path, $normalized, $utf8NoBom)
}

function Get-Sha256Lower {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-ReleaseFile {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Role,
        [Parameter(Mandatory = $true)][string]$MediaType,
        [Parameter(Mandatory = $true)][string]$License,
        [string]$ComponentId,
        [Nullable[int]]$Pages
    )
    $path = Join-Path $stageRoot $Name
    $item = Get-Item -LiteralPath $path
    $result = [ordered]@{
        name = $Name
        role = $Role
        media_type = $MediaType
        bytes = [int64]$item.Length
        sha256 = Get-Sha256Lower -Path $path
        license = $License
    }
    if ($ComponentId) {
        $result.component_id = $ComponentId
    }
    if ($null -ne $Pages) {
        $result.pages = [int]$Pages
    }
    return [pscustomobject]$result
}

function New-DeterministicSourceArchive {
    param(
        [Parameter(Mandatory = $true)][string]$ArchivePath,
        [Parameter(Mandatory = $true)][array]$InputFiles
    )

    $entryRows = @()
    foreach ($inputFile in $InputFiles) {
        $entryRows += [pscustomobject][ordered]@{
            path = $inputFile.ArchivePath
            bytes = [int64]$inputFile.File.Length
            sha256 = Get-Sha256Lower -Path $inputFile.File.FullName
        }
    }
    $entryRows = @($entryRows | Sort-Object -Property path)
    $treeLines = ($entryRows | ForEach-Object { "{0}  {1}" -f $_.sha256, $_.path }) -join "`n"
    $treeText = if ($treeLines) { "$treeLines`n" } else { '' }
    $treeBytes = $utf8NoBom.GetBytes($treeText)
    $treeHashAlgorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $treeSha256 = ([System.BitConverter]::ToString($treeHashAlgorithm.ComputeHash($treeBytes))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $treeHashAlgorithm.Dispose()
    }

    $archiveManifest = [ordered]@{
        '$schema' = 'https://json-schema.org/draft/2020-12/schema'
        schema = 'interlanguage.o013.source-backend-archive.v1'
        release_version = '1.0.0'
        language = 'id-ID'
        role = 'O013'
        generated_on = '2026-08-29'
        deterministic_zip = [ordered]@{
            entry_order = 'ordinal path order'
            entry_timestamp = '1980-01-01T00:00:00 (ZIP/DOS timestamp; timezone unspecified)'
            compression = 'deflate optimal (.NET ZipArchive)'
            path_separator = '/'
        }
        roots = @('LICENSES.md', 'components/duncan', 'components/cring', 'components/original')
        excluded = @(
            'qa/visual/**',
            '**/build-output/**',
            '**/reader-build/**',
            '**/cache/**',
            '**/caches/**',
            '**/temp/**',
            '**/tmp/**',
            '**/__pycache__/**',
            '**/.pytest_cache/**',
            'components/duncan/support/DUNCAN_TRANSLATION_LOG.md',
            'components/cring/support/translate_cring_segments.py',
            'components/cring/support/retranslate_cring_context.py',
            'common generated TeX intermediates and Python bytecode'
        )
        provenance = [ordered]@{
            production_model = 'OpenAI Codex gpt-5.6-sol, Ultra'
            instruction_basis = 'on instructions of the user'
            source_authorship_preserved = $true
        }
        component_rights = @(
            [ordered]@{ component_id = 'O013-K02'; scope = 'Duncan seven-root Indonesian edition'; license = 'CC-BY-4.0' },
            [ordered]@{ component_id = 'O013-K03'; scope = 'six selected and repaired CRing spans with Indonesian translation'; license = 'GFDL-1.2-or-later' },
            [ordered]@{ component_id = 'O013-K04'; scope = 'edition-original learner route and mastery layer'; license = 'CC-BY-4.0' }
        )
        content_entry_count = [int]$entryRows.Count
        content_uncompressed_bytes = [int64](($entryRows | Measure-Object -Property bytes -Sum).Sum)
        canonical_entry_list_sha256 = $treeSha256
        entries = $entryRows
    }
    $archiveManifestJson = (($archiveManifest | ConvertTo-Json -Depth 100) -replace "`r`n", "`n") + "`n"
    $archiveManifestBytes = $utf8NoBom.GetBytes($archiveManifestJson)

    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    if (Test-Path -LiteralPath $ArchivePath) {
        Remove-Item -LiteralPath $ArchivePath -Force
    }
    $fileStream = [System.IO.File]::Open($ArchivePath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    try {
        $zip = [System.IO.Compression.ZipArchive]::new($fileStream, [System.IO.Compression.ZipArchiveMode]::Create, $false, $utf8NoBom)
        try {
            $virtualEntryName = 'SOURCE_ARCHIVE_MANIFEST.json'
            $virtualEntry = $zip.CreateEntry($virtualEntryName, [System.IO.Compression.CompressionLevel]::Optimal)
            $virtualEntry.LastWriteTime = $fixedZipTime
            $virtualEntry.ExternalAttributes = -2119958528 # regular file, mode 0644
            $virtualStream = $virtualEntry.Open()
            try {
                $virtualStream.Write($archiveManifestBytes, 0, $archiveManifestBytes.Length)
            }
            finally {
                $virtualStream.Dispose()
            }

            foreach ($inputFile in $InputFiles) {
                $entry = $zip.CreateEntry($inputFile.ArchivePath, [System.IO.Compression.CompressionLevel]::Optimal)
                $entry.LastWriteTime = $fixedZipTime
                $entry.ExternalAttributes = -2119958528 # regular file, mode 0644
                $sourceStream = [System.IO.File]::OpenRead($inputFile.File.FullName)
                $destinationStream = $entry.Open()
                try {
                    $sourceStream.CopyTo($destinationStream)
                }
                finally {
                    $destinationStream.Dispose()
                    $sourceStream.Dispose()
                }
            }
        }
        finally {
            $zip.Dispose()
        }
    }
    finally {
        $fileStream.Dispose()
    }

    return [pscustomobject][ordered]@{
        content_entry_count = [int]$entryRows.Count
        archive_entry_count = [int]($entryRows.Count + 1)
        content_uncompressed_bytes = [int64](($entryRows | Measure-Object -Property bytes -Sum).Sum)
        archive_manifest_bytes = [int64]$archiveManifestBytes.Length
        canonical_entry_list_sha256 = $treeSha256
    }
}

function Test-SourceArchive {
    param(
        [Parameter(Mandatory = $true)][string]$ArchivePath,
        [Parameter(Mandatory = $true)][int]$ExpectedArchiveEntries
    )

    $stream = [System.IO.File]::OpenRead($ArchivePath)
    try {
        $zip = [System.IO.Compression.ZipArchive]::new($stream, [System.IO.Compression.ZipArchiveMode]::Read, $false, $utf8NoBom)
        try {
            if ($zip.Entries.Count -ne $ExpectedArchiveEntries) {
                throw "ZIP entry count mismatch: expected $ExpectedArchiveEntries, found $($zip.Entries.Count)"
            }
            $manifestEntry = $zip.GetEntry('SOURCE_ARCHIVE_MANIFEST.json')
            if ($null -eq $manifestEntry) {
                throw 'ZIP lacks SOURCE_ARCHIVE_MANIFEST.json'
            }
            $manifestReader = [System.IO.StreamReader]::new($manifestEntry.Open(), $utf8NoBom, $true)
            try {
                $embeddedManifest = ($manifestReader.ReadToEnd() | ConvertFrom-Json)
            }
            finally {
                $manifestReader.Dispose()
            }
            foreach ($expected in $embeddedManifest.entries) {
                $entry = $zip.GetEntry([string]$expected.path)
                if ($null -eq $entry) {
                    throw "ZIP lacks expected entry: $($expected.path)"
                }
                if ([int64]$entry.Length -ne [int64]$expected.bytes) {
                    throw "ZIP size mismatch for $($expected.path)"
                }
                $entryStream = $entry.Open()
                $hashAlgorithm = [System.Security.Cryptography.SHA256]::Create()
                try {
                    $actualHash = ([System.BitConverter]::ToString($hashAlgorithm.ComputeHash($entryStream))).Replace('-', '').ToLowerInvariant()
                }
                finally {
                    $hashAlgorithm.Dispose()
                    $entryStream.Dispose()
                }
                if ($actualHash -ne [string]$expected.sha256) {
                    throw "ZIP hash mismatch for $($expected.path)"
                }
            }
            return $true
        }
        finally {
            $zip.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}

[System.IO.Directory]::CreateDirectory($stageRoot) | Out-Null
$unexpected = @(Get-ChildItem -LiteralPath $stageRoot -Force | Where-Object { $_.Name -notin $outputNames })
if ($unexpected.Count -gt 0) {
    throw "Refusing to modify staging directory containing unexpected entries: $($unexpected.Name -join ', ')"
}
foreach ($name in $outputNames) {
    $path = Join-Path $stageRoot $name
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
    }
}

$readerCopies = @(
    @{ Source = 'artifacts/metode-aljabar-jilid-1-id-lengkap.pdf'; Target = '01_metode-aljabar-jilid-1-id-lengkap.pdf' },
    @{ Source = 'artifacts/catatan-teori-representasi-duncan-id.pdf'; Target = '02_catatan-teori-representasi-duncan-id.pdf' },
    @{ Source = 'artifacts/pilihan-aljabar-komutatif-cring-id.pdf'; Target = '03_pilihan-aljabar-komutatif-cring-id.pdf' },
    @{ Source = 'artifacts/o013-rute-pembelajar-dan-penguasaan-id.pdf'; Target = '04_o013-rute-pembelajar-dan-penguasaan-id.pdf' }
)
foreach ($copy in $readerCopies) {
    $source = Join-Path $repoRoot $copy.Source
    $target = Join-Path $stageRoot $copy.Target
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Missing reader: $source"
    }
    [System.IO.File]::Copy($source, $target, $false)
}
[System.IO.File]::Copy((Join-Path $repoRoot 'LICENSES.md'), (Join-Path $stageRoot 'LICENSES.md'), $false)

$componentRoots = @(
    (Join-Path $repoRoot 'repo/components/duncan')
    (Join-Path $repoRoot 'repo/components/cring')
    (Join-Path $repoRoot 'repo/components/original')
)
$buildExtensionPattern = '(?i)(\.aux|\.bbl|\.bcf|\.blg|\.fls|\.log|\.out|\.run\.xml|\.toc|\.xdv|\.synctex\.gz|\.pyc|\.pyo)$'
$archiveInputs = @()
foreach ($componentRoot in $componentRoots) {
    $componentName = Split-Path -Leaf $componentRoot
    foreach ($file in (Get-ChildItem -LiteralPath $componentRoot -Recurse -File | Sort-Object -Property FullName)) {
        $relativeWithinComponent = [System.IO.Path]::GetRelativePath($componentRoot, $file.FullName).Replace('\', '/')
        $archivePath = "components/$componentName/$relativeWithinComponent"
        $excluded = (
            $archivePath -match '/qa/visual/' -or
            $archivePath -match '/(build-output|reader-build|cache|caches|temp|tmp|__pycache__|\.pytest_cache)/' -or
            $archivePath -eq 'components/duncan/support/DUNCAN_TRANSLATION_LOG.md' -or
            $archivePath -eq 'components/cring/support/translate_cring_segments.py' -or
            $archivePath -eq 'components/cring/support/retranslate_cring_context.py' -or
            $archivePath -match $buildExtensionPattern
        )
        if (-not $excluded) {
            $archiveInputs += [pscustomobject]@{
                File = $file
                ArchivePath = $archivePath
            }
        }
    }
}
$archiveInputs += [pscustomobject]@{
    File = Get-Item -LiteralPath (Join-Path $repoRoot 'LICENSES.md')
    ArchivePath = 'LICENSES.md'
}
$archiveInputs = @($archiveInputs | Sort-Object -Property ArchivePath)
if ($archiveInputs.Count -eq 0) {
    throw 'No source/backend files selected for archive'
}

$sourceArchivePath = Join-Path $stageRoot '05_o013-sumber-backend-1.0.0.zip'
$archiveResult = New-DeterministicSourceArchive -ArchivePath $sourceArchivePath -InputFiles $archiveInputs
if (-not (Test-SourceArchive -ArchivePath $sourceArchivePath -ExpectedArchiveEntries $archiveResult.archive_entry_count)) {
    throw 'Source archive verification failed'
}

$schemaText = @'
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.invalid/schemas/interlanguage.o013.aggregate-release-manifest.v1.json",
  "title": "O013 aggregate release manifest",
  "type": "object",
  "additionalProperties": false,
  "required": ["$schema", "schema", "release", "aggregate_rights", "production_provenance", "components", "files", "source_archive"],
  "properties": {
    "$schema": {"const": "o013-aggregate-manifest.schema.json"},
    "schema": {"const": "interlanguage.o013.aggregate-release-manifest.v1"},
    "release": {
      "type": "object",
      "additionalProperties": false,
      "required": ["version", "generated_on", "language", "role", "title", "status", "coverage", "total_reader_pages", "reader_order", "package_size_limit_bytes", "record_license_hint"],
      "properties": {
        "version": {"const": "1.0.0"},
        "generated_on": {"type": "string", "format": "date"},
        "language": {"const": "id-ID"},
        "role": {"const": "O013"},
        "title": {"type": "string", "minLength": 1},
        "status": {"enum": ["complete", "partial", "finishing"]},
        "coverage": {"type": "string", "minLength": 1},
        "total_reader_pages": {"type": "integer", "minimum": 1},
        "reader_order": {"type": "array", "minItems": 4, "maxItems": 4, "uniqueItems": true, "items": {"type": "string", "minLength": 1}},
        "package_size_limit_bytes": {"type": "integer", "minimum": 1},
        "record_license_hint": {"const": "other-open"}
      }
    },
    "aggregate_rights": {
      "type": "object",
      "additionalProperties": false,
      "required": ["spdx_expression", "statement", "license_file"],
      "properties": {
        "spdx_expression": {"const": "NOASSERTION"},
        "statement": {"type": "string", "minLength": 1},
        "license_file": {"const": "LICENSES.md"}
      }
    },
    "production_provenance": {
      "type": "object",
      "additionalProperties": false,
      "required": ["model", "instruction_basis", "source_authorship_preserved", "non_endorsement"],
      "properties": {
        "model": {"const": "OpenAI Codex gpt-5.6-sol, Ultra"},
        "instruction_basis": {"const": "on instructions of the user"},
        "source_authorship_preserved": {"const": true},
        "non_endorsement": {"type": "string", "minLength": 1}
      }
    },
    "components": {
      "type": "array",
      "minItems": 4,
      "maxItems": 4,
      "items": {
        "type": "object",
        "additionalProperties": true,
        "required": ["component_id", "title", "role", "scope", "source_creator", "license", "reader_file"],
        "properties": {
          "component_id": {"type": "string", "pattern": "^O013-K0[1-4]$"},
          "title": {"type": "string", "minLength": 1},
          "role": {"type": "string", "minLength": 1},
          "scope": {"type": "string", "minLength": 1},
          "source_creator": {"type": "string", "minLength": 1},
          "license": {"type": "object", "required": ["spdx", "name", "url"], "properties": {"spdx": {"type": "string", "minLength": 1}, "name": {"type": "string", "minLength": 1}, "url": {"type": "string", "format": "uri"}}},
          "reader_file": {"type": "string", "minLength": 1}
        }
      }
    },
    "files": {
      "type": "array",
      "minItems": 6,
      "items": {"$ref": "#/definitions/file"}
    },
    "source_archive": {
      "type": "object",
      "additionalProperties": false,
      "required": ["file", "deterministic", "archive_entry_count", "content_entry_count", "content_uncompressed_bytes", "canonical_entry_list_sha256", "embedded_manifest"],
      "properties": {
        "file": {"type": "string", "minLength": 1},
        "deterministic": {"const": true},
        "archive_entry_count": {"type": "integer", "minimum": 1},
        "content_entry_count": {"type": "integer", "minimum": 1},
        "content_uncompressed_bytes": {"type": "integer", "minimum": 1},
        "canonical_entry_list_sha256": {"$ref": "#/definitions/sha256"},
        "embedded_manifest": {"const": "SOURCE_ARCHIVE_MANIFEST.json"}
      }
    }
  },
  "definitions": {
    "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "file": {
      "type": "object",
      "additionalProperties": false,
      "required": ["name", "role", "media_type", "bytes", "sha256", "license"],
      "properties": {
        "name": {"type": "string", "minLength": 1},
        "role": {"type": "string", "minLength": 1},
        "media_type": {"type": "string", "minLength": 1},
        "bytes": {"type": "integer", "minimum": 1},
        "sha256": {"$ref": "#/definitions/sha256"},
        "license": {"type": "string", "minLength": 1},
        "component_id": {"type": "string", "minLength": 1},
        "pages": {"type": "integer", "minimum": 1}
      }
    }
  }
}
'@
$schemaPath = Join-Path $stageRoot 'o013-aggregate-manifest.schema.json'
Write-Utf8NoBomLf -Path $schemaPath -Text $schemaText

$files = @(
    (Get-ReleaseFile -Name '01_metode-aljabar-jilid-1-id-lengkap.pdf' -Role 'primary reader; complete Li Volume 1 Indonesian edition' -MediaType 'application/pdf' -License 'CC-BY-4.0 with separately identified embedded/build-closure rights in LICENSES.md' -ComponentId 'O013-K01' -Pages 521)
    (Get-ReleaseFile -Name '02_catatan-teori-representasi-duncan-id.pdf' -Role 'representation-theory reader' -MediaType 'application/pdf' -License 'CC-BY-4.0' -ComponentId 'O013-K02' -Pages 114)
    (Get-ReleaseFile -Name '03_pilihan-aljabar-komutatif-cring-id.pdf' -Role 'commutative-algebra selected-spans reader' -MediaType 'application/pdf' -License 'GFDL-1.2-or-later; no invariant sections or cover texts' -ComponentId 'O013-K03' -Pages 74)
    (Get-ReleaseFile -Name '04_o013-rute-pembelajar-dan-penguasaan-id.pdf' -Role 'edition-original learner route and mastery reader' -MediaType 'application/pdf' -License 'CC-BY-4.0' -ComponentId 'O013-K04' -Pages 7)
    (Get-ReleaseFile -Name '05_o013-sumber-backend-1.0.0.zip' -Role 'deterministic compact source, build, backend, and compact QA-receipt closure for components O013-K02 through O013-K04' -MediaType 'application/zip' -License 'LicenseRef-Component-Specific')
    (Get-ReleaseFile -Name 'LICENSES.md' -Role 'component rights, attribution, font, and embedded-material notices' -MediaType 'text/markdown' -License 'LicenseRef-Documentation')
)

$manifest = [ordered]@{
    '$schema' = 'o013-aggregate-manifest.schema.json'
    schema = 'interlanguage.o013.aggregate-release-manifest.v1'
    release = [ordered]@{
        version = '1.0.0'
        generated_on = '2026-08-29'
        language = 'id-ID'
        role = 'O013'
        title = 'Aljabar Pascasarjana: Paket Pembelajaran Bahasa Indonesia (O013)'
        status = 'complete'
        coverage = 'Empat pembaca: Methods in Algebra Volume 1 lengkap; tujuh akar catatan teori representasi Duncan lengkap dalam penutupan berlisensi; enam rentang CRing yang dipilih secara tepat; dan lapisan rute serta penguasaan orisinal.'
        total_reader_pages = 716
        reader_order = @(
            '01_metode-aljabar-jilid-1-id-lengkap.pdf',
            '02_catatan-teori-representasi-duncan-id.pdf',
            '03_pilihan-aljabar-komutatif-cring-id.pdf',
            '04_o013-rute-pembelajar-dan-penguasaan-id.pdf'
        )
        package_size_limit_bytes = 500000000
        record_license_hint = 'other-open'
    }
    aggregate_rights = [ordered]@{
        spdx_expression = 'NOASSERTION'
        statement = 'Karya gabungan ini tidak memiliki satu lisensi payung. Setiap komponen mempertahankan lisensi, atribusi, riwayat perubahan, dan batas distribusinya sendiri.'
        license_file = 'LICENSES.md'
    }
    production_provenance = [ordered]@{
        model = 'OpenAI Codex gpt-5.6-sol, Ultra'
        instruction_basis = 'on instructions of the user'
        source_authorship_preserved = $true
        non_endorsement = 'Edisi dan integrasi ini independen; tidak ada afiliasi, persetujuan, dukungan, atau pengesahan oleh penulis sumber, institusi mereka, penerbit, atau pemegang merek yang dinyatakan maupun disiratkan.'
    }
    components = @(
        [ordered]@{
            component_id = 'O013-K01'
            title = 'Metode Aljabar, Jilid 1'
            role = 'organizing graduate-algebra spine'
            scope = 'Complete ten-chapter Methods in Algebra, Volume 1 Indonesian edition'
            source_creator = 'Wen-Wei Li'
            source_authority = [ordered]@{
                repository = 'https://github.com/wenweili/AlJabr-1'
                commit = 'c4f7a01f68f5f407906b4b970640cddbbad85f6b'
                tree = '0f9fd52748165ec89a85ba602ccb949a2ce04694'
            }
            license = [ordered]@{
                spdx = 'CC-BY-4.0'
                name = 'Creative Commons Attribution 4.0 International'
                url = 'https://creativecommons.org/licenses/by/4.0/'
                additional_component_rights = @('CC-BY-SA-3.0', 'OFL-1.1', 'GPL-3.0-with-Fandol-font-exception')
                rights_note = 'Substantive book and Indonesian adaptation are CC BY 4.0; embedded fragments, image/source closure, and fonts retain the separate rights recorded in LICENSES.md.'
            }
            reader_file = '01_metode-aljabar-jilid-1-id-lengkap.pdf'
            reader_pages = 521
        },
        [ordered]@{
            component_id = 'O013-K02'
            title = 'Catatan Teori Representasi'
            role = 'representation-theory component'
            scope = 'Complete Indonesian edition of the seven TeX roots in the licensed repository closure; six external assignment sheets, their 49 problems, and one partial solution are excluded.'
            source_creator = 'Alexander Duncan'
            source_authority = [ordered]@{
                repository = 'https://github.com/vtorsor/representation-theory-notes'
                commit = 'c62d36f41189da4bd3da4671668f68720df54ff7'
                tree = 'e83ee440666133b14dec440158a108069a13e9e4'
                archive_sha256 = '60dd9679c9ebe0c28f31794a7b2cb8552f4b7d68038061024972257280a1852c'
            }
            license = [ordered]@{
                spdx = 'CC-BY-4.0'
                name = 'Creative Commons Attribution 4.0 International'
                url = 'https://creativecommons.org/licenses/by/4.0/'
            }
            reader_file = '02_catatan-teori-representasi-duncan-id.pdf'
            reader_pages = 114
        },
        [ordered]@{
            component_id = 'O013-K03'
            title = 'Pilihan Aljabar Komutatif dari CRing Project'
            role = 'commutative-algebra completion'
            scope = 'Only six exact source-line spans, with nine recorded repairs and separately identified original bridges; not a translation of the full CRing Project.'
            source_creator = 'CRing Project'
            source_authority = [ordered]@{
                official_page = 'https://math.uchicago.edu/~amathew/cr.html'
                archive_url = 'https://math.uchicago.edu/~amathew/CRing.zip'
                archive_sha256 = '151cdf5498622251db9999b082c4b756a5a7e22b07ddd79538c0057472a4234d'
                semantic_boundary = 'six exact source line spans'
            }
            license = [ordered]@{
                spdx = 'GFDL-1.2-or-later'
                name = 'GNU Free Documentation License 1.2 or later'
                url = 'https://www.gnu.org/licenses/old-licenses/fdl-1.2.html'
                invariant_sections = @()
                front_cover_texts = @()
                back_cover_texts = @()
                full_license_included = $true
            }
            reader_file = '03_pilihan-aljabar-komutatif-cring-id.pdf'
            reader_pages = 74
        },
        [ordered]@{
            component_id = 'O013-K04'
            title = 'Rute Keterhubungan dan Penguasaan O013'
            role = 'edition-original connective and mastery layer'
            scope = 'Prerequisites, dependency graph, seven-stage route, eight diagnostics, and eight mastery tasks with two hints and one answer each.'
            source_creator = 'OpenAI Codex gpt-5.6-sol, Ultra, on instructions of the user'
            source_authority = [ordered]@{
                kind = 'edition-original'
                source_authors_not_attributed = @('Wen-Wei Li', 'Alexander Duncan', 'CRing Project')
            }
            license = [ordered]@{
                spdx = 'CC-BY-4.0'
                name = 'Creative Commons Attribution 4.0 International'
                url = 'https://creativecommons.org/licenses/by/4.0/'
            }
            reader_file = '04_o013-rute-pembelajar-dan-penguasaan-id.pdf'
            reader_pages = 7
        }
    )
    files = $files
    source_archive = [ordered]@{
        file = '05_o013-sumber-backend-1.0.0.zip'
        deterministic = $true
        archive_entry_count = [int]$archiveResult.archive_entry_count
        content_entry_count = [int]$archiveResult.content_entry_count
        content_uncompressed_bytes = [int64]$archiveResult.content_uncompressed_bytes
        canonical_entry_list_sha256 = [string]$archiveResult.canonical_entry_list_sha256
        embedded_manifest = 'SOURCE_ARCHIVE_MANIFEST.json'
    }
}
$manifestPath = Join-Path $stageRoot 'o013-aggregate-manifest.json'
$manifestJson = (($manifest | ConvertTo-Json -Depth 100) -replace "`r`n", "`n") + "`n"
Write-Utf8NoBomLf -Path $manifestPath -Text $manifestJson

$schemaValid = Test-Json -Json (Get-Content -LiteralPath $manifestPath -Raw) -SchemaFile $schemaPath
if (-not $schemaValid) {
    throw 'Aggregate manifest failed JSON Schema validation'
}

$sumNames = @($outputNames | Where-Object { $_ -ne 'SHA256SUMS.txt' } | Sort-Object)
$sumLines = foreach ($name in $sumNames) {
    $path = Join-Path $stageRoot $name
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing expected release file before checksum generation: $name"
    }
    "{0}  {1}" -f (Get-Sha256Lower -Path $path), $name
}
Write-Utf8NoBomLf -Path (Join-Path $stageRoot 'SHA256SUMS.txt') -Text (($sumLines -join "`n") + "`n")

$finalFiles = @(Get-ChildItem -LiteralPath $stageRoot -File | Sort-Object -Property Name)
if ($finalFiles.Count -ne $outputNames.Count) {
    throw "Release inventory mismatch: expected $($outputNames.Count), found $($finalFiles.Count)"
}
$finalBytes = [int64](($finalFiles | Measure-Object -Property Length -Sum).Sum)
if ($finalBytes -gt 500000000) {
    throw "Release exceeds 500,000,000-byte cap: $finalBytes"
}

[pscustomobject][ordered]@{
    status = 'PASS'
    staging_directory = $stageRoot
    file_count = $finalFiles.Count
    total_bytes = $finalBytes
    cap_bytes = 500000000
    source_archive_entries = $archiveResult.archive_entry_count
    source_archive_content_bytes = $archiveResult.content_uncompressed_bytes
    source_archive_verified = $true
    manifest_schema_valid = $true
    files = @($finalFiles | ForEach-Object {
        [ordered]@{
            name = $_.Name
            bytes = [int64]$_.Length
            sha256 = Get-Sha256Lower -Path $_.FullName
        }
    })
} | ConvertTo-Json -Depth 10
