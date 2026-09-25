param([string]$PublishDirectory = (Join-Path (Split-Path $PSScriptRoot -Parent) 'artifacts/host-win-x64'))
$ErrorActionPreference = 'Stop'
$repoDir = Split-Path $PSScriptRoot -Parent
$expected = @()
foreach ($package in @('characters/aemeath-v1', 'diagnostic')) {
    $sourceRoot = Join-Path $repoDir "assets/$package"
    $manifest = Get-Content -LiteralPath "$sourceRoot/manifest.json" -Raw | ConvertFrom-Json
    $paths = @('manifest.json') + @($manifest.actions.PSObject.Properties.Value.frames.path | Sort-Object -Unique)
    foreach ($path in $paths) {
        $relative = "$package/$path"
        $source = Join-Path $sourceRoot $path
        $published = Join-Path $PublishDirectory "assets/$relative"
        if (-not (Test-Path -LiteralPath $published -PathType Leaf)) { throw "Missing runtime asset: $relative" }
        if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $published -Algorithm SHA256).Hash) { throw "Asset hash mismatch: $relative" }
        $expected += $relative
    }
}
$assetRoot = Join-Path $PublishDirectory 'assets'
$actual = @(Get-ChildItem -LiteralPath $assetRoot -Recurse -File | ForEach-Object { [IO.Path]::GetRelativePath($assetRoot, $_.FullName).Replace('\', '/') })
if (@(Compare-Object ($expected | Sort-Object) ($actual | Sort-Object)).Count -ne 0) { throw 'Published asset inventory contains extra or missing files.' }
[pscustomobject]@{RuntimeAssetCount=$actual.Count;Sha256='All match repository';ExtraFiles=0}
