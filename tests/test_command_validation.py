"""Tests for command validation and error reporting.

This module tests the validation functionality for command files,
including required field validation, duplicate detection, and error reporting.
"""

from pathlib import Path
import pytest
from sync_engine.parser import CommandParser, Command
from sync_engine.validation import (
    CommandValidator,
    ValidationError,
    ValidationResult,
)


class TestRequiredFieldValidation:
    """Test suite for required field validation."""

    def test_validate_accepts_command_with_all_required_fields(self):
        """Test that validator accepts command with name and description."""
        validator = CommandValidator()

        command = Command(
            name="test-command",
            description="Test description",
            scope="user",
            body="Command body",
            source_path=Path("/tmp/test.md"),
            namespace="",
        )

        result = validator.validate_command(command)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_rejects_command_without_name(self):
        """Test that validator rejects command without name field."""
        validator = CommandValidator()

        command = Command(
            name="",  # Empty name
            description="Test description",
            scope="user",
            body="Command body",
            source_path=Path("/tmp/test.md"),
            namespace="",
        )

        result = validator.validate_command(command)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("name" in error.message.lower() for error in result.errors)

    def test_validate_rejects_command_without_description(self):
        """Test that validator rejects command without description field."""
        validator = CommandValidator()

        command = Command(
            name="test-command",
            description="",  # Empty description
            scope="user",
            body="Command body",
            source_path=Path("/tmp/test.md"),
            namespace="",
        )

        result = validator.validate_command(command)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("description" in error.message.lower() for error in result.errors)

    def test_validate_provides_specific_error_message_for_missing_fields(self):
        """Test that validator provides clear error messages for missing fields."""
        validator = CommandValidator()

        command = Command(
            name="",
            description="",
            scope="user",
            body="Command body",
            source_path=Path("/tmp/test.md"),
            namespace="",
        )

        result = validator.validate_command(command)
        assert not result.is_valid

        # Should have specific errors for both missing fields
        error_messages = [error.message for error in result.errors]
        assert any("name" in msg.lower() and "required" in msg.lower() for msg in error_messages)
        assert any("description" in msg.lower() and "required" in msg.lower() for msg in error_messages)


class TestDuplicateCommandDetection:
    """Test suite for duplicate command name detection."""

    def test_detect_duplicate_commands_in_same_namespace(self):
        """Test that validator detects duplicate command names in same namespace."""
        validator = CommandValidator()

        command1 = Command(
            name="commit",
            description="Git commit",
            scope="user",
            body="Body 1",
            source_path=Path("/tmp/git/commit.md"),
            namespace="git",
        )

        command2 = Command(
            name="commit",  # Duplicate name
            description="Another commit",
            scope="user",
            body="Body 2",
            source_path=Path("/tmp/git/commit2.md"),
            namespace="git",  # Same namespace
        )

        result = validator.check_duplicates([command1, command2])
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("duplicate" in error.message.lower() for error in result.errors)

    def test_allow_same_command_name_in_different_namespaces(self):
        """Test that validator allows same command name in different namespaces."""
        validator = CommandValidator()

        command1 = Command(
            name="build",
            description="Git build",
            scope="user",
            body="Body 1",
            source_path=Path("/tmp/git/build.md"),
            namespace="git",
        )

        command2 = Command(
            name="build",  # Same name
            description="Docker build",
            scope="user",
            body="Body 2",
            source_path=Path("/tmp/docker/build.md"),
            namespace="docker",  # Different namespace
        )

        result = validator.check_duplicates([command1, command2])
        assert result.is_valid
        assert len(result.errors) == 0

    def test_duplicate_error_includes_file_paths(self):
        """Test that duplicate error message includes conflicting file paths."""
        validator = CommandValidator()

        path1 = Path("/tmp/git/commit.md")
        path2 = Path("/tmp/git/commit2.md")

        command1 = Command(
            name="commit",
            description="Git commit",
            scope="user",
            body="Body 1",
            source_path=path1,
            namespace="git",
        )

        command2 = Command(
            name="commit",
            description="Another commit",
            scope="user",
            body="Body 2",
            source_path=path2,
            namespace="git",
        )

        result = validator.check_duplicates([command1, command2])
        assert not result.is_valid

        # Error message should mention both file paths
        error_message = result.errors[0].message
        assert str(path1) in error_message or path1.name in error_message
        assert str(path2) in error_message or path2.name in error_message


class TestYAMLSchemaValidation:
    """Test suite for YAML schema validation with line number tracking."""

    def test_validate_yaml_structure_with_valid_content(self):
        """Test that validator accepts well-formed YAML."""
        validator = CommandValidator()

        yaml_content = """---
name: test
description: Test command
scope: user
---

Body content
"""

        result = validator.validate_yaml(yaml_content, Path("/tmp/test.md"))
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_yaml_rejects_malformed_yaml(self):
        """Test that validator rejects malformed YAML with syntax errors."""
        validator = CommandValidator()

        # Invalid YAML - unclosed quote
        yaml_content = """---
name: "test
description: Test command
---

Body
"""

        result = validator.validate_yaml(yaml_content, Path("/tmp/test.md"))
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_yaml_validation_error_includes_line_number(self):
        """Test that YAML validation errors include line numbers."""
        validator = CommandValidator()

        # Invalid YAML
        yaml_content = """---
name: test
invalid_syntax here
description: Test
---
"""

        result = validator.validate_yaml(yaml_content, Path("/tmp/test.md"))
        assert not result.is_valid

        # Should include line number in error
        error = result.errors[0]
        assert error.line_number is not None
        assert error.line_number > 0

    def test_validate_scope_field_values(self):
        """Test that validator checks scope field has valid values."""
        validator = CommandValidator()

        command = Command(
            name="test",
            description="Test",
            scope="invalid_scope",  # Invalid scope value
            body="Body",
            source_path=Path("/tmp/test.md"),
            namespace="",
        )

        result = validator.validate_command(command)
        assert not result.is_valid
        assert any("scope" in error.message.lower() for error in result.errors)


class TestTimestampTracking:
    """Test suite for command modification timestamp tracking."""

    def test_command_includes_modification_timestamp(self, tmp_path):
        """Test that parsed commands include modification timestamp."""
        parser = CommandParser()

        # Create a temporary file
        command_file = tmp_path / "test.md"
        command_file.write_text("""---
name: test
description: Test
---

Body
""")

        command = parser.parse_file(command_file)

        assert command is not None
        assert hasattr(command, "modified_at")
        assert command.modified_at is not None

    def test_timestamp_reflects_file_modification_time(self, tmp_path):
        """Test that timestamp matches file's modification time."""
        parser = CommandParser()

        # Create a test file
        command_file = tmp_path / "test.md"
        command_file.write_text("""---
name: test
description: Test
---

Body
""")

        command = parser.parse_file(command_file)
        file_mtime = command_file.stat().st_mtime

        assert command is not None
        assert command.modified_at is not None
        # Allow small difference due to precision
        assert abs(command.modified_at - file_mtime) < 1.0


class TestErrorReporting:
    """Test suite for descriptive error messages."""

    def test_validation_error_has_required_fields(self):
        """Test that ValidationError contains all necessary information."""
        error = ValidationError(
            message="Test error",
            field="name",
            line_number=5,
            severity="error"
        )

        assert error.message == "Test error"
        assert error.field == "name"
        assert error.line_number == 5
        assert error.severity == "error"

    def test_validation_result_aggregates_errors(self):
        """Test that ValidationResult can aggregate multiple errors."""
        error1 = ValidationError(
            message="Missing name",
            field="name",
            severity="error"
        )
        error2 = ValidationError(
            message="Missing description",
            field="description",
            severity="error"
        )

        result = ValidationResult(errors=[error1, error2])

        assert not result.is_valid
        assert len(result.errors) == 2
        assert result.errors[0].field == "name"
        assert result.errors[1].field == "description"

    def test_validation_result_format_provides_readable_summary(self):
        """Test that validation result can be formatted for display."""
        error = ValidationError(
            message="Missing required field 'name'",
            field="name",
            line_number=3,
            severity="error"
        )

        result = ValidationResult(errors=[error])
        formatted = result.format_errors()

        assert "name" in formatted
        assert "line 3" in formatted.lower() or "3" in formatted
        assert "error" in formatted.lower()
