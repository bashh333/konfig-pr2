"""Module for computing dependency loading and compilation order."""

from typing import Dict, List, Set, Tuple

from src.graph import DependencyGraph

ZERO_PREREQS = 0


def _build_prerequisite_map(
    graph: DependencyGraph,
) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    """Compute number of prerequisites and reverse dependency map."""
    prereq_counts: Dict[str, int] = {node: 0 for node in graph.nodes}
    dependents: Dict[str, List[str]] = {node: [] for node in graph.nodes}

    for parent, children in graph.edges.items():
        if parent not in prereq_counts:
            prereq_counts[parent] = 0
            dependents[parent] = []

        valid_children = [c for c in children if c in graph.nodes]
        prereq_counts[parent] = len(valid_children)

        for child in valid_children:
            if child not in dependents:
                dependents[child] = []
                prereq_counts[child] = 0
            dependents[child].append(parent)

    return prereq_counts, dependents


def compute_loading_order(
    graph: DependencyGraph,
) -> Tuple[List[str], bool]:
    """Compute topological loading order of packages where deps come first."""
    prereq_counts, dependents = _build_prerequisite_map(graph)

    ready_queue: List[str] = [
        node
        for node in sorted(graph.nodes)
        if prereq_counts[node] == ZERO_PREREQS
    ]

    order: List[str] = []
    while ready_queue:
        current = ready_queue.pop(0)
        order.append(current)

        for dep in sorted(dependents.get(current, [])):
            prereq_counts[dep] -= 1
            if prereq_counts[dep] == ZERO_PREREQS:
                ready_queue.append(dep)

    total_nodes = len(graph.nodes)
    has_cycle = len(order) != total_nodes
    return order, has_cycle
