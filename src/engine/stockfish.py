import chess
import chess.engine


class Stockfish:
    def __init__(self, executable="stockfish/stockfish-ubuntu-x86-64-avx2"):
        self.engine = chess.engine.SimpleEngine.popen_uci(executable)

    def predict_best_move(self, board: chess.Board, depth=10):
        return self.engine.play(board, chess.engine.Limit(depth=depth)).move

    def close(self):
        self.engine.quit()
