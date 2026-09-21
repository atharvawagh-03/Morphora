@echo off
REM ═══════════════════════════════════════════════════════════════════
REM Morphora — Dual Process Launcher (Exhibition / Gallery Kiosk Mode)
REM Launches TouchDesigner project and Python gesture detection engine
REM ═══════════════════════════════════════════════════════════════════

title Morphora Exhibition Launcher
echo ===================================================
echo   Starting Morphora Interactive Installation...
echo ===================================================

cd /d "%~dp0\.."

REM 1. Check if virtual environment exists
if not exist "python\venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found in python\venv.
    echo Run: cd python ^&^& python -m venv venv ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM 2. Launch TouchDesigner (if installed)
echo [1/2] Launching TouchDesigner network...
set "TD_EXE=C:\Program Files\Derivative\TouchDesigner\bin\TouchDesigner.exe"
if exist "%TD_EXE%" (
    if exist "touchdesigner\main.toe" (
        start "" "%TD_EXE%" "%CD%\touchdesigner\main.toe"
    ) else (
        start "" "%TD_EXE%"
    )
    ping 127.0.0.1 -n 4 >nul
) else if exist "touchdesigner\main.toe" (
    start "" "touchdesigner\main.toe"
    ping 127.0.0.1 -n 4 >nul
) else (
    echo [WARNING] TouchDesigner not found. Proceeding with Python only.
)

REM 3. Launch Python Gesture Tracker
echo [2/2] Starting Python MediaPipe Gesture Detection loop...
cd python
start "Morphora Python Tracker" venv\Scripts\python.exe main.py

echo.
echo ===================================================
echo   Morphora is active and streaming OSC on :7000!
echo   Press 'q' inside tracker window to quit.
echo ===================================================
