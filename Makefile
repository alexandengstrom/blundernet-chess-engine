DATA_DIR := training_data
MODEL_DIR := models
ZIP_URL := https://database.nikonoel.fr/lichess_elite_2020-06.zip
ZIP_FILE := $(DATA_DIR)/dataset1.zip
PGN_FILE := $(DATA_DIR)/dataset1.pgn
NAME ?= null

.PHONY: all setup_venv download extract build model clean

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
	python3 src/build.py $(NAME)

download: $(ZIP_FILE)

extract: $(PGN_FILE)

clean:
	rm -rf $(DATA_DIR)
