@echo off
echo Gibraltar Bus Tracker - Modern Web Application
echo =============================================

echo.
echo Checking Python installation...
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found!
echo.

echo Installing/updating requirements...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install requirements.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Starting Gibraltar Bus Tracker server...
echo.
echo The web application will be available at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python server.py

pause