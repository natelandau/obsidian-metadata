"""Obsidian vault representation."""

import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
import json
import rich.repr
from rich import box
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

from obsidian_metadata._config.config import Config, VaultConfig
from obsidian_metadata._utils import alerts
from obsidian_metadata._utils.alerts import logger as log
from obsidian_metadata.models import InsertLocation, MetadataType, Note, VaultMetadata


@dataclass
class VaultFilter:
    """Vault filters."""

    path_filter: str = None
    key_filter: str = None
    value_filter: str = None
    tag_filter: str = None


@rich.repr.auto
class Vault:
    """Representation of the Obsidian vault.

    Attributes:
        vault (Path): Path to the vault.
        dry_run (bool): Whether to perform a dry run.
        backup_path (Path): Path to the backup of the vault.
        notes (list[Note]): List of all notes in the vault.
    """

    def __init__(
        self,
        config: VaultConfig,
        dry_run: bool = False,
        filters: list[VaultFilter] = [],
    ):
        self.config = config.config
        self.vault_path: Path = config.path
        self.name = self.vault_path.name
        self.insert_location: InsertLocation = self._find_insert_location()
        self.dry_run: bool = dry_run
        self.backup_path: Path = self.vault_path.parent / f"{self.vault_path.name}.bak"
        self.exclude_paths: list[Path] = []
        self.metadata = VaultMetadata()
        for p in config.exclude_paths:
            self.exclude_paths.append(Path(self.vault_path / p))

        self.filters = filters
        self.all_note_paths = self._find_markdown_notes()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Processing notes...", total=None)
            self.all_notes: list[Note] = [
                Note(note_path=p, dry_run=self.dry_run) for p in self.all_note_paths
            ]
            self.notes_in_scope = self._filter_notes()

        self._rebuild_vault_metadata()

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover
        """Define rich representation of Vault."""
        yield "vault_path", self.vault_path
        yield "dry_run", self.dry_run
        yield "backup_path", self.backup_path
        yield "num_notes", len(self.all_notes)
        yield "num_notes_in_scope", len(self.notes_in_scope)
        yield "exclude_paths", self.exclude_paths

    def _filter_notes(self) -> list[Note]:
        """Filter notes by path and metadata using the filters defined in self.filters.

        Returns:
            list[Note]: List of notes matching the filters.
        """
        notes_list = self.all_notes.copy()

        for _filter in self.filters:
            if _filter.path_filter is not None:
                notes_list = [
                    n
                    for n in notes_list
                    if re.search(_filter.path_filter, str(n.note_path.relative_to(self.vault_path)))
                ]

            if _filter.tag_filter is not None:
                notes_list = [n for n in notes_list if n.contains_inline_tag(_filter.tag_filter)]

            if _filter.key_filter is not None and _filter.value_filter is not None:
                notes_list = [
                    n
                    for n in notes_list
                    if n.contains_metadata(_filter.key_filter, _filter.value_filter)
                ]
            if _filter.key_filter is not None and _filter.value_filter is None:
                notes_list = [n for n in notes_list if n.contains_metadata(_filter.key_filter)]

        return notes_list

    def _find_insert_location(self) -> InsertLocation:
        """Find the insert location for a note.

        Returns:
            InsertLocation: Insert location for the note.
        """
        if self.config["insert_location"].upper() == "TOP":
            return InsertLocation.TOP
        elif self.config["insert_location"].upper() == "HEADER":
            return InsertLocation.AFTER_TITLE
        elif self.config["insert_location"].upper() == "BOTTOM":
            return InsertLocation.BOTTOM
        else:
            return InsertLocation.BOTTOM

    def _find_markdown_notes(self) -> list[Path]:
        """Build list of all markdown files in the vault.

        Returns:
            list[Path]: List of paths to all matching files in the vault.

        """
        return [
            p.resolve()
            for p in self.vault_path.glob("**/*")
            if p.suffix in [".md", ".MD", ".markdown", ".MARKDOWN"]
            and not any(item in p.parents for item in self.exclude_paths)
        ]

    def _rebuild_vault_metadata(self) -> None:
        """Rebuild vault metadata."""
        self.metadata = VaultMetadata()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Processing notes...", total=None)
            for _note in self.notes_in_scope:
                self.metadata.index_metadata(
                    area=MetadataType.FRONTMATTER, metadata=_note.frontmatter.dict
                )
                self.metadata.index_metadata(
                    area=MetadataType.INLINE, metadata=_note.inline_metadata.dict
                )
                self.metadata.index_metadata(
                    area=MetadataType.TAGS,
                    metadata=_note.inline_tags.list,
                )

    def add_metadata(
        self,
        area: MetadataType,
        key: str = None,
        value: str | list[str] = None,
        location: InsertLocation = None,
    ) -> int:
        """Add metadata to all notes in the vault which do not already contain it.

        Args:
            area (MetadataType): Area of metadata to add to.
            key (str): Key to add.
            value (str|list, optional): Value to add.
            location (InsertLocation, optional): Location to insert metadata. (Defaults to `vault.config.insert_location`)

        Returns:
            int: Number of notes updated.
        """
        if location is None:
            location = self.insert_location

        num_changed = 0

        for _note in self.notes_in_scope:
            if _note.add_metadata(area=area, key=key, value=value, location=location):
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

    def commit_changes(self) -> None:
        """Commit changes by writing to disk."""
        log.debug("Writing changes to vault...")
        if self.dry_run:
            for _note in self.notes_in_scope:
                if _note.has_changes():
                    alerts.dryrun(
                        f"writing changes to {_note.note_path.relative_to(self.vault_path)}"
                    )
            return

        for _note in self.notes_in_scope:
            if _note.has_changes():
                log.trace(f"writing to {_note.note_path}")
                _note.write()

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

        for _note in self.notes_in_scope:
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

        for _note in self.notes_in_scope:
            if _note.delete_metadata(key, value):
                num_changed += 1

        if num_changed > 0:
            self._rebuild_vault_metadata()

        return num_changed

    def export_metadata(self, path: str, format: str = "csv") -> None:
        """Write metadata to a csv file.

        Args:
            path (Path): Path to write csv file to.
            export_as (str, optional): Export as 'csv' or 'json'. Defaults to "csv".
        """
        export_file = Path(path).expanduser().resolve()

        match format:  # noqa: E999
            case "csv":
                with open(export_file, "w", encoding="UTF8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Metadata Type", "Key", "Value"])

                    for key, value in self.metadata.frontmatter.items():
                        if isinstance(value, list):
                            if len(value) > 0:
                                for v in value:
                                    writer.writerow(["frontmatter", key, v])
                            else:
                                writer.writerow(["frontmatter", key, v])

                    for key, value in self.metadata.inline_metadata.items():
                        if isinstance(value, list):
                            if len(value) > 0:
                                for v in value:
                                    writer.writerow(["inline_metadata", key, v])
                            else:
                                writer.writerow(["frontmatter", key, v])
                    for tag in self.metadata.tags:
                        writer.writerow(["tags", "", f"{tag}"])
            case "json":
                dict_to_dump = {
                    "frontmatter": self.metadata.dict,
                    "inline_metadata": self.metadata.inline_metadata,
                    "tags": self.metadata.tags,
                }

                with open(export_file, "w", encoding="UTF8") as f:
                    json.dump(dict_to_dump, f, indent=4, ensure_ascii=False, sort_keys=True)

    def get_changed_notes(self) -> list[Note]:
        """Returns a list of notes that have changes.

        Returns:
            list[Note]: List of notes that have changes.
        """
        changed_notes = []
        for _note in self.notes_in_scope:
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
        table.add_row("Notes in scope", str(len(self.notes_in_scope)))
        table.add_row("Notes excluded from scope", str(self.num_excluded_notes()))
        table.add_row("Active filters", str(len(self.filters)))
        table.add_row("Notes with changes", str(len(self.get_changed_notes())))

        Console().print(table)

    def list_editable_notes(self) -> None:
        """Print a list of notes within the scope that are being edited."""
        table = Table(title="Notes in current scope", show_header=False, box=box.HORIZONTALS)
        for _n, _note in enumerate(self.notes_in_scope, start=1):
            table.add_row(str(_n), str(_note.note_path.relative_to(self.vault_path)))
        Console().print(table)

    def num_excluded_notes(self) -> int:
        """Count number of excluded notes."""
        return len(self.all_notes) - len(self.notes_in_scope)

    def rename_inline_tag(self, old_tag: str, new_tag: str) -> int:
        """Rename an inline tag in the vault.

        Args:
            old_tag (str): Old tag name.
            new_tag (str): New tag name.

        Returns:
            int: Number of notes that had inline tags renamed.
        """
        num_changed = 0

        for _note in self.notes_in_scope:
            if _note.rename_inline_tag(old_tag, new_tag):
                num_changed += 1

        if num_changed > 0:
            self._rebuild_vault_metadata()

        return num_changed

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

        for _note in self.notes_in_scope:
            if _note.rename_metadata(key, value_1, value_2):
                num_changed += 1

        if num_changed > 0:
            self._rebuild_vault_metadata()

        return num_changed

    def transpose_metadata(
        self,
        begin: MetadataType,
        end: MetadataType,
        key: str = None,
        value: str | list[str] = None,
        location: InsertLocation = None,
    ) -> int:
        """Transpose metadata from one type to another.

        Args:
            begin (MetadataType): Metadata type to transpose from.
            end (MetadataType): Metadata type to transpose to.
            key (str, optional): Key to transpose. Defaults to None.
            value (str, optional): Value to transpose. Defaults to None.
            location (InsertLocation, optional): Location to insert metadata. (Defaults to `vault.config.insert_location`)

        Returns:
            int: Number of notes that had metadata transposed.
        """
        if location is None:
            location = self.insert_location

        num_changed = 0
        for _note in self.notes_in_scope:
            if _note.transpose_metadata(
                begin=begin,
                end=end,
                key=key,
                value=value,
                location=location,
            ):
                num_changed += 1

        if num_changed > 0:
            self._rebuild_vault_metadata()

        return num_changed
