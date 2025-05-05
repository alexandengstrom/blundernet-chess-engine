import random
import os
import numpy as np
from chess import pgn
from tqdm import tqdm
from utils import board_to_matrix, generate_full_uci_move_dict
from stockfish import Stockfish
from datetime import datetime


class InfiniteDataset:
    def __init__(self, batch_size=500, use_saved=False):
        self.batch_size = batch_size
        self.use_saved = use_saved
        self.stockfish = Stockfish() if not use_saved else None
        self.move_dict = generate_full_uci_move_dict()
        self.saved_dataset_dir = "training_data/processed"

    def __iter__(self):
        if self.use_saved:
            return self._load_saved_data()
        else:
            return self._generate_data()

    def _generate_data(self, search_depth):
        games = []
        while True:
            for filename in os.listdir("training_data/unprocessed"):
                if not filename.endswith("pgn"):
                    continue
                
                path = os.path.join("training_data", "unprocessed", filename)
                with open(path, "r") as game_data:
                    while True:
                        game = pgn.read_game(game_data)
                        if game is None:
                            break
                        
                        if random.randint(1, 100) > 95: # To get unique combinations of the data
                            games.append(game)

                        if len(games) >= self.batch_size:
                            batch = self._preprocess(games, search_depth)
                            print(f"Generated {len(batch[0])} training samples")
                            yield batch
                            games = []

    def _load_saved_data(self):
        saved_files = sorted(
            [f for f in os.listdir(self.saved_dataset_dir) if f.endswith(".npz")]
        )
        if not saved_files:
            raise RuntimeError("No saved datasets found in training_data/processed")

        while True:
            random.shuffle(saved_files)
            for file in saved_files:
                path = os.path.join(self.saved_dataset_dir, file)
                data = np.load(path)
                print(f"Loaded dataset from {path}")
                yield data["X"], data["y"]

    def _preprocess(self, games, search_depth, save_dir="training_data/processed"):
        board_positions = []
        gold_standard = []

        for game in tqdm(games, desc="Building Next Dataset", unit="game"):
            board = game.board()
            for i, move in enumerate(game.mainline_moves()):
                if i < 5 and random.randint(-1, 5) > i: # Dont use all opening moves, too much repetition
                    board.push(move)
                    continue

                board_positions.append(board_to_matrix(board))
                best_move = self.stockfish.predict_best_move(board, depth=search_depth)
                gold_standard.append(self.move_dict[best_move.uci()])
                board.push(move)

        X = np.array(board_positions)
        y = np.array(gold_standard)

        return X, y

    @staticmethod
    def generate(batch_size=500, num_batches=100, search_depth=5, save_dir="training_data/processed"):
        """Generate and save datasets based on the _generate_data logic."""
        dataset = InfiniteDataset(batch_size=batch_size)

        try:
            for _ in tqdm(range(num_batches), desc="Batches", unit="batch"):
                data_batch = next(dataset._generate_data(search_depth))
                X, y = data_batch
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"dataset_{timestamp}.npz"
                save_path = os.path.join(save_dir, filename)

                os.makedirs(save_dir, exist_ok=True)
                np.savez_compressed(save_path, X=X, y=y)
                print(f"Saved dataset to {save_path}")
                print("Press CTRL+C to stop the generation")
                print()
        except KeyboardInterrupt:
            pass
