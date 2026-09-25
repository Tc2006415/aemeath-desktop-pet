param([Parameter(Mandatory)][string]$FixtureRoot)
$ErrorActionPreference = 'Stop'
$fixture = (Resolve-Path -LiteralPath $FixtureRoot).Path
$tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\')
if (-not $fixture.StartsWith($tempRoot + '\aemeath-qa-', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Only the generated QA temporary fixture is accepted.'
}
$probeRoot = Join-Path $tempRoot ('aemeath-qa-reparse-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $probeRoot | Out-Null
$rootAlias = Join-Path $probeRoot 'root-alias'
New-Item -ItemType Junction -Path $rootAlias -Target $fixture | Out-Null
$framesPackage = Join-Path $probeRoot 'frames-package'
New-Item -ItemType Directory -Path $framesPackage | Out-Null
Copy-Item -LiteralPath (Join-Path $fixture 'manifest.json') -Destination $framesPackage
New-Item -ItemType Junction -Path (Join-Path $framesPackage 'frames') -Target (Join-Path $fixture 'frames') | Out-Null
$sdkExe = Join-Path $env:LOCALAPPDATA 'Aemeath/toolchains/dotnet/10.0.401/dotnet.exe'
$project = Join-Path $PSScriptRoot 'DiagnosticChecks.csproj'
foreach ($candidate in @($rootAlias, $framesPackage)) {
    & $sdkExe run --project $project -c Release --no-build -- reject-package $candidate
    if ($LASTEXITCODE -ne 0) { throw "Reparse rejection failed: $candidate" }
}
# Keep only generated fixtures/links for reproducibility; do not recursively delete through reparse points.
Write-Output "REPARSE_FIXTURE_ROOT=$probeRoot"
