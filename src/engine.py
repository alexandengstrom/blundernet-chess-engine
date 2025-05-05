import numpy as np
from chess import Board
from model import Model
import utils
import os
import random
import chess

class Engine:
    def __init__(self, model):
        self.name = model
    
        if os.path.exists(f"models/{model}"):
            self.model = Model.load(f"models/{model}")
        else:
            raise Exception("No model exists")

    def predict_move(self, board: Board):
        board_matrix = utils.board_to_matrix(board)
        board_matrix = np.expand_dims(board_matrix, axis=0)
        prediction = self.model.model.predict(board_matrix, verbose=0)
        return prediction

    def make_move(self, board: Board, verbose=True):
        # The idea is to make the one move the engine suggests if it has a clear winner
        # If many moves have probabilities close to each other we randomize between those, but at most between the 5 top choices.
        if board.turn == chess.WHITE and board.fullmove_number == 1:
            return self.make_opening_move(board)
        
        available_moves = list(board.legal_moves)
        predicted_logits = self.predict_move(board)[0]

        move_logits = []
        for move in available_moves:
            move_uci = move.uci()
            move_index = self.model.move_dict.get(move_uci)
            if move_index is not None:
                move_logits.append((move, predicted_logits[move_index]))

        if not move_logits:
            return random.choice(available_moves)

        moves, logits = zip(*move_logits)
        probs = softmax(np.array(logits))
        move_probabilities = list(zip(moves, probs))
        move_probabilities.sort(key=lambda x: x[1], reverse=True)

        top_move, top_prob = move_probabilities[0]
        #print(f"Probability for top move: {top_prob}")
        

        threshold_moves = [
            (move, prob) for move, prob in move_probabilities
            if top_prob - prob <= 0.10
        ]

        selected_moves = threshold_moves[:5]

        chosen_move = random.choice([move for move, _ in selected_moves])
        return chosen_move
    

    def make_opening_move(self, board: Board):
        """ Selects a random move from the most common opening moves if engine is white and it's the first move """
        opening_moves = [
            "e2e4", "d2d4", "g1f3", "c2c4", "f2f4", "e2e3", "g1h3", "b1c3"
        ]


        opening_move_uci = random.choice(opening_moves)
        opening_move = chess.Move.from_uci(opening_move_uci)
        if opening_move in board.legal_moves:
            return opening_move
        else:
            return random.choice(list(board.legal_moves))


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()