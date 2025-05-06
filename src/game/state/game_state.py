import pygame
from ..config import TILE_SIZE

class GameState:
    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass
    
    def get_square_under_mouse(self, pos):
        x, y = pos
        file = x // TILE_SIZE
        rank = 7 - (y // TILE_SIZE)
        return file, rank
