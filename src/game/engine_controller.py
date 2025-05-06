from engine import Engine, Model

class EngineController:
    def __init__(self, model_name):
        self.engine = Engine(Model.load(model_name))
        self.turn = False
        self.time = None
