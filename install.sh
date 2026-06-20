#!/bin/bash
set -e

echo "========================================================"
echo "AlphaAlign Installer (macOS / Linux)"
echo "========================================================"
echo ""

echo "[1/3] Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    exit 1
fi
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed or not in PATH."
    exit 1
fi

echo ""
echo "[2/3] Setting up Backend (Python)..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
echo "Installing Python dependencies..."
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo ""
echo "[3/3] Setting up Frontend (Node.js)..."
cd frontend
echo "Installing Node.js dependencies..."
npm install
cd ..

echo ""
echo "========================================================"
echo "Installation Complete!"
echo ""
echo "To start AlphaAlign, run: ./start.sh"
echo "========================================================"
