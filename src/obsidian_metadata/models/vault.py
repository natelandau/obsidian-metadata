"""Obsidian vault representation."""

import re
import shutil
from pathlib import Path

import rich.repr
from rich import box
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

from obsidian_metadata._config import VaultConfig
from obsidian_metadata._utils import alerts
from obsidian_metadata._utils.alerts import logger as log
from obsidian_metadata.models import MetadataType, Note, VaultMetadata


@rich.repr.auto
class Vault:
    """Representation of the Obsidian vault.

    Attributes:
        vault (Path): Path to the vault.
        dry_run (bool): Whether to perform a dry run.
        backup_path (Path): Path to the backup of the vault.
        notes (list[Note]): List of all notes in the vault.
    """

    def __init__(self, config: VaultConfig, dry_run: bool = False, path_filter: str = None):
        self.vault_path: Path = config.path
        self.dry_run: bool = dry_run
        self.backup_path: Path = self.vault_path.parent / f"{self.vault_path.name}.bak"
        self.exclude_paths: list[Path] = []
        self.metadata = VaultMetadata()
        for p in config.exclude_paths:
            self.exclude_paths.append(Path(self.vault_path / p))

        self.path_filter = path_filter
        self.note_paths = self._find_markdown_notes(path_filter)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Processing notes...", total=None)
            self.notes: list[Note] = [
                Note(note_path=p, dry_run=self.dry_run) for p in self.note_paths
            ]

        self._rebuild_vault_metadata()

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover
        """Define rich representation of Vault."""
        yield "vault_path", self.vault_path
        yield "dry_run", self.dry_run
        yield "backup_path", self.backup_path
        yield "num_notes", self.num_notes()
        yield "exclude_paths", self.exclude_paths

    def _find_markdown_notes(self, path_filter: str = None) -> list[Path]:
        """Build list of all markdown files in the vault.

        Args:
            path_filter (str, optional): Regex to filter notes by path.

        Returns:
            list[Path]: List of paths to all matching files in the vault.

        """
        notes_list = [
            p.resolve()
            for p in self.vault_path.glob("**/*")
            if p.suffix in [".md", ".MD", ".markdown", ".MARKDOWN"]
            and not any(item in p.parents for item in self.exclude_paths)
        ]

        if path_filter is not None:
            notes_list = [
                p for p in notes_list if re.search(path_filter, str(p.relative_to(self.vault_path)))
            ]

        return notes_list

    def _rebuild_vault_metadata(self) -> None:
        """Rebuild vault metadata."""
        self.metadata = VaultMetadata()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Processing notes...", total=None)
            for _note in self.notes:
                self.metadata.add_metadata(_note.frontmatter.dict)
                self.metadata.add_metadata(_note.inline_metadata.dict)
                self.metadata.add_metadata({_note.inline_tags.metadata_key: _note.inline_tags.list})

    def add_metadata(self, area: MetadataType, key: str, value: str | list[str] = None) -> int:
        """Add metadata to all notes in the vault.

        Args:
            area (MetadataType): Area of metadata to add to.
            key (str): Key to add.
            value (str|list, optional): Value to add.

        Returns:
            int: Number of notes updated.
        """
        num_changed = 0

        for _note in self.notes:
            if _note.add_metadata(area, key, value):
                num_changed += 1

        if num_changed > 0:
            self._rebuild_vault_metadata()

        return num_changed

    def backup(self) -> None:
        """Backup the vault."""
        log.debug("Backing up vault")
        if self.dry_run:
            alerts.dryrun(f"Backup up vault to: {self.backup_path}")
            print("\n")
            return

        try:
            shutil.copytree(self.vault_path, self.backup_path)

        except FileExistsError:  # pragma: no cover
            log.debug("Backup already exists")
            if not Confirm.ask("Vault backup already exists. Overwrite?"):
                alerts.info("Exiting backup not overwritten.")
                return

            log.debug("Overwriting backup")
            shutil.rmtree(self.backup_path)
            shutil.copytree(self.vault_path, self.backup_path)

        alerts.success(f"Vault backed up to: {self.backup_path}")

    def contains_inline_tag(self, tag: str, is_regex: bool = False) -> bool:
        """Check if vault contains the given inline tag.

        Args:
            tag (str): Tag to check for.
            is_regex (bool, optional): Whether to use regex to match tag.

        Returns:
            bool: True if tag is found in vault.
        """
        return any(_note.contains_inline_tag(tag) for _note in self.notes)

    def contains_metadata(self, key: str, value: str = None, is_regex: bool = False) -> bool:
        """Check if vault contains the given metadata.

        Args:
            key (str): Key to check for. If value is None, will check vault for key.
            value (str, optional): Value to check for.
            is_regex (bool, optional): Whether to use regex to match key/value.

        Returns:
            bool: True if tag is found in vault.
        """
        if value is None:
            return self.metadata.contains(key, is_regex=is_regex)

        return self.metadata.contains(key, value, is_regex=is_regex)

    def delete_backup(self) -> None:
        """Delete the vault backup."""
        log.debug("Deleting vault backup")
        if self.backup_path.exists() and self.dry_run is False:
            shutil.rmtree(self.backup_path)
            alerts.success("Backup deleted")
        elif self.backup_path.exists() and self.dry_run is True:
            alerts.dryrun("Delete backup")
        else:
            alerts.info("No backup found")

    def delete_inline_tag(self, tag: str) -> int:
        """Delete an inline tag in the vault.

        Args:
            tag (str): Tag to delete.

        Returns:
            int: Number of notes that had tag deleted.
        """
        num_changed = 0

        for _note in self.notes:
            if _note.delete_inline_tag(tag):
                num_changed += 1

        if num_changed > 0:
            self._rebuild_vault_metadata()

        return num_changed

    def delete_metadata(self, key: str, value: str = None) -> int:
        """Delete metadata in the vault.

        Args:
            key (str): Key to delete. Regex is supported
            value (str, optional): Value to delete. Regex is supported

        Returns:
            int: Number of notes that had metadata deleted.
        """
        num_changed = 0

        for _note in self.notes:
            if _note.delete_metadata(key, value):
                num_changed += 1

        if num_changed > 0:
            self._rebuild_vault_metadata()

        return num_changed

    def get_changed_notes(self) -> list[Note]:
        """Returns a list of notes that have changes.

        Returns:
            list[Note]: List of notes that have changes.
        """
        changed_notes = []
        for _note in self.notes:
            if _note.has_changes():
                changed_notes.append(_note)

        changed_notes = sorted(changed_notes, key=lambda x: x.note_path)
        return changed_notes

    def info(self) -> None:
        """Print information about the vault."""
        table = Table(show_header=False)
        table.add_row("Vault", str(self.vault_path))
        if self.backup_path.exists():
            table.add_row("Backup path", str(self.backup_path))
        else:
            table.add_row("Backup", "None")
        table.add_row("Notes in scope", str(self.num_notes()))
        table.add_row("Notes excluded from scope", str(self.num_excluded_notes()))
        table.add_row("Active path filter", str(self.path_filter))
        table.add_row("Notes with updates", str(len(self.get_changed_notes())))

        Console().print(table)

    def list_editable_notes(self) -> None:
        """Print a list of notes within the scope that are being edited."""
        table = Table(title="Notes in current scope", show_header=False, box=box.HORIZONTALS)
        for _n, _note in enumerate(self.notes, start=1):
            table.add_row(str(_n), str(_note.note_path.relative_to(self.vault_path)))
        Console().print(table)

    def num_excluded_notes(self) -> int:
        """Count number of excluded notes."""
        excluded_notes = [
            p.resolve()
            for p in self.vault_path.glob("**/*")
            if p.suffix in [".md", ".MD", ".markdown", ".MARKDOWN"] and p not in self.note_paths
        ]
        return len(excluded_notes)

    def num_notes(self) -> int:
        """Number of notes in the vault.

        Returns:
            int: Number of notes in the vault.
        """
        return len(self.notes)

    def rename_metadata(self, key: str, value_1: str, value_2: str = None) -> int:
        """Renames a key or key-value pair in the note's metadata.

        If no value is provided, will rename an entire key.

        Args:
            key (str): Key to rename.
            value_1 (str): Value to rename or new name of key if no value_2 is provided.
            value_2 (str, optional): New value.

        Returns:
            int: Number of notes that had metadata renamed.
        """
        num_changed = 0

        for _note in self.notes:
            if _note.rename_metadata(key, value_1, value_2):
                num_changed += 1

        if num_changed > 0:
            self._rebuild_vault_metadata()

        return num_changed

    def rename_inline_tag(self, old_tag: str, new_tag: str) -> int:
        """Rename an inline tag in the vault.

        Args:
            old_tag (str): Old tag name.
            new_tag (str): New tag name.

        Returns:
            int: Number of notes that had inline tags renamed.
        """
        num_changed = 0

        for _note in self.notes:
            if _note.rename_inline_tag(old_tag, new_tag):
                num_changed += 1

        if num_changed > 0:
            self._rebuild_vault_metadata()

        return num_changed

    def write(self) -> None:
        """Write changes to the vault."""
        log.debug("Writing changes to vault...")
        if self.dry_run is False:
            for _note in self.notes:
                log.trace(f"writing to {_note.note_path}")
                _note.write()
