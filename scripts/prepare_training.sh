#!/bin/bash

STOCKFISH_URL="https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar"
STOCKFISH_TAR="stockfish.tar"
STOCKFISH_EXE="stockfish"

echo "Downloading Stockfish..."
curl -L "$STOCKFISH_URL" -o "$STOCKFISH_TAR"

echo "Extracting..."
tar -xf "$STOCKFISH_TAR"

mv stockfish/* "$STOCKFISH_EXE"

rm -rf stockfish "$STOCKFISH_TAR"

echo "Stockfish is ready."
