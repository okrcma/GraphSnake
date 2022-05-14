"""This module contains AI algorithms for playing snake."""
import random
import networkx as nx

from snake.graph import GameGraph, Edge, VertexType


class AbstractSnakeAlgorithm:
    """Abstract parent class for all algorithms.

    All an algorithm has to do is to choose next edge for the snake based on the game
        state maintained by the game graph.

    Attribute:
        graph: Game graph maintaining the game state.

    """

    def __init__(self, graph: GameGraph):
        """Initializes the algorithm.

        Args:
            graph: Game graph maintaining the game state.

        """
        self.graph = graph

    def choose_next_edge(self) -> Edge:
        """Returns next edge chosen by the algorithm

        The returned edge has to be a valid edge for the snake to move along, especially
            it has to be incident with the snake's head.

        Returns:
            Next edge for the snake.

        """
        raise NotImplementedError


class RandomEdgeAlgorithm(AbstractSnakeAlgorithm):
    """Algorithm which chooses next edge at random."""

    def choose_next_edge(self) -> Edge:
        """Chooses next edge at random."""
        snake_edges = self.graph.get_snakes_next_edges()
        return random.sample(snake_edges, 1)[0]


class ShortestPathAlgorithm(AbstractSnakeAlgorithm):
    """Algorithm which looks for the shortest path to the apple.

    If there are multiple apples, then the algorithm chooses one and looks for
        the shortest path to it, not the shortest path to the closest apple.

    This algorithm can still fail if the snake cuts the graph into separate components.
    If there is no path between the head of the snake and the apple, then a backup
    algorithm is used (by default it's RandomEdgeAlgorithm).

    """

    def __init__(self, graph: GameGraph):
        """Initializes the algorithm."""
        super().__init__(graph)
        self._backup_algorithm = RandomEdgeAlgorithm(graph)

        self._path = []
        self._nx_graph = self._generate_nx_graph()

    def choose_next_edge(self) -> Edge:
        """Returns next edge chosen by the algorithm."""
        if len(self._path) == 0:
            self._find_shortest_path()
        if len(self._path) > 0:
            next_vertex = self._path.pop(0)
            return self.graph.get_edge(self.graph.snake.head, next_vertex)
        return self._backup_algorithm.choose_next_edge()

    def _generate_nx_graph(self):
        nx_graph = nx.Graph()
        for vertex in self.graph.vertices:
            nx_graph.add_node(vertex, vertex_obj=vertex)
        for edge in self.graph.edges:
            nx_graph.add_edge(edge.first, edge.second, edge_obj=edge)
        return nx_graph

    def _find_shortest_path(self):
        available_vertices = [
            vertex
            for vertex in self.graph.vertices
            if vertex.type not in [VertexType.WALL, VertexType.SNAKE]
        ] + [self.graph.snake.head]

        nx_subgraph = self._nx_graph.subgraph(available_vertices)
        try:
            self._path = nx.shortest_path(
                nx_subgraph, self.graph.snake.head, list(self.graph.apples)[0]
            )[1:]
        except nx.exception.NetworkXNoPath:
            self._path = []
