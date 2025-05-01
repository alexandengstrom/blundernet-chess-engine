import chess
import pygame

from .game_state import GameState

class PromotionState(GameState):
    def __init__(self, game, play_state, move):
        self.game = game
        self.move = move
        self.play_state = play_state
        self.renderer = play_state.renderer

        self.choices = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        self.rects = []

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(pos):
                    self.move.promotion = self.choices[i]
                    self.play_state.board.push(self.move)
                    self.play_state.selected_square = None
                    self.play_state.selected_piece = None
                    self.play_state.available_moves = []
                    self.game.change_state(self.play_state)
                    break

    def update(self):
        pass

    def render(self, screen):
            screen.fill((30, 30, 30))
            font = pygame.font.SysFont(None, 48)
            label = font.render("Choose promotion piece:", True, (255, 255, 255))
            screen.blit(label, (50, 50))

            self.rects.clear()
            for i, piece_type in enumerate(self.choices):
                rect = pygame.Rect(60, 120 + i * 80, 64, 64)
                pygame.draw.rect(screen, (80, 80, 80), rect)

                self.renderer.draw_piece_icon(screen, piece_type, self.play_state.board.board.turn, rect)
                self.rects.append(rect)

            pygame.display.flip()
