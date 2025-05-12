import chess

class ChatHandler:
    def __init__(self):
        pass

    def on_game_start(self, board: chess.Board, opponent: str) -> str:
        return f"Good luck, {opponent}! I dont do any search, read about me on Github if interested!"

    def on_win(self, board: chess.Board) -> str:
        return f"Good game!"

    def on_loss(self, board: chess.Board) -> str:
        return f"Well played!"

    def on_draw(self, board: chess.Board) -> str:
        return "A draw! Good game."
    

