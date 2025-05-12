#!/bin/bash

set -e

source venv/bin/activate
python3 src/cli.py train --name "${1:-my_custom_model}"
deactivate
