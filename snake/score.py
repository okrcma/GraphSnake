from graph import GameGraph


class Score:
    def __init__(self, graph: GameGraph):
        self.graph = graph
        self.graph.apple_callback = self._on_eaten_apple

        self._score = 0

    def _on_eaten_apple(self):
        self._score += 1

    def get_score(self):
        return self._score
