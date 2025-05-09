#!/bin/bash

ZIP_URLS=(
    "https://database.nikonoel.fr/lichess_elite_2020-06.zip"
    "https://database.nikonoel.fr/lichess_elite_2020-07.zip"
    "https://database.nikonoel.fr/lichess_elite_2020-08.zip"
    "https://database.nikonoel.fr/lichess_elite_2020-09.zip"
    "https://database.nikonoel.fr/lichess_elite_2020-10.zip"
    "https://database.nikonoel.fr/lichess_elite_2020-11.zip"
    "https://database.nikonoel.fr/lichess_elite_2020-12.zip"
)

TRAINING_DIR="training_data"

mkdir -p $TRAINING_DIR

for ZIP_URL in "${ZIP_URLS[@]}"; do
    ZIP_FILE=$(basename "$ZIP_URL")
    echo "Downloading $ZIP_FILE..."
    curl -L "$ZIP_URL" -o "$ZIP_FILE"

    echo "Extracting $ZIP_FILE..."
    unzip -o "$ZIP_FILE" -d "$TRAINING_DIR"

    rm -f "$ZIP_FILE"
done

echo "Training data is ready."
