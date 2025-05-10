.PHONY: all dataset

all:
	bash scripts/install.sh

dataset:
	bash scripts/prepare_training.sh

model:
ifeq ($(strip $(NAME)),)
	$(error You must provide a model name: make model NAME=my_model_name)
endif
	bash scripts/train_model.sh $(NAME)

bot:
	@if [ -z "$(MODEL)" ]; then \
		echo "No model name provided. Using 'blundernet' as the default."; \
		MODEL="blundernet"; \
	fi
	@echo "Running the bot with model: $(MODEL)"
	bash scripts/run_lichess_bot.sh $(MODEL)

game:
	bash scripts/run_game.sh

check:
	bash scripts/validate_project.sh

stockfish:
	bash scripts/install_stockfish.sh

eval:
ifeq ($(strip $(MODEL)),)
	$(error You must provide a model name: make eval NAME=my_model_name)
endif
	bash scripts/evaluate_model.sh $(MODEL)
