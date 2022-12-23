"""Obsidian vault representation."""
import shutil
from pathlib import Path

import typer
from pydantic import BaseModel
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from obsidian_frontmatter._utils import alerts
from obsidian_frontmatter._utils.alerts import logger as log


class Vault(BaseModel):
    """Representation of the Obsidian vault."""

    vault: Path

    @property
    def notes(self) -> list[Path]:
        """Build list of all markdown files in the vault."""
        log.debug("Indexing vault")
        return [
            p.resolve()
            for p in self.vault.glob("**/*")
            if p.suffix in [".md", ".MD", ".markdown", ".MARKDOWN"]
        ]

    @property
    def backup_path(self) -> Path:
        """Path to the vault backup."""
        return Path(self.vault.parent / f"{self.vault.name}.bak")

    def num_notes(self) -> int:
        """Number of notes in the vault.

        Returns:
            int: Number of notes in the vault.
        """
        return len(self.notes)

    def backup(self) -> None:
        """Backup the vault."""
        log.debug("Backing up vault")

        try:
            shutil.copytree(self.vault, self.backup_path)

        except FileExistsError:
            log.debug("Backup already exists")
            if Confirm.ask("Vault backup already exists. Overwrite?"):
                log.debug("Overwriting backup")
                shutil.rmtree(self.backup_path)
                shutil.copytree(self.vault, self.backup_path)
            else:
                alerts.info("Exiting. Backup not overwritten.")
                raise typer.Exit(code=1)

        alerts.success(f"Vault backed up to: {self.backup_path}")

    def delete_backup(self) -> None:
        """Delete the vault backup."""
        log.debug("Deleting vault backup")
        if self.backup_path.exists():
            shutil.rmtree(self.backup_path)
            alerts.success("Backup deleted")
        else:
            alerts.info("No backup found")

    def info(self) -> None:
        """Print information about the vault."""
        log.debug("Printing vault info")
        table = Table(title="Vault Info", show_header=False)
        table.add_row("Vault", str(self.vault))
        table.add_row("Number of notes", str(self.num_notes()))
        if self.backup_path.exists():
            table.add_row("Backup path", str(self.backup_path))
        else:
            table.add_row("Backup", "None")

        console = Console()
        console.print(table)
