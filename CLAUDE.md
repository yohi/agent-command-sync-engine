# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The AI Agent Command Sync Engine is a Python-based synchronization system that unifies custom command management across multiple AI agent CLIs (ClaudeCode, Codex, GeminiCLI). It solves the problem of command fragmentation by establishing a universal source format and automated transformation pipeline.

## Core Architecture

### Transformation Pipeline Architecture

The system follows a "build-time" transformation approach rather than runtime translation:

1. **Universal Source Format** → Commands defined once in Markdown with YAML frontmatter
2. **Transformation Engine** → Converts universal format to agent-specific formats
3. **Deployment Manager** → Distributes to appropriate agent directories

**Key Architectural Decision**: Pre-generate agent-specific files during sync rather than using runtime proxies or symbolic links. This provides zero runtime overhead and works with existing agent implementations.

### Component Boundaries

- **Sync Engine Core**: Orchestrates parsing → transformation → deployment workflow
- **Command Parser**: Handles YAML frontmatter parsing and metadata validation
- **Transformation Engine**: Delegates to agent-specific transformers (ClaudeCode, Codex, Gemini)
- **Deployment Manager**: Manages file operations, backups, and atomic deployments
- **Framework Ingester**: Integrates third-party frameworks (e.g., SuperClaude)

### Critical Syntax Transformations

The transformation engine must handle incompatible placeholder syntax:

```
Universal Format:    {ARGS}              {SHELL:cmd}
→ ClaudeCode:        $ARGUMENTS          !cmd
→ Codex:             $ARGUMENTS          \!cmd
→ GeminiCLI:         {{args}}            \!{cmd}
```

## Scope Handling Constraints

**Important**: Codex CLI currently lacks project-level scope support. All Codex commands must deploy to `~/.codex/prompts/` regardless of scope metadata. This is a known limitation tracked in the requirements.

## File Organization

```
central-commands/
├── _config/              # Configuration and exclusion patterns
├── _frameworks/          # Third-party framework commands (SuperClaude, etc.)
└── commands/             # User-defined universal commands
    └── {namespace}/      # Namespace directories (e.g., git/, docker/)
```

Target deployment locations:
- ClaudeCode: `~/.claude/commands/` (user), `./.claude/commands/` (project)
- Codex: `~/.codex/prompts/` (user-level only)
- GeminiCLI: `~/.gemini/commands/` (user), `./.gemini/commands/` (project)

## Technology Stack

- **Language**: Python 3.10+
- **CLI Framework**: Typer (type-safe CLI construction)
- **Parsing**: PyYAML (YAML frontmatter)
- **Format Generation**: toml (stdlib), Markdown templating
- **Path Management**: pathlib (OS-agnostic operations)

## Development Commands

Currently no package.json or build configuration exists. When implemented, commands should follow Python conventions:

```bash
# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Run sync engine (when main entry point exists)
python -m sync_engine sync --scope=user

# Run tests (when test suite exists)
pytest tests/

# Type checking (when mypy configured)
mypy src/
```

## Implementation Status

This is a **specification-only** repository. The `.kiro/specs/agent-command-sync-engine/` directory contains:

- `requirements.md`: 8 detailed requirements with acceptance criteria
- `design.md`: Complete technical design with component interfaces and data models
- `tasks.md`: 10 major implementation tasks broken into 45+ subtasks

**No code has been implemented yet.** All development should follow the approved specification documents.

## Key Design Patterns

### Best-Effort Transformation with Warnings

When transforming commands (especially third-party framework commands), the engine uses graceful degradation:

- Transform what's possible for each target agent
- Log warnings for incompatible features
- Mark partial compatibility in metadata
- Preserve original files for reference

Rationale: Maximizes utility while being transparent about limitations.

### Transaction Boundaries

- **Per-file parsing**: Individual command files fail independently
- **Per-agent deployment**: Rollback affects only the failing agent
- **Framework ingestion**: Complete framework import is atomic

### Security Considerations

All shell command execution must:
- Validate against dangerous patterns (`rm -rf`, `curl | sh`)
- Properly escape arguments
- Use subprocess with array arguments (not shell=True)
- Require explicit confirmation for destructive operations

## Spec-Driven Development Workflow

This project follows the Kiro specification methodology. Before implementing any feature:

1. Review the corresponding requirement in `requirements.md`
2. Consult the technical design in `design.md`
3. Follow the task breakdown in `tasks.md`
4. Ensure implementation satisfies all acceptance criteria

## Third-Party Framework Integration Pattern

The "Install-then-Ingest" workflow for frameworks like SuperClaude:

1. Execute framework's standard installation (`pipx install SuperClaude`)
2. Let framework deploy to its default location (`~/.claude/commands/sc/`)
3. Scan framework directory for command files
4. Copy to central repository (`_frameworks/superclaude/`)
5. Trigger sync engine to transform and deploy

This reactive approach works with frameworks' existing installers rather than trying to intercept their deployment.

## Testing Strategy

When implementing tests, follow this structure:

- **Unit Tests**: YAML parsing, placeholder transformation, path resolution, validation logic
- **Integration Tests**: Full sync workflow, framework ingestion, backup/rollback, conflict resolution
- **E2E Tests**: setup-environment.sh execution, multi-agent deployment verification
- **Performance Tests**: Large repository sync (1000+ commands), concurrent deployments

## Migration and Rollback

The deployment manager must:
- Create timestamped backups before overwriting
- Support atomic rollback per agent on failure
- Detect manual modifications and prompt for confirmation

## Non-Goals

Explicitly out of scope for Phase 1:
- MCP (Model Context Protocol) server implementation
- Perfect automatic transformation for all edge cases
- Symbolic link based approaches
- Real-time command synchronization
