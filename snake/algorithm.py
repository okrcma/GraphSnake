"""This module contains AI algorithms for playing snake."""
import random

from snake.graph import GameGraph, Edge


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
