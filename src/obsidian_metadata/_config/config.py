"""Instantiate the configuration object."""

import re
import shutil
from pathlib import Path
from typing import Any

import questionary
import rich.repr
import typer

from obsidian_metadata._utils import alerts, vault_validation
from obsidian_metadata._utils.alerts import logger as log

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore [no-redef]

DEFAULT_CONFIG_FILE: Path = Path(__file__).parent / "default.toml"


@rich.repr.auto
class Config:
    """Configuration class."""

    def __init__(self, config_path: Path = None, vault_path: Path = None) -> None:
        self.config_path: Path = self._validate_config_path(Path(config_path))
        self.config: dict[str, Any] = self._load_config()
        self.config_content: str = self.config_path.read_text()
        self.vault_path: Path = self._validate_vault_path(vault_path)

        try:
            self.exclude_paths: list[Any] = self.config["exclude_paths"]
        except KeyError:
            self.exclude_paths = []

        try:
            self.metadata_location: str = self.config["metadata"]["metadata_location"]
        except KeyError:
            self.metadata_location = "frontmatter"

        try:
            self.tags_location: str = self.config["metadata"]["tags_location"]
        except KeyError:
            self.tags_location = "top"

        log.debug(f"Loaded configuration from '{self.config_path}'")
        log.trace(self.config)

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover
        """Define rich representation of Vault."""
        yield "config_path", self.config_path
        yield "config_content",
        yield "vault_path", self.vault_path
        yield "metadata_location", self.metadata_location
        yield "tags_location", self.tags_location
        yield "exclude_paths", self.exclude_paths

    def _validate_config_path(self, config_path: Path | None) -> Path:
        """Load the configuration path."""
        if config_path is None:
            config_path = Path(Path.home() / f".{__package__.split('.')[0]}.toml")

        if not config_path.exists():
            shutil.copy(DEFAULT_CONFIG_FILE, config_path)
            alerts.info(f"Created default configuration file at '{config_path}'")

        return config_path.expanduser().resolve()

    def _load_config(self) -> dict[str, Any]:
        """Load the configuration file."""
        try:
            with self.config_path.open("rb") as f:
                return tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            alerts.error(f"Could not parse '{self.config_path}'")
            raise typer.Exit(code=1) from e

    def _validate_vault_path(self, vault_path: Path | None) -> Path:
        """Validate the vault path."""
        if vault_path is None:
            try:
                vault_path = Path(self.config["vault"]).expanduser().resolve()
            except KeyError:
                vault_path = Path("/I/Do/Not/Exist")

        if not vault_path.exists():  # pragma: no cover
            alerts.error(f"Vault path not found: '{vault_path}'")

            vault_path = questionary.path(
                "Enter a path to Obsidian vault:",
                only_directories=True,
                validate=vault_validation,
            ).ask()
            if vault_path is None:
                raise typer.Exit(code=1)

            vault_path = Path(vault_path).expanduser().resolve()

            self.write_config_value("vault", str(vault_path))
        return vault_path

    def write_config_value(self, key: str, value: str | int) -> None:
        """Write a new value to the configuration file.

        Args:
            key (str): The key to write.
            value (str|int): The value to write.
        """
        self.config_content = re.sub(
            rf"( *{key} = ['\"])[^'\"]*(['\"].*)", rf"\1{value}\2", self.config_content
        )

        alerts.notice(f"Writing new configuration for '{key}' to '{self.config_path}'")
        self.config_path.write_text(self.config_content)
