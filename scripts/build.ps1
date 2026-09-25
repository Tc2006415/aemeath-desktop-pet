param([switch]$Publish)
$ErrorActionPreference = 'Stop'
$repoDir = Split-Path $PSScriptRoot -Parent
$dotnetExe = Join-Path $env:LOCALAPPDATA 'Aemeath/toolchains/dotnet/10.0.401/dotnet.exe'
if (-not (Test-Path -LiteralPath $dotnetExe)) { throw 'Required user SDK 10.0.401 is not installed.' }
Push-Location $repoDir
try {
    & $dotnetExe restore Aemeath.slnx --locked-mode
    if ($LASTEXITCODE -ne 0) { throw 'Restore failed' }
    & $dotnetExe build Aemeath.slnx -c Release --no-restore
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    if ($Publish) {
        & $dotnetExe publish src/Aemeath.Host/Aemeath.Host.csproj -c Release -r win-x64 --self-contained true -p:PublishTrimmed=false -p:PublishSingleFile=false -o artifacts/host-win-x64
        if ($LASTEXITCODE -ne 0) { throw 'Publish failed' }
    }
} finally { Pop-Location }
