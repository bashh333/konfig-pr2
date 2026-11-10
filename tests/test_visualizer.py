"""Unit tests for D2 diagram rendering."""

import unittest

from src.graph import DependencyGraph
from src.visualizer import render_d2


class TestVisualizer(unittest.TestCase):
    """Test suite for D2 diagram format generation."""

    def test_render_d2_basic(self):
        """Test D2 output contains root styles and directed edges."""
        graph = DependencyGraph("serde")
        graph.add_edge("serde", "serde_derive")
        output = render_d2(graph)

        self.assertIn("direction: right", output)
        self.assertIn('"serde".style.fill', output)
        self.assertIn('"serde" -> "serde_derive"', output)

    def test_render_d2_cycle_styling(self):
        """Test D2 output formats cyclic edge with cycle label and red color."""
        graph = DependencyGraph("A")
        graph.add_edge("A", "B")
        graph.record_cycle("A", "B")
        output = render_d2(graph)

        self.assertIn("(cycle)", output)
        self.assertIn("stroke: red", output)


if __name__ == "__main__":
    unittest.main()
