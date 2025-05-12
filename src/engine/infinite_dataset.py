import os
import sys
import random

import numpy as np
from chess import pgn

from utils import UCI_DICT

from utils import Logger
from .model import Model


class InfiniteDataset:
    def __init__(self, model: Model, data_dir: str):
        self.model = model
        self.data_dir = data_dir

    def __iter__(self):
        while True:
            files = os.listdir(self.data_dir)
            pgn_files = [fl for fl in files if fl.endswith(".pgn")]
            
            if len(files) == 0:
                Logger.error(f"No training data found in directory {self.data_dir}. Quickfix: make dataset")
                sys.exit(1)
                
            elif len(pgn_files) == 0:
                Logger.warning(f"Only found files that doesnt seem to be in PGN-format in directory {self.data_dir}, might crash...")
            
            random.shuffle(files)
            for filename in files:
                path = os.path.join(self.dir, filename)
                with open(path, "r") as data:
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
                            if i < 7 or random.randint(0, 20) > i or random.randint(1, 10) < 8:
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
