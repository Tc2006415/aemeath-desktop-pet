param([ValidateSet('neutral', 'idle-soft', 'idle-smile')][string]$Clip = 'idle-soft', [ValidateRange(1,3)][int]$Scale = 2)
$ErrorActionPreference = 'Stop'
$repoDir = Split-Path $PSScriptRoot -Parent
$exe = Join-Path $repoDir 'artifacts/host-win-x64/Aemeath.Host.exe'
$logFile = Join-Path $repoDir "artifacts/smoke-$Clip-$Scale.jsonl"
if (-not (Test-Path -LiteralPath $exe)) { throw 'Run scripts/validate.ps1 -Publish first.' }
# This intentionally displays the app. Timed application shutdown is not a keyboard/UI acceptance check.
$probe = Start-Process -FilePath $exe -ArgumentList @('--diagnostics', ('"' + $logFile + '"'), '--clip', $Clip, '--scale', "$Scale", '--exit-after-ms', '3500') -WorkingDirectory $env:TEMP -PassThru
if (-not $probe.WaitForExit(15000)) { throw "Owned smoke PID $($probe.Id) did not exit; inspect the application." }
if ($probe.ExitCode -ne 0) { throw "Host exited with code $($probe.ExitCode)." }
$events = @(Get-Content -LiteralPath $logFile | ForEach-Object { $_ | ConvertFrom-Json })
foreach ($kind in @('control-rendered', 'package-loaded', 'pet-loaded', 'render-callback', 'layout', 'shutdown')) {
    if ($kind -notin $events.kind) { throw "Missing own-process evidence: $kind" }
}
if ('package-rejected' -in $events.kind -or 'position-error' -in $events.kind) { throw 'Host diagnostics reported failure.' }
if ($Clip -eq 'idle-smile' -and @($events | Where-Object kind -eq 'natural-end').Count -ne 1) { throw 'Once completion count was not one.' }
if ($Clip -eq 'idle-soft' -and @($events | Where-Object { $_.kind -eq 'frame' -and $_.data.Action -eq 'idle-soft' -and $_.data.FrameIndex -eq 1 }).Count -lt 2) { throw 'Loop did not advance across two cycles.' }
[pscustomobject]@{ Pid = $probe.Id; ExitCode = $probe.ExitCode; Clip = $Clip; Scale = $Scale; Log = $logFile; Evidence = 'Own process only; native UI unverified' }
