from typing import List, Optional

import chess


class Board:
    def __init__(self) -> None:
        self.board: chess.Board = chess.Board()

    def legal_moves(self) -> chess.LegalMoveGenerator:
        return self.board.legal_moves

    def legal_moves_from(self, square: int) -> List[chess.Move]:
        return [move for move in self.board.legal_moves if move.from_square == square]

    def push(self, move: chess.Move) -> bool:
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def is_checkmate(self) -> bool:
        return self.board.is_checkmate()

    def is_check(self) -> bool:
        return self.board.is_check()

    def piece_at(self, square: int) -> Optional[chess.Piece]:
        return self.board.piece_at(square)

    def is_capture(self, move: chess.Move) -> bool:
        return self.board.is_capture(move)
