#!/usr/bin/env bash
set -e

echo "=== Running unit tests ==="
python3 -m unittest discover -s tests -p "test_*.py"

echo ""
echo "=== Running dependency visualizer (Stage 1) ==="
python3 -m src.main --config config.toml
