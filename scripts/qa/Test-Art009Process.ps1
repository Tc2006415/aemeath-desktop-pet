$ErrorActionPreference = 'Stop'
$repoDir = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$exe = Join-Path $repoDir 'artifacts/host-win-x64/Aemeath.Host.exe'
$package = Join-Path $repoDir 'assets/characters/aemeath-v1/source/art009-v1-package'
$logFile = Join-Path $repoDir ('artifacts/qa006-host-' + [Guid]::NewGuid().ToString('N') + '.jsonl')
$probe = Start-Process -FilePath $exe -WindowStyle Hidden -ArgumentList @('--package', ('"' + $package + '"'), '--mode', 'automatic', '--diagnostics', ('"' + $logFile + '"'), '--exit-after-ms', '18500') -WorkingDirectory $env:TEMP -PassThru
if (-not $probe.WaitForExit(30000)) { throw "Owned PID $($probe.Id) did not exit; inspect manually" }
if ($probe.ExitCode -ne 0) { throw "Host exit $($probe.ExitCode)" }
$events = @(Get-Content -LiteralPath $logFile | ForEach-Object { $_ | ConvertFrom-Json })
foreach ($kind in @('control-rendered','package-loaded','pet-loaded','render-callback','shutdown')) { if ($kind -notin $events.kind) { throw "Missing $kind" } }
$loaded = @($events | Where-Object kind -eq 'package-loaded')
if ($loaded.Count -ne 1 -or $loaded[0].data.Version -ne '0.3.0' -or $loaded[0].data.disabled.Count) { throw 'Wrong candidate' }
$frames = @($events | Where-Object kind -eq 'frame')
$smile = @($frames | Where-Object { $_.data.Action -eq 'idle-smile' })
$idle = @($frames | Where-Object { $_.data.Action -eq 'idle-soft' })
if (($smile.data.FrameIndex -join ',') -ne '0,1,2,3,4,5') { throw 'Smile did not show every item in order' }
if ((@($idle.data.FrameIndex | Sort-Object -Unique) -join ',') -ne '0,1,2,3,4,5') { throw 'Idle items missing' }
if (@($events | Where-Object kind -eq 'natural-end').Count -ne 1 -or $idle[-1].ms -le $smile[-1].ms) { throw 'Missing single completion / return to idle' }
if ($smile[0].ms-$idle[0].ms -lt 14900) { throw 'Early smile observation' }
if (@($events | Where-Object { $_.kind -match 'error|rejected' }).Count) { throw 'Host error' }
if (@($frames | Where-Object { $_.data.automatic -ne $true }).Count) { throw 'Wrong mode' }
[pscustomobject]@{ PID=$probe.Id; ExitCode=$probe.ExitCode; Package=$package; SmileIndices=($smile.data.FrameIndex -join ','); SmileDelayMs=($smile[0].ms-$idle[0].ms); Log=$logFile; SHA256=(Get-FileHash -LiteralPath $exe).Hash; Evidence='App-owned process output; not native visual/input acceptance' } | ConvertTo-Json
