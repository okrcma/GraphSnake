from __future__ import annotations

import pygame
import pygame.gfxdraw
import argparse

from control import ControllerFactory, AbstractController
from gui import GUI
from layout import GraphLayout
from score import Score
from algorithm import AlgorithmFactory, AbstractSnakeAlgorithm
from graph import GameGraph
from build import generate_grid, IsometricGridBuilder

GRID_WIDTH = 10
GRID_HEIGHT = 20
EDGE_LENGTH = 40


class ProgramArgumentParser:
    def __init__(self):
        self._parser = argparse.ArgumentParser(description="Run GraphSnake.")
        self._parser.add_argument(
            "-c", "--controller", default="ai", help="Controller of the snake."
        )
        self._parser.add_argument(
            "-a", "--algorithm", default="path", help="Algorithm for the AI controller."
        )
        self._parser.add_argument(
            "-s",
            "--speed",
            type=int,
            default=10,
            help="Number of snake vertices the snake moves per second.",
        )

        self._args = self._parser.parse_args()

    def get_controller(
        self, graph: GameGraph, layout: GraphLayout = None
    ) -> AbstractController | None:
        arg_controller = self._args.controller.lower()
        algorithm = self.get_algorithm(graph)
        return ControllerFactory.get_controller(
            arg_controller, graph, layout, algorithm
        )

    def get_algorithm(self, graph: GameGraph) -> AbstractSnakeAlgorithm | None:
        arg_algorithm = self._args.algorithm.lower()
        return AlgorithmFactory.get_algorithm(arg_algorithm, graph)

    def get_speed(self) -> int:
        return self._args.speed


if __name__ == "__main__":
    args = ProgramArgumentParser()
    pygame.init()

    # graph, layout = generate_grid(GRID_WIDTH, GRID_HEIGHT, EDGE_LENGTH)
    graph, layout = IsometricGridBuilder().build(30)
    score = Score(graph)
    gui = GUI(graph, layout, score)
    controller = args.get_controller(graph, layout)

    clock = pygame.time.Clock()
    done = False
    graph.generate_apple_if_missing()
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.VIDEORESIZE:
                gui.on_window_resize(event)
            controller.handle_event(event)
        controller.update()
        controller.move_snake()
        graph.generate_apple_if_missing()
        gui.draw()

        clock.tick(args.get_speed())

    pygame.quit()
