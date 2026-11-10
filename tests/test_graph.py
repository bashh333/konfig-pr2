"""Unit tests for dependency graph construction and recursive BFS."""

import unittest

from src.graph import (
    DependencyGraph,
    GraphError,
    build_dependency_graph,
    load_test_repository,
    parse_test_repository_content,
)

DEPTH_ZERO = 0
DEPTH_ONE = 1
DEPTH_TWO = 2
DEPTH_THREE = 3
MIN_NODES = 1


class TestGraph(unittest.TestCase):
    """Test suite for recursive BFS and test repository parsing."""

    def test_parse_test_repo_arrows(self):
        """Test parsing adjacency representation with arrow syntax."""
        content = "A -> B, C\nB -> D\nC -> D"
        adj = parse_test_repository_content(content)
        self.assertEqual(adj["A"], ["B", "C"])
        self.assertEqual(adj["B"], ["D"])
        self.assertEqual(adj["C"], ["D"])

    def test_parse_test_repo_colons(self):
        """Test parsing adjacency representation with colon syntax."""
        content = "A: B C\nB: D"
        adj = parse_test_repository_content(content)
        self.assertEqual(adj["A"], ["B", "C"])
        self.assertEqual(adj["B"], ["D"])

    def test_bfs_depth_zero(self):
        """Test recursive BFS stopping at depth zero."""
        adj = {"A": ["B", "C"], "B": ["D"]}
        graph = build_dependency_graph(
            "A", DEPTH_ZERO, lambda n: adj.get(n, [])
        )
        self.assertEqual(graph.nodes, {"A"})
        self.assertEqual(graph.edges["A"], [])

    def test_bfs_depth_one(self):
        """Test recursive BFS stopping at depth one."""
        adj = {"A": ["B", "C"], "B": ["D"]}
        graph = build_dependency_graph(
            "A", DEPTH_ONE, lambda n: adj.get(n, [])
        )
        self.assertEqual(graph.nodes, {"A", "B", "C"})
        self.assertEqual(graph.edges["A"], ["B", "C"])

    def test_bfs_cycle_handling(self):
        """Test cycle detection in recursive BFS."""
        adj = {"A": ["B"], "B": ["C"], "C": ["A"]}
        graph = build_dependency_graph(
            "A", DEPTH_THREE, lambda n: adj.get(n, [])
        )
        self.assertTrue(len(graph.nodes) >= MIN_NODES)
        self.assertIn(("C", "A"), graph.cycles)

    def test_load_test_repo_file_not_found(self):
        """Test exception when test file does not exist."""
        with self.assertRaises(GraphError):
            load_test_repository("non_existent_graph_file.txt")


if __name__ == "__main__":
    unittest.main()
