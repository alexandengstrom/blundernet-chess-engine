#!/bin/bash

source venv/bin/activate
python3 src/cli.py eval --model "${1:-my_custom_model}"
deactivate
