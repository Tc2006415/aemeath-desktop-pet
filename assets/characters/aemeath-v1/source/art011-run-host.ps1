$ErrorActionPreference = 'Stop'
$art011Source = $PSScriptRoot
$art011Repo = (Resolve-Path (Join-Path $art011Source '../../../..')).Path
$art011Exe = Join-Path $art011Repo 'artifacts/host-win-x64/Aemeath.Host.exe'
$art011Package = Join-Path $art011Source 'art011-package'
$art011Runs = foreach ($art011Clip in @('drag-pickup','drag-hold','drag-release')) {
    $art011Log = Join-Path $art011Source ('art011-expression-host-' + $art011Clip + '.jsonl')
    if (Test-Path -LiteralPath $art011Log) { throw ('Keep existing evidence: ' + $art011Log) }
    $art011Proc = Start-Process -FilePath $art011Exe -ArgumentList @('--package',('"' + $art011Package + '"'),'--diagnostics',('"' + $art011Log + '"'),'--mode','manual','--clip',$art011Clip,'--scale','2','--exit-after-ms','2200') -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
    if (-not $art011Proc.WaitForExit(10000)) { throw 'Host timed out' }
    if ($art011Proc.ExitCode -ne 0) { throw 'Host failed' }
    [pscustomobject]@{clip=$art011Clip;pid=$art011Proc.Id;exitCode=$art011Proc.ExitCode;exeSha256=(Get-FileHash -LiteralPath $art011Exe).Hash;manifestSha256=(Get-FileHash -LiteralPath (Join-Path $art011Package 'manifest.json')).Hash}
}
$art011Runs | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 (Join-Path $art011Source 'art011-expression-host-runs.json')
$art011Runs | Format-Table clip,pid,exitCode
$art011Pngs = foreach ($art011File in Get-ChildItem -LiteralPath (Join-Path $art011Package 'frames') -Filter *.png) {
    $art011Info = & (Join-Path $art011Repo 'scripts/qa/Inspect-Png.ps1') -Path $art011File.FullName | ConvertFrom-Json
    $art011Info | Add-Member -NotePropertyName File -NotePropertyValue $art011File.Name
    $art011Info
}
$art011Pngs | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 (Join-Path $art011Source 'art011-expression-png-inspect.json')
$art011Pngs | Format-Table File,Width,Height,Bytes,Semitransparent
