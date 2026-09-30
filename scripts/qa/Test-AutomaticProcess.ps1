$ErrorActionPreference = 'Stop'
$repoDir = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$exe = Join-Path $repoDir 'artifacts/host-win-x64/Aemeath.Host.exe'
$logFile = Join-Path $repoDir ('artifacts/qa-automatic-' + [Guid]::NewGuid().ToString('N') + '.jsonl')
# App-owned diagnostic output only; no native window inspection or input injection.
$probe = Start-Process -FilePath $exe -WindowStyle Hidden -ArgumentList @('--mode', 'automatic', '--diagnostics', ('"' + $logFile + '"'), '--exit-after-ms', '18000') -WorkingDirectory $env:TEMP -PassThru
if (-not $probe.WaitForExit(30000)) { throw "Owned PID $($probe.Id) did not exit; inspect manually." }
if ($probe.ExitCode -ne 0) { throw "Host exit: $($probe.ExitCode)" }
$events = @(Get-Content -LiteralPath $logFile | ForEach-Object { $_ | ConvertFrom-Json })
foreach ($kind in @('control-rendered', 'package-loaded', 'pet-loaded', 'render-callback', 'shutdown')) {
    if ($kind -notin $events.kind) { throw "Missing $kind" }
}
$frames = @($events | Where-Object kind -eq 'frame')
$smile = @($frames | Where-Object { $_.data.Action -eq 'idle-smile' })
$idle = @($frames | Where-Object { $_.data.Action -eq 'idle-soft' })
if ($smile.Count -eq 0 -or $idle.Count -eq 0) { throw 'Missing idle/smile' }
if ($smile[0].ms - $idle[0].ms -lt 14900) { throw 'Early smile' }
if ($idle[-1].ms -le $smile[-1].ms) { throw 'No return to idle' }
if (@($events | Where-Object kind -eq 'natural-end').Count -ne 1) { throw 'Expected exactly one completion' }
if (@($frames | Where-Object { $_.data.automatic -ne $true }).Count) { throw 'Unexpected manual mode' }
[pscustomobject]@{ PID=$probe.Id; ExitCode=$probe.ExitCode; Log=$logFile; SmileDelayMs=($smile[0].ms-$idle[0].ms); SHA256=(Get-FileHash -LiteralPath $exe).Hash; Evidence='App-owned diagnostics; not native UI acceptance' } | ConvertTo-Json
