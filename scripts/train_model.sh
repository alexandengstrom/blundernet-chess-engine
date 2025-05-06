#!/bin/bash

set -e

if [ -z "$(ls -A training_data/processed 2>/dev/null)" ]; then
    echo "Processed training data not found. Need to generate dataset first..."
    bash scripts/generate_dataset.sh
fi

source venv/bin/activate
python3 src/cli.py train --name "${1:-my_custom_model}"
deactivate
