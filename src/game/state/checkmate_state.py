import pygame
import chess

from .game_state import GameState

class CheckmateState(GameState):
    def __init__(self, game, play_state):
        self.game = game
        self.play_state = play_state
        self.renderer = play_state.renderer
        self.winner = "White" if play_state.board.board.turn == chess.BLACK else "Black"

        self.button_font = pygame.font.SysFont(None, 48)
        self.button_text = self.button_font.render("New Game", True, (255, 255, 255))
        self.button_rect = self.button_text.get_rect(center=(game.window.get_width() // 2, game.window.get_height() // 2 + 80))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:  # pylint: disable=no-member
            self.game.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                from .start_state import StartState
                self.game.change_state(StartState(self.game))

    def update(self) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        self.play_state.renderer.draw_board()
        self.play_state.renderer.draw_pieces(self.play_state.board, None)

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont(None, 72)
        text = title_font.render(f"Checkmate! {self.winner} won", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 40))
        screen.blit(text, text_rect)

        pygame.draw.rect(screen, (80, 80, 80), self.button_rect.inflate(20, 10), border_radius=10)
        screen.blit(self.button_text, self.button_rect)

        pygame.display.flip()
