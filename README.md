# Blundernet

Welcome to Blundernet! This is my personal recreational project where I'm trying to create a chess engine using neural networks. My goal is not to build the best chess engine, since I'm not using any techniques such as minimax, alpha-beta pruning, or Monte Carlo search. Instead, I want to explore using only neural networks. The next move is determined by a single pass through the neural network.

I've tried to structure the repo so it's easy to train your own models. It includes a simple Pygame GUI where you can play locally against the models, and a Lichess integration so you can let your models play online.


## Features:
- **Neural Network Driven**: Every move the engine makes is determined entirely by the neural network’s output, with no traditional chess algorithms involved.
- **Model Training**: The repository is designed for easy training of new models, so you can experiment with different architectures and training data.
- **Pygame GUI**: A simple GUI using Pygame is included which allows you to play against your models in a local environment.
- **Lichess Bridge**: With the Lichess integration, you can pit your models against real opponents online by letting them play on Lichess.
- **Evaluation Set**: The evaluation test set i have used is included in the repo, so you can compare your own models to my model as long as you are using the same board matrix representation.
## Installation:
To get started with the project, first clone the repo:
```bash
git clone https://github.com/alexandengstrom/blundernet-chess-engine
```
Navigate to the project directory:
```bash
cd blundernet-chess-engine
```
Install the project with `make` command:
```bash
make
```

## Usage:
Interact with the project using `make`. These are the commands available:
- `make game`: Starts the Pygame GUI where you can play locally against your models. 
- `make dataset`: Downloads a set of PGN-files we will need for the training.
- `make model NAME=your_model_name`: This starts the training process of a model with a given name. If the model already exists it will continue training it.
- `make bot MODEL=your_model_name`: This starts the **Lichess**-bridge which lets your engine play online.
- `make stockfish`: Setups the use of the Stockfish class, only necessary if you want to create your own evaluation data. Also this script is currently platform specific.
- `make check`: Mostly for development, but runs linting and typechecking for the project.

## Engine

### Architecture

This model is a convolutional neural network designed to process an 8×8×18 representation of a chess board. It begins with a convolution and batch normalization layer, followed by 10 residual blocks that each apply two convolutional layers with skip connections to preserve features. After the residual stack, a squeeze-and-excitation block rescales channel-wise features and then the output is passed through a 1×1 convolution, flattened, and fed into two dense layers to produce logits for all possible moves.


### Dataset
The training data is generated on the fly by using data from real chess games. We randomly extract a few positions from randomly selected games, from a randomly selected PGN-file, so we get new data if the the script is run again. These positions are converted into matrix representations using the model's board_to_matrix() method. The games we are sampling from is only matches played between high ranked players.

### Move Prediction
The `Model` class provides a predict method that takes a `chess.Board` object and returns raw scores (logits) for all possible moves in UCI format. The `Engine` class interprets the model's predictions to select a move:
1. **Filter Legal Moves**: From the model's predicted logits (one for each possible UCI move), we extract only those corresponding to currently legal moves on the board.
2. **Renormalize Probabilities**: The model's output is logits over all possible moves — including illegal ones — the remaining values does not form a proper probability distribution. We apply softmax to the logits for only the legal moves to get a valid distribution.
3. **Select Top Candidates**: We find the legal move with the highest probability, then keep all other legal moves within 10% probability of that top probability. This gives a shortlist of high-confidence options, typically up to 5 moves.
4. **Choose Final Move**: We randomly select one move from the top shortlist. In many cases there will only be one option if the model has a clear favorite.

This method is used so we always chooses a legal move, play the most confident move when one clearly stands out and introduces some randomness when multiple moves are similarly good.

If it's the first move of the game as white, the engine plays a random opening from a predefined list.

### Evaluation
To evaluate how well the model performs, I have created some datasets that tests different aspects of playing chess. These are the datasets:
Dataset Descriptions

- **Openings**: Positions extracted from early game stages (turns 0–10) with nearly full material on the board (26–32 pieces). Represents common opening scenarios.
- **Middlegames**: Positions from the middle of games (turns 15–40), with moderate material left (15–25 pieces).
- **Endgames**: Positions from later stages of games (turns 30–100), with fewer pieces remaining (2–14). Focuses on conversion and mating technique.
- **Random**: Randomly generated legal positions from games of varying lengths. Includes a wide variety of positions, including unnatural ones.
- **Checkmates**: Positions where the next move delivers checkmate. Selected from real games where a clear mating move exists.
- **Tactics**: Puzzles filtered by tactical motifs such as fork, pin, and discovered attacks, extracted from a Lichess puzzle CSV.
#### Result

Accuracy is measured as whether the move with the highest predicted probability matches the move suggested by Stockfish at a search depth of 10. It's important to note that we have not filtered for only legal moves — the model outputs logits for all possible moves in UCI format. A prediction is not counted as correct in this evaluation, even if the legal move with the highest logit was correct, if there was an illegal move with a higher logit.

| Dataset     | Loss   | Accuracy |
|-------------|--------|----------|
| Openings    | 1.6343 | 0.4436   |
| Middlegames | 1.8125 | 0.4543   |
| Endgames    | 1.8337 | 0.4411   |
| Random      | 1.7960 | 0.4850   |
| Checkmates  | 1.0876 | 0.6129   |
| Tactics     | 2.6589 | 0.2360   | 

It would be easy to get higher accuracy on openings, since there aren't that many possible move combinations, but I've intentionally filtered out most opening moves from the dataset to avoid overfitting and to see if the model can still learn good openings on its own. Because we sample from real games, the dataset still includes a wide variety of openings, which adds some noise. Still, the model performs as good on openings as it does on other positions. It's also interesting to see that it performs better on random positions than on middlegames and endgames, even though truly random positions are unlikely to occur often in the training data.

The model does best on the checkmate dataset, which shows that it’s good at spotting direct mates. But it struggles on the tactics dataset, where the goal is to find stronger moves that win material or lead to checkmate later. This suggests the model is better at short-term threats than deeper tactical ideas that take a few moves to work, which kind of makes sense.
## Lichess
When running the Lichess-bridge. We will start to listen for incoming requests but also challenge other bot accounts. By default we will allow five games to be played at the same time. When challenging other bots, we will try to find matches that are close to us in ranking. When receiving challenges we will accept everything.

## Final Thoughts

This was my first programming project using TensorFlow. I didn't know much about the framework, nor was I very familiar with which architectures to use. For this project, I experimented with different architectures based on my understanding of the sources linked below, and I also tried various ways of formatting the dataset.

Currently, the `y-labels` are one-hot encoded, but that wasn't my initial plan. My original idea was to create a "gold standard" by letting **Stockfish** evaluate the top 10 moves and then convert those evaluations into a probability distribution. However, I couldn't get this approach to work—every time I tried, the training collapsed and the model ended up predicting uniform probabilities for all moves. I likely did something wrong, but as I'm not an expert in this field, I'm not sure what the issue was.

That said, I didn’t encounter this problem when using one-hot encoding. I also observed better results when using the actual moves played in sample games as the `y-labels`, rather than relying on Stockfish's predictions, even if the evaluation set relies on Stockfish predictions. This approach is also much faster and allows us to generate datasets on the fly.

On paper, the evaluation metrics look promising—random guessing would yield only about 0.02% accuracy. So how does it feel to play against this model? I'd say it performs decently on most moves, but occasionally makes huge blunders. Because of this, it doesn’t stand a chance against engines that use minimax search, especially when playing other bots on Lichess. Just one major mistake is enough to lose a game. So for now, I'm not sure if the model has any practical use, but it was a fun project and I learned a lot.


## Sources
- http://vision.stanford.edu/teaching/cs231n/reports/2015/pdfs/ConvChess.pdf
- https://www.chessprogramming.org/AlphaZero
- https://lczero.org/dev/backend/nn/
- https://medium.com/data-science/predicting-professional-players-chess-moves-with-deep-learning-9de6e305109e
