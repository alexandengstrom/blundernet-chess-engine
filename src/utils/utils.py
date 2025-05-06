import os
from chess import pgn, Board
import chess
import numpy as np

def load_training_data():
    games = []
    
    max_games = 500

    for filename in os.listdir("data/pgn"):
        try:
            path = os.path.join("data/pgn", filename)
            with open(path, "r") as game_data:
                while True:
                    game = pgn.read_game(game_data)
                    if game is None:
                        break
                    games.append(game)
                    
                    if len(games) > max_games:
                        break
        except:
            print(f"Crashed on file {filename}")
            

    print(f"Loaded {len(games)} games from PGN files.")
    return games

def generate_full_uci_move_dict():
    files = 'abcdefgh'
    ranks = '12345678'
    promotion_pieces = ['q', 'r', 'b', 'n']
    
    move_dict = {}

    for from_file in files:
        for from_rank in ranks:
            for to_file in files:
                for to_rank in ranks:
                    move = f"{from_file}{from_rank}{to_file}{to_rank}"
                    move_dict[move] = len(move_dict)

    for from_file in files:
        file_index = files.index(from_file)
        possible_to_files = [from_file]
        if file_index > 0:
            possible_to_files.append(files[file_index - 1])
        if file_index < 7:
            possible_to_files.append(files[file_index + 1])

        for to_file in possible_to_files:
            for piece in promotion_pieces:
                move = f"{from_file}7{to_file}8{piece}"
                move_dict[move] = len(move_dict)
                move = f"{from_file}2{to_file}1{piece}"
                move_dict[move] = len(move_dict)

    return move_dict


def board_to_matrix(board: chess.Board):
    matrix = np.zeros((8, 8, 17), dtype=np.float32)

    piece_map = board.piece_map()
    for square, piece in piece_map.items():
        row = square // 8
        col = square % 8
        piece_type = piece.piece_type - 1
        color_offset = 0 if piece.color == chess.WHITE else 6
        matrix[row, col, piece_type + color_offset] = 1

    if board.turn == chess.WHITE:
        matrix[:, :, 12] = 1

    if board.has_kingside_castling_rights(chess.WHITE):
        matrix[:, :, 13] = 1
    if board.has_queenside_castling_rights(chess.WHITE):
        matrix[:, :, 14] = 1
    if board.has_kingside_castling_rights(chess.BLACK):
        matrix[:, :, 15] = 1
    if board.has_queenside_castling_rights(chess.BLACK):
        matrix[:, :, 16] = 1

    return matrix



def preprocess(games):
    board_positions = []
    gold_standard = []
    move_dict = generate_full_uci_move_dict()

    for game in games:
        board = game.board()
        for move in game.mainline_moves():
            if board.turn == chess.BLACK:
                board_positions.append(board_to_matrix(board))
                move_uci = move.uci()
                gold_standard.append(move_dict[move_uci])
            board.push(move)

    return np.array(board_positions), np.array(gold_standard), move_dict

