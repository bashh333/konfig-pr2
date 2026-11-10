"""Unit tests for topological dependency loading order."""

import unittest

from src.graph import DependencyGraph
from src.order import compute_loading_order


class TestOrder(unittest.TestCase):
    """Test suite for dependency loading order calculation."""

    def test_linear_order(self):
        """Test loading order for linear chain A -> B -> C."""
        graph = DependencyGraph("A")
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        order, has_cycle = compute_loading_order(graph)

        self.assertFalse(has_cycle)
        self.assertEqual(order, ["C", "B", "A"])

    def test_diamond_order(self):
        """Test loading order for diamond graph."""
        graph = DependencyGraph("A")
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        graph.add_edge("B", "D")
        graph.add_edge("C", "D")
        order, has_cycle = compute_loading_order(graph)

        self.assertFalse(has_cycle)
        self.assertEqual(order[0], "D")
        self.assertEqual(order[-1], "A")

    def test_cycle_detection(self):
        """Test loading order detection when cyclic dependency exists."""
        graph = DependencyGraph("A")
        graph.add_edge("A", "B")
        graph.add_edge("B", "A")
        _, has_cycle = compute_loading_order(graph)

        self.assertTrue(has_cycle)


if __name__ == "__main__":
    unittest.main()
