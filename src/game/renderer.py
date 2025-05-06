import os

import chess
import pygame

from .config import DARK, LIGHT, TILE_SIZE


class Renderer:
    def __init__(self, window):
        self.window = window
        self.sprites = self.load_sprites()

    def load_sprites(self):
        sprites = {}
        base_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "sprites"
        )
        for piece in ["p", "n", "b", "r", "q", "k"]:
            for color in ["white", "black"]:
                key = piece.upper() if color == "white" else piece
                path = os.path.join(base_path, f"{color}_{piece}.png")
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.smoothscale(image, (TILE_SIZE, TILE_SIZE))
                sprites[key] = image
        return sprites

    def draw_board(self):
        for rank in range(8):
            for file in range(8):
                is_light = (file + rank) % 2 == 0
                color = LIGHT if is_light else DARK
                rect = pygame.Rect(
                    file * TILE_SIZE, rank * TILE_SIZE, TILE_SIZE, TILE_SIZE
                )
                pygame.draw.rect(self.window, color, rect)

    def draw_pieces(self, board, selected_square):
        for rank in range(8):
            for file in range(8):
                if (file, 7 - rank) == selected_square:
                    continue

                square_index = chess.square(file, 7 - rank)
                piece = board.board.piece_at(square_index)
                if piece:
                    rect = pygame.Rect(
                        file * TILE_SIZE, rank * TILE_SIZE, TILE_SIZE, TILE_SIZE
                    )
                    image = self.sprites.get(piece.symbol())
                    if image:
                        self.window.blit(image, rect)

    def draw_legal_moves(self, moves):
        dot_length = 4
        gap_length = 4
        color = (0, 0, 0)

        for move in moves:
            to_square = move.to_square
            file = chess.square_file(to_square)
            rank = 7 - chess.square_rank(to_square)

            x = file * TILE_SIZE
            y = rank * TILE_SIZE

            for i in range(0, TILE_SIZE, dot_length + gap_length):
                pygame.draw.line(
                    self.window,
                    color,
                    (x + i, y),
                    (min(x + i + dot_length, x + TILE_SIZE), y),
                    3,
                )

            for i in range(0, TILE_SIZE, dot_length + gap_length):
                pygame.draw.line(
                    self.window,
                    color,
                    (x + i, y + TILE_SIZE - 1),
                    (min(x + i + dot_length, x + TILE_SIZE), y + TILE_SIZE - 1),
                    3,
                )

            for i in range(0, TILE_SIZE, dot_length + gap_length):
                pygame.draw.line(
                    self.window,
                    color,
                    (x, y + i),
                    (x, min(y + i + dot_length, y + TILE_SIZE)),
                    3,
                )

            for i in range(0, TILE_SIZE, dot_length + gap_length):
                pygame.draw.line(
                    self.window,
                    color,
                    (x + TILE_SIZE - 1, y + i),
                    (x + TILE_SIZE - 1, min(y + i + dot_length, y + TILE_SIZE)),
                    3,
                )

    def draw_current_move(self, square):
        file = chess.square_file(square)
        rank = 7 - chess.square_rank(square)

        rect = pygame.Rect(file * TILE_SIZE, rank * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.window, (0, 0, 0), rect, width=4)

    def draw_check_highlight(self, board):
        if not board.is_check():
            return

        king_square = board.board.king(board.board.turn)
        if king_square is None:
            return

        file = chess.square_file(king_square)
        rank = 7 - chess.square_rank(king_square)
        rect = pygame.Rect(file * TILE_SIZE, rank * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.window, (255, 0, 0), rect, width=4)

    def draw_dragged_piece(self, piece, pos):
        if piece:
            x, y = pos
            image = self.sprites.get(piece.symbol())
            if image:
                rect = image.get_rect(center=(x, y))
                self.window.blit(image, rect)

    def draw_piece_icon(self, surface, piece_type, color, rect):
        key = {chess.QUEEN: "Q", chess.ROOK: "R", chess.BISHOP: "B", chess.KNIGHT: "N"}[
            piece_type
        ]
        key = key.upper() if color == chess.WHITE else key.lower()
        image = self.sprites.get(key)
        if image:
            scaled = pygame.transform.smoothscale(image, (rect.width, rect.height))
            surface.blit(scaled, rect)
