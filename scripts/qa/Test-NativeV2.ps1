$ErrorActionPreference = 'Stop'
$repoDir = (Resolve-Path "$PSScriptRoot/../..").Path
$testDir = Join-Path $repoDir 'artifacts/qa011/checks'
$candidate = Join-Path $repoDir 'artifacts/qa011/art036-package'
if ((Get-FileHash "$candidate/manifest.json").Hash -ne '95CF8F8102F9631D0A02AE40A46FA497F61D9D423FF350191A399104A0A4B182') { throw 'Wrong ART036' }
$production = [Security.SecurityElement]::Escape((Join-Path $repoDir 'artifacts/qa011-dev-c9bac87/src/Aemeath.Host/Aemeath.Host.csproj'))
New-Item -ItemType Directory $testDir -Force | Out-Null
Copy-Item "$PSScriptRoot/NativeV2Checks.cs.txt" "$testDir/Program.cs"
@"
<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0-windows</TargetFramework><UseWPF>true</UseWPF><RuntimeIdentifier>win-x64</RuntimeIdentifier><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup><ItemGroup><ProjectReference Include="$production" /></ItemGroup></Project>
"@ | Set-Content "$testDir/Qa011.csproj" -Encoding utf8
$sdkExe = Join-Path $env:LOCALAPPDATA 'Aemeath/toolchains/dotnet/10.0.401/dotnet.exe'
& $sdkExe run --project "$testDir/Qa011.csproj" -c Release -- $candidate $testDir
if ($LASTEXITCODE -ne 0) { throw 'Native v2 independent checks failed' }
