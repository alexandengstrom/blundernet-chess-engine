import os
from typing import List

import pygame

from game import config

from .game_state import GameState
from .play_state import PlayState


class StartState(GameState):
    def __init__(self, game) -> None:
        self.game = game
        self.font = pygame.font.SysFont("Arial", 36)
        self.models = list(
            filter(lambda filename: filename.endswith(".keras"), os.listdir("models"))
        )
        self.model_rects: List[pygame.Rect] = []

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:  # pylint: disable=no-member
            self.game.running = False

        elif (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1): # pylint: disable=no-member
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.model_rects):
                if rect.collidepoint(mouse_pos):
                    selected_model = self.models[i]
                    print(f"Selected model: {selected_model}")
                    self.game.change_state(
                        PlayState(self.game, selected_model.replace(".keras", ""))
                    )
                    break

    def update(self) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((30, 30, 30))
        self.model_rects.clear()

        title = self.font.render(
            "Select a model to start a game!", True, (255, 255, 255)
        )
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
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # pylint: disable=no-member
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # pylint: disable=no-member

        pygame.display.flip()
