@echo off
echo Gibraltar Bus Tracker Setup
echo ========================

echo.
echo This script requires Python to be installed.
echo.
echo To install Python:
echo 1. Go to https://www.python.org/downloads/
echo 2. Download Python 3.8 or newer
echo 3. Run the installer and make sure to check "Add Python to PATH"
echo 4. Restart your command prompt
echo 5. Run this script again
echo.

python --version 2>nul
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python first.
    pause
    exit /b 1
)

echo Python found! Installing requirements...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo Setup complete! Now running the bus tracker scraper...
echo.

python gibraltar_bus_scraper.py

pause