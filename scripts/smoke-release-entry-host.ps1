param([Parameter(Mandatory)][string]$PackageRoot)
$ErrorActionPreference = 'Stop'
$repoDir = Split-Path $PSScriptRoot -Parent
$exe = Join-Path $repoDir 'artifacts/host-win-x64/Aemeath.Host.exe'
$logFile = Join-Path $repoDir 'artifacts/smoke-release-entry.jsonl'
$manifestPath = Join-Path $PackageRoot 'manifest.json'
$manifestHash = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash
if ($manifestHash -ne 'EAB91ECB10037DA7320D4E9C9321C8DCE0F122D3B9D5DAA6E101A55E1E319DA3') { throw 'Expected fixed ART019 candidate.' }
$probe = Start-Process -FilePath $exe -ArgumentList @('--package', ('"' + $PackageRoot + '"'), '--mode', 'manual', '--clip', 'drag-hold', '--diagnostics', ('"' + $logFile + '"'), '--exit-after-ms', '4500') -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
if (-not $probe.WaitForExit(15000)) { throw "Owned probe PID $($probe.Id) did not exit." }
if ($probe.ExitCode -ne 0) { throw "Host exit $($probe.ExitCode)" }
$events = @(Get-Content -LiteralPath $logFile | ForEach-Object { $_ | ConvertFrom-Json })
$loaded = @($events | Where-Object kind -eq 'package-loaded')
if ($loaded.Count -ne 1 -or $loaded[0].data.Version -ne '0.4.0' -or $loaded[0].data.SchemaVersion -ne 2 -or $loaded[0].data.ManifestSha256 -ne $manifestHash -or @($loaded[0].data.disabled).Count -ne 0) { throw 'Candidate loading evidence failed.' }
$inventory = @($events | Where-Object kind -eq 'release-entry-inventory')
if ($inventory.Count -ne 1 -or @($inventory[0].data).Count -ne 16) { throw 'Expected 16 preloaded entries.' }
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
foreach ($entry in $inventory[0].data) {
    $expected = $manifest.actions.'drag-release'.entrySequences.PSObject.Properties[$entry.source].Value
    if ($null -eq $expected -or ($expected.durationMs | Measure-Object -Sum).Sum -ne $entry.durationMs -or (($expected.path -join '|') -cne ($entry.paths -join '|'))) { throw 'Loaded entry paths/timing differ from manifest.' }
}
$frames = @($events | Where-Object { $_.kind -eq 'frame' -and $_.data.Action -eq 'drag-hold' })
if (@($frames.data.FrameIndex | Sort-Object -Unique).Count -ne 20) { throw 'Not all 20 hold timing items observed.' }
foreach ($frame in $frames) {
    if ($frame.data.path -cne $manifest.actions.'drag-hold'.frames[$frame.data.FrameIndex].path -or $frame.data.packageEpoch -ne $loaded[0].data.packageEpoch -or $frame.data.submission -le 0) { throw 'Submitted effective frame evidence failed.' }
}
foreach ($kind in @('render-callback','pet-stopped','shutdown')) { if ($kind -notin $events.kind) { throw "Missing $kind" } }
if ('package-rejected' -in $events.kind -or 'position-error' -in $events.kind) { throw 'Host reported failure.' }
if ((Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash -ne $manifestHash) { throw 'Candidate changed during probe.' }
[pscustomobject]@{Pid=$probe.Id;ExitCode=$probe.ExitCode;ManifestSha256=$manifestHash;Entries=16;HoldItems=20;Log=$logFile;Evidence='Real loader/render submissions; no native drag simulation or visual acceptance'}
