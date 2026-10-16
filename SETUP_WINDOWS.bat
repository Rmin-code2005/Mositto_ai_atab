@echo off
setlocal
cd /d "%~dp0"
echo Mositto - first-time setup (internet required)
if exist ".venv\Scripts\python.exe" goto install
py -3.11 --version >nul 2>&1
if errorlevel 1 goto missing
py -3.11 -m venv .venv
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -c "import fastapi, uvicorn, multipart, numpy, PIL, ultralytics; from deepface import DeepFace"
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -c "import hashlib,pathlib; p=pathlib.Path('requirements.txt'); pathlib.Path('.venv/mositto-ready').write_text(hashlib.sha256(p.read_bytes()).hexdigest())"
if errorlevel 1 goto failed
echo Setup completed. Double-click START_WINDOWS.bat to open the app.
exit /b 0
:missing
echo Python 3.11 and the Windows Python Launcher are required.
echo Install Python 3.11 from python.org, then run this file again.
exit /b 1
:failed
echo Setup failed. Check the error above, network access and README_FA.md.
exit /b 1
