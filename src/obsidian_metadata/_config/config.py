"""Instantiate the configuration object."""


from pathlib import Path
from textwrap import dedent
from typing import Any

import questionary
import rich.repr
import tomlkit
import typer

from obsidian_metadata._utils import alerts
from obsidian_metadata._utils.alerts import logger as log


class ConfigQuestions:
    """Questions to ask the user when creating a configuration file."""

    @staticmethod
    def ask_for_vault_path() -> Path:  # pragma: no cover
        """Ask the user for the path to their vault.

        Returns:
            Path: The path to the vault.
        """
        vault_path = questionary.path(
            "Enter a path to Obsidian vault:",
            only_directories=True,
            validate=ConfigQuestions._validate_valid_dir,
        ).ask()
        if vault_path is None:
            raise typer.Exit(code=1)

        return Path(vault_path).expanduser().resolve()

    @staticmethod
    def _validate_valid_dir(path: str) -> bool | str:
        """Validates a valid directory.

        Returns:
            bool | str: True if the path is valid, otherwise a string with the error message.
        """
        path_to_validate: Path = Path(path).expanduser().resolve()
        if not path_to_validate.exists():
            return f"Path does not exist: {path_to_validate}"
        if not path_to_validate.is_dir():
            return f"Path is not a directory: {path_to_validate}"

        return True


@rich.repr.auto
class Config:
    """Representation of a configuration file."""

    def __init__(self, config_path: Path = None, vault_path: Path = None) -> None:

        if vault_path is None:
            self.config_path: Path = self._validate_config_path(Path(config_path))
            self.config: dict[str, Any] = self._load_config()

            if self.config == {}:
                log.error(f"Configuration file is empty: '{self.config_path}'")
                raise typer.Exit(code=1)
        else:
            self.config_path = None
            self.config = {
                "command_line_vault": {"path": vault_path, "exclude_paths": [".git", ".obsidian"]}
            }

        try:
            self.vaults: list[VaultConfig] = [
                VaultConfig(vault_name=key, vault_config=self.config[key]) for key in self.config
            ]
        except TypeError as e:
            log.error(f"Configuration file is invalid: '{self.config_path}'")
            raise typer.Exit(code=1) from e

        log.debug(f"Loaded configuration from '{self.config_path}'")
        log.trace(self.config)

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover
        """Define rich representation of the Config object."""
        yield "config_path", self.config_path
        yield "vaults", self.vaults

    def _validate_config_path(self, config_path: Path | None) -> Path:
        """Load the configuration path."""
        if config_path is None:
            config_path = Path(Path.home() / f".{__package__.split('.')[0]}.toml")

        if not config_path.exists():
            self._write_default_config(config_path)
            alerts.info(f"Created default configuration file at '{config_path}'")

        return config_path.expanduser().resolve()

    def _load_config(self) -> dict[str, Any]:
        """Load the configuration file."""
        try:
            with open(self.config_path, encoding="utf-8") as fp:
                return tomlkit.load(fp)
        except tomlkit.exceptions.TOMLKitError as e:
            alerts.error(f"Could not parse '{self.config_path}'")
            raise typer.Exit(code=1) from e

    def _write_default_config(self, path_to_config: Path) -> None:
        """Write the default configuration file when no config file is found."""
        vault_path = ConfigQuestions.ask_for_vault_path()

        config_text = f"""\
        # Add another vault by replicating this section and changing the name
        ["Vault 1"] # Name of the vault.

            # Path to your obsidian vault
            path = "{vault_path}"

            # Folders within the vault to ignore when indexing metadata
            exclude_paths = [".git", ".obsidian"]"""

        path_to_config.write_text(dedent(config_text))


@rich.repr.auto
class VaultConfig:
    """Representation of a vault configuration."""

    def __init__(self, vault_name: str, vault_config: dict) -> None:
        """Initialize the vault configuration."""
        self.name: str = vault_name
        self.config: dict = vault_config

        try:
            self.path = self._validate_vault_path(self.config["path"])

            Path(self.config["path"]).expanduser().resolve()
        except KeyError:
            self.path = None

        try:
            self.exclude_paths = self.config["exclude_paths"]
        except KeyError:
            self.exclude_paths = []

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover
        """Define rich representation of a vault config."""
        yield "name", self.name
        yield "config", self.config
        yield "path", self.path
        yield "exclude_paths", self.exclude_paths

    def _validate_vault_path(self, vault_path: Path | None) -> Path:
        """Validate the vault path."""
        vault_path = Path(vault_path).expanduser().resolve()

        if not vault_path.exists():
            alerts.error(f"Vault path not found: '{vault_path}'")
            raise typer.Exit(code=1)

        if not vault_path.is_dir():
            alerts.error(f"Vault path is not a directory: '{vault_path}'")
            raise typer.Exit(code=1)

        return vault_path
