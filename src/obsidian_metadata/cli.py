"""obsidian-metadata CLI."""

from pathlib import Path
from typing import Optional

import questionary
import typer

from obsidian_metadata._config import Config
from obsidian_metadata._utils import (
    alerts,
    clear_screen,
    docstring_parameter,
    version_callback,
)
from obsidian_metadata._utils.console import console
from obsidian_metadata.models import Application

app = typer.Typer(add_completion=False, no_args_is_help=True, rich_markup_mode="rich")

typer.rich_utils.STYLE_HELPTEXT = ""

HELP_TEXT = """
"""


@app.command()
@docstring_parameter(__package__)
def main(
    config_file: Path = typer.Option(
        Path(Path.home() / f".{__package__}.toml"),
        help="Specify a custom path to a configuration file",
        show_default=False,
    ),
    export_csv: Path = typer.Option(
        None,
        help="Exports all metadata to a specified CSV file and exits.",
        show_default=False,
        dir_okay=False,
        file_okay=True,
    ),
    export_json: Path = typer.Option(
        None,
        help="Exports all metadata to a specified JSON file and exits.",
        show_default=False,
        dir_okay=False,
        file_okay=True,
    ),
    export_template: Path = typer.Option(
        None,
        help="Exports all notes and their metadata to a specified CSV file and exits. Use to create a template for batch updates.",
        show_default=False,
        dir_okay=False,
        file_okay=True,
    ),
    import_csv: Path = typer.Option(
        None,
        help="Import a CSV file with bulk updates to metadata.",
        show_default=False,
        dir_okay=False,
        file_okay=True,
    ),
    vault_path: Path = typer.Option(
        None,
        help="Path to Obsidian vault",
        show_default=False,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Dry run - don't actually change anything",
    ),
    log_file: Path = typer.Option(
        Path(Path.home() / "logs" / "obsidian_metadata.log"),
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
        0,
        "-v",
        "--verbose",
        show_default=False,
        help="""Set verbosity level (0=WARN, 1=INFO, 2=DEBUG, 3=TRACE)""",
        count=True,
    ),
    version: Optional[bool] = typer.Option(  # noqa: ARG001
        None, "--version", help="Print version and exit", callback=version_callback, is_eager=True
    ),
) -> None:
    r"""Make batch updates to metadata in an Obsidian vault. No changes are made to the Vault until they are explicitly committed.

    [bold] [/]
    [bold underline]It is strongly recommended that you back up your vault prior to committing changes.[/] This script makes changes directly to the markdown files in your vault. Once the changes are committed, there is no ability to recreate the original information unless you have a backup.  Follow the instructions in the script to create a backup of your vault if needed.  The author of this script is not responsible for any data loss that may occur. Use at your own risk.

    [bold underline]Configuration:[/]
    Configuration is specified in a configuration file. On First run, this file will be created at [tan]~/.{0}.env[/]. Any options specified on the command line will override the configuration file.

    Full usage information is available at https://github.com/natelandau/obsidian-metadata

    """
    # Instantiate logger
    alerts.LoggerManager(  # pragma: no cover
        log_file,
        verbosity,
        log_to_file,
    )

    banner = r"""
   ___  _         _     _ _
  / _ \| |__  ___(_) __| (_) __ _ _ __
 | | | | '_ \/ __| |/ _` | |/ _` | '_ \
 | |_| | |_) \__ \ | (_| | | (_| | | | |
  \___/|_.__/|___/_|\__,_|_|\__,_|_| |_|
 |  \/  | ___| |_ __ _  __| | __ _| |_ __ _
 | |\/| |/ _ \ __/ _` |/ _` |/ _` | __/ _` |
 | |  | |  __/ || (_| | (_| | (_| | || (_| |
 |_|  |_|\___|\__\__,_|\__,_|\__,_|\__\__,_|
"""
    clear_screen()
    console.print(banner)

    config: Config = Config(config_path=config_file, vault_path=vault_path)
    if len(config.vaults) == 0:
        typer.echo("No vaults configured. Exiting.")
        raise typer.BadParameter("No vaults configured. Exiting.")

    if len(config.vaults) == 1:
        application = Application(dry_run=dry_run, config=config.vaults[0])
    else:
        vault_names = [vault.name for vault in config.vaults]
        vault_name = questionary.select(
            "Select a vault to process:",
            choices=vault_names,
        ).ask()
        if vault_name is None:
            raise typer.Exit(code=1)

        vault_to_use = next(vault for vault in config.vaults if vault.name == vault_name)
        application = Application(dry_run=dry_run, config=vault_to_use)

    if export_json is not None:
        path = Path(export_json).expanduser().resolve()
        application.noninteractive_export_json(path)
        raise typer.Exit(code=0)
    if export_csv is not None:
        path = Path(export_json).expanduser().resolve()
        application.noninteractive_export_csv(path)
        raise typer.Exit(code=0)
    if export_template is not None:
        path = Path(export_template).expanduser().resolve()
        application.noninteractive_export_template(path)
        raise typer.Exit(code=0)
    if import_csv is not None:
        path = Path(import_csv).expanduser().resolve()
        application.noninteractive_bulk_import(path)
        raise typer.Exit(code=0)

    application.application_main()


if __name__ == "__main__":
    app()
