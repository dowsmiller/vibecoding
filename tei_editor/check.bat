@echo off
setlocal

cd /d "%~dp0"
if errorlevel 1 goto folder_error

if not exist ".venv\Scripts\python.exe" goto environment_error

echo Checking data\transcription.xml...
echo.
".venv\Scripts\python.exe" check_tei.py
set "CHECK_STATUS=%ERRORLEVEL%"
echo.
pause
exit /b %CHECK_STATUS%

:folder_error
echo ERROR: I could not open the TEI editor folder.
goto show_error

:environment_error
echo ERROR: The app setup is missing. Double-click start.bat once, then try this checker again.

:show_error
echo.
pause
exit /b 1
