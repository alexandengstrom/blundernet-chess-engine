#!/bin/bash

NEEDS_PREPARE=false

if [ ! -d "stockfish" ]; then
    echo "Missing: stockfish directory"
    NEEDS_PREPARE=true
fi

if [ ! -d "training_data" ]; then
    echo "Missing: training_data directory"
    NEEDS_PREPARE=true
fi

if [ ! -d "training_data/unprocessed" ] || [ -z "$(ls -A training_data/unprocessed)" ]; then
    echo "Missing or empty: training_data/unprocessed"
    NEEDS_PREPARE=true
fi

if [ "$NEEDS_PREPARE" = true ]; then
    echo "Running prepare_training.sh..."
    bash scripts/prepare_training.sh
fi

source venv/bin/activate
python3 src/cli.py generate
deactivate

