param([switch]$Publish)
$ErrorActionPreference = 'Stop'
$repoDir = Split-Path $PSScriptRoot -Parent
$dotnetExe = Join-Path $env:LOCALAPPDATA 'Aemeath/toolchains/dotnet/10.0.401/dotnet.exe'
Push-Location $repoDir
try {
    & "$PSScriptRoot/build.ps1" -Publish:$Publish
    & $dotnetExe test tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj -c Release --no-build --no-restore --logger trx
    if ($LASTEXITCODE -ne 0) { throw 'Behavior tests failed' }
    git diff --check
    if ($LASTEXITCODE -ne 0) { throw 'Whitespace check failed' }
} finally { Pop-Location }
