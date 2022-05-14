"""This module contains the game logic and classes maintaining the game graph state."""
from __future__ import annotations

import random


class VertexType:
    """Enum of types of vertices."""

    NONE = 0
    EMPTY = 1
    WALL = 2
    SNAKE = 3
    APPLE = 4


class Vertex:
    """Class representing vertices of the game graph.

    Attributes:
        type (VertexType): Type of the vertex.

    """

    def __init__(self, id: str, type: VertexType = VertexType.NONE):
        """Initializes the vertex.

        Args:
            id (str): An ID used to test equality of vertices. No two vertices should
                have the same id.
            type (VertexType): Type of the vertex.

        """
        self._id = id
        self.type = type

    def __eq__(self, other: Vertex) -> bool:
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"<{self._id}>"


class VertexFactory:
    """Creates vertices with incremental IDs."""

    def __init__(self):
        """Initializes the factory."""
        self._next_id_int = 0

    def create_vertex(self, type: VertexType = VertexType.NONE) -> Vertex:
        """Creates new vertex with the given type and unique id.

        Args:
            type (VertexType): Type of the vertex.

        Returns:
            Vertex: The new vertex.

        """
        id = str(self._next_id_int)
        self._next_id_int += 1
        return Vertex(id, type)


class EdgeType:
    """Enum of types of edges."""

    NONE = 0
    EMPTY = 1
    SNAKE = 2
    WALL = 3


class Edge:
    """Class representing edges of the game graph.

    Attributes:
        first (Vertex): First vertex incident with this edge.
        second (Vertex): Second vertex incident with this edge.
        type (EdgeType): Type of the edge.
        directed (bool): Whether the edge is directed or not.

    """

    def __init__(
        self,
        first: Vertex,
        second: Vertex,
        type: EdgeType = EdgeType.NONE,
        directed: bool = False,
    ):
        """Initializes the edge.

        Args:
            first (Vertex): First vertex incident with this edge.
            second (Vertex): Second vertex incident with this edge.
            type (EdgeType): Type of the edge.
            directed (bool): Whether the edge is directed or not.

        """
        self.first = first
        self.second = second
        self.type = type
        self.directed = directed

    def get_other(self, vertex: Vertex) -> Vertex:
        """Returns the vertex of the edge that is not the given vertex.

        Args:
            vertex (Vertex): One of the vertices incident with this edge. The other
                vertex will be returned.

        Returns:
            Vertex: The other vertex.

        """
        if self.first == vertex:
            return self.second
        if self.second == vertex:
            return self.first
        raise ValueError

    def __eq__(self, other: Edge) -> bool:
        """Equality comparison method.

        Edges are equal if they have the same vertices and both are oriented or both
            are not oriented. If the edges are oriented, then the order of the vertices
            matters.

        Args:
            other (Edge): The other edge compared to this edge.

        Returns:
            bool: True if the edges are equal, False otherwise.

        """
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

    def __hash__(self) -> int:
        if self.directed:
            return hash((self.directed, self.first, self.second))
        return hash((self.directed, hash(self.first) + hash(self.second)))

    def __repr__(self) -> str:
        if self.directed:
            return f"({self.first, self.second})"
        return f"{{{self.first}, {self.second}}}"


class Graph:
    """Graph as a set of vertices and a set of edges.

    Attributes:
        vertices (set[Vertex]): Set of vertices of the graph.
        edges (set[Edge]): Set of edges of the graph. Vertices of the edges have
            to be in the set of vertices of this graph.

    """

    def __init__(self, vertices: set[Vertex], edges: set[Edge]):
        """Initializes the graph.

        Args:
            vertices (set[Vertex]): Set of vertices of the graph.
            edges (set[Edge]): Set of edges of the graph. Vertices of the edges have
                to be in the set of vertices of this graph.

        """
        self.vertices = vertices
        self.edges = edges

        if not self.verify():
            raise ValueError("Vertices and edges do not form proper graph.")

        self._edge_dict = {}
        for vertex in self.vertices:
            self._edge_dict.setdefault(vertex, {})
        for edge in self.edges:
            self._edge_dict[edge.first][edge.second] = edge
            if not edge.directed:
                self._edge_dict[edge.second][edge.first] = edge

        self._incidence_dict = {}
        for vertex in self.vertices:
            self._incidence_dict.setdefault(vertex, set())
        for edge in self.edges:
            self._incidence_dict[edge.first].add(edge)
            self._incidence_dict[edge.second].add(edge)

    def get_edge(self, first: Vertex, second: Vertex) -> Edge | None:
        """Returns edge incident with the two given vertices.

        It is important to get the edges using this method rather than creating
            new Edge objects with the same vertices, because the game state is
            maintained by vertices and edges stored in this graph.

        Args:
            first (Vertex): The first vertex of the sought edge.
            second (Vertex): The second vertex of the sought edge.

        Returns:
            Edge: Returns the edge between the two vertices or None if there is
                no such edge in the graph.

        """
        return self._edge_dict[first].get(second)

    def get_incident_edges(self, vertex: Vertex) -> set[Edge]:
        """Returns edges incident with the given vertex.

        Args:
            vertex (Vertex): The vertex with which the edges are incident.

        Returns:
            set[Edge]: Set of edges incident with the given vertex.

        """
        return self._incidence_dict[vertex]

    def verify(self) -> bool:
        """Verifies whether the sets of vertices and edges form a graph.

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
    """Graph with the game logic.

    This is the main class that maintains the game state.

    Attributes:
        vertices (set[Vertex]): Set of vertices of the graph.
        edges (set[Edge]): Set of edges of the graph. Vertices of the edges have
            to be in the set of vertices of this graph.
        snake (Snake): Snake object maintaining the state of the vertices and edges
            of the snake.
        apples (set[Vertex]): Set of vertices which are currently apples.
        apple_callback (Callable[[Vertex], None]): Callback which will be called when
            the snake moves and eats an apple. The vertex parameter of the callback
            will be set to the apple vertex.

    """

    def __init__(
        self, vertices: set[Vertex], edges: set[Edge], snake_vertices: list[Vertex]
    ):
        """Initializes the graph.

        Args:
            vertices (set[Vertex]): Set of vertices of the graph.
            edges (set[Edge]): Set of edges of the graph. Vertices of the edges have
                to be in the set of vertices of this graph.
            snake_vertices (list[Vertex]): List of snake vertices. The vertices have
                to form a path of length at least two. The first vertex will be the
                head, the second vertex will be the tail. The vertices in this list
                have to be in the set of vertices in the previous parameter.

        """
        super().__init__(vertices, edges)
        self.apples = set()
        self.apple_callback = lambda: None

        self.snake = None
        self._set_snake(snake_vertices)

    def _set_snake(self, snake_vertices: list[Vertex]):
        self.snake = Snake.from_vertices(self, snake_vertices)
        self.snake.apple_callback = self._on_eaten_apple

    def get_snakes_next_edges(self) -> set[Edge]:
        """Gets the edges where the snake can move next.

        These edges are all the edges incident with the snake's head except for edges
            of type snake.

        Returns:
            set[Edge]: Set of the edges where the snake can move next.

        """
        return set(
            edge
            for edge in self.get_incident_edges(self.snake.head)
            if edge.type != EdgeType.SNAKE
        )

    def move_snake(self, edge: Edge):
        """Moves the snake along the given edge.

        See Snake.move method for more details.

        Args:
            edge (Edge): Edge incident with snake's head. The snake will move along
                this edge.

        """
        self.snake.move(edge)

    def generate_apple_if_missing(self):
        """Generates new apple if there is currently none in the game."""
        if len(self.apples) == 0:
            self.generate_apple()

    def generate_apple(self):
        """Generates new apple in a random empty vertex."""
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
        head (Vertex): Head of the snake.
        body (list[Edge]): List of edges defining the body as a path from head to tail.
        tail (Vertex): The tail of the snake.
        apple_callback (Callable[[Vertex], None]): Callback which will be called when
            the snake moves and eats an apple. The vertex parameter of the callback
            will be set to the apple vertex.

    """

    def __init__(self, head: Vertex, body: list[Edge], tail: Vertex):
        """Initializes the snake.

        The edges of the body must define a path from head to tail.

        Args:
            head (Vertex): Head of the snake.
            body (list[Edge]): List of edges defining the body as a path from head to tail.
            tail (Vertex): The tail of the snake.

        """
        self.head = head
        self.body = body
        self.tail = tail
        self._left_edge = None

        if not self.verify():
            raise ValueError("Head, body and tail do not form proper snake.")

        self.update_types()
        self.apple_callback = lambda vertex: None

    @classmethod
    def from_vertices(cls, graph: GameGraph, snake_vertices: list[Vertex]) -> Snake:
        """Construct snake from the given list of vertices.

        The list of vertices has to contain at least two vertices, and the vertices
            in order have to form a path. The first vertex is the head and the last
            vertex is the tail.

        Args:
            graph: Game graph in which to construct the snake.
            snake_vertices: List of vertices from which to construct the snake. The
                vertices have to be in the game graph.

        Returns:
            The constructed snake.

        """
        if len(snake_vertices) < 2:
            raise ValueError("Cannot construct snake from less than two vertices.")

        head = snake_vertices[0]
        body = []
        tail = snake_vertices[-1]

        first = head
        for second in snake_vertices[1:]:
            edge = graph.get_edge(first, second)
            body.append(edge)
            first = second

        return cls(head, body, tail)

    def verify(self) -> bool:
        """Verifies that head, body and tail form a snake.

        Body has to form a path with head on one end and tail on the other.

        Returns:
            bool: True or False that head, body and tail form a snake.

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
        return segment == self.tail and self.tail not in segments

    def get_segments(self) -> list[Vertex]:
        """Returns list of the snake's body vertices.

        Returns:
            list[Vertex]: Vertices of the snake in sequence starting from head and
                ending in tail.

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

        All edges and vertices of the snake's current position are set to type snake.
        If the snake moved in the last step (instead of growing), the left vertex
        and edge are set to type empty.

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

        This method updates types of all vertices and edges of the snake and the vertex
            and edge the snake just left. Apple callback is called.

        Args:
            edge (Edge): Edge incident with snake's head. The snake will move along
                this edge.

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
