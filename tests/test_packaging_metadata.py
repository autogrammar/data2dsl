"""Regression checks for the explicitly enumerated standalone-module wheel."""

from __future__ import annotations

import ast
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src"


def _declared_modules() -> set[str]:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)
    return set(project["tool"]["setuptools"]["py-modules"])


def _local_modules() -> set[str]:
    return {path.stem for path in SOURCE_ROOT.glob("*.py")}


def _absolute_imports(module: str) -> set[str]:
    tree = ast.parse((SOURCE_ROOT / f"{module}.py").read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.partition(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.add(node.module.partition(".")[0])
    return imported


def _missing_local_imports(declared: set[str]) -> dict[str, set[str]]:
    local = _local_modules()
    missing: dict[str, set[str]] = {}
    for module in sorted(declared & local):
        omitted = (_absolute_imports(module) & local) - declared
        if omitted:
            missing[module] = omitted
    return missing


def test_packaged_modules_include_every_local_runtime_import() -> None:
    assert _missing_local_imports(_declared_modules()) == {}


def test_regression_probe_detects_omitted_discovery_runtime() -> None:
    declared = _declared_modules() - {"data2dsl_discovery"}

    assert _missing_local_imports(declared)["data2dsl_skill"] == {
        "data2dsl_discovery"
    }
