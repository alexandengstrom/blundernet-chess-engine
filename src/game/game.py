import pygame
import chess
from board import Board
from renderer import Renderer
from audio_player import AudioPlayer
import config
import utils
from engine import Engine
import time
from typing import Optional, Tuple, List
from .state import GameState, PlayState, StartState


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.window = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption("Chess Engine")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state: GameState = StartState(self) 

    def change_state(self, new_state: GameState) -> None:
        self.state.on_exit()
        self.state = new_state
        self.state.on_enter()

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                self.state.handle_event(event)
            self.state.update()
            self.state.render(self.window)
            self.clock.tick(60)
        pygame.quit()

        
        

