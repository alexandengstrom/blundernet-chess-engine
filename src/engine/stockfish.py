import chess
import chess.engine
import math


class Stockfish:
    def __init__(self, executable="stockfish/stockfish-ubuntu-x86-64-avx2"):
        self.engine = chess.engine.SimpleEngine.popen_uci(executable)

    def predict_best_move(self, board: chess.Board, depth=10):
        return self.engine.play(board, chess.engine.Limit(depth=depth)).move
    
    def predict_move_distribution(self, board: chess.Board, depth=5):
        info = self.engine.analyse(
            board,
            chess.engine.Limit(depth=depth),
            multipv=10
        )

        moves_and_scores = []
        for entry in info:
            if "pv" in entry and len(entry["pv"]) > 0:
                move = entry["pv"][0]
                score = entry["score"].pov(board.turn).score(mate_score=100000)
                if score is not None:
                    moves_and_scores.append((move.uci(), score))

        if not moves_and_scores:
            return None

        scores = [s for _, s in moves_and_scores]
        max_score = max(scores)
        exps = [math.exp(s - max_score) for s in scores]
        total = sum(exps)
        probs = [e / total for e in exps]

        return dict(zip((m for m, _ in moves_and_scores), probs))
        

    def close(self):
        self.engine.quit()
