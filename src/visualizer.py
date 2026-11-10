"""Module for rendering dependency graph to D2 diagram syntax."""

from typing import List

from src.graph import DependencyGraph


def _format_d2_node(node_name: str) -> str:
    """Format safe node name identifier for D2 syntax."""
    return f'"{node_name}"'


def _format_edge_statement(source: str, target: str, is_cycle: bool) -> str:
    """Format single D2 edge with optional cycle styling."""
    src = _format_d2_node(source)
    dst = _format_d2_node(target)
    if is_cycle:
        style = "{style.stroke: red; style.bold: true}"
        return f"{src} -> {dst}: (cycle) {style}"
    return f"{src} -> {dst}"


def render_d2(graph: DependencyGraph) -> str:
    """Generate D2 diagram source text from dependency graph."""
    lines: List[str] = [
        "direction: right",
        f'{_format_d2_node(graph.root)}.style.fill: "#87ceeb"',
        f'{_format_d2_node(graph.root)}.style.stroke: "#1e90ff"',
    ]

    for parent in sorted(graph.edges.keys()):
        for child in sorted(graph.edges[parent]):
            is_cyclic = (parent, child) in graph.cycles
            stmt = _format_edge_statement(parent, child, is_cyclic)
            lines.append(stmt)

    return "\n".join(lines)
