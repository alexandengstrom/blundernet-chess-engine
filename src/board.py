import chess

class Board:
    def __init__(self):
        self.board = chess.Board()
        
    def legal_moves(self):
        return self.board.legal_moves
    
    def legal_moves_from(self, square):
        return [move for move in self.board.legal_moves if move.from_square == square]
    
    def push(self, move):
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False
    
    def is_checkmate(self):
        return self.board.is_checkmate()
    
    def is_check(self):
        return self.board.is_check()
    
    def piece_at(self, square):
        return self.board.piece_at(square)
    
    def is_capture(self, move):
        return self.board.is_capture(move)
