@echo off
setlocal
set "PET_ROOT=%~dp0.."
start "" "%PET_ROOT%\artifacts\host-win-x64\Aemeath.Host.exe" --mode automatic --scale 2
endlocal
