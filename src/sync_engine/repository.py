"""Command repository management for central command storage.

This module provides functionality for initializing and managing
the central command repository structure.
"""

from pathlib import Path
from typing import Optional


class CommandRepository:
    """Manages the central command repository structure.

    The repository structure:
    central-commands/
    ├── _config/              # Configuration and exclusion patterns
    │   ├── sync-config.yaml
    │   └── .syncignore
    ├── _frameworks/          # Third-party framework commands
    └── commands/             # User-defined universal commands
        └── {namespace}/      # Namespace directories
    """

    def __init__(self, path: Path):
        """Initialize repository manager.

        Args:
            path: Path to the central command repository.
        """
        self.path = Path(path)

    def initialize(self) -> None:
        """Initialize the repository directory structure.

        Creates the following directories:
        - _config/: Configuration files
        - _frameworks/: Third-party framework commands
        - commands/: User-defined commands

        Also creates default configuration files:
        - _config/sync-config.yaml
        - _config/.syncignore

        This method is idempotent and can be called multiple times safely.
        """
        # Create main directories
        self._create_directory(self.path)
        self._create_directory(self.path / "_config")
        self._create_directory(self.path / "_frameworks")
        self._create_directory(self.path / "commands")

        # Create default configuration files
        self._create_sync_config()
        self._create_syncignore()

    def create_namespace(self, namespace: str) -> Path:
        """Create a namespace directory for organizing commands.

        Args:
            namespace: The namespace path (e.g., 'git', 'docker/compose').

        Returns:
            Path to the created namespace directory.
        """
        namespace_path = self.path / "commands" / namespace
        self._create_directory(namespace_path)
        return namespace_path

    def _create_directory(self, path: Path) -> None:
        """Create a directory if it doesn't exist.

        Args:
            path: Path to the directory to create.
        """
        path.mkdir(parents=True, exist_ok=True)

    def _create_sync_config(self) -> None:
        """Create default sync-config.yaml file."""
        config_path = self.path / "_config" / "sync-config.yaml"

        if not config_path.exists():
            default_config = """# Sync Engine Configuration
# This file contains configuration for the AI Agent Command Sync Engine

# Agent configurations
agents:
  claudecode:
    enabled: true
    user_path: "~/.claude/commands"
    project_path: "./.claude/commands"

  codex:
    enabled: true
    user_path: "~/.codex/prompts"
    # Note: Codex currently only supports user-level scope

  gemini:
    enabled: true
    user_path: "~/.gemini/commands"
    project_path: "./.gemini/commands"

# Default deployment scope
default_scope: "all"  # Options: user, project, all

# Custom transformation rules (optional)
# transformation_rules:
#   - pattern: "custom_placeholder"
#     claudecode: "cc_replacement"
#     codex: "codex_replacement"
#     gemini: "gemini_replacement"
"""
            config_path.write_text(default_config)

    def _create_syncignore(self) -> None:
        """Create default .syncignore file."""
        syncignore_path = self.path / "_config" / ".syncignore"

        if not syncignore_path.exists():
            default_syncignore = """# Sync Engine Ignore Patterns
# Similar to .gitignore syntax

# Ignore hidden files
.*

# Ignore backup files
*.bak
*.tmp
*~

# Ignore OS-specific files
.DS_Store
Thumbs.db

# Ignore editor files
*.swp
*.swo
.vscode/
.idea/

# Ignore test files (optional)
# *test*
# *spec*
"""
            syncignore_path.write_text(default_syncignore)
