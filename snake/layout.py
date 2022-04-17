from __future__ import annotations

import math

from graph import Vertex, Edge, VertexFactory, VertexType, EdgeType, GameGraph, Snake


class GraphLayout:
    """Assigns (x, y)-coordinates to vertices.

    Attributes:
        width: Width of the layout.
        height: Height of the layout.

    """

    def __init__(self, width: float, height: float):
        """Initializes the layout.

        Args:
            width: Width of the layout.
            height: Height of the layout.

        """
        self.width = width
        self.height = height
        self._vertex_coordinates_dict = {}

    def add_vertex(self, vertex: Vertex, x: float, y: float):
        """Adds vertex to the layout.

        Two vertices mustn't have the same coordinates, otherwise vector between them
        would be undefined.

        Args:
            vertex: Vertex to be added to the layout.
            x: x-coordinate of the vertex in the layout.
            y: y-coordinate if the vertex in the layout.

        """
        if (x, y) in self._vertex_coordinates_dict.values():
            raise ValueError("Two vertices mustn't have the same coordinates.")
        self._vertex_coordinates_dict[vertex] = (x, y)

    def get_vertex_coordinates(self, vertex: Vertex) -> tuple[int, int]:
        """Gets rounded vertex coordinates.

        The vertex coordinates are stored as floats but are rounded and returned as ints.

        Args:
            vertex: Vertex for which we get the coordinates.

        Returns:
            Integer coordinates of the vertex.

        """
        x, y = self._vertex_coordinates_dict[vertex]
        return round(x), round(y)

    def get_edge_coordinates(
        self, edge: Edge
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """Gets rounded edge coordinates.

        The edge coordinates are stored as floats but are rounded and returned as ints.

        Args:
            edge: Edge for which we get the coordinates.

        Returns:
            Integer coordinates of the edge.

        """
        return (
            self.get_vertex_coordinates(edge.first),
            self.get_vertex_coordinates(edge.second),
        )

    def edge_to_unit_vector(self, edge: Edge, origin: Vertex) -> UnitVector:
        """Gets unit vector along an edge.

        The direction of the vector is determined by the given vertex: it will be
        the origin of the vector.

        Args:
            edge: Edge along which we get the vector.
            origin: Origin of the vector.

        Returns:
            Unit vector along the edge.

        """
        other = edge.get_other(origin)
        x1, y1 = self.get_vertex_coordinates(origin)
        x2, y2 = self.get_vertex_coordinates(other)
        return UnitVector(x2 - x1, y2 - y1)

    def scale(self, width_ratio: float, height_ratio: float):
        """Scales the coordinates of vertices and width and height of the layout.

        Args:
            width_ratio: Ratio by which to scale x coordinates.
            height_ratio: Ratio by which to scale y coordinates.

        """
        old_coordinate_dict = self._vertex_coordinates_dict
        self._vertex_coordinates_dict = {}
        for vertex, (x, y) in old_coordinate_dict.items():
            self.add_vertex(vertex, x * width_ratio, y * height_ratio)

        self.width *= width_ratio
        self.height *= height_ratio

    def scale_to(self, width: float, height: float):
        """Scales the coordinates of vertices and width and height of the layout.

        The width and height ratios are determined by the current width and height
        of the layout and the given new width and height.

        Args:
            width: New width of the layout.
            height: New height of the layout.

        """
        width_ratio = width / self.width
        height_ratio = height / self.height
        self.scale(width_ratio, height_ratio)


class Vector:
    def __init__(self, x: float, y: float):
        if x == 0 and y == 0:
            raise ValueError("Vector cannot have both coordinates equal to zero.")

        self.x = x
        self.y = y

    def __add__(self, other: Vector):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector):
        return Vector(self.x - other.x, self.y - other.y)

    def get_size(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        size = self.get_size()
        self.x /= size
        self.y /= size

    def get_distance(self, other) -> float:
        if self == other:
            return 0
        return (self - other).get_size()

    def get_closest(self, vectors: set[Vector]) -> Vector:
        if len(vectors) == 0:
            raise ValueError("There are no vectors to choose from.")

        closest = None
        min_distance = None

        for other in vectors:
            distance = self.get_distance(other)
            if min_distance is None or distance < min_distance:
                closest = other
                min_distance = distance

        return closest

    def __eq__(self, other: Vector):
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"


class UnitVector(Vector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.normalize()


# TODO move somewhere else
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
    snake_body = [Edge(snake_head, snake_middle), Edge(snake_middle, snake_tail)]
    snake = Snake(snake_head, snake_body, snake_tail)

    graph = GameGraph(vertices, edges, snake)
    return graph, layout


# NOTE: arbitrary graph can be mapped using networkx.drawing.layout
