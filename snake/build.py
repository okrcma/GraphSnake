from __future__ import annotations

from graph import VertexType, EdgeType, VertexFactory, Edge, GameGraph, Vertex
from layout import GraphLayout


# TODO refactor (note: distance is not needed, walls aren't either)
def generate_grid(width, height, distance):
    def get_vertex_type(i, j, width, height):
        if i == 0 or i == width - 1 or j == 0 or j == height - 1:
            return VertexType.WALL
        return VertexType.EMPTY

    def get_edge_type(first, second):
        if first.type == VertexType.WALL and second.type == VertexType.WALL:
            return EdgeType.WALL
        return EdgeType.EMPTY

    x_offset = y_offset = distance

    factory = VertexFactory()
    layout = GraphLayout(
        (width - 1) * distance + 2 * x_offset, (height - 1) * distance + 2 * y_offset
    )

    vertices = set()
    rows = []
    for j in range(height):
        row = []
        for i in range(width):
            vertex_type = get_vertex_type(i, j, width, height)
            vertex = factory.create_vertex(vertex_type)
            layout.add_vertex(vertex, i * distance + x_offset, j * distance + y_offset)
            vertices.add(vertex)
            row.append(vertex)
        rows.append(row)

    edges = set()
    for i in range(width):
        for j in range(height):
            vertex_a = rows[j][i]
            if i < width - 1:
                vertex_b = rows[j][i + 1]
                edge_type = get_edge_type(vertex_a, vertex_b)
                edge = Edge(vertex_a, vertex_b, edge_type)
                edges.add(edge)
            if j < height - 1:
                vertex_c = rows[j + 1][i]
                edge_type = get_edge_type(vertex_a, vertex_c)
                edge = Edge(vertex_a, vertex_c, edge_type)
                edges.add(edge)

    i, j = width // 2, height // 2
    snake_head = rows[j - 1][i]
    snake_middle = rows[j][i]
    snake_tail = rows[j + 1][i]

    snake_vertices = [snake_head, snake_middle, snake_tail]
    graph = GameGraph(vertices, edges, snake_vertices)
    return graph, layout


class IsometricGridBuilder:
    """Builder for isometric grid graphs and layouts.

       *
      * *
     * * *
    * * * *

    """

    def build(self, base_count: int) -> tuple[GameGraph, GraphLayout]:
        """Build an isometric grid of equilateral triangles.

        Args:
            base_count: Number of vertices on one side of the grid. There have
                to be at least three vertices.

        Returns:
            Graph and layout.

        """
        if base_count < 3:
            raise ValueError(
                "The base of the grid has to have at least three vertices."
            )

        vertices_array = self._build_vertices(base_count)
        edges_set = self._build_edges(vertices_array)

        graph = self._build_graph(vertices_array, edges_set)
        layout = self._build_layout(vertices_array)

        return graph, layout

    def _build_vertices(self, base_count: int) -> list[list[Vertex]]:
        """Build the vertices and return them in 2D array.

        The first index i of the array goes from 0 to base_count, and the second index j
            goes from 0 to base_count-i.

        Args:
            base_count: Number of vertices on one side of the grid.

        Returns:
            The built vertices.

        """
        factory = VertexFactory()
        vertices_array = []

        for i in range(base_count):
            vertices_array.append([])
            for j in range(base_count - i):
                new_vertex = factory.create_vertex(VertexType.EMPTY)
                vertices_array[i].append(new_vertex)

        return vertices_array

    def _build_edges(self, vertices_array: list[list[Vertex]]) -> set[Edge]:
        """Build edges to form the grid."""
        edges_set = set()

        base_count = len(vertices_array[0])
        for i in range(base_count):
            for j in range(base_count - i - 1):
                new_edge = Edge(vertices_array[i][j], vertices_array[i][j + 1])
                edges_set.add(new_edge)
        for i in range(base_count - 1):
            for j in range(base_count - i - 1):
                new_edge = Edge(vertices_array[i][j], vertices_array[i + 1][j])
                edges_set.add(new_edge)
        for i in range(1, base_count):
            for j in range(base_count - i):
                new_edge = Edge(vertices_array[i][j], vertices_array[i - 1][j + 1])
                edges_set.add(new_edge)

        return edges_set

    def _build_graph(
        self, vertices_array: list[list[Vertex]], edges_set: set[Edge]
    ) -> GameGraph:
        """Build graph from the vertices and edges."""
        vertices_set = set(vertex for x in vertices_array for vertex in x)
        snake_vertices = vertices_array[0][0:3]
        return GameGraph(vertices_set, edges_set, snake_vertices)

    def _build_layout(self, vertices_array: list[list[Vertex]]) -> GraphLayout:
        """Build layout for the vertices."""
        base_count = len(vertices_array[0])
        width = height = base_count + 1
        layout = GraphLayout(width, height)

        for i in range(base_count):
            for j in range(base_count - i):
                x = (j + 1) + i / 2
                y = height - (i + 1)
                layout.add_vertex(vertices_array[i][j], x, y)

        return layout


# NOTE: arbitrary graph can be mapped using networkx.drawing.layout
