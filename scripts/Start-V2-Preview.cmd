@echo off
setlocal
set "PET_ROOT=%~dp0.."
start "" "%PET_ROOT%\artifacts\native-v2-win-x64\Aemeath.Host.exe" --package "%PET_ROOT%\assets\characters\aemeath-v1\source\art036-package" --mode automatic --scale 2
endlocal
