from __future__ import annotations

import pygame

from graph import GameGraph
from layout import GraphLayout, UnitVector
from algorithm import AbstractSnakeAlgorithm


class ControllerFactory:
    @classmethod
    def get_controller(
        cls,
        name: str,
        graph: GameGraph,
        layout: GraphLayout = None,
        algorithm: AbstractSnakeAlgorithm = None,
    ) -> AbstractController | None:
        if name == "wsad":
            return WSADController(graph, layout)
        if name == "mouse":
            return MouseController(graph, layout)
        if name == "ai":
            return AIController(graph, algorithm)
        return None


class AbstractController:
    def __init__(self, graph: GameGraph):
        self.graph = graph

    def handle_event(self, event):
        raise NotImplemented

    def update(self):
        raise NotImplemented

    def move_snake(self):
        raise NotImplemented


class GUIController(AbstractController):
    def __init__(self, graph: GameGraph, layout: GraphLayout):
        super().__init__(graph)
        self.layout = layout

        self.direction = self.get_snakes_initial_direction()

    def get_snakes_initial_direction(self):
        vertex = self.graph.snake.head
        edge = self.graph.snake.body[0]
        return self.layout.edge_to_unit_vector(edge, edge.get_other(vertex))

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def move_snake(self):
        if self.direction is None:
            raise ValueError("Direction is not set.")
        self._move_snake(self.direction)

    def _move_snake(self, direction: UnitVector):
        snake_edges = self.graph.get_snakes_next_edges()
        snake_directions_dict = {
            self.layout.edge_to_unit_vector(edge, self.graph.snake.head): edge
            for edge in snake_edges
        }
        snake_next_direction = direction.get_closest(set(snake_directions_dict.keys()))
        snake_next_edge = snake_directions_dict[snake_next_direction]
        self.graph.move_snake(snake_next_edge)


class WSADController(GUIController):
    class Direction:
        UP = UnitVector(0, -1)
        DOWN = UnitVector(0, 1)
        LEFT = UnitVector(-1, 0)
        RIGHT = UnitVector(1, 0)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self.direction = self.Direction.LEFT
            if event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.direction = self.Direction.RIGHT
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.direction = self.Direction.UP
            if event.key in [pygame.K_DOWN, pygame.K_s]:
                self.direction = self.Direction.DOWN


class MouseController(GUIController):
    def update(self):
        x1, y1 = self.layout.get_vertex_coordinates(self.graph.snake.head)
        x2, y2 = pygame.mouse.get_pos()
        self.direction = UnitVector(x2 - x1, y2 - y1)


class AIController(AbstractController):
    def __init__(self, graph: GameGraph, algorithm: AbstractSnakeAlgorithm):
        super().__init__(graph)
        self.algorithm = algorithm

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def move_snake(self):
        snake_next_edge = self.algorithm.choose_next_edge()
        self.graph.move_snake(snake_next_edge)
