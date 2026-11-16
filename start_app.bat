@echo off
setlocal

set "ROOT=%~dp0"
set "VENV_PYTHON=%ROOT%.venv\Scripts\python.exe"
pushd "%ROOT%" || (
    echo Could not open the project folder.
    echo Press any key to end the script...
    pause
    exit /b 1
)

if exist "%VENV_PYTHON%" goto python_ready

set "PYTHON_CMD="
py -3.13 --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3.13"

if not defined PYTHON_CMD (
    python --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if defined PYTHON_CMD goto create_venv

echo Python 3.13 was not found. Downloading the official Python installer...
set "PYTHON_VERSION=3.13"
set "INSTALLER=%TEMP%\python-%PYTHON_VERSION%-amd64.exe"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'Stop'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe' -OutFile '%INSTALLER%'"
if errorlevel 1 (
    echo Failed to download Python. Check your internet connection and try again.
    pause
    exit /b 1
)

"%INSTALLER%" /quiet InstallAllUsers=0 TargetDir="%LOCALAPPDATA%\Programs\Python\Python313" Include_pip=1 Include_launcher=0 PrependPath=0
if errorlevel 1 (
    echo Python installation failed.
    del "%INSTALLER%" >nul 2>&1
    pause
    exit /b 1
)
del "%INSTALLER%" >nul 2>&1

set "PATH=%LOCALAPPDATA%\Programs\Python\Python313;%LOCALAPPDATA%\Programs\Python\Python313\Scripts;%PATH%"
if not exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    echo Python installation completed, but python.exe was not found.
    pause
    exit /b 1
)
set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"

:create_venv
%PYTHON_CMD% -m venv "%ROOT%.venv"
if errorlevel 1 (
    echo Failed to create the project virtual environment.
    pause
    exit /b 1
)

:python_ready
set "PATH=%ROOT%.venv\Scripts;%PATH%"
set "DEADLOCK_SEEDER_API_URL=http://127.0.0.1:8000"

echo Installing or updating project requirements...
"%VENV_PYTHON%" -m pip install -r "%ROOT%requirements.txt"
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

start "Deadlock Backend" /D "%ROOT%" cmd.exe /k ""%VENV_PYTHON%" -m uvicorn backend.src.handlers.lambda_handler:app --reload"
start "Deadlock Frontend" /D "%ROOT%" cmd.exe /k ""%VENV_PYTHON%" -m streamlit run frontend\legacy_streamlit_app.py"

echo Backend and frontend started in separate windows.
popd
exit /b 0
