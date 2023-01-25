"""Questions for the cli."""


from typing import Any

import questionary
from rich import print

from obsidian_metadata._config import VaultConfig
from obsidian_metadata._utils.alerts import logger as log
from obsidian_metadata.models import Patterns, Vault
from obsidian_metadata._utils import alerts
from obsidian_metadata.models.questions import Questions

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

    def load_vault(self, path_filter: str = None) -> None:
        """Load the vault.

        Args:
            path_filter (str, optional): Regex to filter notes by path.
        """
        self.vault: Vault = Vault(config=self.config, dry_run=self.dry_run, path_filter=path_filter)
        log.info(f"Indexed {self.vault.num_notes()} notes from {self.vault.vault_path}")
        self.questions = Questions(vault=self.vault)

    def main_app(self) -> None:
        """Questions for the main application."""
        self.load_vault()

        while True:
            print("\n")
            self.vault.info()

            match self.questions.ask_main_application():  # noqa: E999
                case None:
                    break
                case "filter_notes":
                    self.load_vault(path_filter=self.questions.ask_for_filter_path())
                case "all_metadata":
                    self.vault.metadata.print_metadata()
                case "backup_vault":
                    self.vault.backup()
                case "delete_backup":
                    self.vault.delete_backup()
                case "list_notes":
                    self.vault.list_editable_notes()
                case "rename_inline_tag":
                    self.rename_inline_tag()
                case "delete_inline_tag":
                    self.delete_inline_tag()
                case "rename_key":
                    self.rename_key()
                case "delete_key":
                    self.delete_key()
                case "rename_value":
                    self.rename_value()
                case "delete_value":
                    self.delete_value()
                case "review_changes":
                    self.review_changes()
                case "commit_changes":
                    if self.commit_changes():
                        break

                    log.error("Commit failed. Please run with -vvv for more info.")
                    break

                case "abort":
                    break

        print("Done!")
        return

    def rename_key(self) -> None:
        """Renames a key in the vault."""

        original_key = self.questions.ask_for_existing_key(
            question="Which key would you like to rename?"
        )
        if original_key is None:
            return

        new_key = self.questions.ask_for_new_key()
        if new_key is None:
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

        original_tag = self.questions.ask_for_existing_inline_tag(question="Which tag to rename?")
        if original_tag is None:
            return

        new_tag = self.questions.ask_for_new_tag("New tag")
        if new_tag is None:
            return

        num_changed = self.vault.rename_inline_tag(original_tag, new_tag)
        if num_changed == 0:
            alerts.warning(f"No notes were changed")
            return

        alerts.success(
            f"Renamed [reverse]{original_tag}[/] to [reverse]{new_tag}[/] in {num_changed} notes"
        )
        return

    def delete_inline_tag(self) -> None:
        """Delete an inline tag."""
        tag = self.questions.ask_for_existing_inline_tag(
            question="Which tag would you like to delete?"
        )

        num_changed = self.vault.delete_inline_tag(tag)
        if num_changed == 0:
            alerts.warning(f"No notes were changed")
            return

        alerts.success(f"Deleted inline tag: {tag} in {num_changed} notes")
        return

    def delete_key(self) -> None:
        """Delete a key from the vault."""
        key_to_delete = self.questions.ask_for_existing_keys_regex(
            question="Regex for the key(s) you'd like to delete?"
        )
        if key_to_delete is None:
            return

        num_changed = self.vault.delete_metadata(key_to_delete)
        if num_changed == 0:
            alerts.warning(f"No notes found with a key matching: [reverse]{key_to_delete}[/]")
            return

        alerts.success(
            f"Deleted keys matching: [reverse]{key_to_delete}[/] from {num_changed} notes"
        )

        return

    def rename_value(self) -> None:
        """Rename a value in the vault."""
        key = self.questions.ask_for_existing_key(
            question="Which key contains the value to rename?"
        )
        if key is None:
            return

        question_key = Questions(vault=self.vault, key=key)
        value = question_key.ask_for_existing_value(
            question="Which value would you like to rename?"
        )
        if value is None:
            return

        new_value = question_key.ask_for_new_value()
        if new_value is None:
            return

        num_changes = self.vault.rename_metadata(key, value, new_value)
        if num_changes == 0:
            alerts.warning(f"No notes were changed")
            return

        alerts.success(f"Renamed '{key}:{value}' to '{key}:{new_value}' in {num_changes} notes")

    def delete_value(self) -> None:
        """Delete a value from the vault."""
        key = self.questions.ask_for_existing_key(
            question="Which key contains the value to delete?"
        )
        if key is None:
            return

        questions2 = Questions(vault=self.vault, key=key)
        value = questions2.ask_for_existing_value_regex(question="Regex for the value to delete")
        if value is None:
            return

        num_changed = self.vault.delete_metadata(key, value)
        if num_changed == 0:
            alerts.warning(f"No notes found matching: {key}: {value}")
            return

        alerts.success(
            f"Deleted value [reverse]{value}[/] from key [reverse]{key}[/] in {num_changed} notes"
        )

        return

    def review_changes(self) -> None:
        """Review all changes in the vault."""
        changed_notes = self.vault.get_changed_notes()

        if len(changed_notes) == 0:
            alerts.info("No changes to review.")
            return

        print(f"\nFound {len(changed_notes)} changed notes in the vault.\n")
        answer = self.questions.ask_confirm(
            question="View diffs of individual files?", default=False
        )
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
        choices.append({"name": "Return", "value": "return"})

        while True:
            note_to_review = self.questions.ask_for_selection(
                choices=choices,
                question="Select a new to view the diff",
            )
            if note_to_review is None or note_to_review == "return":
                break
            changed_notes[note_to_review].print_diff()

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

            self.vault.write()
            alerts.success(f"{len(changed_notes)} changes committed to disk. Exiting")
            return True

        return False
