@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto dependencies
py -3.13 --version >nul 2>&1
if not errorlevel 1 (
    py -3.13 -m venv .venv
    goto venv_created
)
py -3.12 --version >nul 2>&1
if not errorlevel 1 (
    py -3.12 -m venv .venv
    goto venv_created
)
py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    py -3.11 -m venv .venv
    goto venv_created
)
echo Python 3.11 ou plus recent est requis. Voir README.md.
pause
exit /b 1
:venv_created
if not exist ".venv\Scripts\python.exe" exit /b 1
:dependencies
".venv\Scripts\python.exe" -c "import streamlit, pytest, tzdata" >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Installation incomplete. Voir README.md et verifier la connexion Internet.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.headless false --browser.gatherUsageStats false
