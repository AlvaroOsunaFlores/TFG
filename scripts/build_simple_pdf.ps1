param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath,
    [int]$MaxCharsPerLine = 92
)

function Escape-PdfText {
    param([string]$Text)
    $escaped = $Text.Replace('\', '\\')
    $escaped = $escaped.Replace('(', '\(')
    $escaped = $escaped.Replace(')', '\)')
    return $escaped
}

function Wrap-Line {
    param(
        [string]$Line,
        [int]$Width
    )

    if ([string]::IsNullOrWhiteSpace($Line)) {
        return @("")
    }

    $words = $Line -split '\s+'
    $lines = New-Object System.Collections.Generic.List[string]
    $current = ""

    foreach ($word in $words) {
        if ($current.Length -eq 0) {
            $current = $word
            continue
        }

        if (($current.Length + 1 + $word.Length) -le $Width) {
            $current = "$current $word"
        } else {
            $lines.Add($current)
            $current = $word
        }
    }

    if ($current.Length -gt 0) {
        $lines.Add($current)
    }
    return $lines
}

function Add-PdfObject {
    param(
        [System.Collections.Generic.List[byte[]]]$Objects,
        [string]$Content
    )

    $encoding = [System.Text.Encoding]::GetEncoding(28591)
    $Objects.Add($encoding.GetBytes($Content))
    return $Objects.Count
}

$inputFullPath = Resolve-Path $InputPath
$rawLines = Get-Content -Path $inputFullPath -Encoding UTF8
$renderLines = New-Object System.Collections.Generic.List[string]

foreach ($line in $rawLines) {
    foreach ($wrapped in (Wrap-Line -Line $line -Width $MaxCharsPerLine)) {
        $renderLines.Add($wrapped)
    }
}

$linesPerPage = 46
$pages = @()
for ($index = 0; $index -lt $renderLines.Count; $index += $linesPerPage) {
    $end = [Math]::Min($index + $linesPerPage - 1, $renderLines.Count - 1)
    $pages += ,($renderLines[$index..$end])
}

$objects = New-Object 'System.Collections.Generic.List[byte[]]'
$fontId = Add-PdfObject -Objects $objects -Content "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
$pagesId = 2
$pageCount = $pages.Count
$pageIds = @()
$contentIds = @()

for ($i = 0; $i -lt $pageCount; $i++) {
    $pageIds += 3 + $i
}
for ($i = 0; $i -lt $pageCount; $i++) {
    $contentIds += 3 + $pageCount + $i
}
$catalogId = 3 + ($pageCount * 2)

$kids = ($pageIds | ForEach-Object { "$_ 0 R" }) -join ' '
$null = Add-PdfObject -Objects $objects -Content "<< /Type /Pages /Kids [ $kids ] /Count $pageCount >>"

for ($i = 0; $i -lt $pageCount; $i++) {
    $pageContent = "<< /Type /Page /Parent $pagesId 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 $fontId 0 R >> >> /Contents $($contentIds[$i]) 0 R >>"
    $null = Add-PdfObject -Objects $objects -Content $pageContent
}

foreach ($page in $pages) {
    $contentBuilder = New-Object System.Text.StringBuilder
    $null = $contentBuilder.AppendLine("BT")
    $null = $contentBuilder.AppendLine("/F1 11 Tf")
    $null = $contentBuilder.AppendLine("50 760 Td")

    $first = $true
    foreach ($line in $page) {
        if (-not $first) {
            $null = $contentBuilder.AppendLine("0 -15 Td")
        }
        $escaped = Escape-PdfText $line
        $null = $contentBuilder.AppendLine("($escaped) Tj")
        $first = $false
    }
    $null = $contentBuilder.AppendLine("ET")
    $stream = $contentBuilder.ToString()
    $streamBytes = [System.Text.Encoding]::GetEncoding(28591).GetBytes($stream)
    $contentObject = "<< /Length $($streamBytes.Length) >>`nstream`n$stream`nendstream"
    $null = Add-PdfObject -Objects $objects -Content $contentObject
}

$null = Add-PdfObject -Objects $objects -Content "<< /Type /Catalog /Pages $pagesId 0 R >>"

$outputDir = Split-Path -Parent $OutputPath
if ($outputDir) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

$encoding = [System.Text.Encoding]::GetEncoding(28591)
$memory = New-Object System.IO.MemoryStream
$writer = New-Object System.IO.BinaryWriter($memory, $encoding)
$writer.Write($encoding.GetBytes("%PDF-1.4`n"))

$offsets = New-Object System.Collections.Generic.List[int]
$offsets.Add(0)

for ($i = 0; $i -lt $objects.Count; $i++) {
    $offsets.Add([int]$memory.Position)
    $writer.Write($encoding.GetBytes("$($i + 1) 0 obj`n"))
    $writer.Write($objects[$i])
    $writer.Write($encoding.GetBytes("`nendobj`n"))
}

$xrefStart = [int]$memory.Position
$writer.Write($encoding.GetBytes("xref`n"))
$writer.Write($encoding.GetBytes("0 $($objects.Count + 1)`n"))
$writer.Write($encoding.GetBytes("0000000000 65535 f `n"))
for ($i = 1; $i -le $objects.Count; $i++) {
    $writer.Write($encoding.GetBytes(("{0:0000000000} 00000 n `n" -f $offsets[$i])))
}

$writer.Write($encoding.GetBytes("trailer`n"))
$writer.Write($encoding.GetBytes("<< /Size $($objects.Count + 1) /Root $catalogId 0 R >>`n"))
$writer.Write($encoding.GetBytes("startxref`n$xrefStart`n%%EOF"))
$writer.Flush()

$outputFile = New-Item -ItemType File -Force -Path $OutputPath
[System.IO.File]::WriteAllBytes($outputFile.FullName, $memory.ToArray())
