$ErrorActionPreference = 'Stop'
$repoDir = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$exe = Join-Path $repoDir 'artifacts/host-win-x64/Aemeath.Host.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw 'Publish the fixed host commit first.' }
$runDir = Join-Path $repoDir ('artifacts/qa-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $runDir | Out-Null
$badPackage = Join-Path $runDir 'bad-neutral'
Copy-Item -LiteralPath (Join-Path $repoDir 'assets/diagnostic') -Destination $badPackage -Recurse
[IO.File]::WriteAllBytes((Join-Path $badPackage 'frames/neutral.png'), [byte[]](1,2,3))
foreach ($probeCase in @(
    @{ Name='loop-2'; Clip='idle-soft'; Scale=2; Bad=$false },
    @{ Name='once-1'; Clip='idle-smile'; Scale=1; Bad=$false },
    @{ Name='bad-neutral'; Clip='neutral'; Scale=2; Bad=$true }
)) {
    $logFile = Join-Path $runDir ($probeCase.Name + '.jsonl')
    $hostArgs = @('--diagnostics', ('"' + $logFile + '"'), '--clip', $probeCase.Clip, '--scale', $probeCase.Scale, '--exit-after-ms', '2500')
    if ($probeCase.Bad) { $hostArgs += @('--package', ('"' + $badPackage + '"')) }
    # App-owned diagnostics only. No synthetic input, screenshots or native UI automation.
    $process = Start-Process -FilePath $exe -ArgumentList $hostArgs -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
    if (-not $process.WaitForExit(15000)) { throw "Owned QA PID $($process.Id) did not exit; no keyboard-exit claim can be made." }
    if ($process.ExitCode -ne 0) { throw "Host $($probeCase.Name) exited $($process.ExitCode)" }
    $events = @(Get-Content -LiteralPath $logFile | ForEach-Object { $_ | ConvertFrom-Json })
    foreach ($kind in @('startup','control-rendered','timed-smoke-exit','shutdown')) {
        if ($kind -notin $events.kind) { throw "$($probeCase.Name): missing $kind" }
    }
    if ($probeCase.Bad) {
        if ('package-rejected' -notin $events.kind -or 'pet-loaded' -in $events.kind) { throw 'First bad package did not stay at control-only path.' }
        $rejection = @($events | Where-Object kind -eq 'package-rejected')
        if ($rejection[0].data.retained) { throw 'First bad load claims retained package.' }
    } else {
        if ('position-error' -in $events.kind -or 'package-rejected' -in $events.kind) { throw 'Host reported positioning/package error.' }
        foreach ($kind in @('package-loaded','pet-loaded','render-callback','layout')) {
            if ($kind -notin $events.kind) { throw "$($probeCase.Name): missing $kind" }
        }
        $layout = @($events | Where-Object kind -eq 'layout')[-1].data
        if ($layout.dpi -le 0 -or $layout.widthPx -ne 96*$probeCase.Scale -or $layout.heightPx -ne 104*$probeCase.Scale) { throw 'Reported physical geometry differs from contract.' }
        $ends = @($events | Where-Object kind -eq 'natural-end')
        if ($probeCase.Clip -eq 'idle-smile') {
            if ($ends.Count -ne 1) { throw 'Once clip did not end exactly once.' }
            $frames = @($events | Where-Object kind -eq 'frame')
            if ($frames[-1].data.Action -ne 'neutral') { throw 'Once clip failed to return to neutral.' }
        } else {
            if ($ends.Count -ne 0) { throw 'Loop unexpectedly emitted natural-end.' }
            $secondFrames = @($events | Where-Object { $_.kind -eq 'frame' -and $_.data.Action -eq 'idle-soft' -and $_.data.FrameIndex -eq 1 })
            if ($secondFrames.Count -lt 2) { throw 'Loop did not advance across two cycles.' }
        }
        Write-Output ("Geometry {0}: DPI={1}; {2}x{3} px; clientOffset={4},{5}" -f $probeCase.Name,$layout.dpi,$layout.widthPx,$layout.heightPx,$layout.clientOffsetX,$layout.clientOffsetY)
    }
    Write-Output "PASS process probe $($probeCase.Name); PID=$($process.Id); ExitCode=$($process.ExitCode); Log=$logFile"
}
Get-FileHash -LiteralPath $exe -Algorithm SHA256
Write-Output 'LIMIT: own-process diagnostics/timed shutdown only; transparency, mouse, hit testing and keyboard/Narrator remain unverified.'
