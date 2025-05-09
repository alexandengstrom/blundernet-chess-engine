from engine import Evaluator, Model, Stockfish
import chess

# board = chess.Board("rnb1k1nr/pppp1ppp/5q2/P1b1p3/8/1P6/2PPPPPP/RNBQKBNR b KQkq - 0 4")
# stockfish = Stockfish()
# print(stockfish.predict_move_distribution(board, 5))


Evaluator.evaluate(Model.load("blundernet1"))
#Evaluator.generate_testset("tests/evaluation/testset.pgn", 5000)