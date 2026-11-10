"""Main entry point for Dependency Visualizer CLI application."""

import argparse
import sys
from typing import Sequence

from src.config import ConfigError, load_config


def parse_args(args: Sequence[str]) -> argparse.Namespace:
    """Parse command line arguments for configuration path."""
    parser = argparse.ArgumentParser(
        description="Cargo dependency graph visualizer (Variant 22)."
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_path",
        default="config.toml",
        help="Path to TOML configuration file (default: config.toml)",
    )
    return parser.parse_args(args)


def print_config_parameters(config) -> None:
    """Print configuration parameters in key-value format for Stage 1."""
    for key, value in config.to_dict().items():
        print(f"{key}: {value}")


def main(argv: Sequence[str] = None) -> int:
    """Run CLI application for Stage 1."""
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    try:
        config = load_config(args.config_path)
    except ConfigError as err:
        sys.stderr.write(f"Configuration error: {err}\n")
        return 1
    except Exception as err:
        sys.stderr.write(f"Unexpected error: {err}\n")
        return 1

    print_config_parameters(config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
