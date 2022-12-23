"""obsidian-frontmatter CLI."""

import inspect
from pathlib import Path
from typing import Any, Optional

import typer
from rich import print

from obsidian_frontmatter.__version__ import __version__
from obsidian_frontmatter._utils import (
    Configuration,
    Vault,
    alerts,
    ask_for_vault,
    docstring_parameter,
)
from obsidian_frontmatter._utils.alerts import logger as log

app = typer.Typer(add_completion=False, no_args_is_help=True, rich_markup_mode="rich")

typer.rich_utils.STYLE_HELPTEXT = ""

state: dict[str, Any] = {}


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        print(f"{__package__}: v{__version__}")
        raise typer.Exit()


@app.command(short_help="Configure your Obsidian vault")
def vault(
    backup: bool = typer.Option(
        False,
        "--backup",
        help="Create a backup of the vault",
    ),
    delete_backup: bool = typer.Option(
        False,
        "--delete-backup",
        help="Delete the vault backup",
    ),
) -> None:
    """Configure and work with the vault."""
    config = state["configuration"]
    log.trace(f"Configuration: {config}")

    vault = Vault(vault=config.vault_path)

    if backup:
        vault.backup()
    if delete_backup:
        vault.delete_backup()
    else:
        vault.info()


@app.callback()
@docstring_parameter(__package__)
def main(
    vault_path: Path = typer.Option(
        None,
        help="Path to Obsidian vault",
        show_default=False,
    ),
    config_file: Path = typer.Option(
        Path(Path.home() / f".{__package__}.env"),
        help="Specify a custom path to a configuration file",
        show_default=False,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Dry run - don't actually change anything",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force changes without prompting for confirmation. Use with caution!",
        show_default=True,
    ),
    log_file: Path = typer.Option(
        Path(Path.home() / "logs" / "obsidian_frontmatter.log"),
        help="Path to log file",
        show_default=True,
        dir_okay=False,
        file_okay=True,
        exists=False,
    ),
    log_to_file: bool = typer.Option(
        False,
        "--log-to-file",
        help="Log to file",
        show_default=True,
    ),
    verbosity: int = typer.Option(
        1,
        "-v",
        "--verbose",
        show_default=False,
        help="""Set verbosity level (0=WARN, 1=INFO, 2=DEBUG, 3=TRACE)""",
        count=True,
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", help="Print version and exit", callback=version_callback, is_eager=True
    ),
) -> Configuration:
    """Update frontmatter within an Obsidian vault.

    \n
    \nConfiguration is specified in an configuration file. On First run, this file will be created at [tan]~/.{0}.env[/]. Any options specified on the command line will override the configuration file.
    """  # noqa: D301
    # Instantiate logger
    alerts.LoggerManager(  # pragma: no cover
        log_file,
        verbosity,
        log_to_file,
    )

    if not config_file.exists():

        if vault_path is None:
            vault_path = ask_for_vault()  # pragma: no cover

        config_content = f"""
        vault_path={vault_path}
        """

        config_file.touch()
        config_file.write_text(inspect.cleandoc(config_content))
        print(f"Created configuration file: {config_file}")

    if vault_path is None:
        configuration = Configuration(
            _env_file=config_file,
            dry_run=dry_run,
            force=force,
            log_file=log_file,
            log_to_file=log_to_file,
            verbosity=verbosity,
        )
    else:
        configuration = Configuration(
            _env_file=config_file,
            dry_run=dry_run,
            force=force,
            log_file=log_file,
            log_to_file=log_to_file,
            verbosity=verbosity,
            vault_path=vault_path,
        )

    log.trace(f"Configuration: {configuration}")

    state["configuration"] = configuration
    return configuration


if __name__ == "__main__":
    app()
