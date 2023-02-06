"""Questions for the cli."""


from typing import Any
from pathlib import Path
import questionary
from rich import print
from rich import box
from rich.console import Console
from rich.table import Table
from obsidian_metadata._config import VaultConfig
from obsidian_metadata._utils.alerts import logger as log
from obsidian_metadata.models import Patterns, Vault, VaultFilter
from obsidian_metadata._utils import alerts
from obsidian_metadata.models.questions import Questions
from obsidian_metadata.models.enums import MetadataType

PATTERNS = Patterns()


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

            match self.questions.ask_application_main():  # noqa: E999
                case "vault_actions":
                    self.application_vault()
                case "inspect_metadata":
                    self.application_inspect_metadata()
                case "filter_notes":
                    self.application_filter()
                case "add_metadata":
                    self.application_add_metadata()
                case "rename_metadata":
                    self.application_rename_metadata()
                case "delete_metadata":
                    self.application_delete_metadata()
                case "transpose_metadata":
                    self.application_transpose_metadata()
                case "review_changes":
                    self.review_changes()
                case "commit_changes":
                    self.commit_changes()
                case _:
                    break

        print("Done!")
        return

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
                    alerts.warning(f"No notes were changed")
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
                    alerts.warning(f"No notes were changed")
                    return

                alerts.success(f"Added metadata to {num_changed} notes")
            case _:  # pragma: no cover
                return

    def application_delete_metadata(self) -> None:
        alerts.usage("Delete either a key and all associated values, or a specific value.")

        choices = [
            {"name": "Delete key", "value": "delete_key"},
            {"name": "Delete value", "value": "delete_value"},
            {"name": "Delete inline tag", "value": "delete_inline_tag"},
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
            case "delete_inline_tag":
                self.delete_inline_tag()
            case _:  # pragma: no cover
                return

    def application_rename_metadata(self) -> None:
        """Rename metadata."""
        alerts.usage("Select the type of metadata to rename.")

        choices = [
            {"name": "Rename key", "value": "rename_key"},
            {"name": "Rename value", "value": "rename_value"},
            {"name": "Rename inline tag", "value": "rename_inline_tag"},
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
            case "rename_inline_tag":
                self.rename_inline_tag()
            case _:  # pragma: no cover
                return

    def application_filter(self) -> None:
        """Filter notes."""
        alerts.usage("Limit the scope of notes to be processed with one or more filters.")

        choices = [
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
                    if path is None or path == "":  # pragma: no cover
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
                    if value == "":
                        self.filters.append(VaultFilter(key_filter=key))
                    else:
                        self.filters.append(VaultFilter(key_filter=key, value_filter=value))
                    self._load_vault()

                case "apply_tag_filter":
                    tag = self.questions.ask_existing_inline_tag()
                    if tag is None or tag == "":
                        return

                    self.filters.append(VaultFilter(tag_filter=tag))
                    self._load_vault()

                case "list_filters":
                    if len(self.filters) == 0:
                        alerts.notice("No filters have been applied")
                        return

                    print("")
                    table = Table(
                        "Opt",
                        "Filter",
                        "Type",
                        title="Current Filters",
                        show_header=False,
                        box=box.HORIZONTALS,
                    )
                    for _n, filter in enumerate(self.filters, start=1):
                        if filter.path_filter is not None:
                            table.add_row(
                                str(_n),
                                f"Path regex: [tan bold]{filter.path_filter}",
                                end_section=bool(_n == len(self.filters)),
                            )
                        elif filter.tag_filter is not None:
                            table.add_row(
                                str(_n),
                                f"Tag filter: [tan bold]{filter.tag_filter}",
                                end_section=bool(_n == len(self.filters)),
                            )
                        elif filter.key_filter is not None and filter.value_filter is None:
                            table.add_row(
                                str(_n),
                                f"Key filter: [tan bold]{filter.key_filter}",
                                end_section=bool(_n == len(self.filters)),
                            )
                        elif filter.key_filter is not None and filter.value_filter is not None:
                            table.add_row(
                                str(_n),
                                f"Key/Value : [tan bold]{filter.key_filter}={filter.value_filter}",
                                end_section=bool(_n == len(self.filters)),
                            )
                    table.add_row(f"{len(self.filters) + 1}", "Clear All")
                    table.add_row(f"{len(self.filters) + 2}", "Return to Main Menu")
                    Console().print(table)

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

    def application_inspect_metadata(self) -> None:
        """View metadata."""
        alerts.usage(
            "Inspect the metadata in your vault. Note, uncommitted changes will be reflected in these reports"
        )

        choices = [
            {"name": "View all metadata", "value": "all_metadata"},
            {"name": "View all frontmatter", "value": "all_frontmatter"},
            {"name": "View all inline_metadata", "value": "all_inline"},
            {"name": "View all keys", "value": "all_keys"},
            {"name": "View all inline tags", "value": "all_tags"},
            questionary.Separator(),
            {"name": "Write all metadata to CSV", "value": "export_csv"},
            {"name": "Write all metadata to JSON file", "value": "export_json"},
            questionary.Separator(),
            {"name": "Back", "value": "back"},
        ]
        while True:
            match self.questions.ask_selection(choices=choices, question="Select a vault action"):
                case "all_metadata":
                    print("")
                    self.vault.metadata.print_metadata(area=MetadataType.ALL)
                    print("")
                case "all_frontmatter":
                    print("")
                    self.vault.metadata.print_metadata(area=MetadataType.FRONTMATTER)
                    print("")
                case "all_inline":
                    print("")
                    self.vault.metadata.print_metadata(area=MetadataType.INLINE)
                    print("")
                case "all_keys":
                    print("")
                    self.vault.metadata.print_metadata(area=MetadataType.KEYS)
                    print("")
                case "all_tags":
                    print("")
                    self.vault.metadata.print_metadata(area=MetadataType.TAGS)
                    print("")
                case "export_csv":
                    path = self.questions.ask_path(question="Enter a path for the CSV file")
                    if path is None:
                        return
                    self.vault.export_metadata(path=path, format="csv")
                    alerts.success(f"Metadata written to {path}")
                case "export_json":
                    path = self.questions.ask_path(question="Enter a path for the JSON file")
                    if path is None:
                        return
                    self.vault.export_metadata(path=path, format="json")
                    alerts.success(f"Metadata written to {path}")
                case _:
                    return

    def application_transpose_metadata(self) -> None:
        """Transpose metadata."""
        alerts.usage("Transpose metadata from frontmatter to inline or vice versa.")

        choices = [
            {"name": "Transpose frontmatter to inline", "value": "frontmatter_to_inline"},
            {"name": "Transpose inline to frontmatter", "value": "inline_to_frontmatter"},
        ]
        match self.questions.ask_selection(
            choices=choices, question="Select metadata to transpose"
        ):
            case "frontmatter_to_inline":
                self.transpose_metadata(begin=MetadataType.FRONTMATTER, end=MetadataType.INLINE)
            case "inline_to_frontmatter":
                self.transpose_metadata(begin=MetadataType.INLINE, end=MetadataType.FRONTMATTER)
            case _:  # pragma: no cover
                return

    def application_vault(self) -> None:
        """Vault actions."""
        alerts.usage("Create or delete a backup of your vault.")

        choices = [
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
            print("\n")
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
            return True

        return True

    def delete_inline_tag(self) -> None:
        """Delete an inline tag."""
        tag = self.questions.ask_existing_inline_tag(question="Which tag would you like to delete?")

        num_changed = self.vault.delete_inline_tag(tag)
        if num_changed == 0:
            alerts.warning(f"No notes were changed")
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

        num_changed = self.vault.delete_metadata(key_to_delete)
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

        num_changed = self.vault.delete_metadata(key, value)
        if num_changed == 0:
            alerts.warning(f"No notes found matching: {key}: {value}")
            return

        alerts.success(
            f"Deleted value [reverse]{value}[/] from key [reverse]{key}[/] in {num_changed} notes"
        )

        return

    def noninteractive_export_csv(self, path: Path) -> None:
        """Export the vault metadata to CSV."""
        self._load_vault()
        self.vault.export_metadata(format="json", path=str(path))
        alerts.success(f"Exported metadata to {path}")

    def noninteractive_export_json(self, path: Path) -> None:
        """Export the vault metadata to JSON."""
        self._load_vault()
        self.vault.export_metadata(format="json", path=str(path))
        alerts.success(f"Exported metadata to {path}")

    def rename_key(self) -> None:
        """Renames a key in the vault."""

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
            alerts.warning(f"No notes were changed")
            return

        alerts.success(
            f"Renamed [reverse]{original_key}[/] to [reverse]{new_key}[/] in {num_changed} notes"
        )

    def rename_inline_tag(self) -> None:
        """Rename an inline tag."""

        original_tag = self.questions.ask_existing_inline_tag(question="Which tag to rename?")
        if original_tag is None:  # pragma: no cover
            return

        new_tag = self.questions.ask_new_tag("New tag")
        if new_tag is None:  # pragma: no cover
            return

        num_changed = self.vault.rename_inline_tag(original_tag, new_tag)
        if num_changed == 0:
            alerts.warning(f"No notes were changed")
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
            alerts.warning(f"No notes were changed")
            return

        alerts.success(f"Renamed '{key}:{value}' to '{key}:{new_value}' in {num_changes} notes")

    def review_changes(self) -> None:
        """Review all changes in the vault."""
        changed_notes = self.vault.get_changed_notes()

        if len(changed_notes) == 0:
            alerts.info("No changes to review.")
            return

        alerts.info(f"Found {len(changed_notes)} changed notes in the vault")
        choices: list[dict[str, Any] | questionary.Separator] = [questionary.Separator()]
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

    def transpose_metadata(self, begin: MetadataType, end: MetadataType) -> None:
        """Transpose metadata from one format to another.

        Args:
            begin: The format to transpose from.
            end: The format to transpose to.
        """
        choices = [
            {"name": f"Transpose all {begin.value} to {end.value}", "value": "transpose_all"},
            {"name": "Transpose a key", "value": "transpose_key"},
            {"name": "Transpose a value", "value": "transpose_value"},
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
                    alerts.warning(f"No notes were changed")
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
                    alerts.warning(f"No notes were changed")
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
                    alerts.warning(f"No notes were changed")
                    return

                alerts.success(
                    f"Transposed key: `{key}:{value}` from {begin.value} to {end.value} in {num_changed} notes"
                )
            case _:
                return
