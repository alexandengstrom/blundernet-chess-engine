import requests
import chess
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import random
import time


from engine import Engine
from logger import Logger

class LichessBot:
    def __init__(self, engine, token, max_games=5):
        self.engine: Engine = engine
        self.token: str = token
        self.max_games: int = max_games
        self.active_games = set()
        self.active_games_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_games)
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/x-ndjson"
        }
        self.bot_id = self.get_id()
        threading.Thread(target=self.periodic_challenger, daemon=True).start()

        
        
    def get_id(self):        
        try:
            resp = requests.get("https://lichess.org/api/account", headers=self.headers)
            resp.raise_for_status()
            return resp.json()["id"]
        except Exception as e:
            print("Failed to get bot ID:", e)
            raise
        
    def stream_events(self):
        url = "https://lichess.org/api/stream/event"
        response = requests.get(url, headers=self.headers, stream=True)
        for line in response.iter_lines():
            if line:
                yield json.loads(line)

    def accept_challenge(self, challenge_id):
        url = f"https://lichess.org/api/challenge/{challenge_id}/accept"
        requests.post(url, headers=self.headers)

    def stream_game(self, game_id):
        url = f"https://lichess.org/api/bot/game/stream/{game_id}"
        response = requests.get(url, headers=self.headers, stream=True)
        for line in response.iter_lines():
            if line:
                yield json.loads(line)

    def make_move(self, game_id, move):
        url = f"https://lichess.org/api/bot/game/{game_id}/move/{move}"
        response = requests.post(url, headers=self.headers)
        if response.status_code != 200:
            print("Failed to make move:", response.text)

    def run(self):
        Logger.info("Listening for incoming challenges...")
        for event in self.stream_events():
            if event['type'] == 'challenge':
                if event['challenge']['variant']['key'] == 'standard':
                    with self.active_games_lock:
                        if len(self.active_games) < self.max_games:
                            Logger.info(f"Accepting challenge: {event['challenge']['id']}")
                            self.accept_challenge(event['challenge']['id'])
                        else:
                            Logger.warning("Too many active games. Declining challenge.")
            elif event['type'] == 'gameStart':
                game_id = event['game']['id']
                with self.active_games_lock:
                    if len(self.active_games) < self.max_games:
                        self.active_games.add(game_id)
                        Logger.info(f"Game started: {game_id}")
                        self.executor.submit(self.play_game_wrapper, game_id)
                    else:
                        Logger.info(f"Max concurrent games reached. Ignoring game {game_id}")

    def play_game_wrapper(self, game_id):
        try:
            self.play_game(game_id)
        finally:
            with self.active_games_lock:
                self.active_games.discard(game_id)

    def play_game(self, game_id):
        board = chess.Board()
        is_white = None
        for event in self.stream_game(game_id):
            if event['type'] == 'gameFull':
                moves = event['state']['moves'].split()
                for move in moves:
                    board.push_uci(move)
                if event['white']['id'] == self.bot_id:
                    is_white = True
                    Logger.info(f"[Game {game_id}] We are playing as white!")
                else:
                    is_white = False
                    Logger.info(f"[Game {game_id}] We are playing as black!")

                self.send_chat(game_id, "Hello, I am a bot that only predicts my moves using a neural network trained on a low-end laptop.")
                
                if (is_white and board.turn == chess.WHITE) or (not is_white and board.turn == chess.BLACK):
                    self.respond(game_id, board)
            elif event['type'] == 'gameState':
                moves = event['moves'].split()
                board = chess.Board()
                for move in moves:
                    board.push_uci(move)
                if (is_white and board.turn == chess.WHITE) or (not is_white and board.turn == chess.BLACK):
                    self.respond(game_id, board)
            elif event['type'] == 'chatLine':
                continue
            elif event['type'] == 'gameFinish':
                self.send_chat(game_id, "Good game! Thanks for playing. 😊")
                winner = event.get('winner', None)
                
                if winner is None:
                    Logger.info(f"[Game {game_id}] over: Draw.")
                elif (winner == 'white' and is_white) or (winner == 'black' and not is_white):
                    Logger.info(f"[Game {game_id}] over: We won!")
                else:
                    Logger.info(f"[Game {game_id}] over: We lost.")
                break

        
    def challenge_other_bot(self):
        opponents = self.find_opponent()

        if not opponents:
            Logger.warning("No opponents found.")
            return

        opponents = [bot for bot in opponents if bot["id"].lower() != self.bot_id.lower()]
        if not opponents:
            Logger.warning("No valid opponents (excluding self).")
            return

        opponent = random.choice(opponents)
        opponent_id = opponent["id"]
        Logger.info(f"Challenging bot: {opponent_id}")
        timelimit = random.choice([15, 30, 45, 60, 90])
        print(timelimit)

        url = f"https://lichess.org/api/challenge/{opponent_id}"
        data = {
            "clock.limit": timelimit,
            "clock.increment": 0,
            "rated": "true",
            "color": "random"
        }
        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            Logger.info(f"Challenge sent to {opponent_id}")
        else:
            Logger.warning(f"Failed to challenge {opponent_id}: {response.status_code} - {response.text}")

    def periodic_challenger(self):
        while True:
            time.sleep(60)
            with self.active_games_lock:
                if len(self.active_games) < self.max_games:
                    Logger.info("Attempting to challenge an opponent.")
                    self.challenge_other_bot()
                else:
                    Logger.debug("Active games ongoing. Skipping challenge.")
    
    def find_opponent(self, max_results=200):
        url = f"https://lichess.org/api/bot/online?nb={max_results}"
        response = requests.get(url, headers=self.headers, stream=True)

        if response.status_code != 200:
            Logger.warning(f"Failed to fetch online bots: {response.status_code}")
            return

        opponents = []
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    opponents.append(data)
                except json.JSONDecodeError as e:
                    Logger.warning(f"Failed to parse line: {e}")
        
        return opponents


    def respond(self, game_id, board):
        if board.is_game_over():
            Logger.info(f"Game {game_id} is over. Result: {board.result()}")
            return
        
        move = self.engine.make_move(board)
        Logger.debug(f"Game {game_id}: Made move {move}")
        self.make_move(game_id, move)
        
    def send_chat(self, game_id, text, room="player"):
        url = f"https://lichess.org/api/bot/game/{game_id}/chat"
        data = {"room": room, "text": text}
        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            Logger.warning(f"Failed to send chat: {response.status_code} - {response.text}")


