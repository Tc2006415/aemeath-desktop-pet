$ErrorActionPreference = 'Stop'
$repoDir = Split-Path $PSScriptRoot -Parent
$exe = Join-Path $repoDir 'artifacts/host-win-x64/Aemeath.Host.exe'
$logFile = Join-Path $repoDir 'artifacts/smoke-automatic.jsonl'
if (-not (Test-Path -LiteralPath $exe)) { throw 'Run scripts/build.ps1 -Publish first.' }
# No package/mode override: exercise the double-click defaults from another cwd.
# Diagnostics and timed shutdown provide own-process evidence, not native visual acceptance.
$probe = Start-Process -FilePath $exe -ArgumentList @('--diagnostics', ('"' + $logFile + '"'), '--exit-after-ms', '18500') -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
if (-not $probe.WaitForExit(30000)) { throw "Owned smoke PID $($probe.Id) did not exit; inspect the application." }
if ($probe.ExitCode -ne 0) { throw "Host exited with code $($probe.ExitCode)." }
$events = @(Get-Content -LiteralPath $logFile | ForEach-Object { $_ | ConvertFrom-Json })
$loaded = @($events | Where-Object kind -eq 'package-loaded')
if ($loaded.Count -ne 1 -or $loaded[0].data.Id -ne 'aemeath-v1' -or $loaded[0].data.Version -ne '0.3.0' -or $loaded[0].data.Kind -ne 'character' -or @($loaded[0].data.disabled).Count -ne 0) { throw 'Default character package/version was not loaded successfully.' }
if (@($events | Where-Object { $_.kind -in @('package-rejected','position-error') }).Count -gt 0) { throw 'Application reported a package or positioning failure.' }
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
[pscustomobject]@{Pid=$probe.Id; ExitCode=$probe.ExitCode; Package='aemeath-v1/0.3.0'; Log=$logFile; Evidence='Default automatic / own-process only; character UI unverified'}
