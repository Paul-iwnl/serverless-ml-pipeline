#!/bin/bash

# Path to venv
VENV_PATH="$HOME/venv"

# If venv doesn't exist, create it
if [ ! -d "$VENV_PATH" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_PATH"
fi

# Activate venv
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Optional: install common packages
pip install --upgrade pip
pip install requests praw pandas
echo "Virtual environment activated and packages installed."

#To activate, use: source ./start_venv.sh
#To deactivate, use: deactivate
