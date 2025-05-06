#!/bin/bash

STOCKFISH_URL="https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar"
STOCKFISH_TAR="stockfish.tar"
STOCKFISH_EXE="stockfish"
ZIP_URL="https://database.nikonoel.fr/lichess_elite_2020-06.zip"
ZIP_FILE="lichess_elite_2020-06.zip"
TRAINING_DIR="training_data/unprocessed"

echo "Downloading Stockfish..."
curl -L "$STOCKFISH_URL" -o "$STOCKFISH_TAR"

echo "Extracting..."
tar -xf "$STOCKFISH_TAR"
rm -rf "$STOCKFISH_TAR"

echo "Stockfish is ready."

mkdir -p training_data/processed
mkdir -p $TRAINING_DIR

echo "Downloading training data..."
curl -L "$ZIP_URL" -o "$ZIP_FILE"

echo "Extracting training data..."
unzip -o "$ZIP_FILE" -d "$TRAINING_DIR"

rm -f "$ZIP_FILE"

echo "Training data is ready."
