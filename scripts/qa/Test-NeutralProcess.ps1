$ErrorActionPreference = 'Stop'
$repoDir = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$exe = Join-Path $repoDir 'artifacts/host-win-x64/Aemeath.Host.exe'
$package = Join-Path $repoDir 'assets/characters/aemeath-v1'
$logFile = Join-Path $repoDir ('artifacts/qa-neutral-' + [Guid]::NewGuid().ToString('N') + '.jsonl')
$probe = Start-Process -FilePath $exe -WindowStyle Hidden -ArgumentList @('--package', ('"' + $package + '"'), '--mode', 'automatic', '--diagnostics', ('"' + $logFile + '"'), '--exit-after-ms', '17000') -WorkingDirectory $env:TEMP -PassThru
if (-not $probe.WaitForExit(30000)) { throw "Owned PID $($probe.Id) did not exit; inspect manually" }
if ($probe.ExitCode -ne 0) { throw "Host exit $($probe.ExitCode)" }
$events = @(Get-Content -LiteralPath $logFile | ForEach-Object { $_ | ConvertFrom-Json })
foreach ($kind in @('control-rendered','package-loaded','pet-loaded','render-callback','shutdown')) {
    if ($kind -notin $events.kind) { throw "Missing $kind" }
}
$loaded = @($events | Where-Object kind -eq 'package-loaded')
if ($loaded.Count -ne 1 -or $loaded[0].data.Id -ne 'aemeath-v1' -or $loaded[0].data.Kind -ne 'character' -or $loaded[0].data.disabled.Count -ne 0) { throw 'Wrong package' }
$frames = @($events | Where-Object kind -eq 'frame')
if ($frames.Count -eq 0 -or @($frames | Where-Object { $_.data.Action -ne 'neutral' -or $_.data.FrameIndex -ne 0 -or $_.data.automatic -ne $true }).Count -gt 0) { throw 'Fallback unexpectedly changed' }
# Layout redraws may log the same frame again; only a new playback instance is a restart.
if (@($frames.data.PlaybackId | Select-Object -Unique).Count -ne 1) { throw 'Fallback playback restarted' }
if (@($events | Where-Object { $_.kind -match 'error|rejected|natural-end' }).Count) { throw 'Unexpected failure or completion' }
$duration = ($events | Where-Object kind -eq 'shutdown')[0].ms - $frames[0].ms
if ($duration -lt 15000) { throw 'Probe did not cover smile threshold' }
[pscustomobject]@{ PID=$probe.Id; ExitCode=$probe.ExitCode; NeutralDurationMs=$duration; Log=$logFile; SHA256=(Get-FileHash -LiteralPath $exe).Hash; Evidence='App-owned process log only; no native input/desktop visual acceptance' } | ConvertTo-Json
