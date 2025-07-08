@echo off
REM SAM Simple Launcher for Windows
REM This batch file starts SAM using Streamlit

echo Starting SAM...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if Streamlit is available
python -m streamlit --version >nul 2>&1
if errorlevel 1 (
    echo Error: Streamlit is not installed
    echo Installing Streamlit...
    python -m pip install streamlit
    if errorlevel 1 (
        echo Failed to install Streamlit
        pause
        exit /b 1
    )
)

REM Start SAM
echo Starting SAM on http://localhost:8502
echo Press Ctrl+C to stop SAM
echo.

python -m streamlit run secure_streamlit_app.py --server.port 8502 --server.address localhost --browser.gatherUsageStats false

echo.
echo SAM has stopped
pause
