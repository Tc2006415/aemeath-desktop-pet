$ErrorActionPreference='Stop'
$art013Root=$PSScriptRoot
$art013Repo=(Resolve-Path (Join-Path $art013Root '../../../..')).Path
$art013Exe=Join-Path $art013Repo 'artifacts/host-win-x64/Aemeath.Host.exe'
$art013Package=Join-Path $art013Root 'art013-package'
$art013Log=Join-Path $art013Root 'art013-host-hold.jsonl'
if (Test-Path -LiteralPath $art013Log) { throw 'Keep existing log; use a fresh evidence filename for rerun' }
$art013Proc=Start-Process -FilePath $art013Exe -ArgumentList @('--package',('"'+$art013Package+'"'),'--diagnostics',('"'+$art013Log+'"'),'--mode','manual','--clip','drag-hold','--scale','2','--exit-after-ms','4200') -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
if (-not $art013Proc.WaitForExit(12000) -or $art013Proc.ExitCode -ne 0) { throw 'Host failed' }
[pscustomobject]@{pid=$art013Proc.Id;exitCode=$art013Proc.ExitCode;exeSha256=(Get-FileHash -LiteralPath $art013Exe).Hash;manifestSha256=(Get-FileHash -LiteralPath (Join-Path $art013Package 'manifest.json')).Hash} | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $art013Root 'art013-host-run.json')
$art013Checks=foreach ($art013File in Get-ChildItem -LiteralPath (Join-Path $art013Package 'frames') -Filter *.png) {
    $art013Info=& (Join-Path $art013Repo 'scripts/qa/Inspect-Png.ps1') -Path $art013File.FullName | ConvertFrom-Json
    $art013Info | Add-Member -NotePropertyName Name -NotePropertyValue $art013File.Name
    $art013Info
}
$art013Checks | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 (Join-Path $art013Root 'art013-png-inspect.json')
Get-Content (Join-Path $art013Root 'art013-host-run.json')
$art013Checks | Format-Table Name,Width,Height,Bytes,Semitransparent
