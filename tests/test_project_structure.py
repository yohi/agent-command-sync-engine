"""Tests for project structure validation.

This module contains tests to verify that the project structure
is correctly initialized according to the specification.
"""

import sys
from pathlib import Path

import pytest


class TestProjectStructure:
    """Test suite for validating project directory structure."""

    def test_src_package_exists(self):
        """Test that src package directory exists."""
        src_dir = Path("src")
        assert src_dir.exists(), "src directory should exist"
        assert src_dir.is_dir(), "src should be a directory"

    def test_sync_engine_package_exists(self):
        """Test that sync_engine package exists within src."""
        sync_engine_dir = Path("src/sync_engine")
        assert sync_engine_dir.exists(), "src/sync_engine directory should exist"
        assert sync_engine_dir.is_dir(), "src/sync_engine should be a directory"

    def test_sync_engine_package_init(self):
        """Test that sync_engine package has __init__.py."""
        init_file = Path("src/sync_engine/__init__.py")
        assert init_file.exists(), "src/sync_engine/__init__.py should exist"
        assert init_file.is_file(), "src/sync_engine/__init__.py should be a file"

    def test_sync_engine_importable(self):
        """Test that sync_engine package can be imported."""
        # Add src to path for import
        src_path = Path("src").resolve()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        # Should not raise ImportError
        import sync_engine
        assert hasattr(sync_engine, "__version__"), "Package should have __version__ attribute"

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists."""
        requirements_file = Path("requirements.txt")
        assert requirements_file.exists(), "requirements.txt should exist"
        assert requirements_file.is_file(), "requirements.txt should be a file"

    def test_requirements_contains_typer(self):
        """Test that requirements.txt includes Typer."""
        requirements_file = Path("requirements.txt")
        content = requirements_file.read_text()
        assert "typer" in content.lower(), "requirements.txt should include typer"

    def test_requirements_contains_pyyaml(self):
        """Test that requirements.txt includes PyYAML."""
        requirements_file = Path("requirements.txt")
        content = requirements_file.read_text()
        assert "pyyaml" in content.lower(), "requirements.txt should include pyyaml"

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists for project metadata."""
        pyproject_file = Path("pyproject.toml")
        assert pyproject_file.exists(), "pyproject.toml should exist"
        assert pyproject_file.is_file(), "pyproject.toml should be a file"

    def test_pytest_config_in_pyproject(self):
        """Test that pyproject.toml contains pytest configuration."""
        pyproject_file = Path("pyproject.toml")
        content = pyproject_file.read_text()
        assert "pytest" in content.lower(), "pyproject.toml should include pytest configuration"
