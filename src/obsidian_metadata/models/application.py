"""Questions for the cli."""


from typing import Any

import questionary
import typer
from rich import print

from obsidian_metadata._config import Config
from obsidian_metadata._utils import alerts, clear_screen
from obsidian_metadata._utils.alerts import logger as log
from obsidian_metadata.models import Patterns, Vault

PATTERNS = Patterns()


class Application:
    """Questions for use in the cli.

    Contains methods which ask a series of questions to the user and return a dictionary with their answers.

    More info: https://questionary.readthedocs.io/en/stable/pages/advanced.html#create-questions-from-dictionaries
    """

    def __init__(self, config: Config, dry_run: bool) -> None:
        self.config = config
        self.dry_run = dry_run
        self.custom_style = questionary.Style(
            [
                ("separator", "bold fg:#6C6C6C"),
                ("instruction", "fg:#6C6C6C"),
                ("highlighted", "bold reverse"),
                ("pointer", "bold"),
            ]
        )

        clear_screen()

    def load_vault(self, path_filter: str = None) -> None:
        """Load the vault.

        Args:
            path_filter (str, optional): Regex to filter notes by path.
        """
        self.vault: Vault = Vault(config=self.config, dry_run=self.dry_run, path_filter=path_filter)
        log.info(f"Indexed {self.vault.num_notes()} notes from {self.vault.vault_path}")

    def main_app(self) -> None:  # noqa: C901
        """Questions for the main application."""
        self.load_vault()

        while True:
            self.vault.info()
            operation = questionary.select(
                "What do you want to do?",
                choices=[
                    questionary.Separator("\n-- VAULT ACTIONS -----------------"),
                    {"name": "Backup vault", "value": "backup_vault"},
                    {"name": "Delete vault backup", "value": "delete_backup"},
                    {"name": "View all metadata", "value": "all_metadata"},
                    {"name": "List notes in scope", "value": "list_notes"},
                    {
                        "name": "Filter the notes being processed by their path",
                        "value": "filter_notes",
                    },
                    questionary.Separator("\n-- INLINE TAG ACTIONS ---------"),
                    questionary.Separator("Tags in the note body"),
                    {
                        "name": "Rename an inline tag",
                        "value": "rename_inline_tag",
                    },
                    {
                        "name": "Delete an inline tag",
                        "value": "delete_inline_tag",
                    },
                    questionary.Separator("\n-- METADATA ACTIONS -----------"),
                    questionary.Separator("Frontmatter or inline metadata"),
                    {"name": "Rename Key", "value": "rename_key"},
                    {"name": "Delete Key", "value": "delete_key"},
                    {"name": "Rename Value", "value": "rename_value"},
                    {"name": "Delete Value", "value": "delete_value"},
                    questionary.Separator("\n-- REVIEW/COMMIT CHANGES ------"),
                    {"name": "Review changes", "value": "review_changes"},
                    {"name": "Commit changes", "value": "commit_changes"},
                    questionary.Separator("-------------------------------"),
                    {"name": "Quit", "value": "abort"},
                ],
                use_shortcuts=False,
                style=self.custom_style,
            ).ask()

            if operation == "filter_notes":
                path_filter = questionary.text(
                    "Enter a regex to filter notes by path",
                    validate=lambda text: len(text) > 0,
                ).ask()
                if path_filter is None:
                    continue
                self.load_vault(path_filter=path_filter)

            if operation == "all_metadata":
                self.vault.metadata.print_metadata()

            if operation == "backup_vault":
                self.vault.backup()

            if operation == "delete_backup":
                self.vault.delete_backup()

            if operation == "list_notes":
                self.vault.list_editable_notes()

            if operation == "rename_inline_tag":
                self.rename_inline_tag()

            if operation == "delete_inline_tag":
                self.delete_inline_tag()

            if operation == "rename_key":
                self.rename_key()

            if operation == "delete_key":
                self.delete_key()

            if operation == "rename_value":
                self.rename_value()

            if operation == "delete_value":
                self.delete_value()

            if operation == "review_changes":
                self.review_changes()

            if operation == "commit_changes":
                self.commit_changes()

            if operation == "abort":
                break

        print("Done!")
        return

    def rename_key(self) -> None:
        """Renames a key in the vault."""

        def validate_key(text: str) -> bool:
            """Validate the key name."""
            if self.vault.metadata.contains(text):
                return True
            return False

        def validate_new_key(text: str) -> bool:
            """Validate the tag name."""
            if PATTERNS.validate_key_text.search(text) is not None:
                return False
            if len(text) == 0:
                return False

            return True

        original_key = questionary.text(
            "Which key would you like to rename?",
            validate=validate_key,
        ).ask()
        if original_key is None:
            return

        new_key = questionary.text(
            "New key name",
            validate=validate_new_key,
        ).ask()
        if new_key is None:
            return

        self.vault.rename_metadata(original_key, new_key)

    def rename_inline_tag(self) -> None:
        """Rename an inline tag."""

        def validate_new_tag(text: str) -> bool:
            """Validate the tag name."""
            if PATTERNS.validate_tag_text.search(text) is not None:
                return False
            if len(text) == 0:
                return False

            return True

        original_tag = questionary.text(
            "Which tag would you like to rename?",
            validate=lambda text: True
            if self.vault.contains_inline_tag(text)
            else "Tag not found in vault",
        ).ask()
        if original_tag is None:
            return

        new_tag = questionary.text(
            "New tag name",
            validate=validate_new_tag,
        ).ask()
        if new_tag is None:
            return

        self.vault.rename_inline_tag(original_tag, new_tag)
        alerts.success(f"Renamed [reverse]{original_tag}[/] to [reverse]{new_tag}[/]")
        return

    def delete_inline_tag(self) -> None:
        """Delete an inline tag."""
        tag = questionary.text(
            "Which tag would you like to delete?",
            validate=lambda text: True
            if self.vault.contains_inline_tag(text)
            else "Tag not found in vault",
        ).ask()
        if tag is None:
            return

        self.vault.delete_inline_tag(tag)
        alerts.success(f"Deleted inline tag: {tag}")
        return

    def delete_key(self) -> None:
        """Delete a key from the vault."""
        while True:
            key_to_delete = questionary.text("Regex for the key(s) you'd like to delete?").ask()
            if key_to_delete is None:
                return

            if not self.vault.metadata.contains(key_to_delete, is_regex=True):
                alerts.warning(f"No matching keys in the vault: {key_to_delete}")
                continue

            num_changed = self.vault.delete_metadata(key_to_delete)
            if num_changed == 0:
                alerts.warning(f"No notes found matching: [reverse]{key_to_delete}[/]")
                return

            alerts.success(
                f"Deleted keys matching: [reverse]{key_to_delete}[/] from {num_changed} notes"
            )
            break

        return

    def rename_value(self) -> None:
        """Rename a value in the vault."""
        key = questionary.text(
            "Which key contains the value to rename?",
            validate=lambda text: True
            if self.vault.metadata.contains(text)
            else "Key not found in vault",
        ).ask()
        if key is None:
            return

        value = questionary.text(
            "Which value would you like to rename?",
            validate=lambda text: True
            if self.vault.metadata.contains(key, text)
            else f"Value not found in {key}",
        ).ask()
        if value is None:
            return

        new_value = questionary.text(
            "New value?",
            validate=lambda text: True
            if not self.vault.metadata.contains(key, text)
            else f"Value already exists in {key}",
        ).ask()

        if self.vault.rename_metadata(key, value, new_value):
            alerts.success(f"Renamed [reverse]{key}: {value}[/] to [reverse]{key}: {new_value}[/]")

    def delete_value(self) -> None:
        """Delete a value from the vault."""
        while True:
            key = questionary.text(
                "Which key contains the value to delete?",
            ).ask()
            if key is None:
                return
            if not self.vault.metadata.contains(key, is_regex=True):
                alerts.warning(f"No keys in value match: {key}")
                continue
            break

        while True:
            value = questionary.text(
                "Regex for the value to delete",
            ).ask()
            if value is None:
                return
            if not self.vault.metadata.contains(key, value, is_regex=True):
                alerts.warning(f"No matching key value pairs found in the vault: {key}: {value}")
                continue

            num_changed = self.vault.delete_metadata(key, value)
            if num_changed == 0:
                alerts.warning(f"No notes found matching: [reverse]{key}: {value}[/]")
                return

            alerts.success(
                f"Deleted {num_changed} entries matching: [reverse]{key}[/]: [reverse]{value}[/]"
            )

            break

        return

    def review_changes(self) -> None:
        """Review all changes in the vault."""
        changed_notes = self.vault.get_changed_notes()

        if len(changed_notes) == 0:
            alerts.info("No changes to review.")
            return

        print(f"\nFound {len(changed_notes)} changed notes in the vault.\n")
        answer = questionary.confirm("View diffs of individual files?", default=False).ask()
        if not answer:
            return

        choices: list[dict[str, Any] | questionary.Separator] = [questionary.Separator()]
        for n, note in enumerate(changed_notes, start=1):
            _selection = {
                "name": f"{n}: {note.note_path.relative_to(self.vault.vault_path)}",
                "value": n - 1,
            }
            choices.append(_selection)

        choices.append(questionary.Separator())
        choices.append({"name": "Return", "value": "skip"})

        while True:
            note_to_review = questionary.select(
                "Select a new to view the diff.",
                choices=choices,
                use_shortcuts=False,
                style=self.custom_style,
            ).ask()
            if note_to_review is None or note_to_review == "skip":
                break
            changed_notes[note_to_review].print_diff()

    def commit_changes(self) -> None:
        """Write all changes to disk."""
        changed_notes = self.vault.get_changed_notes()

        if len(changed_notes) == 0:
            print("\n")
            alerts.notice("No changes to commit.\n")
            return

        backup = questionary.confirm("Create backup before committing changes").ask()
        if backup is None:
            return
        if backup:
            self.vault.backup()

        if questionary.confirm(f"Commit {len(changed_notes)} changed files to disk?").ask():

            self.vault.write()
            alerts.success("Changes committed to disk. Exiting.")
            typer.Exit()

        return
