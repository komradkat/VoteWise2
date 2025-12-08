#!/bin/bash
set -e
VENV_DIR="/home/komradkat/.gemini/votewise_venv"

echo "Creating virtual environment at $VENV_DIR..."
# Create without pip to avoid ensurepip issues on some systems
python3 -m venv --without-pip "$VENV_DIR"

echo "Installing pip..."
curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
"$VENV_DIR/bin/python3" get-pip.py
rm get-pip.py

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install -r requirements.txt

echo "✅ Setup complete! You can now use ./run_dev.sh to start the server."
