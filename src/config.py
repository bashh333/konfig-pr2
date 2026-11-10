"""Module for loading and validating configuration in TOML format."""

from dataclasses import dataclass
import os
from typing import Any, Dict

MIN_DEPTH = 0
MIN_QUOTED_LEN = 2


class ConfigError(Exception):
    """Exception raised for configuration errors."""


@dataclass
class Config:
    """Class representing application configuration parameters."""

    package_name: str
    repo_url: str
    test_mode: bool
    package_version: str
    max_depth: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration parameters to dictionary."""
        return {
            "package_name": self.package_name,
            "repo_url": self.repo_url,
            "test_mode": self.test_mode,
            "package_version": self.package_version,
            "max_depth": self.max_depth,
        }


def _parse_quoted_string(val_str: str) -> Any:
    """Parse quoted string if matching quotation rules."""
    quotes = ('"', "'")
    for quote in quotes:
        has_quotes = val_str.startswith(quote) and val_str.endswith(quote)
        if has_quotes and len(val_str) >= MIN_QUOTED_LEN:
            return val_str[1:-1]
    return None


def _parse_boolean(val_str: str) -> Any:
    """Parse boolean literal from string."""
    if val_str == "true":
        return True
    if val_str == "false":
        return False
    return None


def _parse_number(val_str: str) -> Any:
    """Parse integer or float from string representation."""
    try:
        return int(val_str)
    except ValueError:
        pass
    try:
        return float(val_str)
    except ValueError as err:
        raise ConfigError(f"Unsupported value format: {val_str}") from err


def _parse_scalar(val_str: str) -> Any:
    """Parse scalar TOML value into a Python object."""
    str_val = _parse_quoted_string(val_str)
    if str_val is not None:
        return str_val

    bool_val = _parse_boolean(val_str)
    if bool_val is not None:
        return bool_val

    return _parse_number(val_str)


def _parse_simple_toml(content: str) -> Dict[str, Any]:
    """Fallback parser for basic TOML configuration files."""
    data: Dict[str, Any] = {}
    current_section: Dict[str, Any] = data

    for line_num, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section_name = line[1:-1].strip()
            if not section_name:
                raise ConfigError(f"Empty section at line {line_num}")
            data[section_name] = {}
            current_section = data[section_name]
            continue
        if "=" not in line:
            raise ConfigError(f"Invalid TOML line {line_num}: {line}")
        key_part, val_part = line.split("=", 1)
        key = key_part.strip()
        val_clean = val_part.split("#", 1)[0].strip()
        if not key:
            raise ConfigError(f"Missing key at line {line_num}")
        current_section[key] = _parse_scalar(val_clean)

    return data


def parse_toml(content: str) -> Dict[str, Any]:
    """Parse TOML content using tomllib if available, else fallback."""
    try:
        import tomllib

        return tomllib.loads(content)
    except ImportError:
        return _parse_simple_toml(content)
    except Exception as exc:
        raise ConfigError(f"Failed to parse TOML content: {exc}") from exc


def _validate_string_param(param_name: str, value: Any) -> None:
    """Validate that parameter is a non-empty string."""
    if not isinstance(value, str):
        raise ConfigError(f"Parameter '{param_name}' must be a string")
    if not value:
        raise ConfigError(f"Parameter '{param_name}' cannot be empty")


def _validate_test_mode(value: Any) -> None:
    """Validate that test_mode parameter is a boolean."""
    if not isinstance(value, bool):
        raise ConfigError("Parameter 'test_mode' must be a boolean")


def _validate_max_depth(value: Any) -> None:
    """Validate that max_depth parameter is a valid integer."""
    if isinstance(value, bool):
        raise ConfigError("Parameter 'max_depth' cannot be boolean")
    if not isinstance(value, int):
        raise ConfigError("Parameter 'max_depth' must be an integer")
    if value < MIN_DEPTH:
        raise ConfigError(
            f"Parameter 'max_depth' must be >= {MIN_DEPTH}, got {value}"
        )


def _validate_types_and_values(raw: Dict[str, Any]) -> None:
    """Validate data types and specific value rules."""
    _validate_string_param("package_name", raw["package_name"])
    _validate_string_param("repo_url", raw["repo_url"])
    _validate_string_param("package_version", raw["package_version"])
    _validate_test_mode(raw["test_mode"])
    _validate_max_depth(raw["max_depth"])


def validate_config(raw_data: Dict[str, Any]) -> Config:
    """Validate dictionary structure and build Config instance."""
    flat_data: Dict[str, Any] = {}
    for key, value in raw_data.items():
        if isinstance(value, dict):
            flat_data.update(value)
        else:
            flat_data[key] = value

    required_keys = (
        "package_name",
        "repo_url",
        "test_mode",
        "package_version",
        "max_depth",
    )
    for req_key in required_keys:
        if req_key not in flat_data:
            raise ConfigError(f"Missing required parameter: '{req_key}'")

    _validate_types_and_values(flat_data)

    return Config(
        package_name=flat_data["package_name"],
        repo_url=flat_data["repo_url"],
        test_mode=flat_data["test_mode"],
        package_version=flat_data["package_version"],
        max_depth=flat_data["max_depth"],
    )


def load_config(file_path: str) -> Config:
    """Load, parse and validate TOML configuration from file."""
    if not os.path.exists(file_path):
        raise ConfigError(f"Configuration file does not exist: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file_handle:
            content = file_handle.read()
    except OSError as err:
        raise ConfigError(f"Unable to read file {file_path}: {err}") from err

    parsed_data = parse_toml(content)
    return validate_config(parsed_data)
