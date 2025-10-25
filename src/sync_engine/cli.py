"""Command-line interface for Agent Command Sync Engine.

This module provides the main CLI interface using Typer.
"""

from typing import Optional

import typer
from rich.console import Console

from sync_engine import __version__

app = typer.Typer(
    name="sync-engine",
    help="Unified command management across multiple AI agent CLIs",
    add_completion=False,
)

console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
    ),
) -> None:
    """AI Agent Command Sync Engine - Unified command management."""
    if version:
        console.print(f"[bold]Agent Command Sync Engine[/bold] version {__version__}")
        raise typer.Exit()


@app.command()
def sync(
    scope: str = typer.Option(
        "all",
        "--scope",
        "-s",
        help="Deployment scope: user, project, or all",
    ),
    agents: str = typer.Option(
        "all",
        "--agents",
        "-a",
        help="Comma-separated list of target agents (claudecode, codex, gemini). If not specified, syncs to all agents.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Show what would be done without making changes",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-V",
        help="Enable verbose output",
    ),
) -> None:
    """Synchronize commands to agent directories.

    This command reads commands from the central repository and deploys
    them to configured AI agent directories.
    """
    console.print("[bold]Sync Engine[/bold] - Command synchronization")
    console.print(f"Scope: {scope}")
    console.print(f"Agents: {agents}")
    console.print(f"Dry run: {dry_run}")
    console.print(f"Verbose: {verbose}")

    if dry_run:
        console.print("[yellow]Dry run mode - no changes will be made[/yellow]")

    # Placeholder implementation
    console.print("[green]Sync completed successfully![/green]")


if __name__ == "__main__":
    app()
