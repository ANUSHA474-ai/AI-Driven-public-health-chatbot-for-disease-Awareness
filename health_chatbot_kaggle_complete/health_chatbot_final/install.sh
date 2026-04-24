#!/bin/bash

echo "========================================================================"
echo "AI HEALTH CHATBOT - AUTOMATED INSTALLER"
echo "========================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/5] Checking Python version..."
python3 --version

echo ""
echo "[2/5] Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies"
    echo "Try running: python3 -m pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "[3/5] Creating necessary directories..."
mkdir -p models data templates static/css static/js

echo ""
echo "[4/5] Verifying dataset..."
if [ -f "data/diseases.csv" ]; then
    echo "✓ Dataset found: diseases.csv"
else
    echo "✗ WARNING: diseases.csv not found in data folder"
fi

echo ""
echo "[5/5] Installation complete!"
echo ""
echo "========================================================================"
echo "READY TO START!"
echo "========================================================================"
echo ""
echo "To start the application, run:"
echo "    python3 app.py"
echo ""
echo "Then open your browser to:"
echo "    http://localhost:5000"
echo ""
echo "========================================================================"
echo ""
