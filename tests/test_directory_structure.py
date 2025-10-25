"""Tests for central command repository directory structure.

This module contains tests to verify that the central command
repository structure is properly initialized and managed.
"""

from pathlib import Path
import pytest


class TestDirectoryStructure:
    """Test suite for central command repository structure."""

    def test_central_commands_directory_creation(self, tmp_path):
        """Test that central-commands directory can be created."""
        from sync_engine.repository import CommandRepository

        repo_path = tmp_path / "test-repo"
        repo = CommandRepository(repo_path)
        repo.initialize()

        assert repo_path.exists(), "Repository directory should exist"
        assert repo_path.is_dir(), "Repository should be a directory"

    def test_config_directory_creation(self, tmp_path):
        """Test that _config directory is created."""
        from sync_engine.repository import CommandRepository

        repo_path = tmp_path / "test-repo"
        repo = CommandRepository(repo_path)
        repo.initialize()

        config_dir = repo_path / "_config"
        assert config_dir.exists(), "_config directory should exist"
        assert config_dir.is_dir(), "_config should be a directory"

    def test_frameworks_directory_creation(self, tmp_path):
        """Test that _frameworks directory is created."""
        from sync_engine.repository import CommandRepository

        repo_path = tmp_path / "test-repo"
        repo = CommandRepository(repo_path)
        repo.initialize()

        frameworks_dir = repo_path / "_frameworks"
        assert frameworks_dir.exists(), "_frameworks directory should exist"
        assert frameworks_dir.is_dir(), "_frameworks should be a directory"

    def test_commands_directory_creation(self, tmp_path):
        """Test that commands directory is created."""
        from sync_engine.repository import CommandRepository

        repo_path = tmp_path / "test-repo"
        repo = CommandRepository(repo_path)
        repo.initialize()

        commands_dir = repo_path / "commands"
        assert commands_dir.exists(), "commands directory should exist"
        assert commands_dir.is_dir(), "commands should be a directory"

    def test_sync_config_file_creation(self, tmp_path):
        """Test that sync-config.yaml is created."""
        from sync_engine.repository import CommandRepository

        repo_path = tmp_path / "test-repo"
        repo = CommandRepository(repo_path)
        repo.initialize()

        sync_config = repo_path / "_config" / "sync-config.yaml"
        assert sync_config.exists(), "sync-config.yaml should exist"
        assert sync_config.is_file(), "sync-config.yaml should be a file"

    def test_syncignore_file_creation(self, tmp_path):
        """Test that .syncignore is created."""
        from sync_engine.repository import CommandRepository

        repo_path = tmp_path / "test-repo"
        repo = CommandRepository(repo_path)
        repo.initialize()

        syncignore = repo_path / "_config" / ".syncignore"
        assert syncignore.exists(), ".syncignore should exist"
        assert syncignore.is_file(), ".syncignore should be a file"

    def test_initialize_is_idempotent(self, tmp_path):
        """Test that initialize can be called multiple times safely."""
        from sync_engine.repository import CommandRepository

        repo_path = tmp_path / "test-repo"
        repo = CommandRepository(repo_path)

        # Initialize twice
        repo.initialize()
        repo.initialize()

        # Should still have all directories
        assert (repo_path / "_config").exists()
        assert (repo_path / "_frameworks").exists()
        assert (repo_path / "commands").exists()

    def test_namespace_directory_creation(self, tmp_path):
        """Test that namespace directories can be created."""
        from sync_engine.repository import CommandRepository

        repo_path = tmp_path / "test-repo"
        repo = CommandRepository(repo_path)
        repo.initialize()

        # Create a namespace
        namespace_path = repo.create_namespace("git")
        assert namespace_path.exists(), "Namespace directory should exist"
        assert namespace_path.is_dir(), "Namespace should be a directory"
        assert namespace_path == repo_path / "commands" / "git"

    def test_nested_namespace_creation(self, tmp_path):
        """Test that nested namespaces can be created."""
        from sync_engine.repository import CommandRepository

        repo_path = tmp_path / "test-repo"
        repo = CommandRepository(repo_path)
        repo.initialize()

        # Create nested namespace
        namespace_path = repo.create_namespace("docker/compose")
        assert namespace_path.exists(), "Nested namespace should exist"
        assert namespace_path == repo_path / "commands" / "docker" / "compose"
