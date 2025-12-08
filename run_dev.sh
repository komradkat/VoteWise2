#!/bin/bash
VENV_PYTHON="/home/komradkat/.gemini/votewise_venv/bin/python3"

# Check if python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Error: Virtual environment python not found at $VENV_PYTHON"
    echo "Please wait for the installation to complete or run the setup manually."
    exit 1
fi

echo "🚀 Starting VoteWise2 Development Server..."
echo "Using virtual environment: $VENV_PYTHON"
echo "----------------------------------------"

# Execute the server
exec "$VENV_PYTHON" manage.py runserver "$@"
