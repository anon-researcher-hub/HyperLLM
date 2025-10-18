@echo off
REM HyperLLM GUI Launcher for Windows
REM This script launches the HyperLLM GUI application

echo ========================================
echo  HyperLLM Multi-Agent System GUI
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo Starting GUI...
echo.

REM Launch the GUI
python main.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start GUI
    pause
)

