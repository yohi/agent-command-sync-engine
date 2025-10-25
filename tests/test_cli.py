"""Tests for command-line interface.

This module contains tests to verify that the CLI framework
is correctly configured and functional.
"""

import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

# Add src to path for import
src_path = Path("src").resolve()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from sync_engine.cli import app

runner = CliRunner()


class TestCLI:
    """Test suite for CLI functionality."""

    def test_cli_app_exists(self):
        """Test that CLI app is defined."""
        assert app is not None, "CLI app should be defined"

    def test_cli_help_command(self):
        """Test that CLI has help command."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0, "Help command should succeed"
        assert "sync-engine" in result.stdout.lower() or "usage" in result.stdout.lower()

    def test_cli_version_option(self):
        """Test that CLI has version option."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0, "Version command should succeed"

    def test_sync_command_exists(self):
        """Test that sync command is registered."""
        result = runner.invoke(app, ["sync", "--help"])
        assert result.exit_code == 0, "Sync command help should work"
        assert "sync" in result.stdout.lower()

    def test_sync_command_has_scope_option(self):
        """Test that sync command has scope option."""
        result = runner.invoke(app, ["sync", "--help"])
        assert result.exit_code == 0
        assert "--scope" in result.stdout or "scope" in result.stdout.lower()

    def test_sync_command_has_agents_option(self):
        """Test that sync command has agents option."""
        result = runner.invoke(app, ["sync", "--help"])
        assert result.exit_code == 0
        assert "--agents" in result.stdout or "agents" in result.stdout.lower()

    def test_sync_command_has_dry_run_flag(self):
        """Test that sync command has dry-run flag."""
        result = runner.invoke(app, ["sync", "--help"])
        assert result.exit_code == 0
        assert "--dry-run" in result.stdout or "dry-run" in result.stdout.lower()

    def test_sync_command_has_verbose_flag(self):
        """Test that sync command has verbose flag."""
        result = runner.invoke(app, ["sync", "--help"])
        assert result.exit_code == 0
        assert "--verbose" in result.stdout or "verbose" in result.stdout.lower()
