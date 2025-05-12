import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
import traceback

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
        self.last_moves: Dict[str, Optional[str]] = {}
        
    def stats(self):
        info = self.api.get_account()

        matches_played = info["count"]["all"]
        wins = info["count"]["win"]
        draws = info["count"]["draw"]
        losses = info["count"]["loss"]

        win_pct = (wins / matches_played) * 100 if matches_played else 0
        draw_pct = (draws / matches_played) * 100 if matches_played else 0
        loss_pct = (losses / matches_played) * 100 if matches_played else 0

        bullet_rating = info["perfs"].get("bullet", {}).get("rating", "N/A")
        blitz_rating = info["perfs"].get("blitz", {}).get("rating", "N/A")
        rapid_rating = info["perfs"].get("rapid", {}).get("rating", "N/A")

        username = info["username"]

        print(f"\nStats for {username}")
        print("=" * 30)
        print(f"Total games played : {matches_played}")
        print(f"  Wins             : {wins} ({win_pct:.2f}%)")
        print(f"  Draws            : {draws} ({draw_pct:.2f}%)")
        print(f"  Losses           : {losses} ({loss_pct:.2f}%)")
        print("-" * 30)
        print(f"Bullet rating      : {bullet_rating}")
        print(f"Blitz rating       : {blitz_rating}")
        print(f"Rapid rating       : {rapid_rating}")
        print("=" * 30)
        

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
        threading.Thread(target=self.periodic_challenger, daemon=True).start()
        Logger.info("Listening for incoming challenges...")
        
        for event in self.api.stream_events():
            if event["type"] == "challenge":
                challenge = event["challenge"]
                if (
                    challenge["variant"]["key"] == "standard" and
                    challenge["challenger"]["id"].lower() != self.bot_id.lower()
                ):
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
            elif event["type"] == "challengeDeclined":
                Logger.info(f"Challenge was declined by {challenge["destUser"]["id"]}.")
            elif event["type"] == "gameStart":
                game_id = event["game"]["id"]
                with self.active_games_lock:
                    if len(self.active_games) < self.max_games:
                        self.active_games.add(game_id)
                        Logger.info(f"Game started: {game_id}")
                        self.executor.submit(self.play_game_wrapper, game_id)
                    else:
                        Logger.warning(
                            f"Max concurrent games reached. Ignoring game {game_id}"
                        )
            elif event["type"] == "gameFinish":
                game = event["game"]
                board = chess.Board(game["fen"])
                our_color = game["color"]
                game_id = game["id"]
                status = game.get("status", {}).get("name", "unknown").lower()
                opponent_id = game.get("opponent", {}).get("id", "Unknown")
                result = board.result()

                if (result == "1-0" and our_color == "white") or (result == "0-1" and our_color == "black"):
                    Logger.info(f"\033[92mWe won the game {game_id} against {opponent_id}, status: {status}!\033[0m")

                elif (result == "1-0" and our_color == "black") or (result == "0-1" and our_color == "white"):
                    Logger.info(f"\033[91mWe lost the game {game_id} against {opponent_id}, status: {status}.\033[0m")
                elif status == "aborted":
                    Logger.info(f"Game {game_id} vs {opponent_id} was aborted.")
                else:
                    Logger.info(f"Game {game_id} vs {opponent_id} ended with status {status}")

    def play_game_wrapper(self, game_id: str) -> None:
        try:
            self.play_game(game_id)
        except Exception as e:
            error_message = f"Game {game_id} crashed. Exception: {str(e)}\n{traceback.format_exc()}"
            Logger.error(error_message)
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
            
        last_move = moves[-1] if moves else None
        if self.last_moves.get(game_id) == last_move:
            return

        if (is_white and board.turn == chess.WHITE) or (not is_white and board.turn == chess.BLACK):
            self.last_moves[game_id] = last_move
            self.respond(game_id, board, is_white)


    def handle_game_finish(self, is_white: Optional[bool], game_id: str, board: chess.Board) -> None:
        winner = None
        
        result = board.result()
        
        if result == "1-0":
            winner = "white"
        elif result == "0-1":
            winner = "black"

        if winner is None:
            self.send_chat(game_id, self.chat.on_draw(board))
        elif (winner == "white" and is_white) or (winner == "black" and not is_white):
            self.send_chat(game_id, self.chat.on_win(board))
        else:
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

        num_to_keep = max(1, len(opponents_with_rating) // 5)
        closest_opponents = opponents_with_rating[:num_to_keep]

        opponent = random.choice(closest_opponents)
        opponent_id = opponent["id"]
        username = opponent["username"]
        timelimit = random.choice([60])

        response = self.api.challenge(opponent_id, timelimit)
        if response.status_code == 200:
            Logger.info(f"Challenge sent to {username} with rating {opponent["perfs"]["bullet"]["rating"]} for a {timelimit}s game.")
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
