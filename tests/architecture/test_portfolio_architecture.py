from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_portfolio_architecture.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_portfolio_architecture", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PortfolioArchitectureTests(unittest.TestCase):
    def test_checker_passes_from_repo_root(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER)],
            check=False,
            text=True,
            capture_output=True,
            cwd=REPO_ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_checker_passes_from_non_root_cwd(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER)],
            check=False,
            text=True,
            capture_output=True,
            cwd="/tmp",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_malformed_sections_clean_fail(self) -> None:
        checker = _load_checker()
        malformed_contract = {
            "schema_version": "1.0.0",
            "repository": "not-an-object",
            "preservation": None,
            "architecture": {},
            "source_layout": [],
            "limits": "bad",
            "libraries": {},
            "interfaces": {},
            "tests": {},
            "data": {},
            "governance": {},
            "exceptions": [],
        }
        errors = checker.validate_contract(malformed_contract)
        self.assertIsInstance(errors, list)
        self.assertTrue(errors)
        self.assertIn("contract.repository must be an object", errors)
        self.assertIn("contract.preservation must be an object", errors)
        self.assertIn("contract.source_layout must be an object", errors)
        self.assertIn("contract.limits must be an object", errors)
        joined = "\n".join(errors)
        self.assertNotIn("Traceback", joined)
        self.assertNotIn("AttributeError", joined)
        self.assertNotIn("TypeError", joined)

    def test_runtime_dir_excludes_init_only_package(self) -> None:
        checker = _load_checker()
        root = REPO_ROOT / "tests" / "architecture" / "data"
        root.mkdir(parents=True, exist_ok=True)
        try:
            pkg = root / "pkg"
            pkg.mkdir(exist_ok=True)
            (pkg / "__init__.py").write_text("", encoding="utf-8")
            runtime_dirs = checker._runtime_dirs_with_python(root)
            self.assertEqual(runtime_dirs, set())
            (pkg / "mod.py").write_text("x = 1\n", encoding="utf-8")
            runtime_dirs = checker._runtime_dirs_with_python(root)
            self.assertEqual(runtime_dirs, {pkg})
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_validate_source_handles_missing_limits(self) -> None:
        checker = _load_checker()
        contract = {
            "schema_version": "1.0.0",
            "source_layout": {},
            "limits": None,
            "libraries": {},
            "interfaces": {},
            "tests": {},
            "governance": {},
            "data": {},
            "architecture": {},
            "repository": {
                "owner": "x",
                "name": "x",
                "profile": "legacy",
                "status": "x",
                "enforcement": "Advisory",
            },
            "preservation": {
                "archival_notice": "x",
                "supersession_notice": "x",
                "revival_gates": ["a", "b", "c"],
                "provenance": "x",
                "license_warning": "x",
                "security_warning": "x",
                "private_data_warning": "x",
            },
            "exceptions": [],
        }
        error_list: list[str] = []
        checker.validate_source(contract, {}, error_list)
        self.assertIn("contract.limits must be an object", error_list)

    def test_validate_source_handles_malformed_array_fields(self) -> None:
        checker = _load_checker()
        contract = {
            "schema_version": "1.0.0",
            "source_layout": {
                "python_rules_applicable": True,
                "python_source_roots": "not-a-list",
                "allowed_non_python_files": {},
                "metadata_names": 123,
                "future_rule": "x",
            },
            "limits": {
                "max_immediate_runtime_entries": 10,
                "max_python_module_lines": 500,
            },
            "libraries": {},
            "interfaces": {},
            "tests": {},
            "governance": {},
            "data": {},
            "architecture": {},
            "repository": {
                "owner": "x",
                "name": "x",
                "profile": "legacy",
                "status": "x",
                "enforcement": "Advisory",
            },
            "preservation": {
                "archival_notice": "x",
                "supersession_notice": "x",
                "revival_gates": ["a", "b", "c"],
                "provenance": "x",
                "license_warning": "x",
                "security_warning": "x",
                "private_data_warning": "x",
            },
            "exceptions": [],
        }
        error_list: list[str] = []
        checker.validate_source(contract, {}, error_list)
        self.assertIn("contract.source_layout.python_source_roots must be an array", error_list)
        self.assertIn("contract.source_layout.allowed_non_python_files must be an array", error_list)
        self.assertIn("contract.source_layout.metadata_names must be an array", error_list)

    def test_dormant_python_scanning_ignores_invalid_root(self) -> None:
        checker = _load_checker()
        contract = {
            "schema_version": "1.0.0",
            "source_layout": {
                "python_rules_applicable": True,
                "python_source_roots": ["does_not_exist"],
            },
            "limits": {
                "max_immediate_runtime_entries": 10,
                "max_python_module_lines": 500,
            },
            "libraries": {},
            "interfaces": {},
            "tests": {},
            "governance": {},
            "data": {},
            "architecture": {},
            "repository": {
                "owner": "x",
                "name": "x",
                "profile": "legacy",
                "status": "x",
                "enforcement": "Advisory",
            },
            "preservation": {
                "archival_notice": "x",
                "supersession_notice": "x",
                "revival_gates": ["a", "b", "c"],
                "provenance": "x",
                "license_warning": "x",
                "security_warning": "x",
                "private_data_warning": "x",
            },
            "exceptions": [],
        }
        error_list: list[str] = []
        checker.validate_source(contract, {}, error_list)
        self.assertIn("declared Python source root is missing: does_not_exist", error_list)


if __name__ == "__main__":
    unittest.main()
