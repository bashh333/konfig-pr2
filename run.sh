#!/usr/bin/env bash
set -e

echo "=== 1. Running Unit Tests ==="
python3 -m unittest discover -s tests -p "test_*.py"

echo ""
echo "=== 2. Stage 1 Demo: Configuration Parameters ==="
python3 -m src.main --config config.toml --stage 1

echo ""
echo "=== 3. Stage 2 Demo: Direct Dependencies ==="
python3 -m src.main --config config.toml --stage 2

echo ""
echo "=== 4. Stage 3 Demo: BFS Graph (Test Repository with Cycles) ==="
cat << 'EOF' > test_config_stage3.toml
package_name = "A"
repo_url = "test_data/cyclic.txt"
test_mode = true
package_version = "1.0.0"
max_depth = 5
EOF
python3 -m src.main --config test_config_stage3.toml --stage 3

echo ""
echo "=== 5. Stage 4 Demo: Loading Order (Branching Graph) ==="
cat << 'EOF' > test_config_stage4.toml
package_name = "A"
repo_url = "test_data/branching.txt"
test_mode = true
package_version = "1.0.0"
max_depth = 5
EOF
python3 -m src.main --config test_config_stage4.toml --stage 4

echo ""
echo "=== 6. Stage 5 Demo: D2 Diagram Output ==="
python3 -m src.main --config config.toml --stage 5

rm -f test_config_stage3.toml test_config_stage4.toml
echo ""
echo "=== All stages completed successfully! ==="
