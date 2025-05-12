import random

import chess
import numpy as np
from chess import Board

from engine.model import Model
from utils import UCI_DICT, Logger


class Engine:
    def __init__(self, model):
        assert isinstance(model, Model)

        self.model = model
        self.name = model.name

    def make_move(self, board: Board, verbose=False):
        available_moves = list(board.legal_moves)
        predicted_logits = self.model.predict(board)[0]

        move_logits = []
        for move in available_moves:
            move_uci = move.uci()
            move_index = UCI_DICT.get(move_uci)
            if move_index is not None:
                move_logits.append((move, predicted_logits[move_index]))

        if not move_logits:
            return random.choice(available_moves)

        moves, logits = zip(*move_logits)
        probs = softmax(np.array(logits))
        move_probabilities = list(zip(moves, probs))
        move_probabilities.sort(key=lambda x: x[1], reverse=True)

        _, top_prob = move_probabilities[0]
        
        # This is so we add more variation into the game the first 20 moves
        move_count = board.fullmove_number
        span = (11 - move_count) / 100 if move_count < 10 else 0.01
        

        threshold_moves = [
            (move, prob) for move, prob in move_probabilities if top_prob - prob <= span
        ]

        selected_moves = threshold_moves[:5]

        chosen_move = random.choice([move for move, _ in selected_moves])

        if verbose:
            Logger.info("Probabilities for top moves according to engine:")
            for move, prob in move_probabilities[:5]:
                if move == chosen_move:
                    color = "\033[92m"
                else:
                    color = "\033[93m"
                reset = "\033[0m"
                print(f"\t{color}{move}: {prob:.3f}{reset}")

        return chosen_move


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()
