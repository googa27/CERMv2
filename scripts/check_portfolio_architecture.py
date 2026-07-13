#!/usr/bin/env python3
"""Advisory Project #24 architecture/preservation checker.

The contract is written as JSON, a valid subset of YAML 1.2, so this bootstrap
checker remains dependency-free. It intentionally avoids invasive runtime tests
for legacy/fork/hardware preservation repositories.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "ARCHITECTURE.yaml"
REQUIRED_TOP_LEVEL = {
    "schema_version", "repository", "preservation", "architecture",
    "source_layout", "limits", "libraries", "interfaces", "tests",
    "data", "governance", "exceptions",
}
REQUIRED_EXCEPTION_FIELDS = {
    "rule", "path", "reason", "owner", "risk", "accepted_ceiling", "refactoring_trigger",
}
REQUIRED_PRESERVATION_FIELDS = {
    "archival_notice", "supersession_notice", "revival_gates", "provenance",
    "license_warning", "security_warning", "private_data_warning",
}
IGNORED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".ruff_cache", ".mypy_cache", "build", "dist",
}
DEFAULT_METADATA = {"__init__.py", "README.md", "ARCHITECTURE.md", "ARCHITECTURE.yaml", "py.typed"}


def ignored_name(name: str) -> bool:
    return name in IGNORED_DIRS or name.endswith(".egg-info")


def ignored_path(path: Path) -> bool:
    return any(ignored_name(part) for part in path.parts)


def load_contract() -> dict[str, Any]:
    try:
        payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing {CONTRACT.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            "docs/ARCHITECTURE.yaml must remain JSON-compatible YAML 1.2 "
            f"for the dependency-free bootstrap checker: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise ValueError("architecture contract root must be an object")
    return payload


def exception_map(contract: dict[str, Any], errors: list[str]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, item in enumerate(contract.get("exceptions", [])):
        if not isinstance(item, dict):
            errors.append(f"exceptions[{index}] must be an object")
            continue
        missing = REQUIRED_EXCEPTION_FIELDS - set(item)
        if missing:
            errors.append(f"exceptions[{index}] missing metadata: {sorted(missing)}")
            continue
        key = (str(item["rule"]), str(item["path"]))
        if key in result:
            errors.append(f"duplicate exception for {key[0]}:{key[1]}")
        result[key] = item
    return result


def require_exception(exceptions: dict[tuple[str, str], dict[str, Any]], rule: str, path: str, actual: int, errors: list[str]) -> None:
    item = exceptions.get((rule, path))
    if item is None:
        errors.append(f"{rule} violation at {path}: {actual}; no documented exception")
        return
    ceiling = item.get("accepted_ceiling")
    if not isinstance(ceiling, int):
        errors.append(f"{rule} exception at {path} must have integer accepted_ceiling")
    elif actual > ceiling:
        errors.append(f"{rule} no-growth ratchet exceeded at {path}: {actual}>{ceiling}")


def _runtime_dirs_with_python(root: Path) -> set[Path]:
    runtime_dirs: set[Path] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirpath = Path(dirpath)
        dirnames[:] = sorted(d for d in dirnames if not ignored_name(d) and not d.startswith("."))
        filtered = [f for f in filenames if not ignored_path(dirpath / f)]
        if any(Path(f).suffix == ".py" and f != "__init__.py" for f in filtered):
            runtime_dirs.add(dirpath)
    return runtime_dirs


def validate_source(contract: dict[str, Any], exceptions: dict[tuple[str, str], dict[str, Any]], errors: list[str]) -> None:
    layout = contract.get("source_layout")
    if not isinstance(layout, dict):
        errors.append("contract.source_layout must be an object")
        return
    if not layout.get("python_rules_applicable", True):
        return

    limits = contract.get("limits")
    if not isinstance(limits, dict):
        errors.append("contract.limits must be an object")
        return

    max_entries = limits.get("max_immediate_runtime_entries")
    max_lines = limits.get("max_python_module_lines")
    if not isinstance(max_entries, int) or not isinstance(max_lines, int):
        errors.append("contract.limits must define integer max_immediate_runtime_entries and max_python_module_lines")
        return

    shape_errors: list[str] = []
    if "python_source_roots" in layout and not isinstance(layout["python_source_roots"], list):
        shape_errors.append("contract.source_layout.python_source_roots must be an array")
    if "allowed_non_python_files" in layout and not isinstance(layout["allowed_non_python_files"], list):
        shape_errors.append("contract.source_layout.allowed_non_python_files must be an array")
    if "metadata_names" in layout and not isinstance(layout["metadata_names"], list):
        shape_errors.append("contract.source_layout.metadata_names must be an array")
    if shape_errors:
        errors.extend(shape_errors)
        return

    allowed_non_python = layout.get("allowed_non_python_files", [])
    metadata_names = layout.get("metadata_names", [])
    roots = layout.get("python_source_roots", [])
    metadata = DEFAULT_METADATA | set(metadata_names)
    for source_root in (ROOT / p for p in roots):
        rel_root = source_root.relative_to(ROOT).as_posix()
        if not source_root.is_dir():
            errors.append(f"declared Python source root is missing: {rel_root}")
            continue
        runtime_dir_set = _runtime_dirs_with_python(source_root)
        for current, dirs, files in os.walk(source_root):
            dirs[:] = sorted(d for d in dirs if not ignored_name(d) and not d.startswith("."))
            current_path = Path(current)
            rel_dir = current_path.relative_to(ROOT).as_posix()
            runtime_dirs = [d for d in dirs if (current_path / d) in runtime_dir_set]
            runtime_files = [f for f in files if f.endswith(".py") and f != "__init__.py"]
            count = len(runtime_dirs) + len(runtime_files)
            if count > max_entries:
                require_exception(exceptions, "source_fanout", rel_dir, count, errors)
            for filename in files:
                rel = (current_path / filename).relative_to(ROOT).as_posix()
                if filename.endswith((".py", ".pyi")) or filename in metadata or rel in set(allowed_non_python):
                    continue
                require_exception(exceptions, "source_entry_type", rel, 1, errors)
        for module in sorted(source_root.rglob("*.py")):
            if ignored_path(module):
                continue
            try:
                lines = len(module.read_text(encoding="utf-8").splitlines())
            except UnicodeDecodeError:
                errors.append(f"Python module is not UTF-8 text: {module.relative_to(ROOT)}")
                continue
            if lines > max_lines:
                require_exception(exceptions, "python_module_max_lines", module.relative_to(ROOT).as_posix(), lines, errors)


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_TOP_LEVEL - set(contract)
    if missing:
        errors.append(f"contract missing top-level keys: {sorted(missing)}")
        return errors

    exceptions = exception_map(contract, errors)

    repo = contract.get("repository")
    if not isinstance(repo, dict):
        errors.append("contract.repository must be an object")
    else:
        for key in ("owner", "name", "profile", "status", "enforcement"):
            if not repo.get(key):
                errors.append(f"repository.{key} is required")
        if repo.get("profile") != "legacy":
            errors.append("repository.profile must remain legacy for Project #24 preservation repos")
        if str(repo.get("enforcement", "")).lower() != "advisory":
            errors.append("repository.enforcement must be Advisory unless the repo is formally revived")

    preservation = contract.get("preservation")
    if not isinstance(preservation, dict):
        errors.append("contract.preservation must be an object")
    else:
        missing_preservation = REQUIRED_PRESERVATION_FIELDS - set(preservation)
        if missing_preservation:
            errors.append(f"preservation missing keys: {sorted(missing_preservation)}")
        for key in (
            "archival_notice",
            "supersession_notice",
            "license_warning",
            "security_warning",
            "private_data_warning",
        ):
            if not str(preservation.get(key, "")).strip():
                errors.append(f"preservation.{key} must be non-empty")
        revival = preservation.get("revival_gates", [])
        if not isinstance(revival, list) or len(revival) < 3:
            errors.append("preservation.revival_gates must list at least three precise gates")

    readme = ROOT / "README.md"
    if not readme.is_file():
        errors.append("README.md is required for root preservation notice")
    else:
        text = readme.read_text(encoding="utf-8", errors="ignore")
        required_fragments = ["Project #24", "Preservation notice", "Revival gates"]
        for fragment in required_fragments:
            if fragment not in text:
                errors.append(f"README.md missing preservation fragment: {fragment}")

    limits = contract.get("limits")
    if not isinstance(limits, dict):
        errors.append("contract.limits must be an object")
    else:
        if limits.get("max_immediate_runtime_entries") != 10:
            errors.append("default max_immediate_runtime_entries must be 10; repo override belongs in an exception")
        if limits.get("max_python_module_lines") != 500:
            errors.append("default max_python_module_lines must be 500; repo override belongs in an exception")

    governance = contract.get("governance")
    if not isinstance(governance, dict):
        errors.append("contract.governance must be an object")
    else:
        required_docs = governance.get("required_documents", [])
        for rel in required_docs:
            path = ROOT / rel
            if not path.is_file() or not path.read_text(encoding="utf-8", errors="ignore").strip():
                errors.append(f"required document missing or empty: {rel}")

    tests = contract.get("tests")
    if not isinstance(tests, dict):
        errors.append("contract.tests must be an object")
    else:
        for suite in tests.get("required_suites", []):
            path = ROOT / "tests" / suite
            if not path.is_dir():
                errors.append(f"required test suite directory missing: tests/{suite}")

    interfaces = contract.get("interfaces")
    if not isinstance(interfaces, dict):
        errors.append("contract.interfaces must be an object")
    else:
        ai = interfaces.get("ai", {})
        human = interfaces.get("human", {})
        if not isinstance(ai, dict) or ai.get("context_file") != "AGENTS.md":
            errors.append("interfaces.ai.context_file must be AGENTS.md")
        if not isinstance(ai, dict) or not ai.get("interaction") or not ai.get("capability_discovery"):
            errors.append("AI interaction and capability discovery decisions are required")
        if not isinstance(human, dict) or not human.get("interaction") or not human.get("dunder_policy"):
            errors.append("human interaction and dunder policy decisions are required")

    libraries = contract.get("libraries")
    if not isinstance(libraries, dict):
        errors.append("contract.libraries must be an object")
    else:
        decisions = libraries.get("decisions", [])
        if not isinstance(decisions, list):
            errors.append("contract.libraries.decisions must be an array")
        elif not libraries.get("selection_policy") or len(decisions) < 2:
            errors.append("maintained-library selection policy and at least two decisions are required")

    source = contract.get("source_layout")
    if not isinstance(source, dict):
        errors.append("contract.source_layout must be an object")
    else:
        validate_source(contract, exceptions, errors)

    return errors


def main() -> int:
    try:
        contract = load_contract()
        errors = validate_contract(contract)
    except ValueError as exc:
        errors = [str(exc)]
    if errors:
        print("portfolio architecture check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("portfolio architecture check passed (advisory legacy/preservation profile)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
