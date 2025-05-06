import numpy as np

class Evaluator:
    def __init__(self):
        pass

    @staticmethod
    def evaluate(model):
        tests = ["random", "checkmates", "endgame", "real_positions"]

        for test in tests:
            data = np.load(f"tests/evaluation/{test}.npz")
            x = data["X"]
            y = data["y"]

            print(f"Evaluating {test} on {len(x)} positions...")
            loss, accuracy = model.evaluate(x, y, batch_size=64)
            print(f"\nFinal Evaluation - Loss: {loss:.4f}, Accuracy: {accuracy:.2%}")
