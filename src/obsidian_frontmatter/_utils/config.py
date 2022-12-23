"""Loads the configuration of the script."""

from pathlib import Path

import typer
from pydantic import BaseSettings, validator

from obsidian_frontmatter._utils import alerts


def ask_for_vault() -> Path:  # pragma: no cover
    """Ask the user for a valid vault path."""
    while True:
        path: Path = Path(typer.prompt("Enter a path to your Obsidian vault", type=Path))
        path = path.expanduser().resolve()

        if not path.exists():
            alerts.error(f"Path not found: '{path}'")
            continue

        if not path.is_dir():
            alerts.error(f"Path is not a directory: '{path}'")
            continue

        return path


class Configuration(BaseSettings):
    """Configuration data."""

    vault_path: Path | None
    dry_run: bool = False
    force: bool = False
    log_file: Path = None
    log_to_file: bool = False
    verbosity: int = 0

    @validator("vault_path")
    def vault_path_must_exist(cls, v: Path) -> Path:
        """Vault path must exist."""
        if not v:
            alerts.error("Must specify a path to an obsidian vault")
            raise typer.Exit(code=1)

        v = v.expanduser().resolve()

        if not v.exists():
            alerts.error(f"Vault path not found: '{v}'")
            raise typer.Exit(code=1)

        if not v.is_dir():
            alerts.error(f"Vault path is not a directory: '{v}'")
            raise typer.Exit(code=1)

        return v

    class Config:
        """Configuration for the pydantic model."""

        @classmethod
        def customise_sources(
            cls,
            init_settings: dict,
            env_settings: dict,
            file_secret_settings: dict,
        ) -> tuple[dict, dict, dict]:
            """Customize the sources of the configuration."""
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )
