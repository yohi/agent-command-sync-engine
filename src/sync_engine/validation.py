"""Command validation and error reporting.

This module provides validation functionality for command files,
including required field checks, duplicate detection, and YAML schema validation.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import re
import yaml

if TYPE_CHECKING:
    from sync_engine.parser import Command


# Common patterns
FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n",
    re.DOTALL | re.MULTILINE
)


@dataclass
class ValidationError:
    """Represents a validation error with context.

    Attributes:
        message: Human-readable error message
        field: Field name that caused the error (optional)
        line_number: Line number in source file (optional)
        severity: Error severity ('error', 'warning', 'info')
    """

    message: str
    field: Optional[str] = None
    line_number: Optional[int] = None
    severity: str = "error"


@dataclass
class ValidationResult:
    """Result of validation operation.

    Attributes:
        errors: List of validation errors
        warnings: List of validation warnings
    """

    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    def add_error(
        self,
        message: str,
        field: Optional[str] = None,
        line_number: Optional[int] = None
    ) -> None:
        """Add an error to the validation result."""
        self.errors.append(
            ValidationError(
                message=message,
                field=field,
                line_number=line_number,
                severity="error"
            )
        )

    def add_warning(
        self,
        message: str,
        field: Optional[str] = None,
        line_number: Optional[int] = None
    ) -> None:
        """Add a warning to the validation result."""
        self.warnings.append(
            ValidationError(
                message=message,
                field=field,
                line_number=line_number,
                severity="warning"
            )
        )

    def format_errors(self) -> str:
        """Format errors for display.

        Returns:
            Formatted string with all errors
        """
        if not self.errors:
            return "No errors"

        lines = []
        for error in self.errors:
            parts = [f"{error.severity.upper()}:"]

            if error.field:
                parts.append(f"field '{error.field}'")

            if error.line_number:
                parts.append(f"at line {error.line_number}")

            parts.append(f"- {error.message}")

            lines.append(" ".join(parts))

        return "\n".join(lines)


class CommandValidator:
    """Validator for command files and metadata."""

    # Valid scope values
    VALID_SCOPES = {"user", "project", "all"}

    # Required metadata fields
    REQUIRED_FIELDS = {"name", "description"}

    def __init__(self):
        """Initialize the command validator."""
        pass

    def validate_command(self, command: "Command") -> ValidationResult:
        """Validate a command object.

        Args:
            command: Command object to validate

        Returns:
            ValidationResult with any validation errors
        """
        result = ValidationResult()

        # Check required fields
        if not command.name or command.name.strip() == "":
            result.add_error(
                message="Required field 'name' is missing or empty",
                field="name"
            )

        if not command.description or command.description.strip() == "":
            result.add_error(
                message="Required field 'description' is missing or empty",
                field="description"
            )

        # Validate scope value
        if command.scope and command.scope not in self.VALID_SCOPES:
            result.add_error(
                message=f"Invalid scope value '{command.scope}'. Must be one of: {', '.join(sorted(self.VALID_SCOPES))}",
                field="scope"
            )

        return result

    def check_duplicates(self, commands: List["Command"]) -> ValidationResult:
        """Check for duplicate command names within namespaces.

        Args:
            commands: List of Command objects to check

        Returns:
            ValidationResult with duplicate detection errors
        """
        result = ValidationResult()

        # Group commands by namespace
        namespace_commands: Dict[str, List] = {}

        for command in commands:
            ns = command.namespace
            if ns not in namespace_commands:
                namespace_commands[ns] = []
            namespace_commands[ns].append(command)

        # Check for duplicates within each namespace
        for namespace, ns_commands in namespace_commands.items():
            name_to_commands: Dict[str, List] = {}

            for command in ns_commands:
                name = command.name
                if name not in name_to_commands:
                    name_to_commands[name] = []
                name_to_commands[name].append(command)

            # Report duplicates
            for name, cmds in name_to_commands.items():
                if len(cmds) > 1:
                    paths = [str(cmd.source_path) for cmd in cmds]
                    ns_display = f"namespace '{namespace}'" if namespace else "root namespace"
                    result.add_error(
                        message=f"Duplicate command name '{name}' found in {ns_display}: {', '.join(paths)}",
                        field="name"
                    )

        return result

    def validate_yaml(self, content: str, file_path: Path) -> ValidationResult:
        """Validate YAML frontmatter structure.

        Args:
            content: File content with YAML frontmatter
            file_path: Path to the file being validated

        Returns:
            ValidationResult with YAML validation errors
        """
        result = ValidationResult()

        # Extract frontmatter using shared pattern
        match = FRONTMATTER_PATTERN.match(content)
        if not match:
            result.add_error(
                message="No valid YAML frontmatter found",
                line_number=1
            )
            return result

        yaml_content = match.group(1)

        # Try to parse YAML
        try:
            yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            # Extract line number if available
            line_number = None
            if hasattr(e, "problem_mark"):
                mark = e.problem_mark
                line_number = mark.line + 2  # +2 to account for "---" line

            result.add_error(
                message=f"Invalid YAML syntax: {str(e)}",
                line_number=line_number
            )

        return result

    def validate_metadata_schema(
        self, metadata: Dict[str, Any], file_path: Path
    ) -> ValidationResult:
        """Validate metadata against expected schema.

        Args:
            metadata: Metadata dictionary to validate
            file_path: Path to the file being validated

        Returns:
            ValidationResult with schema validation errors
        """
        result = ValidationResult()

        # Check required fields
        for field_name in self.REQUIRED_FIELDS:
            if field_name not in metadata or not metadata[field_name]:
                result.add_error(
                    message=f"Required field '{field_name}' is missing",
                    field=field_name
                )

        # Validate scope if present
        if "scope" in metadata:
            scope = metadata["scope"]
            if scope not in self.VALID_SCOPES:
                result.add_error(
                    message=f"Invalid scope value '{scope}'. Must be one of: {', '.join(sorted(self.VALID_SCOPES))}",
                    field="scope"
                )

        # Validate arguments if present
        if "arguments" in metadata:
            arguments = metadata["arguments"]
            if not isinstance(arguments, list):
                result.add_error(
                    message="Field 'arguments' must be a list",
                    field="arguments"
                )
            else:
                for i, arg in enumerate(arguments):
                    if not isinstance(arg, dict):
                        result.add_error(
                            message=f"Argument at index {i} must be a dictionary",
                            field="arguments"
                        )
                    elif "name" not in arg:
                        result.add_error(
                            message=f"Argument at index {i} is missing 'name' field",
                            field="arguments"
                        )

        # Validate shell_execution if present
        if "shell_execution" in metadata:
            shell_exec = metadata["shell_execution"]
            if not isinstance(shell_exec, bool):
                result.add_error(
                    message="Field 'shell_execution' must be a boolean",
                    field="shell_execution"
                )

        # Validate tags if present
        if "tags" in metadata:
            tags = metadata["tags"]
            if not isinstance(tags, list):
                result.add_error(
                    message="Field 'tags' must be a list",
                    field="tags"
                )

        return result
