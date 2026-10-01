$ErrorActionPreference = 'Stop'
$repoDir = Split-Path $PSScriptRoot -Parent
$exe = Join-Path $repoDir 'artifacts/host-win-x64/Aemeath.Host.exe'
$logFile = Join-Path $repoDir 'artifacts/smoke-automatic.jsonl'
if (-not (Test-Path -LiteralPath $exe)) { throw 'Run scripts/build.ps1 -Publish first.' }
# No package/mode override: exercise the double-click defaults from another cwd.
# Diagnostics and timed shutdown provide own-process evidence, not native visual acceptance.
$probe = Start-Process -FilePath $exe -ArgumentList @('--diagnostics', ('"' + $logFile + '"'), '--exit-after-ms', '12000') -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
if (-not $probe.WaitForExit(25000)) { throw "Owned smoke PID $($probe.Id) did not exit; inspect the application." }
if ($probe.ExitCode -ne 0) { throw "Host exited with code $($probe.ExitCode)." }
$events = @(Get-Content -LiteralPath $logFile | ForEach-Object { $_ | ConvertFrom-Json })
$loaded = @($events | Where-Object kind -eq 'package-loaded')
if ($loaded.Count -ne 1 -or $loaded[0].data.Id -ne 'aemeath-v1' -or $loaded[0].data.Version -ne '0.5.0' -or $loaded[0].data.SchemaVersion -ne 3 -or $loaded[0].data.Kind -ne 'character' -or $loaded[0].data.profile -ne 'layered-idle-drag-v1' -or $loaded[0].data.ManifestSha256 -ne '95CF8F8102F9631D0A02AE40A46FA497F61D9D423FF350191A399104A0A4B182' -or @($loaded[0].data.disabled).Count -ne 0) { throw 'Default character package/version was not loaded successfully.' }
$inventory = @($events | Where-Object kind -eq 'behavior-inventory')
if ($inventory.Count -ne 1 -or $inventory[0].data.keys -ne 64 -or $inventory[0].data.routes -ne 64 -or $inventory[0].data.tails -ne 5) { throw 'Default behavior inventory is incomplete.' }
if (@($events | Where-Object { $_.kind -in @('package-rejected','position-error') }).Count -gt 0) { throw 'Application reported a package or positioning failure.' }
foreach ($kind in @('control-rendered', 'package-loaded', 'pet-loaded', 'render-callback', 'shutdown')) {
    if ($kind -notin $events.kind) { throw "Missing own-process evidence: $kind" }
}
$frames = @($events | Where-Object kind -eq 'frame')
if ('idle' -notin $frames.data.BehaviorPhase -or 'blink' -notin $frames.data.BehaviorPhase) { throw 'Automatic idle/blink was not observed.' }
if (@($events | Where-Object { $_.kind -eq 'frame' -and $_.data.automatic -ne $true }).Count -gt 0) { throw 'Unexpected manual frame in automatic run.' }
[pscustomobject]@{Pid=$probe.Id; ExitCode=$probe.ExitCode; Package='aemeath-v1/0.5.0'; Log=$logFile; Evidence='Default automatic / own-process only; native mouse and visual interaction unverified'}
