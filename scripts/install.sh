#!/bin/bash

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating a new one..."
    python3 -m venv venv
else
    echo "Virtual environment found. Using existing one."
fi

source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping pip install."
fi

touch .token_file
echo REPLACE_WITH_YOUR_LICHESS_TOKEN >> .token_file

deactivate

echo "Downloading default model"

mkdir -p models
curl -L -o models/blundernet.keras https://github.com/alexandengstrom/blundernet-chess-engine/releases/download/v1.0.0/blundernet.keras

echo "Setup complete."