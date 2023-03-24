"""Questions for the cli."""


from pathlib import Path
from typing import Any

import questionary
import typer
from rich import box
from rich.table import Table

from obsidian_metadata._config import VaultConfig
from obsidian_metadata._utils import alerts, validate_csv_bulk_imports
from obsidian_metadata._utils.console import console
from obsidian_metadata.models import InsertLocation, Vault, VaultFilter
from obsidian_metadata.models.enums import MetadataType
from obsidian_metadata.models.questions import Questions


class Application:
    """Questions for use in the cli.

    Contains methods which ask a series of questions to the user and return a dictionary with their answers.

    More info: https://questionary.readthedocs.io/en/stable/pages/advanced.html#create-questions-from-dictionaries
    """

    def __init__(self, config: VaultConfig, dry_run: bool) -> None:
        self.config = config
        self.dry_run = dry_run
        self.questions = Questions()
        self.filters: list[VaultFilter] = []

    def _load_vault(self) -> None:
        """Load the vault."""
        if len(self.filters) == 0:
            self.vault: Vault = Vault(config=self.config, dry_run=self.dry_run)
        else:
            self.vault = Vault(config=self.config, dry_run=self.dry_run, filters=self.filters)

        alerts.success(
            f"Loaded {len(self.vault.notes_in_scope)} notes from {len(self.vault.all_notes)} total notes"
        )
        self.questions = Questions(vault=self.vault)

    def application_main(self) -> None:
        """Questions for the main application."""
        self._load_vault()

        while True:
            self.vault.info()

            match self.questions.ask_application_main():
                case "vault_actions":
                    self.application_vault()
                case "export_metadata":
                    self.application_export_metadata()
                case "inspect_metadata":
                    self.application_inspect_metadata()
                case "import_from_csv":
                    self.application_import_csv()
                case "filter_notes":
                    self.application_filter()
                case "add_metadata":
                    self.application_add_metadata()
                case "rename_metadata":
                    self.application_rename_metadata()
                case "delete_metadata":
                    self.application_delete_metadata()
                case "reorganize_metadata":
                    self.application_reorganize_metadata()
                case "review_changes":
                    self.review_changes()
                case "commit_changes":
                    self.commit_changes()
                case _:
                    break

        console.print("Done!")

    def application_add_metadata(self) -> None:
        """Add metadata."""
        alerts.usage(
            "Add new metadata to your vault. Currently only supports adding to the frontmatter of a note."
        )

        area = self.questions.ask_area()
        match area:
            case MetadataType.FRONTMATTER | MetadataType.INLINE:
                key = self.questions.ask_new_key(question="Enter the key for the new metadata")
                if key is None:  # pragma: no cover
                    return

                value = self.questions.ask_new_value(
                    question="Enter the value for the new metadata"
                )
                if value is None:  # pragma: no cover
                    return

                num_changed = self.vault.add_metadata(
                    area=area, key=key, value=value, location=self.vault.insert_location
                )
                if num_changed == 0:  # pragma: no cover
                    alerts.warning("No notes were changed")
                    return

                alerts.success(f"Added metadata to {num_changed} notes")

            case MetadataType.TAGS:
                tag = self.questions.ask_new_tag()
                if tag is None:  # pragma: no cover
                    return

                num_changed = self.vault.add_metadata(
                    area=area, value=tag, location=self.vault.insert_location
                )

                if num_changed == 0:  # pragma: no cover
                    alerts.warning("No notes were changed")
                    return

                alerts.success(f"Added metadata to {num_changed} notes")
            case _:  # pragma: no cover
                return

    def application_delete_metadata(self) -> None:
        """Delete metadata."""
        alerts.usage("Delete either a key and all associated values, or a specific value.")

        choices = [
            questionary.Separator(),
            {"name": "Delete inline tag", "value": "delete_tag"},
            {"name": "Delete key", "value": "delete_key"},
            {"name": "Delete value", "value": "delete_value"},
            questionary.Separator(),
            {"name": "Back", "value": "back"},
        ]
        match self.questions.ask_selection(
            choices=choices, question="Select a metadata type to delete"
        ):
            case "delete_key":
                self.delete_key()
            case "delete_value":
                self.delete_value()
            case "delete_tag":
                self.delete_tag()
            case _:  # pragma: no cover
                return

    def application_rename_metadata(self) -> None:
        """Rename metadata."""
        alerts.usage("Select the type of metadata to rename.")

        choices = [
            questionary.Separator(),
            {"name": "Rename inline tag", "value": "rename_tag"},
            {"name": "Rename key", "value": "rename_key"},
            {"name": "Rename value", "value": "rename_value"},
            questionary.Separator(),
            {"name": "Back", "value": "back"},
        ]
        match self.questions.ask_selection(
            choices=choices, question="Select a metadata type to rename"
        ):
            case "rename_key":
                self.rename_key()
            case "rename_value":
                self.rename_value()
            case "rename_tag":
                self.rename_tag()
            case _:  # pragma: no cover
                return

    def application_filter(self) -> None:  # noqa: C901,PLR0911,PLR0912
        """Filter notes."""
        alerts.usage("Limit the scope of notes to be processed with one or more filters.")

        choices = [
            questionary.Separator(),
            {"name": "Apply new regex path filter", "value": "apply_path_filter"},
            {"name": "Apply new metadata filter", "value": "apply_metadata_filter"},
            {"name": "Apply new in-text tag filter", "value": "apply_tag_filter"},
            {"name": "List and clear filters", "value": "list_filters"},
            {"name": "List notes in scope", "value": "list_notes"},
            questionary.Separator(),
            {"name": "Back", "value": "back"},
        ]
        while True:
            match self.questions.ask_selection(choices=choices, question="Select an action"):
                case "apply_path_filter":
                    path = self.questions.ask_filter_path()
                    if path is None or not path:  # pragma: no cover
                        return

                    self.filters.append(VaultFilter(path_filter=path))
                    self._load_vault()

                case "apply_metadata_filter":
                    key = self.questions.ask_existing_key()
                    if key is None:  # pragma: no cover
                        return

                    questions2 = Questions(vault=self.vault, key=key)
                    value = questions2.ask_existing_value(
                        question="Enter the value for the metadata filter",
                    )
                    if value is None:  # pragma: no cover
                        return
                    if not value:
                        self.filters.append(VaultFilter(key_filter=key))
                    else:
                        self.filters.append(VaultFilter(key_filter=key, value_filter=value))
                    self._load_vault()

                case "apply_tag_filter":
                    tag = self.questions.ask_existing_tag()
                    if tag is None or not tag:
                        return

                    self.filters.append(VaultFilter(tag_filter=tag))
                    self._load_vault()

                case "list_filters":
                    if len(self.filters) == 0:
                        alerts.notice("No filters have been applied")
                        return

                    console.print("")
                    table = Table(
                        "Opt",
                        "Filter",
                        "Type",
                        title="Current Filters",
                        show_header=False,
                        box=box.HORIZONTALS,
                    )
                    for _n, _filter in enumerate(self.filters, start=1):
                        if _filter.path_filter is not None:
                            table.add_row(
                                str(_n),
                                f"Path regex: [tan bold]{_filter.path_filter}",
                                end_section=bool(_n == len(self.filters)),
                            )
                        elif _filter.tag_filter is not None:
                            table.add_row(
                                str(_n),
                                f"Tag filter: [tan bold]{_filter.tag_filter}",
                                end_section=bool(_n == len(self.filters)),
                            )
                        elif _filter.key_filter is not None and _filter.value_filter is None:
                            table.add_row(
                                str(_n),
                                f"Key filter: [tan bold]{_filter.key_filter}",
                                end_section=bool(_n == len(self.filters)),
                            )
                        elif _filter.key_filter is not None and _filter.value_filter is not None:
                            table.add_row(
                                str(_n),
                                f"Key/Value : [tan bold]{_filter.key_filter}={_filter.value_filter}",
                                end_section=bool(_n == len(self.filters)),
                            )
                    table.add_row(f"{len(self.filters) + 1}", "Clear All")
                    table.add_row(f"{len(self.filters) + 2}", "Return to Main Menu")
                    console.print(table)

                    num = self.questions.ask_number(
                        question="Enter the number of the filter to clear"
                    )
                    if num is None:
                        return
                    if int(num) <= len(self.filters):
                        self.filters.pop(int(num) - 1)
                        self._load_vault()
                        return
                    if int(num) == len(self.filters) + 1:
                        self.filters = []
                        self._load_vault()
                        return

                case "list_notes":
                    self.vault.list_editable_notes()

                case _:
                    return

    def application_import_csv(self) -> None:
        """Import CSV for  bulk changes to metadata."""
        alerts.usage(
            "Import CSV to make build changes to metadata. The CSV must have the following columns: path, type, key, value. Where type is one of 'frontmatter', 'inline_metadata', or 'tag'. Note: this will not create new notes."
        )

        path = self.questions.ask_path(question="Enter path to a CSV file", valid_file=True)

        if path is None:
            return

        csv_path = Path(path).expanduser()

        if "csv" not in csv_path.suffix.lower():
            alerts.error("File must be a CSV file")
            return

        note_paths = [
            str(n.note_path.relative_to(self.vault.vault_path)) for n in self.vault.all_notes
        ]

        dict_from_csv = validate_csv_bulk_imports(csv_path, note_paths)
        num_changed = self.vault.update_from_dict(dict_from_csv)

        if num_changed == 0:
            alerts.warning("No notes were changed")
            return

        alerts.success(f"Rewrote metadata for {num_changed} notes.")

    def application_export_metadata(self) -> None:
        """Export metadata to various formats."""
        alerts.usage(
            "Export the metadata in your vault. Note, uncommitted changes will be reflected in these files. The notes csv export can be used as template for importing bulk changes"
        )
        choices = [
            questionary.Separator(),
            {"name": "Metadata by type to CSV", "value": "export_csv"},
            {"name": "Metadata by type to JSON", "value": "export_json"},
            {
                "name": "Metadata by note to CSV [Bulk import template]",
                "value": "export_notes_csv",
            },
            questionary.Separator(),
            {"name": "Back", "value": "back"},
        ]
        while True:
            match self.questions.ask_selection(choices=choices, question="Export format"):
                case "export_csv":
                    path = self.questions.ask_path(question="Enter a path for the CSV file")
                    if path is None:
                        return
                    self.vault.export_metadata(path=path, export_format="csv")
                    alerts.success(f"CSV written to {path}")
                case "export_json":
                    path = self.questions.ask_path(question="Enter a path for the JSON file")
                    if path is None:
                        return
                    self.vault.export_metadata(path=path, export_format="json")
                    alerts.success(f"JSON written to {path}")
                case "export_notes_csv":
                    path = self.questions.ask_path(question="Enter a path for the CSV file")
                    if path is None:
                        return
                    self.vault.export_notes_to_csv(path=path)
                    alerts.success(f"CSV written to {path}")
                    return
                case _:
                    return

    def application_inspect_metadata(self) -> None:
        """View metadata."""
        alerts.usage(
            "Inspect the metadata in your vault. Note, uncommitted changes will be reflected in these reports"
        )

        choices = [
            questionary.Separator(),
            {"name": "View all frontmatter", "value": "all_frontmatter"},
            {"name": "View all inline metadata", "value": "all_inline"},
            {"name": "View all inline tags", "value": "all_tags"},
            {"name": "View all keys", "value": "all_keys"},
            {"name": "View all metadata", "value": "all_metadata"},
            questionary.Separator(),
            {"name": "Back", "value": "back"},
        ]
        while True:
            match self.questions.ask_selection(choices=choices, question="Select an action"):
                case "all_metadata":
                    console.print("")
                    self.vault.metadata.print_metadata(area=MetadataType.ALL)
                    console.print("")
                case "all_frontmatter":
                    console.print("")
                    self.vault.metadata.print_metadata(area=MetadataType.FRONTMATTER)
                    console.print("")
                case "all_inline":
                    console.print("")
                    self.vault.metadata.print_metadata(area=MetadataType.INLINE)
                    console.print("")
                case "all_keys":
                    console.print("")
                    self.vault.metadata.print_metadata(area=MetadataType.KEYS)
                    console.print("")
                case "all_tags":
                    console.print("")
                    self.vault.metadata.print_metadata(area=MetadataType.TAGS)
                    console.print("")
                case _:
                    return

    def application_reorganize_metadata(self) -> None:
        """Reorganize metadata.

        This portion of the application deals with moving metadata between types (inline to frontmatter, etc.) and moving the location of inline metadata within a note.

        """
        alerts.usage("Move metadata within notes.")
        alerts.usage("    1. Transpose frontmatter to inline or vice versa.")
        alerts.usage("    2. Move the location of inline metadata within a note.")

        choices = [
            questionary.Separator(),
            {"name": "Move inline metadata to top of note", "value": "move_to_top"},
            {
                "name": "Move inline metadata beneath the first header",
                "value": "move_to_after_header",
            },
            {"name": "Move inline metadata to bottom of the note", "value": "move_to_bottom"},
            {"name": "Transpose frontmatter to inline", "value": "frontmatter_to_inline"},
            {"name": "Transpose inline to frontmatter", "value": "inline_to_frontmatter"},
            questionary.Separator(),
            {"name": "Back", "value": "back"},
        ]
        match self.questions.ask_selection(
            choices=choices, question="Select metadata to transpose"
        ):
            case "frontmatter_to_inline":
                self.transpose_metadata(begin=MetadataType.FRONTMATTER, end=MetadataType.INLINE)
            case "inline_to_frontmatter":
                self.transpose_metadata(begin=MetadataType.INLINE, end=MetadataType.FRONTMATTER)
            case "move_to_top":
                self.move_inline_metadata(location=InsertLocation.TOP)
            case "move_to_after_header":
                self.move_inline_metadata(location=InsertLocation.AFTER_TITLE)
            case "move_to_bottom":
                self.move_inline_metadata(location=InsertLocation.BOTTOM)
            case _:  # pragma: no cover
                return

    def application_vault(self) -> None:
        """Vault actions."""
        alerts.usage("Create or delete a backup of your vault.")

        choices = [
            questionary.Separator(),
            {"name": "Backup vault", "value": "backup_vault"},
            {"name": "Delete vault backup", "value": "delete_backup"},
            questionary.Separator(),
            {"name": "Back", "value": "back"},
        ]

        while True:
            match self.questions.ask_selection(choices=choices, question="Select a vault action"):
                case "backup_vault":
                    self.vault.backup()
                case "delete_backup":
                    self.vault.delete_backup()
                case _:
                    return

    def commit_changes(self) -> bool:
        """Write all changes to disk.

        Returns:
            True if changes were committed, False otherwise.
        """
        changed_notes = self.vault.get_changed_notes()

        if len(changed_notes) == 0:
            console.print("\n")
            alerts.notice("No changes to commit.\n")
            return False

        backup = questionary.confirm("Create backup before committing changes").ask()
        if backup is None:
            return False
        if backup:
            self.vault.backup()

        if questionary.confirm(f"Commit {len(changed_notes)} changed files to disk?").ask():
            self.vault.commit_changes()

        if not self.dry_run:
            alerts.success(f"{len(changed_notes)} changes committed to disk. Exiting")
            raise typer.Exit(0)

        return True

    def delete_tag(self) -> None:
        """Delete an inline tag."""
        tag = self.questions.ask_existing_tag(question="Which tag would you like to delete?")

        num_changed = self.vault.delete_tag(tag)
        if num_changed == 0:
            alerts.warning("No notes were changed")
            return

        alerts.success(f"Deleted inline tag: {tag} in {num_changed} notes")
        return

    def delete_key(self) -> None:
        """Delete a key from the vault."""
        key_to_delete = self.questions.ask_existing_keys_regex(
            question="Regex for the key(s) you'd like to delete?"
        )
        if key_to_delete is None:  # pragma: no cover
            return

        num_changed = self.vault.delete_metadata(
            key=key_to_delete, area=MetadataType.ALL, is_regex=True
        )
        if num_changed == 0:
            alerts.warning(f"No notes found with a key matching: [reverse]{key_to_delete}[/]")
            return

        alerts.success(
            f"Deleted keys matching: [reverse]{key_to_delete}[/] from {num_changed} notes"
        )

        return

    def delete_value(self) -> None:
        """Delete a value from the vault."""
        key = self.questions.ask_existing_key(question="Which key contains the value to delete?")
        if key is None:  # pragma: no cover
            return

        questions2 = Questions(vault=self.vault, key=key)
        value = questions2.ask_existing_value_regex(question="Regex for the value to delete")
        if value is None:  # pragma: no cover
            return

        num_changed = self.vault.delete_metadata(
            key=key, value=value, area=MetadataType.ALL, is_regex=True
        )
        if num_changed == 0:
            alerts.warning(f"No notes found matching: {key}: {value}")
            return

        alerts.success(
            f"Deleted value [reverse]{value}[/] from key [reverse]{key}[/] in {num_changed} notes"
        )

        return

    def move_inline_metadata(self, location: InsertLocation) -> None:
        """Move inline metadata to the selected location."""
        num_changed = self.vault.move_inline_metadata(location)
        if num_changed == 0:
            alerts.warning("No notes were changed")
            return

        alerts.success(f"Moved inline metadata to {location.value} in {num_changed} notes")

    def noninteractive_bulk_import(self, path: Path) -> None:
        """Bulk update metadata from a CSV from the command line.

        Args:
            path: Path to the CSV file containing the metadata to update.
        """
        self._load_vault()
        note_paths = [
            str(n.note_path.relative_to(self.vault.vault_path)) for n in self.vault.all_notes
        ]
        dict_from_csv = validate_csv_bulk_imports(path, note_paths)
        num_changed = self.vault.update_from_dict(dict_from_csv)
        if num_changed == 0:
            alerts.warning("No notes were changed")
            return

        alerts.success(f"{num_changed} notes specified in '{path}'")
        alerts.info("Review changes and commit.")
        while True:
            self.vault.info()

            match self.questions.ask_application_main():
                case "vault_actions":
                    self.application_vault()
                case "inspect_metadata":
                    self.application_inspect_metadata()
                case "review_changes":
                    self.review_changes()
                case "commit_changes":
                    self.commit_changes()
                case _:
                    break

        console.print("Done!")

    def noninteractive_export_csv(self, path: Path) -> None:
        """Export the vault metadata to CSV."""
        self._load_vault()
        self.vault.export_metadata(export_format="csv", path=str(path))
        alerts.success(f"Exported metadata to {path}")

    def noninteractive_export_json(self, path: Path) -> None:
        """Export the vault metadata to JSON."""
        self._load_vault()
        self.vault.export_metadata(export_format="json", path=str(path))
        alerts.success(f"Exported metadata to {path}")

    def noninteractive_export_template(self, path: Path) -> None:
        """Export the vault metadata to CSV."""
        self._load_vault()
        with console.status(
            "Preparing export...  [dim](Can take a while for large vaults)[/]",
            spinner="bouncingBall",
        ):
            self.vault.export_notes_to_csv(path=str(path))
        alerts.success(f"Exported metadata to {path}")

    def rename_key(self) -> None:
        """Rename a key in the vault."""
        original_key = self.questions.ask_existing_key(
            question="Which key would you like to rename?"
        )
        if original_key is None:  # pragma: no cover
            return

        new_key = self.questions.ask_new_key()
        if new_key is None:  # pragma: no cover
            return

        num_changed = self.vault.rename_metadata(original_key, new_key)
        if num_changed == 0:
            alerts.warning("No notes were changed")
            return

        alerts.success(
            f"Renamed [reverse]{original_key}[/] to [reverse]{new_key}[/] in {num_changed} notes"
        )

    def rename_tag(self) -> None:
        """Rename an inline tag."""
        original_tag = self.questions.ask_existing_tag(question="Which tag to rename?")
        if original_tag is None:  # pragma: no cover
            return

        new_tag = self.questions.ask_new_tag("New tag")
        if new_tag is None:  # pragma: no cover
            return

        num_changed = self.vault.rename_tag(original_tag, new_tag)
        if num_changed == 0:
            alerts.warning("No notes were changed")
            return

        alerts.success(
            f"Renamed [reverse]{original_tag}[/] to [reverse]{new_tag}[/] in {num_changed} notes"
        )
        return

    def rename_value(self) -> None:
        """Rename a value in the vault."""
        key = self.questions.ask_existing_key(question="Which key contains the value to rename?")
        if key is None:  # pragma: no cover
            return

        question_key = Questions(vault=self.vault, key=key)
        value = question_key.ask_existing_value(question="Which value would you like to rename?")
        if value is None:  # pragma: no cover
            return

        new_value = question_key.ask_new_value()
        if new_value is None:  # pragma: no cover
            return

        num_changes = self.vault.rename_metadata(key, value, new_value)
        if num_changes == 0:
            alerts.warning("No notes were changed")
            return

        alerts.success(f"Renamed '{key}:{value}' to '{key}:{new_value}' in {num_changes} notes")

    def review_changes(self) -> None:
        """Review all changes in the vault."""
        changed_notes = self.vault.get_changed_notes()

        if len(changed_notes) == 0:
            alerts.info("No changes to review.")
            return

        alerts.info(f"Found {len(changed_notes)} changed notes in the vault")
        choices: list[dict[str, Any] | questionary.Separator] = []
        choices.append(questionary.Separator())
        for n, note in enumerate(changed_notes, start=1):
            _selection = {
                "name": f"{n}: {note.note_path.relative_to(self.vault.vault_path)}",
                "value": n - 1,
            }
            choices.append(_selection)

        choices.append(questionary.Separator())
        choices.append({"name": "Return", "value": "return"})

        while True:
            note_to_review = self.questions.ask_selection(
                choices=choices,
                question="Select an updated note to view the diff",
            )
            if note_to_review is None or note_to_review == "return":
                break
            changed_notes[note_to_review].print_diff()

    def transpose_metadata(self, begin: MetadataType, end: MetadataType) -> None:  # noqa: PLR0911
        """Transpose metadata from one format to another.

        Args:
            begin: The format to transpose from.
            end: The format to transpose to.
        """
        choices = [
            {"name": f"Transpose all {begin.value} to {end.value}", "value": "transpose_all"},
            {"name": "Transpose a key", "value": "transpose_key"},
            {"name": "Transpose a value", "value": "transpose_value"},
            questionary.Separator(),
            {"name": "Back", "value": "back"},
        ]
        match self.questions.ask_selection(choices=choices, question="Select an action to perform"):
            case "transpose_all":
                num_changed = self.vault.transpose_metadata(
                    begin=begin,
                    end=end,
                    location=self.vault.insert_location,
                )

                if num_changed == 0:
                    alerts.warning("No notes were changed")
                    return

                alerts.success(f"Transposed {begin.value} to {end.value} in {num_changed} notes")
            case "transpose_key":
                key = self.questions.ask_existing_key(question="Which key to transpose?")
                if key is None:  # pragma: no cover
                    return

                num_changed = self.vault.transpose_metadata(
                    begin=begin,
                    end=end,
                    key=key,
                    location=self.vault.insert_location,
                )

                if num_changed == 0:
                    alerts.warning("No notes were changed")
                    return

                alerts.success(
                    f"Transposed key: `{key}` from {begin.value} to {end.value} in {num_changed} notes"
                )
            case "transpose_value":
                key = self.questions.ask_existing_key(question="Which key contains the value?")
                if key is None:  # pragma: no cover
                    return

                questions2 = Questions(vault=self.vault, key=key)
                value = questions2.ask_existing_value(question="Which value to transpose?")
                if value is None:  # pragma: no cover
                    return

                num_changed = self.vault.transpose_metadata(
                    begin=begin,
                    end=end,
                    key=key,
                    value=value,
                    location=self.vault.insert_location,
                )

                if num_changed == 0:
                    alerts.warning("No notes were changed")
                    return

                alerts.success(
                    f"Transposed key: `{key}:{value}` from {begin.value} to {end.value} in {num_changed} notes"
                )
            case _:
                return
