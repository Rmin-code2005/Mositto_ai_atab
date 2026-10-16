@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto setup
".venv\Scripts\python.exe" -c "import hashlib,pathlib,sys; m=pathlib.Path('.venv/mositto-ready'); sys.exit(0 if m.exists() and m.read_text()==hashlib.sha256(pathlib.Path('requirements.txt').read_bytes()).hexdigest() else 1)"
if errorlevel 1 goto setup
goto launch
:setup
call "%~dp0SETUP_WINDOWS.bat"
if errorlevel 1 goto failed
:launch
".venv\Scripts\python.exe" launcher.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo Mositto could not start. The error is shown above.
pause
exit /b 1
