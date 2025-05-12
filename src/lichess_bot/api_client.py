import requests
import threading
import time
from typing import Dict, Generator, List, Optional
import json

class ApiClient:
    BASE_URL = "https://lichess.org/api"

    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/x-ndjson"
        })
        self.block_until: float = 0
        self.lock = threading.Lock()

    def _handle_rate_limit(self, response: requests.Response) -> None:
        if response.status_code == 429:
            with self.lock:
                self.block_until = time.time() + 15 * 60
            raise RuntimeError("Rate limited: pausing for 15 minutes")

    def _wait_if_blocked(self) -> None:
        while time.time() < self.block_until:
            time.sleep(60)

    def _get(self, endpoint: str, stream: bool = False) -> requests.Response:
        self._wait_if_blocked()
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, stream=stream, timeout=10)
        self._handle_rate_limit(response)
        response.raise_for_status()
        return response

    def _post(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        self._wait_if_blocked()
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.session.post(url, data=data, headers=headers, timeout=10)
        self._handle_rate_limit(response)
        return response

    def get_account(self) -> Dict:
        return self._get("account").json()

    def get_rating(self) -> int:
        return self.get_account()["perfs"]["bullet"]["rating"]

    def stream_events(self) -> Generator[Dict, None, None]:
        response = self._get("stream/event", stream=True)
        for line in response.iter_lines():
            if line:
                yield json.loads(line)

    def accept_challenge(self, challenge_id: str) -> None:
        self._post(f"challenge/{challenge_id}/accept")

    def stream_game(self, game_id: str) -> Generator[Dict, None, None]:
        response = self._get(f"bot/game/stream/{game_id}", stream=True)
        for line in response.iter_lines():
            if line:
                yield json.loads(line)

    def make_move(self, game_id: str, move: str) -> requests.Response:
        return self._post(f"bot/game/{game_id}/move/{move}")

    def send_chat(self, game_id: str, text: str, room: str = "player") -> requests.Response:
        data = {"room": room, "text": text}
        return self._post(f"bot/game/{game_id}/chat", data=data)

    def challenge(self, opponent_id: str, time_limit: int) -> requests.Response:
        data = {
            "clock.limit": time_limit,
            "clock.increment": 0,
            "rated": "true",
            "color": "random"
        }
        return self._post(f"challenge/{opponent_id}", data=data)

    def get_online_bots(self, max_results: int = 200) -> List[Dict]:
        response = self._get(f"bot/online?nb={max_results}", stream=True)
        bots = []
        for line in response.iter_lines():
            if line:
                bots.append(json.loads(line))
        return bots
