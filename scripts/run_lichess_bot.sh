#!/bin/bash

if [ -z "$1" ]; then
    MODEL_NAME="blundernet"
else
    MODEL_NAME="$1"
fi

if [ -f .token ]; then
    echo "Token found, starting the bot!"
else
    read -rp "Enter your Lichess API token: " TOKEN
    echo

    echo "$TOKEN" > .token
    echo "Token saved to .token"
fi

source venv/bin/activate

python3 src/cli.py lichess --model "$MODEL_NAME"

deactivate
