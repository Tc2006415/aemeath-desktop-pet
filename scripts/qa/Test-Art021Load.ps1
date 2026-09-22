$ErrorActionPreference = 'Stop'
$repoDir = (Resolve-Path "$PSScriptRoot/../..").Path
$qaDir = Join-Path $repoDir 'artifacts/qa010'
$formal = 'C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1'
$source = 'C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source'
$candidate = Join-Path $qaDir 'package'
New-Item -ItemType Directory "$candidate/frames" -Force | Out-Null
Copy-Item "$formal/manifest.json" "$candidate/manifest.json"
Copy-Item "$formal/frames/*.png" "$candidate/frames"
foreach ($name in @('soft-light','soft-peak')) { Copy-Item "$source/art021-$name-v1-m2-96.png" "$candidate/frames/$name.png" }
$changes = @(Get-ChildItem "$candidate/frames/*.png" | Where-Object { (Get-FileHash $_.FullName).Hash -ne (Get-FileHash "$formal/frames/$($_.Name)").Hash } | Select-Object -ExpandProperty Name)
if (($changes -join ',') -ne 'soft-light.png,soft-peak.png') { throw 'Unexpected candidate differences' }
if ((Get-FileHash "$candidate/manifest.json").Hash -ne (Get-FileHash "$formal/manifest.json").Hash) { throw 'Manifest changed' }
$production = [Security.SecurityElement]::Escape((Join-Path $repoDir 'artifacts/qa009-dev-74d8442/src/Aemeath.Host/Aemeath.Host.csproj'))
@"
<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0-windows</TargetFramework><UseWPF>true</UseWPF><RuntimeIdentifier>win-x64</RuntimeIdentifier><ImplicitUsings>enable</ImplicitUsings></PropertyGroup><ItemGroup><ProjectReference Include="$production" /></ItemGroup></Project>
"@ | Set-Content "$qaDir/Qa010.csproj" -Encoding utf8
@'
using Aemeath.Host;
using Aemeath.Presentation;
var p=PackageLoader.Load(args[0],PngDecoder.Decode);
if(p.SchemaVersion!=2 || p.Version!="0.4.0" || p.Images.Count!=16 || p.Clips.Count!=6 || p.DisabledActions.Count!=0 || p.Clips["idle-soft"].DurationMs!=1400 || p.Clips["drag-release"].EntrySequences.Count!=16) throw new Exception("Candidate loader mismatch");
Console.WriteLine($"PASS: schema={p.SchemaVersion}; version={p.Version}; images={p.Images.Count}; actions={p.Clips.Count}; disabled=0; idle=1400ms; entries=16; manifest={p.ManifestSha256}");
'@ | Set-Content "$qaDir/Program.cs" -Encoding utf8
$sdkExe = Join-Path $env:LOCALAPPDATA 'Aemeath/toolchains/dotnet/10.0.401/dotnet.exe'
& $sdkExe run --project "$qaDir/Qa010.csproj" -c Release -- $candidate | Tee-Object "$qaDir/loader-result.txt"
if ($LASTEXITCODE -ne 0) { throw 'ART021 loader check failed' }
