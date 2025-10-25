"""Command file parser for extracting metadata and content.

This module provides functionality for parsing command files,
extracting YAML frontmatter metadata, and scanning repositories.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

import yaml


@dataclass
class Command:
    """Represents a parsed command with metadata and body.

    Attributes:
        name: Command name from metadata
        description: Command description from metadata
        scope: Deployment scope (user, project, or all)
        body: Command body content (without frontmatter)
        source_path: Path to the source command file
        namespace: Command namespace derived from directory structure
        arguments: Optional list of command arguments
        shell_execution: Whether command uses shell execution
        tags: Optional list of tags for categorization
        metadata: Raw metadata dictionary
    """

    name: str
    description: str
    scope: str
    body: str
    source_path: Path
    namespace: str
    arguments: Optional[List[Dict[str, Any]]] = None
    shell_execution: bool = False
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class CommandParser:
    """Parser for command files with YAML frontmatter."""

    # Regex pattern to match YAML frontmatter
    FRONTMATTER_PATTERN = re.compile(
        r"^---\s*\n(.*?)\n---\s*\n(.*)$",
        re.DOTALL | re.MULTILINE
    )

    def __init__(self):
        """Initialize the command parser."""
        pass

    def scan_repository(self, repo_path: Path) -> List[Command]:
        """Scan repository for all command files.

        Args:
            repo_path: Path to the central command repository

        Returns:
            List of parsed Command objects
        """
        repo_path = Path(repo_path)
        commands_dir = repo_path / "commands"

        if not commands_dir.exists():
            return []

        commands = []
        # Recursively find all .md files in commands directory
        for command_file in commands_dir.rglob("*.md"):
            try:
                command = self.parse_file(command_file, repo_path)
                if command:
                    commands.append(command)
            except Exception as e:
                # Log error but continue processing other files
                print(f"Error parsing {command_file}: {e}")
                continue

        return commands

    def parse_file(self, file_path: Path, repo_path: Optional[Path] = None) -> Optional[Command]:
        """Parse a command file and extract metadata and body.

        Args:
            file_path: Path to the command file
            repo_path: Optional path to repository root for namespace detection

        Returns:
            Parsed Command object or None if parsing fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return None

        content = file_path.read_text(encoding="utf-8")

        # Parse frontmatter
        metadata = self.parse_frontmatter(content)

        if not metadata:
            return None

        # Extract body
        body = self.extract_body(content)

        # Detect namespace
        namespace = self._detect_namespace(file_path, repo_path)

        # Build Command object
        command = Command(
            name=metadata.get("name", ""),
            description=metadata.get("description", ""),
            scope=metadata.get("scope", "user"),
            body=body,
            source_path=file_path,
            namespace=namespace,
            arguments=metadata.get("arguments"),
            shell_execution=metadata.get("shell_execution", False),
            tags=metadata.get("tags"),
            metadata=metadata,
        )

        return command

    def parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse YAML frontmatter from content.

        Args:
            content: File content with YAML frontmatter

        Returns:
            Dictionary of metadata or None if no frontmatter found
        """
        match = self.FRONTMATTER_PATTERN.match(content)

        if not match:
            return None

        yaml_content = match.group(1)

        try:
            metadata = yaml.safe_load(yaml_content)
            return metadata if metadata else {}
        except yaml.YAMLError as e:
            print(f"YAML parsing error: {e}")
            return None

    def extract_body(self, content: str) -> str:
        """Extract command body without frontmatter.

        Args:
            content: File content with YAML frontmatter

        Returns:
            Command body content
        """
        match = self.FRONTMATTER_PATTERN.match(content)

        if not match:
            # No frontmatter, return entire content
            return content

        # Return content after frontmatter
        body = match.group(2)
        return body.strip()

    def _detect_namespace(
        self, file_path: Path, repo_path: Optional[Path] = None
    ) -> str:
        """Detect namespace from file path structure.

        Args:
            file_path: Path to the command file
            repo_path: Optional path to repository root

        Returns:
            Namespace string (e.g., "git", "docker/compose")
        """
        if not repo_path:
            # Try to find commands directory in path
            parts = file_path.parts
            try:
                commands_idx = parts.index("commands")
                namespace_parts = parts[commands_idx + 1 : -1]  # Exclude filename
                return "/".join(namespace_parts) if namespace_parts else ""
            except ValueError:
                return ""

        repo_path = Path(repo_path)
        commands_dir = repo_path / "commands"

        try:
            # Get relative path from commands directory
            relative_path = file_path.relative_to(commands_dir)
            # Get parent directories (namespace)
            namespace_parts = relative_path.parts[:-1]  # Exclude filename
            return "/".join(namespace_parts) if namespace_parts else ""
        except ValueError:
            return ""
