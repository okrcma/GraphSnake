"""Module for keeping score of the game."""
from __future__ import annotations

from graph import GameGraph


class Score:
    """Class keeping score of the game."""

    def __init__(self, graph: GameGraph):
        """Initialize the score.

        Sets move and apple callbacks to the graph.

        Args:
            graph: Game graph.

        """
        self.graph = graph
        self.graph.move_callback = self._on_before_move
        self.graph.apple_callback = self._on_eaten_apple

        self._moves = 0
        self._score = 0

    def _on_before_move(self):
        self._moves += 1

    def _on_eaten_apple(self):
        self._score += 1

    def get_moves(self) -> int:
        """Get number of snake moves."""
        return self._moves

    def get_score(self) -> int:
        """Get number of eaten apples."""
        return self._score

    def get_moves_per_point(self) -> float:
        """Get average number of snake moves per eaten apple."""
        if self._score == 0:
            return 0.0
        return self._moves / self._score
