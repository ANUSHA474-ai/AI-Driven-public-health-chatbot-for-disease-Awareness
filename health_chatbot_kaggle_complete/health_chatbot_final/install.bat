@echo off
echo ========================================================================
echo AI HEALTH CHATBOT - AUTOMATED INSTALLER
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

echo.
echo [2/5] Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Try running: py -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo [3/5] Creating necessary directories...
if not exist "models" mkdir models
if not exist "data" mkdir data
if not exist "templates" mkdir templates
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js

echo.
echo [4/5] Verifying dataset...
if exist "data\diseases.csv" (
    echo ✓ Dataset found: diseases.csv
) else (
    echo ✗ WARNING: diseases.csv not found in data folder
)

echo.
echo [5/5] Installation complete!
echo.
echo ========================================================================
echo READY TO START!
echo ========================================================================
echo.
echo To start the application, run:
echo     python app.py
echo.
echo Then open your browser to:
echo     http://localhost:5000
echo.
echo ========================================================================
echo.
pause
