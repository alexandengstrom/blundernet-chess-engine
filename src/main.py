from game import Game
from engine import Engine
from evaluator import Evaluator
from model import Model


if __name__ == "__main__":
    #Game().run()
    
    #Evaluator.generate("tests/evaluation/test_set.pgn")
    model = Model.load("models/blundernet4.keras")
    Evaluator().evaluate(model)
    #Evaluator.compare_models(Engine("blundernet.keras"), Engine("blundernet2.keras"))