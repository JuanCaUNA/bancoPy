@echo off
:: filepath: c:\Users\juanc\Documents\GitHub\bancoPy\pythonProject\run.bat
:: SINPE Banking System Startup Script

echo 🏦 SINPE Banking System - Python Implementation
echo ==============================================

:: Check if Python 3 is installed
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python 3 is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

:: Check for existing virtual environment or create a new one
if exist .venv\ (
    echo ✅ Using existing virtual environment in .venv
) else (
    if exist venv\ (
        echo ✅ Using existing virtual environment in venv
    ) else (
        echo 🔧 Creating virtual environment...
        python -m venv .venv
        if %ERRORLEVEL% NEQ 0 (
            echo ❌ Failed to create virtual environment.
            exit /b 1
        )
    )
)

:: Activate virtual environment (try both potential locations)
echo 🔄 Activating virtual environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
    ) else (
        echo ❌ Virtual environment activation script not found.
        exit /b 1
    )
)

:: Create database directory if it doesn't exist
if not exist database mkdir database

:: Run the application
echo 🚀 Starting SINPE Banking System...
echo.
echo Features:
echo   • Terminal UI with rich interface
echo   • REST API server on http://127.0.0.1:5000
echo   • SQLite database with sample data
echo   • SINPE transfer simulation
echo   • User and account management
echo.
echo Press Ctrl+C to stop the application
echo.

python main.py

:: Deactivate virtual environment when done
if exist .venv\Scripts\deactivate.bat (
    call .venv\Scripts\deactivate.bat
) else (
    if exist venv\Scripts\deactivate.bat (
        call venv\Scripts\deactivate.bat
    )
)