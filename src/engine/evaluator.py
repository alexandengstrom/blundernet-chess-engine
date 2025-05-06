import numpy as np
from chess import Board, pgn
import chess
import random
from engine import Stockfish
from utils import board_to_matrix, generate_full_uci_move_dict

class Evaluator:
    def __init__(self):
        pass
    
    @staticmethod
    def evaluate(model):
        tests = ["random", "checkmates", "endgame", "real_positions"]
        
        for test in tests:
            data = np.load(f"tests/evaluation/{test}.npz")
            X = data["X"]
            y = data["y"]

            print(f"Evaluating {test} on {len(X)} positions...")
            loss, accuracy = model.evaluate(X, y, batch_size=64)
            print(f"\nFinal Evaluation - Loss: {loss:.4f}, Accuracy: {accuracy:.2%}")

    @staticmethod
    def compare_models(engine1, engine2, num_games=20):
        assert num_games % 2 == 0, "Number of games should be even to balance colors"

        results = {"engine1_wins": 0, "engine2_wins": 0, "draws": 0}

        for i in range(num_games):
            board = Board()
            if i % 2 == 0:
                white, black = engine1, engine2
            else:
                white, black = engine2, engine1

            while not board.is_game_over():
                move = white.make_move(board, verbose=False) if board.turn == chess.WHITE else black.make_move(board)
                board.push(move)

            result = board.result()
            winner = None
            if result == "1-0":
                if white == engine1:
                    results["engine1_wins"] += 1
                    winner = engine1
                else:
                    results["engine2_wins"] += 1
                    winner = engine2
            elif result == "0-1":
                if black == engine1:
                    results["engine1_wins"] += 1
                    winner = engine1
                else:
                    results["engine2_wins"] += 1
                    winner = engine2
            else:
                results["draws"] += 1

            if (i + 1) % 50 == 0:
                print(f"Completed {i + 1}/{num_games} games")
            
            if winner:
                print(f"Game {i+1}/{num_games}: {winner.name}")
            else:
                print(f"Game {i+1}/{num_games}: Draw")

        print("\nFinal Results after", num_games, "games:")
        print(f"Engine 1 Wins: {results['engine1_wins']}")
        print(f"Engine 2 Wins: {results['engine2_wins']}")
        print(f"Draws: {results['draws']}")
        print(f"Engine 1 Win Rate: {results['engine1_wins'] / num_games:.2%}")
        print(f"Engine 2 Win Rate: {results['engine2_wins'] / num_games:.2%}")

        
    @staticmethod
    def generate(pgn_file):
        X, y = create_random_positions_set(10000)
        np.savez_compressed("tests/evaluation/random.npz", X=X, y=y)
        X, y = create_check_in_one_set(10000, "tests/evaluation/test_set.pgn")
        np.savez_compressed("tests/evaluation/checkmates.npz", X=X, y=y)
        # X, y = create_real_positions_set(10000, "tests/evaluation/test_set.pgn")
        # np.savez_compressed("tests/evaluation/real_positions.npz", X=X, y=y)
        # X, y = create_endgame_set(10000, "tests/evaluation/test_set.pgn")
        # np.savez_compressed("tests/evaluation/endgame.npz", X=X, y=y)
        
def create_endgame_set(num_tests, filename):
    board_states = []
    best_moves = []
    
    stockfish = Stockfish()
    move_dict = generate_full_uci_move_dict()
    
    with open(filename, "r") as game_data:
        while len(board_states) < num_tests:
            game = pgn.read_game(game_data)
            if game is None:
                break
            
            board = game.board()
            move_counter = 0
            
            for move in game.mainline_moves():
                board.push(move)
                move_counter += 1

                if board.is_game_over():
                    break
                
                if move_counter < 40:
                    continue

                piece_count = sum(
                    1 for piece in board.piece_map().values() if piece.piece_type != chess.KING
                )
                
                if piece_count <= 6 and random.random() < 0.2:
                    best_move = stockfish.predict_best_move(board).uci()
                    if best_move in move_dict:
                        board_states.append(board_to_matrix(board))
                        best_moves.append(move_dict[best_move])
                
                if len(board_states) >= num_tests:
                    break
    
    X = np.array(board_states)
    y = np.array(best_moves)
    
    return X, y

        
def create_real_positions_set(num_tests, filename):
    board_states = []
    best_moves = []
    
    stockfish = Stockfish()
    move_dict = generate_full_uci_move_dict()
    
    with open(filename, "r") as game_data:
        while len(board_states) < num_tests:
            game = pgn.read_game(game_data)
            if game is None:
                break
            
            board = game.board()
            for move in game.mainline_moves():
                if random.randint(1, 100) > 95:
                    board_states.append(board_to_matrix(board))
                    best_moves.append(move_dict[stockfish.predict_best_move(board).uci()])        
                
                board.push(move)
                
    X = np.array(board_states)
    y = np.array(best_moves)
    
    return X, y
            

def create_check_in_one_set(num_tests, filename):
    board_states = []
    best_moves = []
    
    move_dict = generate_full_uci_move_dict()
    
    with open(filename, "r") as game_data:
        while len(board_states) < num_tests:
            game = pgn.read_game(game_data)
            if game is None:
                break
            
            board = Board()
            node = game
            prev_node = None
            
            while node.variations:
                prev_node = node
                node = node.variation(0)
                board.push(node.move)
            
            if board.is_checkmate():
                board.pop()
                checkmating_move = node.move
                board_states.append(board_to_matrix(board))
                best_moves.append(move_dict[checkmating_move.uci()])

    X = np.array(board_states)
    y = np.array(best_moves)
    
    return X, y
    

def create_random_positions_set(num_tests):
    board_states = []
    best_moves = []
    
    stockfish = Stockfish()
    move_dict = generate_full_uci_move_dict()
    
    while len(board_states) < num_tests:
        board = Board()
        
        for _ in range(1, 100):
            move = random.choice(list(board.legal_moves))
            
            board.push(move)
            
            if board.is_game_over():
                break
            
        else:
            board_states.append(board_to_matrix(board))
            best_moves.append(move_dict[stockfish.predict_best_move(board).uci()])
    
    X = np.array(board_states)
    y = np.array(best_moves)

    return X, y