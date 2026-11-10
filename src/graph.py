"""Module for dependency graph construction, recursive BFS and test repo."""

import os
import re
from typing import Callable, Dict, List, Set, Tuple

INITIAL_DEPTH = 0
DEPTH_INCREMENT = 1
MIN_PARTS_COUNT = 2


class GraphError(Exception):
    """Exception raised for graph construction and traversal errors."""


class DependencyGraph:
    """Represents a directed dependency graph with cycle detection."""

    def __init__(self, root: str) -> None:
        """Initialize empty dependency graph with root node."""
        self.root: str = root
        self.nodes: Set[str] = {root}
        self.edges: Dict[str, List[str]] = {root: []}
        self.cycles: List[Tuple[str, str]] = []

    def add_node(self, node: str) -> None:
        """Add node to graph if not present."""
        self.nodes.add(node)
        if node not in self.edges:
            self.edges[node] = []

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add directed edge between nodes."""
        self.add_node(from_node)
        self.add_node(to_node)
        if to_node not in self.edges[from_node]:
            self.edges[from_node].append(to_node)

    def record_cycle(self, from_node: str, to_node: str) -> None:
        """Record detected cyclic dependency edge."""
        cycle_pair = (from_node, to_node)
        if cycle_pair not in self.cycles:
            self.cycles.append(cycle_pair)


def bfs_recursive(
    current_level: List[str],
    graph: DependencyGraph,
    dep_provider: Callable[[str], List[str]],
    visited: Set[str],
    current_depth: int,
    max_depth: int,
) -> None:
    """Traverse dependencies using recursive Breadth-First Search (BFS)."""
    if not current_level:
        return
    if current_depth >= max_depth:
        return

    next_level: List[str] = []
    for node in current_level:
        try:
            deps = dep_provider(node)
        except Exception:
            deps = []

        for dep in deps:
            graph.add_edge(node, dep)
            if dep in visited:
                graph.record_cycle(node, dep)
            else:
                visited.add(dep)
                next_level.append(dep)

    bfs_recursive(
        next_level,
        graph,
        dep_provider,
        visited,
        current_depth + DEPTH_INCREMENT,
        max_depth,
    )


def _split_test_line(raw_line: str) -> Tuple[str, str]:
    """Split line by arrow or colon separator."""
    if "->" in raw_line:
        parts = raw_line.split("->", 1)
        return parts[0].strip(), parts[1].strip()
    if ":" in raw_line:
        parts = raw_line.split(":", 1)
        return parts[0].strip(), parts[1].strip()
    return raw_line.strip(), ""


def parse_test_repository_content(content: str) -> Dict[str, List[str]]:
    """Parse test repository graph mapping packages named with uppercase."""
    adj: Dict[str, List[str]] = {}
    for line in content.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        source, target_str = _split_test_line(line_clean)
        if not source:
            continue
        targets = [t for t in re.split(r"[\s,]+", target_str) if t]
        if source not in adj:
            adj[source] = []
        for t in targets:
            if t not in adj[source]:
                adj[source].append(t)
    return adj


def load_test_repository(file_path: str) -> Dict[str, List[str]]:
    """Load test repository mapping from file."""
    if not os.path.exists(file_path):
        raise GraphError(f"Test repository file does not exist: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f_handle:
            content = f_handle.read()
    except OSError as err:
        raise GraphError(f"Cannot read test file {file_path}: {err}") from err
    return parse_test_repository_content(content)


def build_dependency_graph(
    root: str,
    max_depth: int,
    dep_provider: Callable[[str], List[str]],
) -> DependencyGraph:
    """Build complete dependency graph starting from root package."""
    graph = DependencyGraph(root)
    visited: Set[str] = {root}
    bfs_recursive(
        [root], graph, dep_provider, visited, INITIAL_DEPTH, max_depth
    )
    return graph
