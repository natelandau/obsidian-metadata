#!/usr/bin/env python
"""Script to update the pyproject.toml file with the latest versions of the dependencies."""
from pathlib import Path
from textwrap import wrap

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore [no-redef]

import sh
from rich.console import Console

console = Console()


def dryrun(msg: str) -> None:
    """Print a message if the dry run flag is set.

    Args:
        msg: Message to print
    """
    console.print(f"[cyan]DRYRUN   | {msg}[/cyan]")


def success(msg: str) -> None:
    """Print a success message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"[green]SUCCESS  | {msg}[/green]")


def warning(msg: str) -> None:
    """Print a warning message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"[yellow]WARNING  | {msg}[/yellow]")


def error(msg: str) -> None:
    """Print an error message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"[red]ERROR    | {msg}[/red]")


def notice(msg: str) -> None:
    """Print a notice message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"[bold]NOTICE   | {msg}[/bold]")


def info(msg: str) -> None:
    """Print a notice message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"INFO     | {msg}")


def usage(msg: str, width: int = 80) -> None:
    """Print a usage message without using logging.

    Args:
        msg: Message to print
        width (optional): Width of the message
    """
    for _n, line in enumerate(wrap(msg, width=width)):
        if _n == 0:
            console.print(f"[dim]USAGE    | {line}")
        else:
            console.print(f"[dim]         | {line}")


def debug(msg: str) -> None:
    """Print a debug message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"[blue]DEBUG    | {msg}[/blue]")


def dim(msg: str) -> None:
    """Print a message in dimmed color.

    Args:
        msg: Message to print
    """
    console.print(f"[dim]{msg}[/dim]")


# Load the pyproject.toml file
pyproject = Path(__file__).parents[1] / "pyproject.toml"

if not pyproject.exists():
    console.print("pyproject.toml file not found")
    raise SystemExit(1)

with pyproject.open("rb") as f:
    try:
        data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise SystemExit(1) from e


# Get the latest versions of all dependencies
info("Getting latest versions of dependencies...")
packages: dict = {}
for line in sh.poetry("--no-ansi", "show", "--outdated").splitlines():
    package, current, latest = line.split()[:3]
    packages[package] = {"current_version": current, "new_version": latest}

if not packages:
    success("All dependencies are up to date")
    raise SystemExit(0)


dependencies = data["tool"]["poetry"]["dependencies"]
groups = data["tool"]["poetry"]["group"]

for p in dependencies:
    if p in packages:
        notice(
            f"Updating {p} from {packages[p]['current_version']} to {packages[p]['new_version']}"
        )
        sh.poetry("add", f"{p}@latest", _fg=True)


for group in groups:
    for p in groups[group]["dependencies"]:
        if p in packages:
            notice(
                f"Updating {p} from {packages[p]['current_version']} to {packages[p]['new_version']}"
            )
            sh.poetry("add", f"{p}@latest", "--group", group, _fg=True)

sh.poetry("update", _fg=True)
success("All dependencies are up to date")
raise SystemExit(0)
