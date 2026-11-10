"""Unit tests for configuration parsing and validation."""

from contextlib import redirect_stderr, redirect_stdout
import io
import os
import tempfile
import unittest

from src.config import (
    Config,
    ConfigError,
    load_config,
    parse_toml,
    validate_config,
)
from src.main import main


class TestConfig(unittest.TestCase):
    """Test suite for configuration loading, parsing and error handling."""

    def test_valid_config_loading(self):
        """Test loading valid configuration."""
        raw_toml = (
            'package_name = "serde"\n'
            'repo_url = "https://index.crates.io"\n'
            "test_mode = false\n"
            'package_version = "1.0.195"\n'
            "max_depth = 3\n"
        )
        data = parse_toml(raw_toml)
        config = validate_config(data)

        self.assertEqual(config.package_name, "serde")
        self.assertEqual(config.repo_url, "https://index.crates.io")
        self.assertFalse(config.test_mode)
        self.assertEqual(config.package_version, "1.0.195")
        self.assertEqual(config.max_depth, 3)

    def test_valid_config_with_sections(self):
        """Test loading valid configuration structured in sections."""
        raw_toml = (
            "[project]\n"
            'package_name = "tokio"\n'
            'package_version = "1.35.0"\n'
            "[repository]\n"
            'repo_url = "https://crates.io"\n'
            "test_mode = true\n"
            "max_depth = 0\n"
        )
        config = validate_config(parse_toml(raw_toml))
        self.assertEqual(config.package_name, "tokio")
        self.assertTrue(config.test_mode)
        self.assertEqual(config.max_depth, 0)

    def test_missing_file_raises_error(self):
        """Test error handling when configuration file does not exist."""
        with self.assertRaises(ConfigError) as ctx:
            load_config("non_existent_file_path.toml")
        self.assertIn("does not exist", str(ctx.exception))

    def test_invalid_toml_syntax(self):
        """Test error handling on invalid TOML syntax."""
        invalid_content = "this is not valid toml = = ="
        with self.assertRaises(ConfigError):
            parse_toml(invalid_content)

    def test_missing_package_name(self):
        """Test error handling when package_name is missing."""
        data = {
            "repo_url": "https://crates.io",
            "test_mode": False,
            "package_version": "1.0.0",
            "max_depth": 2,
        }
        with self.assertRaises(ConfigError) as ctx:
            validate_config(data)
        self.assertIn("package_name", str(ctx.exception))

    def test_empty_package_name(self):
        """Test error handling when package_name is an empty string."""
        data = {
            "package_name": "",
            "repo_url": "https://crates.io",
            "test_mode": False,
            "package_version": "1.0.0",
            "max_depth": 2,
        }
        with self.assertRaises(ConfigError) as ctx:
            validate_config(data)
        self.assertIn("package_name", str(ctx.exception))

    def test_invalid_repo_url(self):
        """Test error handling when repo_url is missing or empty."""
        data = {
            "package_name": "serde",
            "repo_url": "",
            "test_mode": False,
            "package_version": "1.0.0",
            "max_depth": 2,
        }
        with self.assertRaises(ConfigError) as ctx:
            validate_config(data)
        self.assertIn("repo_url", str(ctx.exception))

    def test_invalid_test_mode_type(self):
        """Test error handling when test_mode is not a boolean."""
        data = {
            "package_name": "serde",
            "repo_url": "https://crates.io",
            "test_mode": "not_a_bool",
            "package_version": "1.0.0",
            "max_depth": 2,
        }
        with self.assertRaises(ConfigError) as ctx:
            validate_config(data)
        self.assertIn("test_mode", str(ctx.exception))

    def test_invalid_package_version(self):
        """Test error handling when package_version is empty."""
        data = {
            "package_name": "serde",
            "repo_url": "https://crates.io",
            "test_mode": False,
            "package_version": "",
            "max_depth": 2,
        }
        with self.assertRaises(ConfigError) as ctx:
            validate_config(data)
        self.assertIn("package_version", str(ctx.exception))

    def test_negative_max_depth(self):
        """Test error handling when max_depth is negative."""
        data = {
            "package_name": "serde",
            "repo_url": "https://crates.io",
            "test_mode": False,
            "package_version": "1.0.0",
            "max_depth": -1,
        }
        with self.assertRaises(ConfigError) as ctx:
            validate_config(data)
        self.assertIn("max_depth", str(ctx.exception))

    def test_invalid_max_depth_type(self):
        """Test error handling when max_depth is not an integer."""
        data = {
            "package_name": "serde",
            "repo_url": "https://crates.io",
            "test_mode": False,
            "package_version": "1.0.0",
            "max_depth": "deep",
        }
        with self.assertRaises(ConfigError) as ctx:
            validate_config(data)
        self.assertIn("max_depth", str(ctx.exception))

    def test_cli_execution_success(self):
        """Test successful CLI execution with valid config file."""
        with tempfile.NamedTemporaryFile(
            "w", suffix=".toml", delete=False
        ) as tmp:
            tmp.write(
                'package_name = "test_pkg"\n'
                'repo_url = "https://crates.io"\n'
                "test_mode = false\n"
                'package_version = "0.1.0"\n'
                "max_depth = 1\n"
            )
            tmp_path = tmp.name

        try:
            with io.StringIO() as captured_out:
                with redirect_stdout(captured_out):
                    exit_code = main(["--config", tmp_path])
            self.assertEqual(exit_code, 0)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_cli_execution_error(self):
        """Test CLI error return code when config is invalid."""
        with io.StringIO() as captured_err:
            with redirect_stderr(captured_err):
                exit_code = main(["--config", "non_existent.toml"])
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
