$ErrorActionPreference = 'Stop'
$repoDir = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$testDir = Join-Path $repoDir 'artifacts/qa007-controller'
$production = Join-Path $repoDir 'artifacts/qa007-production-164856a/src/Aemeath.Host/Aemeath.Host.csproj'
$candidate = Join-Path $repoDir 'artifacts/qa007-art-395fce2/assets/characters/aemeath-v1/source/art011-package'
New-Item -ItemType Directory -Path $testDir -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Art011ControllerChecks.cs.txt') -Destination (Join-Path $testDir 'Program.cs')
$escapedProduction = [Security.SecurityElement]::Escape($production)
@"
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0-windows</TargetFramework><UseWPF>true</UseWPF><RuntimeIdentifier>win-x64</RuntimeIdentifier><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup>
  <ItemGroup><ProjectReference Include="$escapedProduction" /></ItemGroup>
</Project>
"@ | Set-Content -LiteralPath (Join-Path $testDir 'Qa007.csproj') -Encoding utf8
$sdkExe = Join-Path $env:LOCALAPPDATA 'Aemeath/toolchains/dotnet/10.0.401/dotnet.exe'
& $sdkExe run --project (Join-Path $testDir 'Qa007.csproj') -c Release -- $candidate
if ($LASTEXITCODE -ne 0) { throw 'QA007 controller checks failed' }
