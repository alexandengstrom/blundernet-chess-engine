import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

import chess

from engine import Engine
from utils import Logger
from .api_client import ApiClient
from .chat_handler import ChatHandler


class LichessBot:
    def __init__(self, engine: Engine, token: str, max_games: int = 5) -> None:
        self.api = ApiClient(token)
        self.engine: Engine = engine
        self.chat: ChatHandler = ChatHandler()
        self.max_games: int = max_games
        self.active_games: set[str] = set()
        self.active_games_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_games)
        self.bot_id = self.get_id()
        threading.Thread(target=self.periodic_challenger, daemon=True).start()

    def get_id(self) -> str:
        try:
            resp = self.api.get_account()
            return resp["id"]
        except:
            Logger.error("Failed to get bot ID:")
            raise
        
    def get_our_rating(self) -> int:
        try:
            resp = self.api.get_account()
            return resp["perfs"]["bullet"]["rating"]
        except Exception as e:
            print("Failed to get bot rating:", e)
            raise

    def make_move(self, game_id: str, move: str) -> None:
        response = self.api.make_move(game_id, move)
        if response.status_code != 200:
            print("Failed to make move:", response.text)

    def run(self) -> None:
        Logger.info("Listening for incoming challenges...")
        for event in self.api.stream_events():
            if event["type"] == "challenge":
                if event["challenge"]["variant"]["key"] == "standard":
                    with self.active_games_lock:
                        if len(self.active_games) < self.max_games:
                            Logger.info(
                                f"Accepting challenge: {event['challenge']['id']}"
                            )
                            self.api.accept_challenge(event["challenge"]["id"])
                        else:
                            Logger.warning(
                                "Too many active games. Declining challenge."
                            )
            elif event["type"] == "gameStart":
                game_id = event["game"]["id"]
                with self.active_games_lock:
                    if len(self.active_games) < self.max_games:
                        self.active_games.add(game_id)
                        Logger.info(f"Game started: {game_id}")
                        self.executor.submit(self.play_game_wrapper, game_id)
                    else:
                        Logger.info(
                            f"Max concurrent games reached. Ignoring game {game_id}"
                        )

    def play_game_wrapper(self, game_id: str) -> None:
        try:
            self.play_game(game_id)
        except:
            Logger.error(f"Game {game_id} crashed")
        finally:
            with self.active_games_lock:
                self.active_games.discard(game_id)

    def play_game(self, game_id: str) -> None:
        board = chess.Board()
        is_white = None

        for event in self.api.stream_game(game_id):
            event_type = event["type"]

            if event_type == "gameFull":
                is_white = self.handle_game_full(event, game_id, board)
            elif event_type == "gameState":
                self.handle_game_state(event, is_white, game_id, board)
            elif event_type == "chatLine":
                continue
            elif event_type == "gameFinish":
                break

    def handle_game_full(self, event: Dict, game_id: str, board: chess.Board) -> bool:
        moves = event["state"]["moves"].split()
        for move in moves:
            board.push_uci(move)

        is_white = event["white"]["id"] == self.bot_id
        Logger.info(f"[Game {game_id}] We are playing as {'white' if is_white else 'black'}!")

        opponent = event["black"]["name"] if is_white else event["white"]["name"]

        self.send_chat(
            game_id,
            self.chat.on_game_start(board, opponent),
        )

        if (is_white and board.turn == chess.WHITE) or (not is_white and board.turn == chess.BLACK):
            self.respond(game_id, board, is_white)

        return is_white


    def handle_game_state(self, event: Dict, is_white: Optional[bool], game_id: str, board: chess.Board) -> None:
        if is_white is None:
            Logger.warning(f"[Game {game_id}] Game state received before determining color.")
            return

        moves = event["moves"].split()
        board.clear_stack()
        board.reset()

        for move in moves:
            board.push_uci(move)

        if (is_white and board.turn == chess.WHITE) or (not is_white and board.turn == chess.BLACK):
            self.respond(game_id, board, is_white)


    def handle_game_finish(self, is_white: Optional[bool], game_id: str, board: chess.Board) -> None:
        winner = None
        Logger.info(f"Game {game_id} is finished!")
        
        result = board.result()
        
        if result == "1-0":
            winner = "white"
        elif result == "0-1":
            winner = "black"

        if winner is None:
            Logger.info(f"[Game {game_id}] over: Draw.")
            self.send_chat(game_id, self.chat.on_draw(board))
        elif (winner == "white" and is_white) or (winner == "black" and not is_white):
            Logger.info(f"[Game {game_id}] over: We won!")
            self.send_chat(game_id, self.chat.on_win(board))
        else:
            Logger.info(f"[Game {game_id}] over: We lost.")
            self.send_chat(game_id, self.chat.on_loss(board))


    def challenge_other_bot(self) -> None:
        opponents = self.api.get_online_bots()
        
        if not opponents:
            Logger.warning("No opponents found.")
            return
        
        our_rating = None
        
        for bot in opponents:
            if bot["id"].lower() == self.bot_id.lower():
                our_rating = bot.get("perfs", {}).get("bullet", {}).get("rating")
                break
            
        if our_rating is None:
            Logger.warning("Could not determine own bullet rating, will send another request")
            our_rating = self.get_our_rating()



        opponents = [
            bot for bot in opponents if bot["id"].lower() != self.bot_id.lower()
        ]
        if not opponents:
            Logger.warning("No valid opponents (excluding self).")
            return
        
        opponents_with_rating = [
        bot for bot in opponents if "perfs" in bot and "bullet" in bot["perfs"]
    ]
        opponents_with_rating.sort(
            key=lambda bot: abs(bot["perfs"]["bullet"]["rating"] - our_rating)
        )

        num_to_keep = max(1, len(opponents_with_rating) // 10)
        closest_opponents = opponents_with_rating[:num_to_keep]

        opponent = random.choice(closest_opponents)
        opponent_id = opponent["id"]
        username = opponent["username"]
        Logger.info(f"Challenging bot: {username}")
        timelimit = random.choice([30, 45, 60])

        response = self.api.challenge(opponent_id, timelimit)
        if response.status_code == 200:
            Logger.info(f"Challenge sent to {username} with rating {opponent["perfs"]["bullet"]["rating"]}")
        else:
            Logger.warning(
                f"Failed to challenge {opponent_id}: {response.status_code} - {response.text}"
            )

    def periodic_challenger(self) -> None:
        while True:
            with self.active_games_lock:
                if len(self.active_games) < self.max_games:
                    Logger.info("Attempting to challenge an opponent.")
                    self.challenge_other_bot()
                else:
                    Logger.debug("Active games ongoing. Skipping challenge.")
                    
            time.sleep(300)

    def respond(self, game_id: str, board: chess.Board, is_white: bool) -> None:
        if board.is_game_over():
            self.handle_game_finish(is_white, game_id, board)
            return

        move = self.engine.make_move(board)
        Logger.debug(f"Game {game_id}: Made move {move}")
        self.make_move(game_id, move)

    def send_chat(self, game_id: str, text: str, room: str = "player") -> None:
        response = self.api.send_chat(game_id, text, room)
        if response.status_code != 200:
            Logger.warning(
                f"Failed to send chat: {response.status_code} - {response.text}"
            )
