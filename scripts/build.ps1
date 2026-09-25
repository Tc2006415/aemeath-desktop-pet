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
        # Remove stale packaged assets only; source assets and other artifacts are never touched.
        $publishRoot = [IO.Path]::GetFullPath((Join-Path $repoDir 'artifacts/host-win-x64'))
        $assetOutput = [IO.Path]::GetFullPath((Join-Path $publishRoot 'assets'))
        if (-not $assetOutput.StartsWith(([IO.Path]::GetFullPath($repoDir) + [IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) { throw 'Publish assets escaped workspace.' }
        foreach ($directory in @((Join-Path $repoDir 'artifacts'), $publishRoot, $assetOutput)) {
            if ((Test-Path -LiteralPath $directory) -and ((Get-Item -LiteralPath $directory).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Refusing publish cleanup through a reparse point.' }
        }
        if (Test-Path -LiteralPath $assetOutput) { Remove-Item -LiteralPath $assetOutput -Recurse -Force }
        & $dotnetExe publish src/Aemeath.Host/Aemeath.Host.csproj -c Release -r win-x64 --self-contained true -p:PublishTrimmed=false -p:PublishSingleFile=false -o artifacts/host-win-x64
        if ($LASTEXITCODE -ne 0) { throw 'Publish failed' }
        & "$PSScriptRoot/Test-PublishedAssets.ps1" -PublishDirectory $publishRoot
    }
} finally { Pop-Location }
