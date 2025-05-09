import os
import random
from datetime import datetime

import numpy as np
from chess import pgn
from tqdm import tqdm

from utils import UCI_DICT

from .stockfish import Stockfish
from utils import Logger
from .model import Model
import chess


class InfiniteDataset:
    def __init__(self, model: Model):
        self.model = model

    def __iter__(self):
        while True:
            files = os.listdir("training_data")
            random.shuffle(files)
            for filename in files:
                with open(f"training_data/{filename}", "r") as data:
                    x = []
                    y = []
                    while True:
                        game = pgn.read_game(data)

                        if game is None:
                            break

                        if random.randint(1, 10) < 8:
                            continue

                        board = game.board()

                        for i, move in enumerate(game.mainline_moves()):
                            if i < 8 or random.randint(0, 20) > i or random.randint(1, 10) < 8:
                                board.push(move)
                                continue

                            x.append(self.model.board_to_matrix(board))
                            y.append(UCI_DICT[move.uci()])

                            board.push(move)

                            if len(x) >= 100000:
                                x_r = np.array(x)
                                y_r = np.array(y)
                                x.clear()
                                y.clear()

                                yield x_r, y_r
