#!/bin/bash
set -e

echo "========================================================"
echo "AlphaAlign Installer (macOS / Linux)"
echo "========================================================"
echo ""

INSTALL_DIR="$HOME/AlphaAlign"
REPO_URL="https://github.com/AlphaHorizon-AI/AlphaAlign/archive/refs/heads/main.zip"
TEMP_ZIP="/tmp/AlphaAlign_main.zip"
TEMP_EXTRACT="/tmp/AlphaAlign_extract"

echo "[1/4] Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    exit 1
fi
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed or not in PATH."
    exit 1
fi

echo ""
echo "[2/4] Downloading AlphaAlign..."
curl -fsSL -o "$TEMP_ZIP" "$REPO_URL"

echo "Extracting AlphaAlign..."
rm -rf "$TEMP_EXTRACT"
unzip -q "$TEMP_ZIP" -d "$TEMP_EXTRACT"

echo "Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
# Use rsync to copy, excluding data and venv to preserve on upgrade
if command -v rsync &> /dev/null; then
    rsync -a "$TEMP_EXTRACT/AlphaAlign-main/" "$INSTALL_DIR/" --exclude "data" --exclude "backend/venv" --exclude "frontend/node_modules"
else
    cp -R "$TEMP_EXTRACT/AlphaAlign-main/"* "$INSTALL_DIR/"
fi

# Cleanup
rm -f "$TEMP_ZIP"
rm -rf "$TEMP_EXTRACT"

cd "$INSTALL_DIR"

echo ""
echo "[3/4] Setting up Backend (Python)..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
echo "Installing Python dependencies..."
source venv/bin/activate
python3 -m pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt >/dev/null
cd ..

echo ""
echo "[4/4] Setting up Frontend (Node.js)..."
cd frontend
echo "Installing Node.js dependencies..."
npm install >/dev/null
cd ..

echo ""
echo "========================================================"
echo "Installation Complete!"
echo ""
echo "AlphaAlign is installed in $INSTALL_DIR"
echo "To start AlphaAlign, run:"
echo "cd ~/AlphaAlign && ./start.sh"
echo "========================================================"
