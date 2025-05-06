import chess
import numpy as np

def generate_full_uci_move_dict():
    files = "abcdefgh"
    ranks = "12345678"
    promotion_pieces = ["q", "r", "b", "n"]

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


UCI_DICT = generate_full_uci_move_dict()
