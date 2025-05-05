# Blundernet Chess Engine
Welcome to Blundernet! This is my personal recreational project where I am trying to create a chess engine using neural networks. My goal is not to create the best chess engine since i am not using any techniques such as minimax, instead i want to explore using only neural networks. Every move the engine makes is decided only by what the neural network outputs. The only exception is if the engine is playing as white, then the first move will be randomized between 8 different choices.

The repo also contains a simple graphical interface made in Pygame where you should play against the models.

## The Model
The model is created with TensorFlow. The network is fed an input tensor representing the state of the board and the output layer has as many neurons as possible moves in uci-format. 

### Performance

To evaluate how well the models performs, four distinct test sets have been created:

- **Real Positions**: Taken from real games, with Stockfish-predicted next moves as labels.  
- **Random Positions**: Artificially generated positions that might not occur often in real games, with Stockfish-predicted next moves as labels.  
- **Endgame Positions**: Real-game positions limited to the endgame phase, with Stockfish-predicted next moves as labels. 
- **Checkmate Positions**: Real positions where the next move leads to checkmate, using the actual game move as the label.

#### Model Accuracy

| Generation         | Real Positions | Random Positions | Endgame Positions | Checkmate Positions |
|--------------------|----------------|------------------|-------------------|---------------------|
| Blundernet Gen 1   | 32.41%         | 26.60%           | 27.53%            | 19.56%              |
