from __future__ import annotations

import random


class VertexType:
    NONE = 0
    EMPTY = 1
    WALL = 2
    SNAKE = 3
    APPLE = 4


class Vertex:
    def __init__(self, id: str, type: VertexType = VertexType.NONE):
        self._id = id
        self.type = type

    def __eq__(self, other: Vertex):
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"<{self._id}>"


class VertexFactory:
    def __init__(self):
        self._next_id_int = 0

    def create_vertex(self, type: VertexType = VertexType.NONE) -> Vertex:
        id = str(self._next_id_int)
        self._next_id_int += 1
        return Vertex(id, type)


class EdgeType:
    NONE = 0
    EMPTY = 1
    SNAKE = 2
    WALL = 3


class Edge:
    def __init__(
        self,
        first: Vertex,
        second: Vertex,
        type: EdgeType = EdgeType.NONE,
        directed: bool = False,
    ):
        self.first = first
        self.second = second
        self.type = type
        self.directed = directed

    def get_other(self, vertex: Vertex) -> Vertex:
        if self.first == vertex:
            return self.second
        if self.second == vertex:
            return self.first
        raise ValueError

    def __eq__(self, other: Edge):
        if self.directed:
            return (
                other.directed
                and self.first == other.first
                and self.second == other.second
            )

        return not other.directed and (
            (self.first == other.first and self.second == other.second)
            or (self.first == other.second and self.second == other.first)
        )

    def __hash__(self):
        if self.directed:
            return hash((self.directed, self.first, self.second))
        return hash((self.directed, hash(self.first) + hash(self.second)))

    def __repr__(self):
        if self.directed:
            return f"({self.first, self.second})"
        return f"{{{self.first}, {self.second}}}"


class Graph:
    def __init__(self, vertices: set[Vertex], edges: set[Edge]):
        self.vertices = vertices
        self.edges = edges

        if not self.verify():
            raise ValueError("Vertices and edges do not form proper graph.")

        self._incidence_dict = {}
        for vertex in self.vertices:
            self._incidence_dict.setdefault(vertex, set())
        for edge in self.edges:
            self._incidence_dict[edge.first].add(edge)
            self._incidence_dict[edge.second].add(edge)

    def get_incident_edges(self, vertex: Vertex):
        return self._incidence_dict[vertex]

    def verify(self):
        """Verifies if the sets of vertices and edges form a graph.

        Both vertices of each edge have to be in `self.vertices` and looped edges
        (i.e. edges with only one vertex) are not allowed.

        Returns:
            bool: True or False that the sets of vertices and edges form a graph.
        """
        for edge in self.edges:
            if (
                edge.first not in self.vertices
                or edge.second not in self.vertices
                or edge.first == edge.second
            ):
                return False
        return True


class GameGraph(Graph):
    def __init__(self, vertices: set[Vertex], edges: set[Edge], snake: Snake):
        super().__init__(vertices, edges)
        self.snake = snake
        self.apples = set()
        self.snake.apple_callback = self._on_eaten_apple

        self.apple_callback = lambda: None

    def get_snakes_next_edges(self):
        return set(
            edge
            for edge in self.get_incident_edges(self.snake.head)
            if edge.type != EdgeType.SNAKE
        )

    def move_snake(self, edge: Edge):
        self.snake.move(edge)

    def generate_apple_if_missing(self):
        if len(self.apples) == 0:
            self.generate_apple()

    def generate_apple(self):
        empty_vertices = list(self._get_empty_vertices())
        idx = random.randrange(
            len(empty_vertices)
        )  # TODO generate with seeded generator given by Game
        apple = empty_vertices[idx]
        apple.type = VertexType.APPLE
        self.apples.add(apple)

    def _get_empty_vertices(self):
        return set(
            vertex for vertex in self.vertices if vertex.type == VertexType.EMPTY
        )

    def _on_eaten_apple(self, vertex: Vertex):
        self.apples.remove(vertex)
        self.apple_callback()


class Snake:
    """Class representing the snake.

    Attributes:
        head: Head of the snake.
        body: List of edges defining the body as a path from head to tail.
        tail: The tail of the snake.

    """

    def __init__(self, head: Vertex, body: list[Edge], tail: Vertex):
        """Initializes the snake.

        The edges of the body must define a path from head to tail.

        Args:
            head: Head of the snake.
            body: List of edges defining the body as a path from head to tail.
            tail: The tail of the snake.
        """
        self.head = head
        self.body = body
        self.tail = tail
        self._left_edge = None

        self.verify()
        self.update_types()

        self.apple_callback = lambda vertex: None

    def verify(self) -> bool:
        """Verifies that head, body and tail form a snake.

        Body has to form a path with head on one end and tail on the other.

        Returns:
            True or False that head, body and tail form a snake.
        """
        segments = set()
        segment = self.head
        for edge in self.body:
            if segment in segments:
                return False
            segments.add(segment)
            try:
                segment = edge.get_other(segment)
            except ValueError:
                return False
        return segment == self.tail

    def get_segments(self) -> list[Vertex]:
        """Returns list of snake's body vertices.

        Returns:
            Vertices of the snake in sequence starting from head and ending in tail.
        """
        segments = []
        segment = self.head
        for edge in self.body:
            segments.append(segment)
            segment = edge.get_other(segment)
        segments.append(self.tail)
        return segments

    def update_types(self):
        """Update types of all edges and vertices of the snake.

        All edges and vertices of snake's current position are set to type snake.
        If snaked moved in the last step (instead of growing), the left vertex and edge
        are set to type empty.

        """
        for vertex in self.get_segments():
            vertex.type = VertexType.SNAKE
        for edge in self.body:
            edge.type = EdgeType.SNAKE
        if self._left_edge is not None:
            left_vertex = self._left_edge.get_other(self.tail)
            left_vertex.type = VertexType.EMPTY
            self._left_edge.type = EdgeType.EMPTY

    def move(self, edge: Edge):
        """Moves the snake along the given edge.

        The edge has to be incident with snake's head. The other vertex of the edge
        is the next vertex to which the snake will move. If the next vertex is a wall
        or snake, then the snake dies. If the next vertex is an apple, then the snake
        doesn't move, but instead grows such that its tail remains the same.

        This method updates types of all vertices and edges of the snake and also
        the left vertex and edge.

        Args:
            edge: Edge incident with snake's head. The snake will move along this edge.

        """
        next_vertex = edge.get_other(self.head)
        if next_vertex.type in [VertexType.WALL, VertexType.SNAKE]:
            self.die()

        self.head = next_vertex
        if next_vertex.type == VertexType.APPLE:
            self._on_eaten_apple(next_vertex)
            self._left_edge = None
            self.body = [edge] + self.body
        else:
            self._left_edge = self.body[-1]
            self.body = [edge] + self.body[:-1]
            self.tail = self._left_edge.get_other(self.tail)

        self.update_types()

    def _on_eaten_apple(self, vertex: Vertex):
        self.apple_callback(vertex)

    def die(self):
        raise Exception("Snake died!")  # TODO
