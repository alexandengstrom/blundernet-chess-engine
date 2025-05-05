STOCKFISH_URL := https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar
STOCKFISH_TAR := stockfish.tar
STOCKFISH_EXE := stockfish

DATA_DIR := training_data
MODEL_DIR := models
ZIP_URL := https://database.nikonoel.fr/lichess_elite_2020-06.zip
ZIP_FILE := $(DATA_DIR)/dataset1.zip
PGN_FILE := $(DATA_DIR)/dataset1.pgn
NAME ?= null

BATCH_SIZE ?= 500
NUM_FILES ?= 100

.PHONY: all setup_venv download extract build model clean stockfish

all: setup_venv

setup_venv:
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
	else \
		echo "Virtual environment already exists."; \
	fi
	@. venv/bin/activate && \
		echo "Installing dependencies..." && \
		pip install --upgrade pip && \
		pip install -r requirements.txt

$(DATA_DIR):
	@if [ ! -d "$(DATA_DIR)" ]; then \
		echo "Downloading and extracting data..."; \
		mkdir -p $(DATA_DIR); \
		mkdir -p $(MODEL_DIR); \
		curl -L $(ZIP_URL) -o $(ZIP_FILE); \
		unzip -o $(ZIP_FILE) -d $(DATA_DIR); \
		rm -f $(ZIP_FILE); \
	else \
		echo "Data already exists. Skipping download and extraction."; \
	fi

$(PGN_FILE): $(DATA_DIR)

model: $(PGN_FILE)
	@. venv/bin/activate && python3 src/cli.py train --name $(NAME)

dataset:
	@echo "Generating dataset with batch size $(BATCH_SIZE) and creating $(NUM_FILES) files..."
	@. venv/bin/activate && python3 src/cli.py generate --batch_size $(BATCH_SIZE) --num_files $(NUM_FILES)

download: $(ZIP_FILE)

extract: $(PGN_FILE)

stockfish:
	@echo "Downloading Stockfish..."
	@curl -L $(STOCKFISH_URL) -o $(STOCKFISH_TAR)
	@echo "Extracting..."
	@tar -xf $(STOCKFISH_TAR)
	@mv stockfish/* $(STOCKFISH_EXE)
	@rm -rf stockfish $(STOCKFISH_TAR)
	@echo "Stockfish is ready."

clean:
	rm -rf $(DATA_DIR)
