"""Unit tests for Cargo dependency collection from sparse index."""

import unittest
from unittest.mock import MagicMock, patch

from src.collector import (
    CollectorError,
    build_package_url,
    get_crates_io_prefix,
    get_direct_dependencies,
    parse_version_deps,
)


class TestCollector(unittest.TestCase):
    """Test suite for sparse index URL building and dependency extraction."""

    def test_prefix_single_letter(self):
        """Test prefix computation for single-letter package name."""
        prefix = get_crates_io_prefix("a")
        self.assertEqual(prefix, "1/a")

    def test_prefix_two_letters(self):
        """Test prefix computation for two-letter package name."""
        prefix = get_crates_io_prefix("cc")
        self.assertEqual(prefix, "2/cc")

    def test_prefix_three_letters(self):
        """Test prefix computation for three-letter package name."""
        prefix = get_crates_io_prefix("foo")
        self.assertEqual(prefix, "3/f/foo")

    def test_prefix_four_or_more_letters(self):
        """Test prefix computation for longer package names."""
        prefix = get_crates_io_prefix("serde")
        self.assertEqual(prefix, "se/rd/serde")

    def test_build_package_url(self):
        """Test assembling package URL with trailing slash handling."""
        url = build_package_url("https://index.crates.io/", "serde")
        self.assertEqual(url, "https://index.crates.io/se/rd/serde")

    def test_parse_version_deps_filters_correctly(self):
        """Test dependency parsing filters non-normal and optional deps."""
        sample_lines = [
            (
                '{"vers": "0.1.0", "deps": ['
                '{"name": "dep_old", "kind": "normal"}'
                "]}"
            ),
            (
                '{"vers": "0.2.0", "deps": ['
                '{"name": "normal_dep", "kind": "normal", "optional": false},'
                '{"name": "dev_dep", "kind": "dev", "optional": false},'
                '{"name": "opt_dep", "kind": "normal", "optional": true},'
                '{"name": "normal_dep", "kind": "normal", "optional": false}'
                "]}"
            ),
        ]
        deps = parse_version_deps(sample_lines, "0.2.0")
        self.assertEqual(deps, ["normal_dep"])

    def test_parse_version_not_found(self):
        """Test error when requested version is not in metadata."""
        sample_lines = ['{"vers": "1.0.0", "deps": []}']
        with self.assertRaises(CollectorError) as ctx:
            parse_version_deps(sample_lines, "2.0.0")
        self.assertIn("not found", str(ctx.exception))

    @patch("src.collector.fetch_package_lines")
    def test_get_direct_dependencies(self, mock_fetch):
        """Test get_direct_dependencies with mocked fetch response."""
        mock_fetch.return_value = [
            (
                '{"vers": "1.0.195", "deps": ['
                '{"name": "serde_derive", "kind": "normal", "optional": false}'
                "]}"
            )
        ]
        deps = get_direct_dependencies(
            "https://index.crates.io", "serde", "1.0.195"
        )
        self.assertEqual(deps, ["serde_derive"])


if __name__ == "__main__":
    unittest.main()
