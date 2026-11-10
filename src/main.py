"""Main CLI entry point for Cargo dependency graph visualizer."""

import argparse
import sys
from typing import Callable, List, Sequence

from src.collector import CollectorError, get_direct_dependencies
from src.config import Config, ConfigError, load_config
from src.graph import (
    DependencyGraph,
    GraphError,
    build_dependency_graph,
    load_test_repository,
)
from src.order import compute_loading_order
from src.visualizer import render_d2

STAGE_ONE = 1
STAGE_TWO = 2
STAGE_THREE = 3
STAGE_FOUR = 4
STAGE_FIVE = 5
EXIT_OK = 0
EXIT_ERR = 1
EMPTY_COUNT = 0


def parse_args(args: Sequence[str]) -> argparse.Namespace:
    """Parse CLI arguments for configuration path and execution stage."""
    parser = argparse.ArgumentParser(
        description="Cargo dependency graph visualizer (Variant 22)."
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_path",
        default="config.toml",
        help="Path to TOML configuration file",
    )
    parser.add_argument(
        "-s",
        "--stage",
        dest="stage",
        type=int,
        default=STAGE_FIVE,
        help="Pipeline stage to execute (1 to 5, default: 5)",
    )
    return parser.parse_args(args)


def _create_dep_provider(config: Config) -> Callable[[str], List[str]]:
    """Create dependency provider function based on test_mode."""
    if config.test_mode:
        test_adj = load_test_repository(config.repo_url)
        return lambda name: test_adj.get(name, [])

    cache: dict = {}

    def provider(pkg_name: str) -> List[str]:
        if pkg_name in cache:
            return cache[pkg_name]
        try:
            deps = get_direct_dependencies(
                config.repo_url, pkg_name, config.package_version
            )
        except CollectorError:
            deps = []
        cache[pkg_name] = deps
        return deps

    return provider


def run_stage_one(config: Config) -> None:
    """Print configuration parameters in key-value format."""
    for key, val in config.to_dict().items():
        print(f"{key}: {val}")


def run_stage_two(config: Config, provider: Callable) -> None:
    """Fetch and print direct dependencies for specified package."""
    deps = provider(config.package_name)
    print(f"Direct dependencies for {config.package_name}:")
    if len(deps) == EMPTY_COUNT:
        print("  (no dependencies)")
    for dep in deps:
        print(f"  - {dep}")


def run_stage_three(graph: DependencyGraph) -> None:
    """Print built dependency graph nodes and detected cycles."""
    print(f"Graph nodes ({len(graph.nodes)}): {sorted(graph.nodes)}")
    for parent in sorted(graph.edges.keys()):
        children = graph.edges[parent]
        print(f"  {parent} -> {children}")
    if len(graph.cycles) > EMPTY_COUNT:
        print(f"Cycles detected: {graph.cycles}")


def run_stage_four(graph: DependencyGraph) -> None:
    """Compute and display topological loading order of dependencies."""
    order, has_cycle = compute_loading_order(graph)
    print("Loading order (dependencies first):")
    for idx, pkg in enumerate(order, start=1):
        print(f"  {idx}. {pkg}")
    if has_cycle:
        print("Warning: cyclic dependency detected, partial order produced.")


def run_stage_five(graph: DependencyGraph) -> None:
    """Generate and display D2 diagram text representation."""
    d2_output = render_d2(graph)
    print("=== D2 Diagram Output ===")
    print(d2_output)


def dispatch_stage(
    stage: int, config: Config, provider: Callable, graph: DependencyGraph
) -> None:
    """Dispatch pipeline execution based on selected stage number."""
    if stage == STAGE_ONE:
        run_stage_one(config)
    elif stage == STAGE_TWO:
        run_stage_two(config, provider)
    elif stage == STAGE_THREE:
        run_stage_three(graph)
    elif stage == STAGE_FOUR:
        run_stage_four(graph)
    else:
        run_stage_five(graph)


def main(argv: Sequence[str] = None) -> int:
    """Run CLI application pipeline."""
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    try:
        config = load_config(args.config_path)
        provider = _create_dep_provider(config)
        graph = build_dependency_graph(
            config.package_name, config.max_depth, provider
        )
        dispatch_stage(args.stage, config, provider, graph)
        return EXIT_OK
    except (ConfigError, GraphError, CollectorError) as err:
        sys.stderr.write(f"Error: {err}\n")
        return EXIT_ERR
    except Exception as err:
        sys.stderr.write(f"Unexpected error: {err}\n")
        return EXIT_ERR


if __name__ == "__main__":
    sys.exit(main())
