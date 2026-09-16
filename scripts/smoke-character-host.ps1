$ErrorActionPreference = 'Stop'
$repoDir = Split-Path $PSScriptRoot -Parent
$exe = Join-Path $repoDir 'artifacts/host-win-x64/Aemeath.Host.exe'
$logFile = Join-Path $repoDir 'artifacts/smoke-automatic.jsonl'
if (-not (Test-Path -LiteralPath $exe)) { throw 'Run scripts/build.ps1 -Publish first.' }
# Own-process playback evidence only. No simulated mouse events or character visual acceptance.
$probe = Start-Process -FilePath $exe -ArgumentList @('--mode', 'automatic', '--diagnostics', ('"' + $logFile + '"'), '--exit-after-ms', '18000') -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
if (-not $probe.WaitForExit(30000)) { throw "Owned smoke PID $($probe.Id) did not exit; inspect the application." }
if ($probe.ExitCode -ne 0) { throw "Host exited with code $($probe.ExitCode)." }
$events = @(Get-Content -LiteralPath $logFile | ForEach-Object { $_ | ConvertFrom-Json })
foreach ($kind in @('control-rendered', 'package-loaded', 'pet-loaded', 'render-callback', 'shutdown')) {
    if ($kind -notin $events.kind) { throw "Missing own-process evidence: $kind" }
}
$smile = @($events | Where-Object { $_.kind -eq 'frame' -and $_.data.Action -eq 'idle-smile' })
$idle = @($events | Where-Object { $_.kind -eq 'frame' -and $_.data.Action -eq 'idle-soft' })
if ($smile.Count -eq 0 -or $idle.Count -eq 0) { throw 'Automatic idle or smile was not observed.' }
if ($smile[0].ms - $idle[0].ms -lt 14900) { throw 'Automatic smile started before the idle wait elapsed.' }
if (@($events | Where-Object kind -eq 'natural-end').Count -ne 1) { throw 'Expected one smile completion.' }
if ($idle[-1].ms -le $smile[-1].ms) { throw 'Smile did not return to idle.' }
if (@($events | Where-Object { $_.kind -eq 'frame' -and $_.data.automatic -ne $true }).Count -gt 0) { throw 'Unexpected manual frame in automatic run.' }
[pscustomobject]@{Pid=$probe.Id; ExitCode=$probe.ExitCode; Log=$logFile; Evidence='Diagnostic package / own-process only; character UI unverified'}
