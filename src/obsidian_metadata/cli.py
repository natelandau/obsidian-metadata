"""obsidian-metadata CLI."""


from pathlib import Path
from typing import Optional

import questionary
import typer
from rich import print

from obsidian_metadata._config import Config
from obsidian_metadata._utils import (
    alerts,
    clear_screen,
    docstring_parameter,
    version_callback,
)
from obsidian_metadata.models import Application

app = typer.Typer(add_completion=False, no_args_is_help=True, rich_markup_mode="rich")

typer.rich_utils.STYLE_HELPTEXT = ""

HELP_TEXT = """
"""


@app.command()
@docstring_parameter(__package__)
def main(
    vault_path: Path = typer.Option(
        None,
        help="Path to Obsidian vault",
        show_default=False,
    ),
    config_file: Path = typer.Option(
        Path(Path.home() / f".{__package__}.toml"),
        help="Specify a custom path to a configuration file",
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
    version: Optional[bool] = typer.Option(
        None, "--version", help="Print version and exit", callback=version_callback, is_eager=True
    ),
) -> None:
    r"""A script to make batch updates to metadata in an Obsidian vault. No changes are made to the Vault until they are explicitly committed.

    [bold] [/]
    [bold underline]It is strongly recommended that you back up your vault prior to committing changes.[/] This script makes changes directly to the markdown files in your vault. Once the changes are committed, there is no ability to recreate the original information unless you have a backup.  Follow the instructions in the script to create a backup of your vault if needed.  The author of this script is not responsible for any data loss that may occur. Use at your own risk.

    [bold underline]Configuration:[/]
    Configuration is specified in a configuration file. On First run, this file will be created at [tan]~/.{0}.env[/]. Any options specified on the command line will override the configuration file.

    [bold underline]Usage:[/]
    [tan]Obsidian-metadata[/] provides a menu of sub-commands.

    [bold underline]Vault Actions[/]
        • Backup:        Create a backup of the vault.
        • Delete Backup: Delete a backup of the vault.

    [bold underline]Inspect Metadata[/]
        • View all metadata in the vault

    [bold underline]Filter Notes in Scope[/]
    Limit the scope of notes to be processed with a regex.
        • Apply regex:          Set a regex to limit scope
        • List notes in scope:  List notes that will be processed.

    [bold underline]Add Metadata[/]
        • Add metadata to the frontmatter
        • [dim]Add to inline metadata (Not yet implemented)[/]
        • [dim]Add to inline tag (Not yet implemented)[/]

    [bold underline]Rename Metadata[/]
        • Rename a key
        • Rename a value
        • rename an inline tag

    [bold underline]Delete Metadata[/]
        • Delete a key and associated values
        • Delete a value from a key
        • Delete an inline tag

    [bold underline]Review Changes[/]
        • View a diff of the changes that will be made

    [bold underline]Commit Changes[/]
        • Commit changes to the vault

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
    print(banner)

    config: Config = Config(config_path=config_file, vault_path=vault_path)
    if len(config.vaults) == 0:
        typer.echo("No vaults configured. Exiting.")
        raise typer.Exit(1)

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

    application.application_main()


if __name__ == "__main__":
    app()
