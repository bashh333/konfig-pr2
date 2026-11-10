"""Module for collecting direct dependencies of Rust (Cargo) packages."""

import json
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request

PREFIX_ONE = 1
PREFIX_TWO = 2
PREFIX_THREE = 3
KIND_NORMAL = "normal"
HTTP_TIMEOUT = 10
INDEX_HOST = "index.crates.io"


class CollectorError(Exception):
    """Exception raised for dependency collection errors."""


def get_crates_io_prefix(pkg_name: str) -> str:
    """Compute sparse index path prefix for given package name."""
    lower_name = pkg_name.lower()
    name_len = len(lower_name)

    if name_len == PREFIX_ONE:
        return f"1/{lower_name}"
    if name_len == PREFIX_TWO:
        return f"2/{lower_name}"
    if name_len == PREFIX_THREE:
        first_char = lower_name[0]
        return f"3/{first_char}/{lower_name}"

    part1 = lower_name[:2]
    part2 = lower_name[2:4]
    return f"{part1}/{part2}/{lower_name}"


def build_package_url(base_url: str, pkg_name: str) -> str:
    """Build full URL to package file in sparse index."""
    clean_base = base_url.rstrip("/")
    prefix = get_crates_io_prefix(pkg_name)
    return f"{clean_base}/{prefix}"


def fetch_package_lines(url: str) -> List[str]:
    """Fetch raw lines of package metadata from URL."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CargoDependencyVisualizer/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            raw_data = resp.read().decode("utf-8")
            return [line.strip() for line in raw_data.splitlines() if line]
    except urllib.error.HTTPError as err:
        raise CollectorError(
            f"HTTP error {err.code} while fetching {url}"
        ) from err
    except urllib.error.URLError as err:
        raise CollectorError(
            f"Network error while connecting to {url}: {err.reason}"
        ) from err
    except OSError as err:
        raise CollectorError(f"Failed to read from {url}: {err}") from err


def _is_normal_dependency(dep: Dict[str, Any]) -> bool:
    """Check if dependency kind is normal and not optional."""
    kind = dep.get("kind", KIND_NORMAL)
    if kind != KIND_NORMAL:
        return False
    if dep.get("optional", False):
        return False
    return True


def _extract_deps_from_entry(entry: Dict[str, Any]) -> List[str]:
    """Extract filtered dependency names from version entry."""
    deps: List[str] = []
    raw_deps = entry.get("deps", [])
    for dep in raw_deps:
        if _is_normal_dependency(dep):
            dep_name = dep.get("name")
            if dep_name and dep_name not in deps:
                deps.append(dep_name)
    return deps


def parse_version_deps(lines: List[str], target_version: str) -> List[str]:
    """Find specific version in metadata lines and return its dependencies."""
    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        if entry.get("vers") == target_version:
            return _extract_deps_from_entry(entry)

    raise CollectorError(f"Version '{target_version}' not found in metadata")


def get_direct_dependencies(
    repo_url: str, pkg_name: str, pkg_ver: str
) -> List[str]:
    """Fetch direct dependencies for given package version."""
    url = build_package_url(repo_url, pkg_name)
    lines = fetch_package_lines(url)
    return parse_version_deps(lines, pkg_ver)
