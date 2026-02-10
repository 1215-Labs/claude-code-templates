"""
E2B Sandbox CLI - Main entry point.

A CLI for managing E2B sandboxes and performing operations.
Extracted from references/agent-sandbox-skill with browser automation removed.
"""

import os
import click
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables from .env file
# Check skill root first, then project root, then home directory
_skill_root = Path(__file__).parent.parent
for _env_candidate in [
    _skill_root / ".env",
    Path.cwd() / ".env",
    Path.home() / ".env",
]:
    if _env_candidate.exists():
        load_dotenv(_env_candidate)
        break

# Also load from E2B_API_KEY env var (already set in environment)
# dotenv won't overwrite existing env vars by default

# Import command groups
from .commands.sandbox import sandbox
from .commands.files import files
from .commands.exec import exec

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    E2B Sandbox CLI - Control sandboxes from the command line.

    This CLI provides comprehensive sandbox management capabilities:
    - Create, connect to, and manage sandboxes (sandbox)
    - Perform file operations with SDK APIs (files)
    - Execute any command with full control (exec)

    Most commands require a SANDBOX_ID. You can get one by:
    1. Creating a new sandbox: sbx init
    2. Or: sbx sandbox create

    Tip: For multi-agent workflows, capture the sandbox ID in your context
    and use it directly in commands (avoid shell variables for safety).
    """
    pass


# Add command groups
cli.add_command(sandbox)
cli.add_command(files)
cli.add_command(exec)


# Add an init command for quick sandbox setup
@cli.command()
@click.option(
    "--template",
    "-t",
    default=None,
    help="Sandbox template name or ID",
)
@click.option(
    "--timeout", default=600, help="Sandbox timeout in seconds (default: 10 minutes)"
)
@click.option("--env", "-e", multiple=True, help="Environment variables (KEY=VALUE)")
@click.option("--name", "-n", default=None, help="Sandbox name (stored in metadata)")
def init(template, timeout, env, name):
    """
    Initialize a new sandbox and display the ID.

    Creates a new sandbox and outputs the sandbox ID. Capture the ID
    from the output and store it in your context for subsequent commands.

    Templates:
        Use --template to specify a pre-built template with tools installed.

    Examples:
        sbx init
        sbx init --template fullstack-vue-fastapi-node22 --timeout 43200 --name my-workflow
    """
    try:
        from .modules import sandbox as sbx_module

        console.print("[yellow]Initializing new sandbox...[/yellow]")
        if template:
            console.print(f"[dim]Template: {template}[/dim]")

        # Parse env vars
        envs = {}
        for e in env:
            if "=" in e:
                key, value = e.split("=", 1)
                envs[key] = value

        # Add name to metadata if provided
        metadata = {}
        if name:
            metadata["name"] = name

        sbx = sbx_module.create_sandbox(
            template=template,
            timeout=timeout,
            envs=envs if envs else None,
            metadata=metadata if metadata else None,
        )

        console.print(f"\n[green]Sandbox created successfully![/green]")
        console.print(f"\n[cyan]Sandbox ID:[/cyan] {sbx.sandbox_id}")
        if name:
            console.print(f"[cyan]Name:[/cyan] {name}")
        if template:
            console.print(f"[dim]Template: {template}[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    cli()
