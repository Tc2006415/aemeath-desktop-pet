param([Parameter(Mandatory)][string]$PackageRoot)
$ErrorActionPreference = 'Stop'
$repoDir = Split-Path $PSScriptRoot -Parent
$exe = Join-Path $repoDir 'artifacts/native-v2-win-x64/Aemeath.Host.exe'
$manifestPath = Join-Path $PackageRoot 'manifest.json'
$fixedSha = '95CF8F8102F9631D0A02AE40A46FA497F61D9D423FF350191A399104A0A4B182'
if ((Get-FileHash -LiteralPath $manifestPath).Hash -ne $fixedSha) { throw 'Expected fixed ART036 manifest.' }
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$runs = @(@{Name='automatic';Mode='automatic';Clip=$null;Ms=12000},@{Name='manual-wink';Mode='manual';Clip='idle-smile';Ms=3000},@{Name='manual-release';Mode='manual';Clip='drag-release';Ms=3000})
foreach ($run in $runs) {
    $logFile = Join-Path $repoDir ('artifacts/smoke-v2-' + $run.Name + '.jsonl')
    $arguments = @('--package', ('"' + $PackageRoot + '"'), '--mode', $run.Mode, '--diagnostics', ('"' + $logFile + '"'), '--exit-after-ms', $run.Ms)
    if ($run.Clip) { $arguments += @('--clip', $run.Clip) }
    $probe = Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
    if (-not $probe.WaitForExit(25000)) { throw "Owned probe PID $($probe.Id) did not exit; inspect this process." }
    if ($probe.ExitCode -ne 0) { throw "Host exited $($probe.ExitCode)" }
    $events = @(Get-Content -LiteralPath $logFile | ForEach-Object { $_ | ConvertFrom-Json })
    $loaded = @($events | Where-Object kind -eq 'package-loaded')
    if ($loaded.Count -ne 1 -or $loaded[0].data.SchemaVersion -ne 3 -or $loaded[0].data.Version -ne '0.5.0' -or $loaded[0].data.ManifestSha256 -ne $fixedSha -or $loaded[0].data.profile -ne 'layered-idle-drag-v1' -or @($loaded[0].data.disabled).Count -ne 0) { throw 'Incorrect loaded package.' }
    $inventory = @($events | Where-Object kind -eq 'behavior-inventory')
    if ($inventory.Count -ne 1 -or $inventory[0].data.keys -ne 64 -or $inventory[0].data.routes -ne 64 -or $inventory[0].data.tails -ne 5) { throw 'Incomplete behavior inventory.' }
    $frames = @($events | Where-Object kind -eq 'frame')
    if ($frames.Count -eq 0) { throw 'No render submissions.' }
    foreach ($frame in $frames) {
        $registered = $manifest.behavior.images.PSObject.Properties[$frame.data.FrameKey].Value
        if ($null -eq $registered -or $registered.path -cne $frame.data.path -or $frame.data.submission -le 0 -or $frame.data.packageEpoch -ne $loaded[0].data.packageEpoch) { throw 'Invalid submitted key/path/epoch.' }
    }
    if ($run.Mode -eq 'automatic') {
        if ('blink' -notin $frames.data.BehaviorPhase -or 'idle' -notin $frames.data.BehaviorPhase) { throw 'Automatic idle/blink not observed.' }
    } else {
        $played = @($frames | Where-Object { $_.data.Action -eq $run.Clip })
        if (@($played.data.FrameIndex | Sort-Object -Unique).Count -ne @($manifest.actions.PSObject.Properties[$run.Clip].Value.frames).Count) { throw 'Manual base frames incomplete.' }
        if (@($events | Where-Object kind -eq 'natural-end').Count -ne 1) { throw 'Expected one manual completion.' }
    }
    foreach ($kind in @('render-callback','pet-stopped','shutdown')) { if ($kind -notin $events.kind) { throw "Missing $kind" } }
    if (@($events | Where-Object { $_.kind -in @('package-rejected','position-error') }).Count -ne 0) { throw 'Host failure logged.' }
    [pscustomobject]@{Run=$run.Name;Pid=$probe.Id;ExitCode=$probe.ExitCode;ManifestSha256=$fixedSha;Log=$logFile;Evidence='Owned process/render submissions only; native mouse and visual acceptance not performed'}
}
if ((Get-FileHash -LiteralPath $manifestPath).Hash -ne $fixedSha) { throw 'Manifest changed during smoke.' }
