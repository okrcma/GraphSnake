import pytest

from snake.graph import VertexFactory, Vertex, Edge, Snake


class TestSnakeValidity:
    """Tests for snake validity verification."""

    def _get_walk(self, vertices: list[Vertex]):
        edges = []
        first = vertices[0]
        for second in vertices[1:]:
            edges.append(Edge(first, second))
            first = second
        return edges

    @pytest.mark.parametrize("n", [2, 3, 1000])
    def test_path_snake(self, n):
        """Test snake from a path."""
        vertices = VertexFactory().create_multiple(n)
        head = vertices[0]
        tail = vertices[-1]
        body = self._get_walk(vertices)

        Snake(head, body, tail)

    def test_point_snake(self):
        """Test snake with only one vertex."""
        head = tail = VertexFactory().create_vertex()
        body = []

        with pytest.raises(ValueError):
            Snake(head, body, tail)

    def test_cycle_snake(self):
        """Test snake from a cycle."""
        vertices = VertexFactory().create_multiple(3)
        head = tail = vertices[0]
        body = self._get_walk(vertices + [head])

        with pytest.raises(ValueError):
            Snake(head, body, tail)

    def test_trail_snake(self):
        """Test snake from a trail."""
        vertices = VertexFactory().create_multiple(5)
        head = vertices[0]
        tail = vertices[-1]
        body = self._get_walk(
            [
                vertices[0],
                vertices[1],
                vertices[2],
                vertices[3],
                vertices[1],
                vertices[4],
            ]
        )

        with pytest.raises(ValueError):
            Snake(head, body, tail)

    def test_disconnected_snake(self):
        """Test snake from disconnected vertices."""
        vertices = VertexFactory().create_multiple(2)
        head = vertices[0]
        tail = vertices[-1]
        body = []

        with pytest.raises(ValueError):
            Snake(head, body, tail)

    def test_tail_in_middle_snake(self):
        """Test snake with tail in the middle."""
        vertices = VertexFactory().create_multiple(3)
        head = vertices[0]
        tail = vertices[1]
        body = self._get_walk(vertices)

        with pytest.raises(ValueError):
            Snake(head, body, tail)

    def test_loop_snake(self):
        """Test snake with looped edge."""
        vertices = VertexFactory().create_multiple(2)
        head = vertices[0]
        tail = vertices[1]
        body = self._get_walk([head] + vertices)

        with pytest.raises(ValueError):
            Snake(head, body, tail)
