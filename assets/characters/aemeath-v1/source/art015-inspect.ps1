$ErrorActionPreference = 'Stop'
$art015Results = @()
foreach ($art015Name in @('b2-v1','b2-v2','b7-v1','b7-v2')) {
    $art015Path = Join-Path $PSScriptRoot "art015-$art015Name-96.png"
    if (Test-Path -LiteralPath $art015Path) {
        $art015Result = & (Join-Path $PSScriptRoot '../../../../scripts/qa/Inspect-Png.ps1') -Path $art015Path | ConvertFrom-Json
        if ($art015Result.Width -ne 96 -or $art015Result.Height -ne 104 -or $art015Result.PngBitDepth -ne 8 -or $art015Result.PngColorType -ne 6 -or $art015Result.Semitransparent -ne 0 -or $art015Result.Bytes -gt 262144) { throw "Invalid candidate $art015Name" }
        $art015Results += [pscustomobject]@{Candidate=$art015Name; Inspection=$art015Result}
    }
}
$art015Results | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 (Join-Path $PSScriptRoot 'art015-png-inspect.json')
$art015Results | ConvertTo-Json -Depth 5
