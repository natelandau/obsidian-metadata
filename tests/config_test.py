# type: ignore
"""Tests for the configuration module."""

from pathlib import Path

import pytest
import typer

from obsidian_frontmatter._utils import Configuration
from obsidian_frontmatter.cli import main as app


def test_vault_validation(capsys, tmp_path) -> None:
    """Test validation of vault paths."""
    with pytest.raises(typer.Exit):
        Configuration()

        captured = capsys.readouterr()
        assert captured.out == "ERROR    | Must specify a path to an obsidian vault\n"

    with pytest.raises(typer.Exit):
        Configuration(vault_path="/some/dir/vault")

        captured = capsys.readouterr()
        assert captured.out == "ERROR    | Vault path not found: '/some/dir/vault'\n"

    file = Path(tmp_path / "vault.txt")
    file.touch()
    with pytest.raises(typer.Exit):
        Configuration(vault_path=file)

        captured = capsys.readouterr()
        assert "ERROR    | Vault path is not a directory:" in captured.out


def test_configuration_class(tmp_path) -> None:
    """Test loading a configuration file."""
    vault_path = Path(tmp_path / "vault/")
    vault_path.mkdir()

    config = Configuration(vault_path=vault_path)
    assert config.vault_path == vault_path
    assert config.dry_run is False
    assert config.force is False
    assert config.log_file is None
    assert config.log_to_file is False
    assert config.verbosity == 0


def test_create_nonexistant_config(tmp_path):
    """Test creating a non-existant configuration file."""
    log_file = Path(tmp_path / "log.txt")
    config_file = Path(tmp_path / "config.env")
    vault_path = Path(tmp_path / "vault/")
    vault_path.mkdir()

    assert config_file.exists() is False
    app(
        vault_path=vault_path,
        config_file=config_file,
        dry_run=False,
        force=False,
        log_file=log_file,
        log_to_file=False,
        verbosity=3,
    )
    assert config_file.exists() is True


def test_configuration_from_cli(tmp_path, capsys):
    """Test changing configuration from the CLI."""
    log_file = Path(tmp_path / "log.txt")

    vault_path = Path(tmp_path / "vault/")
    vault_path.mkdir()

    env_file = Path(tmp_path / "config.env")
    env_file.write_text(f"vault_path='{vault_path}'")

    print(env_file.read_text())

    configuration = app(
        config_file=env_file,
        dry_run=False,
        force=False,
        log_file=log_file,
        log_to_file=False,
        verbosity=3,
        vault_path=None,
    )

    assert configuration.vault_path == vault_path
    assert configuration.dry_run is False
    assert configuration.force is False
    assert configuration.log_file == log_file
    assert configuration.log_to_file is False
    assert configuration.verbosity == 3

    configuration = app(
        config_file=env_file,
        dry_run=False,
        force=False,
        log_file=log_file,
        log_to_file=False,
        verbosity=0,
        vault_path=None,
    )

    assert configuration.vault_path == vault_path
    assert configuration.dry_run is False
    assert configuration.force is False
    assert configuration.log_file == log_file
    assert configuration.log_to_file is False
    assert configuration.verbosity == 0
