import chess
import pygame
import time

from .game_state import GameState
from .promotion_state import PromotionState
from ..renderer import Renderer
from ..audio_player import AudioPlayer
from utils import Board
from engine import Engine

ENGINE_PLAY = True

class PlayState(GameState):
    def __init__(self, game, model) -> None:
        self.game = game
        self.board = Board()
        self.renderer = Renderer(game.window)
        self.audio_player = AudioPlayer()
        self.engine = Engine(model)

        self.selected_square = None
        self.selected_piece = None
        self.released_square = None
        self.available_moves = []

        self.engines_turn = False
        self.engine_move_time = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.game.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            self.selected_square = self.get_square_under_mouse(pos)
            square_index = chess.square(*self.selected_square)
            self.selected_piece = self.board.board.piece_at(square_index)
            self.available_moves = self.board.legal_moves_from(square_index)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            pos = pygame.mouse.get_pos()
            self.released_square = self.get_square_under_mouse(pos)
            self._handle_move()

    def _handle_move(self):
        if self.selected_square and self.released_square:
            from_sq = chess.square(*self.selected_square)
            to_sq = chess.square(*self.released_square)
            is_promotion = False
            move = None

            if (self.board.piece_at(from_sq).piece_type == chess.PAWN and
                    chess.square_rank(to_sq) in (0, 7)):
                is_promotion = True
                move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN) # Temp to be a valid move
            else:
                move = chess.Move(from_sq, to_sq)

            if move in self.board.board.legal_moves:
                self.audio_player.play("take" if self.board.is_capture(move) else "knock")
                
                if is_promotion:
                    self.game.change_state(PromotionState(self.game, self, move))
                    return
                    
                self.board.push(move)
                self.engines_turn = True
                self.engine_move_time = time.time() + 1

        self.selected_square = None
        self.selected_piece = None
        self.available_moves = []

    def update(self) -> None:
        if ENGINE_PLAY:
            if self.engines_turn and self.engine_move_time and time.time() >= self.engine_move_time:
                move = self.engine.make_move(self.board.board)
                self.audio_player.play("take" if self.board.is_capture(move) else "knock")
                self.board.push(move)
                self.engines_turn = False
                self.engine_move_time = None


    def render(self, screen: pygame.Surface) -> None:
        self.renderer.draw_board(self.board)
        if self.available_moves:
            self.renderer.draw_legal_moves(self.available_moves)
            hover_square = chess.square(*self.get_square_under_mouse(pygame.mouse.get_pos()))
            if hover_square in {move.to_square for move in self.available_moves}:
                self.renderer.draw_current_move(hover_square)

        self.renderer.draw_check_highlight(self.board)
        self.renderer.draw_pieces(self.board, self.selected_square)
        self.renderer.draw_dragged_piece(self.selected_piece, pygame.mouse.get_pos())
        pygame.display.flip()

