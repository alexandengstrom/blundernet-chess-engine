import pygame
import os

import config
from .play_state import PlayState
from .game_state import GameState

class StartState(GameState):
    def __init__(self, game: "Game") -> None:
        self.game = game
        self.font = pygame.font.SysFont("Arial", 36)
        self.models = list(filter(lambda filename: filename.endswith(".keras"), os.listdir("models")))
        self.model_rects = []

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.game.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.model_rects):
                if rect.collidepoint(mouse_pos):
                    selected_model = self.models[i]
                    print(f"Selected model: {selected_model}")
                    self.game.change_state(PlayState(self.game, selected_model))
                    break

    def update(self) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((30, 30, 30))
        self.model_rects.clear()

        title = self.font.render("Select a model to start a game!", True, (255, 255, 255))
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 40))

        mouse_pos = pygame.mouse.get_pos()
        hovering = False

        for i, model_name in enumerate(self.models):
            rect = pygame.Rect(100, 120 + i * 60, 400, 40)
            is_hovered = rect.collidepoint(mouse_pos)
            color = (255, 255, 0) if is_hovered else (200, 200, 0)
            text = self.font.render(model_name.replace(".keras", ""), True, color)
            screen.blit(text, rect.topleft)
            self.model_rects.append(rect)
            if is_hovered:
                hovering = True

        if hovering:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()

