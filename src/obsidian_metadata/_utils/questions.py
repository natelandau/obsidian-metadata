"""Functions for asking questions to the user and validating responses."""
from pathlib import Path

import questionary
import typer


class Questions:
    """Class for asking questions to the user and validating responses."""

    @staticmethod
    def ask_for_vault_path() -> Path:  # pragma: no cover
        """Ask the user for the path to their vault."""
        vault_path = questionary.path(
            "Enter a path to Obsidian vault:",
            only_directories=True,
            validate=Questions._validate_vault,
        ).ask()
        if vault_path is None:
            raise typer.Exit(code=1)

        return Path(vault_path).expanduser().resolve()

    @staticmethod
    def _validate_vault(path: str) -> bool | str:
        """Validates the vault path."""
        path_to_validate: Path = Path(path).expanduser().resolve()
        if not path_to_validate.exists():
            return f"Path does not exist: {path_to_validate}"
        if not path_to_validate.is_dir():
            return f"Path is not a directory: {path_to_validate}"

        return True
