$ErrorActionPreference = 'Stop'
$repoDir = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$testDir = Join-Path $repoDir 'artifacts/qa009-independent'
$production = Join-Path $repoDir 'artifacts/qa009-dev-74d8442/src/Aemeath.Host/Aemeath.Host.csproj'
$candidate = Join-Path $repoDir 'artifacts/qa009-art019'
if ((Get-FileHash "$candidate/manifest.json").Hash -ne 'EAB91ECB10037DA7320D4E9C9321C8DCE0F122D3B9D5DAA6E101A55E1E319DA3') { throw 'Wrong candidate' }
New-Item -ItemType Directory -Path $testDir -Force | Out-Null
Copy-Item "$PSScriptRoot/ReleaseEntry009.cs.txt" "$testDir/Program.cs"
$escapedProduction = [Security.SecurityElement]::Escape($production)
@"
<Project Sdk="Microsoft.NET.Sdk">
 <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0-windows</TargetFramework><UseWPF>true</UseWPF><RuntimeIdentifier>win-x64</RuntimeIdentifier><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup>
 <ItemGroup><ProjectReference Include="$escapedProduction" /></ItemGroup>
</Project>
"@ | Set-Content "$testDir/Qa009.csproj" -Encoding utf8
$sdkExe = Join-Path $env:LOCALAPPDATA 'Aemeath/toolchains/dotnet/10.0.401/dotnet.exe'
& $sdkExe run --project "$testDir/Qa009.csproj" -c Release -- $candidate $testDir
if ($LASTEXITCODE -ne 0) { throw 'QA009 independent checks failed' }
