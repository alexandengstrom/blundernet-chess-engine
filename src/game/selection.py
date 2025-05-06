from typing import Optional, Tuple, List
import chess


class Selection:
    def __init__(self) -> None:
        self.selected_square: Optional[Tuple[int, int]] = None
        self.selected_piece: Optional[chess.Piece] = None
        self.released_square: Optional[Tuple[int, int]] = None
        self.available_moves: List[chess.Move] = []

    def reset(self) -> None:
        self.selected_square = None
        self.selected_piece = None
        self.released_square = None
        self.available_moves = []
