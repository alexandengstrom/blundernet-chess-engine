import random
from chess import pgn
import chess
import numpy as np
import os
from tqdm import tqdm
from typing import List
import csv

from .stockfish import Stockfish
from .model import Model
from utils import UCI_DICT



class Evaluator:
    def __init__(self):
        pass
    
    @staticmethod
    def evaluate(model: Model):
        results = []

        test_sets = [
            ("Openings", "openings.npz"),
            ("Middlegames", "middlegames.npz"),
            ("Endgames", "endgames.npz"),
            ("Random", "random.npz"),
            ("Checkmates", "checkmates.npz"),
            ("Tactics", "tactics.npz")
        ]

        for name, file in test_sets:
            loss, accuracy = Evaluator.run_test(model, file)
            results.append((name, f"{loss:.4f}", f"{accuracy:.4f}"))

        col_widths = [max(len(str(row[i])) for row in results + [("Dataset", "Loss", "Accuracy")]) for i in range(3)]
        print()
        print(f"{'Dataset'.ljust(col_widths[0])}  {'Loss'.ljust(col_widths[1])}  {'Accuracy'.ljust(col_widths[2])}")
        print("-" * (sum(col_widths) + 4))

        for row in results:
            print(f"{row[0].ljust(col_widths[0])}  {row[1].ljust(col_widths[1])}  {row[2].ljust(col_widths[2])}")
    
    @staticmethod
    def run_test(model: Model, dataset: str):
        path = os.path.join("tests", "evaluation", dataset)
        data = np.load(path, allow_pickle=True)

                
        loss, accuracy = model.evaluate(data["X"], data["y"], batch_size=64)
        return loss, accuracy
        

    @staticmethod
    def generate_testset(pgn_file: str, num_tests: int):
        games = []
        
        stockfish = Stockfish()
        
        with open(pgn_file, "r", encoding="utf-8") as game_data:
            while True:
                game = pgn.read_game(game_data)
                if game is None:
                    break
                
                games.append(game)
                
                if len(games) > num_tests:
                    break
                
        print("Done collecting games")
                
        random.shuffle(games)

        openings_x, openings_y = Evaluator.create_set(
            games, num_tests, stockfish, max_turn=10, min_turn=0, max_pieces=32, min_pieces=26
        )
        np.savez_compressed(os.path.join("tests", "evaluation", "openings.npz"), X=openings_x, y=openings_y)
        
        openings_x.clear()
        openings_y.clear()
        
        
        middlegames_x, middlegames_y = Evaluator.create_set(
            games, num_tests, stockfish, max_turn=40, min_turn=15, max_pieces=25, min_pieces=15
        )
        
        np.savez_compressed(os.path.join("tests", "evaluation", "middlegames.npz"), X=middlegames_x, y=middlegames_y)
        
        middlegames_x.clear()
        middlegames_y.clear()
        
        
        endgames_x, endgames_y = Evaluator.create_set(
            games, num_tests, stockfish, max_turn=100, min_turn=30, max_pieces=14, min_pieces=2
        )

        np.savez_compressed(os.path.join("tests", "evaluation", "endgames.npz"), X=endgames_x, y=endgames_y)
        endgames_x.clear()
        endgames_y.clear()
        
        checkmates_x, checkmates_y = Evaluator.create_checkmate_set(games, num_tests, stockfish)
        np.savez_compressed(os.path.join("tests", "evaluation", "checkmates.npz"), X=checkmates_x, y=checkmates_y)
        checkmates_x.clear()
        checkmates_y.clear()
        
        random_x, random_y = Evaluator.create_random_set(num_tests, stockfish)
        np.savez_compressed(os.path.join("tests", "evaluation", "random.npz"), X=random_x, y=random_y)
        
        tactics_x, tactics_y = Evaluator.create_puzzle_set("tests/evaluation/puzzles.csv", ["fork", "pin", "discoveredAttack"], 1000, stockfish)
        np.savez_compressed(os.path.join("tests", "evaluation", "tactics.npz"), X=tactics_x, y=tactics_y)
        
        stockfish.close()       
        
    @staticmethod
    def create_set(games, num_tests: int, stockfish: Stockfish, max_turn: int, min_turn: int, max_pieces: int, min_pieces: int):
        x = []
        y = []
        
        for game in tqdm(games, desc="Generating Dataset", unit="game", colour='green'):
            board_state = Evaluator.get_filtered_move(game, max_turn=max_turn, min_turn=min_turn, max_pieces=max_pieces, min_pieces=min_pieces)
            
            if not board_state:
                continue
            
            best_move = stockfish.predict_best_move(board_state, depth=10)
                    
            if not best_move:
                continue
                    
            x.append(Model.board_to_matrix(board_state))
                    
            y.append(UCI_DICT[best_move.uci()])
            
            if len(x) >= num_tests:
                break
            
        return x, y
    
    @staticmethod
    def create_checkmate_set(games, num_tests: int, stockfish: Stockfish):
        x = []
        y = []
        
        for game in tqdm(games, desc="Generating Dataset", unit="game", colour='green'):
            board = game.board()
            
            for move in game.mainline_moves():
                board_copy = board.copy()
                
                board.push(move)
                
                if board.is_checkmate():
                    move_probs = stockfish.predict_move_distribution(board_copy, depth=10)
                    
                    if len([prob for move, prob in move_probs.items() if prob > 0.8]) != 1:
                        continue
                    
                    best_move = stockfish.predict_best_move(board_copy, depth=10)
                    x.append(Model.board_to_matrix(board_copy))
                    y.append(UCI_DICT[best_move.uci()])
                    
            if len(x) >= num_tests:
                break
            
        return x, y
                        
                        
                        
    @staticmethod
    def create_random_set(num_tests: int, stockfish: Stockfish):
        x: List[np.ndarray] = []
        y: List[int] = []
        
        while len(x) < num_tests:
            board = chess.Board()
            
            depth = random.randint(1, 100)
            for _ in range(depth):
                move = random.choice(list(board.legal_moves))
                board.push(move)
                
                if board.is_checkmate():
                    break
            
                
            best_move = stockfish.predict_best_move(board, depth=10)
            if not best_move:
                continue
            
            x.append(Model.board_to_matrix(board))
            y.append(UCI_DICT[best_move.uci()])
            
        return x, y
        


    @staticmethod
    def get_filtered_move(game: pgn.Game, max_turn: int, min_turn: int, max_pieces: int, min_pieces: int):
        board = game.board()
        matching_positions = []

        for move in game.mainline_moves():
            board.push(move)
            turn = board.fullmove_number * 2 - (0 if board.turn else 1)
            piece_count = len(board.piece_map())

            if min_turn <= turn <= max_turn and min_pieces <= piece_count <= max_pieces:
                matching_positions.append(board.copy())

        if matching_positions:
            return random.choice(matching_positions)
        else:
            return None

    @staticmethod
    def create_puzzle_set(puzzle_csv: str, theme_filter: List[str], num_tests: int, stockfish: Stockfish):
        x, y = [], []

        with open(puzzle_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not any(theme in row["Themes"] for theme in theme_filter):
                    continue

                board = chess.Board(row["FEN"])
                best_move = stockfish.predict_best_move(board, depth=10)

                if not best_move:
                    continue

                x.append(Model.board_to_matrix(board))
                y.append(UCI_DICT[best_move.uci()])

                if len(x) >= num_tests:
                    break

        return x, y
