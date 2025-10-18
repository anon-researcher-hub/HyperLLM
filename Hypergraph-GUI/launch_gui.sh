#!/bin/bash
# HyperLLM GUI Launcher for Linux/Mac
# This script launches the HyperLLM GUI application

echo "========================================"
echo " HyperLLM Multi-Agent System GUI"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "Starting GUI..."
echo ""

# Launch the GUI
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to start GUI"
    read -p "Press Enter to continue..."
fi

