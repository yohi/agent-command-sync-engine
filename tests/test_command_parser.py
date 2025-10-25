"""Tests for command file parsing and metadata extraction.

This module contains tests to verify that command files are correctly
parsed and metadata is properly extracted from YAML frontmatter.
"""

from pathlib import Path
import pytest
import tempfile


class TestCommandParser:
    """Test suite for command parsing functionality."""

    def test_parser_can_be_instantiated(self):
        """Test that CommandParser can be created."""
        from sync_engine.parser import CommandParser

        parser = CommandParser()
        assert parser is not None

    def test_scan_repository_finds_command_files(self, tmp_path):
        """Test that parser can scan repository for command files."""
        from sync_engine.parser import CommandParser
        from sync_engine.repository import CommandRepository

        # Create repository with a command file
        repo = CommandRepository(tmp_path)
        repo.initialize()

        # Create a command file
        git_namespace = repo.create_namespace("git")
        command_file = git_namespace / "commit.md"
        command_file.write_text("""---
name: commit
description: Create a git commit
---

Command body here
""")

        # Scan for commands
        parser = CommandParser()
        commands = parser.scan_repository(tmp_path)

        assert len(commands) > 0
        assert any(cmd.name == "commit" for cmd in commands)

    def test_parse_yaml_frontmatter(self):
        """Test parsing YAML frontmatter from command content."""
        from sync_engine.parser import CommandParser

        content = """---
name: test-command
description: Test command description
scope: user
---

Command body content
"""

        parser = CommandParser()
        metadata = parser.parse_frontmatter(content)

        assert metadata is not None
        assert metadata["name"] == "test-command"
        assert metadata["description"] == "Test command description"
        assert metadata["scope"] == "user"

    def test_extract_metadata_fields(self):
        """Test extraction of all metadata fields."""
        from sync_engine.parser import CommandParser

        content = """---
name: docker-build
description: Build a docker image
scope: project
arguments:
  - name: tag
    required: true
    description: Image tag
shell_execution: true
tags: [docker, build]
---

Build docker image
"""

        parser = CommandParser()
        metadata = parser.parse_frontmatter(content)

        assert metadata["name"] == "docker-build"
        assert metadata["description"] == "Build a docker image"
        assert metadata["scope"] == "project"
        assert "arguments" in metadata
        assert len(metadata["arguments"]) == 1
        assert metadata["arguments"][0]["name"] == "tag"
        assert metadata["shell_execution"] is True
        assert "docker" in metadata["tags"]

    def test_parse_command_file(self, tmp_path):
        """Test parsing a complete command file."""
        from sync_engine.parser import CommandParser

        # Create a test command file
        command_file = tmp_path / "test.md"
        command_file.write_text("""---
name: test
description: Test command
scope: user
---

# Test Command

This is the command body.
""")

        parser = CommandParser()
        command = parser.parse_file(command_file)

        assert command is not None
        assert command.name == "test"
        assert command.description == "Test command"
        assert command.scope == "user"
        assert "Test Command" in command.body
        assert command.source_path == command_file

    def test_namespace_detection_from_path(self, tmp_path):
        """Test that namespace is correctly detected from file path."""
        from sync_engine.parser import CommandParser
        from sync_engine.repository import CommandRepository

        # Create repository with nested namespace
        repo = CommandRepository(tmp_path)
        repo.initialize()

        docker_compose_ns = repo.create_namespace("docker/compose")
        command_file = docker_compose_ns / "up.md"
        command_file.write_text("""---
name: up
description: Start services
---

Start docker compose services
""")

        parser = CommandParser()
        command = parser.parse_file(command_file)

        assert command.namespace == "docker/compose"

    def test_scan_finds_multiple_commands(self, tmp_path):
        """Test that scan finds all command files in repository."""
        from sync_engine.parser import CommandParser
        from sync_engine.repository import CommandRepository

        repo = CommandRepository(tmp_path)
        repo.initialize()

        # Create multiple commands
        git_ns = repo.create_namespace("git")
        (git_ns / "commit.md").write_text("---\nname: commit\n---\nBody")
        (git_ns / "push.md").write_text("---\nname: push\n---\nBody")

        docker_ns = repo.create_namespace("docker")
        (docker_ns / "build.md").write_text("---\nname: build\n---\nBody")

        parser = CommandParser()
        commands = parser.scan_repository(tmp_path)

        assert len(commands) == 3
        command_names = [cmd.name for cmd in commands]
        assert "commit" in command_names
        assert "push" in command_names
        assert "build" in command_names

    def test_parser_extracts_body_without_frontmatter(self):
        """Test that command body doesn't include frontmatter."""
        from sync_engine.parser import CommandParser

        content = """---
name: test
description: Test
---

This is the body.
It has multiple lines.
"""

        parser = CommandParser()
        metadata = parser.parse_frontmatter(content)
        body = parser.extract_body(content)

        assert "---" not in body
        assert "name: test" not in body
        assert "This is the body." in body
        assert "It has multiple lines." in body

    def test_parser_handles_missing_frontmatter(self):
        """Test that parser handles files without YAML frontmatter."""
        from sync_engine.parser import CommandParser

        content = """Just plain content without frontmatter.
No YAML here.
"""

        parser = CommandParser()
        result = parser.parse_frontmatter(content)

        # Should return None or empty dict for missing frontmatter
        assert result is None or result == {}
