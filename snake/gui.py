from __future__ import annotations

import pygame
import pygame.gfxdraw

from graph import GameGraph, Vertex, VertexType, EdgeType, Edge
from layout import GraphLayout
from score import Score


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


class GUI:
    def __init__(self, graph: GameGraph, layout: GraphLayout, score: Score):
        self.graph = graph
        self.layout = layout

        self.window_width = 1000
        self.window_height = 800

        self.graph_panel = Panel(GraphSurface(graph, layout, 800, 800), 0, 0)
        self.score_panel = Panel(ScoreSurface(score, 200, 800), 800, 0)
        self.panels = [self.graph_panel, self.score_panel]
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height), flags=pygame.RESIZABLE
        )

    def draw(self):
        for panel in self.panels:
            panel.draw(self.screen)
        pygame.display.flip()

    def on_window_resize(self, event):
        self.scale_to(event.w, event.h)

    def scale_to(self, width: int, height: int):
        width_ratio = width / self.window_width
        height_ratio = height / self.window_height

        for panel in self.panels:
            panel.scale(width_ratio, height_ratio)

        self.window_width = width
        self.window_height = height


class AbstractSurface:
    def get_surface(self):
        raise NotImplemented

    def draw(self):
        raise NotImplemented

    def scale(self, width_ratio: float, height_ratio: float):
        raise NotImplemented


class Panel:
    def __init__(self, surface: AbstractSurface, x: int, y: int):
        self.surface = surface
        self.x = x
        self.y = y

    def draw(self, screen):
        self.surface.draw()
        screen.blit(self.surface.get_surface(), (self.x, self.y))

    def scale(self, width_ratio: float, height_ratio: float):
        self.surface.scale(width_ratio, height_ratio)
        self.x *= width_ratio
        self.y *= height_ratio


class GraphSurface(AbstractSurface):
    def __init__(self, graph: GameGraph, layout: GraphLayout, width: int, height: int):
        self.graph = graph
        self.layout = layout

        self.layout.scale_to(width, height)
        self._surface = pygame.Surface((width, height))

        self.vertex_radius = 10

    def get_surface(self):
        return self._surface

    def draw(self):
        for edge in self.graph.edges:
            (x1, y1), (x2, y2) = self.layout.get_edge_coordinates(edge)
            pygame.gfxdraw.line(
                self._surface,
                x1,
                y1,
                x2,
                y2,
                self.get_edge_color(edge),
            )
        for vertex in self.graph.vertices:
            x, y = self.layout.get_vertex_coordinates(vertex)
            pygame.gfxdraw.filled_circle(
                self._surface,
                x,
                y,
                self.vertex_radius,
                self.get_vertex_color(vertex),
            )

    def scale(self, width_ratio: float, height_ratio: float):
        self.layout.scale(width_ratio, height_ratio)
        self._surface = pygame.Surface((self.layout.width, self.layout.height))

    def get_vertex_color(self, vertex: Vertex):
        if vertex.type == VertexType.WALL:
            return Color.GRAY
        if vertex.type == VertexType.SNAKE:
            return Color.GREEN
        if vertex.type == VertexType.APPLE:
            return Color.RED
        return Color.WHITE

    def get_edge_color(self, edge: Edge):
        if edge.type == EdgeType.WALL:
            return Color.GRAY
        if edge.type == EdgeType.SNAKE:
            return Color.GREEN
        return Color.WHITE


class ScoreSurface(AbstractSurface):
    BACKGROUND_COLOR = Color.BLACK
    TEXT_COLOR = Color.WHITE
    TEXT_FONT = "latinmodernmono"

    def __init__(self, score: Score, width: int, height: int):
        self.score = score

        self.width = width
        self.height = height
        self._surface = pygame.Surface((width, height))

        self._font = pygame.freetype.SysFont(self.TEXT_FONT, 1)

    def get_surface(self) -> pygame.Surface:
        return self._surface

    def draw(self):
        self._surface.fill(self.BACKGROUND_COLOR)

        score_string = f"{self.score.get_score():5.0f}"
        self._draw_text("SCORE", 0)
        self._draw_text(score_string, 1)

        moves_string = f"{self.score.get_moves():5.0f}"
        self._draw_text("MOVES", 2)
        self._draw_text(moves_string, 3)

        ratio_string = f"{self.score.get_moves_per_point():5.0f}"
        self._draw_text("  AVG", 4)
        self._draw_text(ratio_string, 5)

    def scale(self, width_ratio: float, height_ratio: float):
        self.width *= width_ratio
        self.height *= height_ratio
        self._surface = pygame.Surface((self.width, self.height))

    def _draw_text(self, text: str, line_number: int):
        x = self._get_font_offset()
        y = self._get_font_offset() + self._get_font_size() * line_number
        self._text_surface = self._font.render_to(
            surf=self._surface,
            dest=(x, y),
            text=text,
            fgcolor=self.TEXT_COLOR,
            size=self._get_font_size(),
        )

    def _get_font_size(self) -> int:
        return self.width // 3

    def _get_font_offset(self) -> int:
        return self.width // 12
