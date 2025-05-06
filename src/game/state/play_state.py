import time

import chess
import pygame

from utils import Board

from ..audio_player import AudioPlayer
from ..renderer import Renderer
from ..engine_controller import EngineController
from ..selection import Selection
from .game_state import GameState
from .promotion_state import PromotionState
from .checkmate_state import CheckmateState


ENGINE_PLAY = True


class PlayState(GameState):
    def __init__(self, game, model_name) -> None:
        self.game = game
        self.board = Board()
        self.renderer = Renderer(game.window)
        self.audio_player = AudioPlayer()
        self.engine = EngineController(model_name)

        self.selection = Selection()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT: # pylint: disable=no-member
            self.game.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # pylint: disable=no-member
            pos = pygame.mouse.get_pos()
            self.selection.selected_square = self.get_square_under_mouse(pos)
            if self.selection.selected_square is not None:
                square_index = chess.square(*self.selection.selected_square)
                self.selection.selected_piece = self.board.board.piece_at(square_index)
                self.selection.available_moves = self.board.legal_moves_from(square_index)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1: # pylint: disable=no-member
            pos = pygame.mouse.get_pos()
            self.selection.released_square = self.get_square_under_mouse(pos)
            self._handle_move()

    def _handle_move(self):
        if self.selection.selected_square and self.selection.released_square:
            from_sq = chess.square(*self.selection.selected_square)
            to_sq = chess.square(*self.selection.released_square)
            is_promotion = False
            move = None

            if self.board.piece_at(
                from_sq
            ).piece_type == chess.PAWN and chess.square_rank(to_sq) in (0, 7):
                is_promotion = True
                move = chess.Move(
                    from_sq, to_sq, promotion=chess.QUEEN
                )  # Temp to be a valid move
            else:
                move = chess.Move(from_sq, to_sq)

            if move in self.board.board.legal_moves:
                self.audio_player.play(
                    "take" if self.board.is_capture(move) else "knock"
                )

                if is_promotion:
                    self.game.change_state(PromotionState(self.game, self, move))
                    return

                self.board.push(move)
                self.engine.turn = True
                self.engine.time = time.time() + 1

        self.selection.reset()
        if self.board.board.is_checkmate():
            self.game.change_state(CheckmateState(self.game, self))


    def update(self) -> None:
        if ENGINE_PLAY:
            if (
                self.engine.turn
                and self.engine.time
                and time.time() >= self.engine.time
            ):
                move = self.engine.engine.make_move(self.board.board)
                self.audio_player.play(
                    "take" if self.board.is_capture(move) else "knock"
                )
                self.board.push(move)
                self.engine.turn = False
                self.engine.time = None

                if self.board.board.is_checkmate():
                    self.game.change_state(CheckmateState(self.game, self))

    def render(self, screen: pygame.Surface) -> None:
        self.renderer.draw_board()
        if self.selection.available_moves:
            self.renderer.draw_legal_moves(self.selection.available_moves)
            square = self.get_square_under_mouse(pygame.mouse.get_pos())
            if square is not None:
                hover_square = chess.square(*square)
                if hover_square in {move.to_square for move in self.selection.available_moves}:
                    self.renderer.draw_current_move(hover_square)

        self.renderer.draw_check_highlight(self.board)
        self.renderer.draw_pieces(self.board, self.selection.selected_square)
        self.renderer.draw_dragged_piece(self.selection.selected_piece, pygame.mouse.get_pos())
        pygame.display.flip()
