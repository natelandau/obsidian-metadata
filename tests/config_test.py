# type: ignore
"""Tests for the configuration module."""

from pathlib import Path
from textwrap import dedent

import pytest
import typer

from obsidian_metadata._config.config import Config, ConfigQuestions


def test_validate_valid_dir() -> None:
    """Test vault validation."""
    assert ConfigQuestions._validate_valid_dir("tests/") is True
    assert "Path is not a directory" in ConfigQuestions._validate_valid_dir("pyproject.toml")
    assert "Path does not exist" in ConfigQuestions._validate_valid_dir("tests/vault2")


def test_broken_config_file(capsys) -> None:
    """Test loading a broken config file."""
    config_file = Path("tests/fixtures/broken_config_file.toml")

    with pytest.raises(typer.Exit):
        Config(config_path=config_file)
    captured = capsys.readouterr()
    assert "Could not parse" in captured.out


def test_vault_path_errors(tmp_path, capsys) -> None:
    """Test loading a config file with a vault path that doesn't exist."""
    config_file = Path(tmp_path / "config.toml")
    with pytest.raises(typer.Exit):
        Config(config_path=config_file, vault_path=Path("tests/fixtures/does_not_exist"))
    captured = capsys.readouterr()
    assert "Vault path not found" in captured.out

    with pytest.raises(typer.Exit):
        Config(config_path=config_file, vault_path=Path("tests/fixtures/test_vault/sample_note.md"))
    captured = capsys.readouterr()
    assert "Vault path is not a directory" in captured.out


def test_multiple_vaults_okay() -> None:
    """Test multiple vaults."""
    config_file = Path("tests/fixtures/multiple_vaults.toml")

    config = Config(config_path=config_file)
    assert config.config == {
        "Sample Vault": {
            "exclude_paths": [".git", ".obsidian", "ignore_folder"],
            "insert_location": "top",
            "path": "tests/fixtures/sample_vault",
        },
        "Test Vault": {
            "exclude_paths": [".git", ".obsidian", "ignore_folder"],
            "path": "tests/fixtures/test_vault",
        },
    }
    assert len(config.vaults) == 2
    assert config.vaults[0].name == "Sample Vault"
    assert config.vaults[0].path == Path("tests/fixtures/sample_vault").expanduser().resolve()
    assert config.vaults[0].exclude_paths == [".git", ".obsidian", "ignore_folder"]
    assert config.vaults[1].name == "Test Vault"
    assert config.vaults[1].path == Path("tests/fixtures/test_vault").expanduser().resolve()
    assert config.vaults[1].exclude_paths == [".git", ".obsidian", "ignore_folder"]


def test_single_vault() -> None:
    """Test multiple vaults."""
    config_file = Path("tests/fixtures/test_vault_config.toml")

    config = Config(config_path=config_file)
    assert config.config == {
        "Test Vault": {
            "exclude_paths": [".git", ".obsidian", "ignore_folder"],
            "path": "tests/fixtures/test_vault",
            "insert_location": "BOTTOM",
        }
    }
    assert len(config.vaults) == 1
    assert config.vaults[0].name == "Test Vault"
    assert config.vaults[0].path == Path("tests/fixtures/test_vault").expanduser().resolve()
    assert config.vaults[0].exclude_paths == [".git", ".obsidian", "ignore_folder"]


def test_no_config_no_vault(tmp_path, mocker) -> None:
    """Test creating a config on first run."""
    fake_vault = Path(tmp_path / "vault")
    fake_vault.mkdir()

    mocker.patch(
        "obsidian_metadata._config.config.ConfigQuestions.ask_for_vault_path",
        return_value=fake_vault,
    )

    config_file = Path(tmp_path / "config.toml")
    Config(config_path=config_file)

    content = config_file.read_text()
    sample_config = f"""\
    # Add another vault by replicating this section and changing the name
    ["Vault 1"] # Name of the vault.

        # Path to your obsidian vault
        # Note for Windows users: Windows paths must use `\\` as the path separator due to a limitation with how TOML parses strings.
        #   Example: "C:\\Users\\username\\Documents\\Obsidian"
        path = "{str(fake_vault)}"

        # Folders within the vault to ignore when indexing metadata
        exclude_paths = [".git", ".obsidian"]

        # Location to add new metadata. One of:
        #    TOP:            Directly after frontmatter.
        #    AFTER_TITLE:    After the first header following frontmatter.
        #    BOTTOM:         The bottom of the note
        insert_location = "BOTTOM\"
        """

    assert config_file.exists() is True
    assert content == dedent(sample_config)

    new_config = Config(config_path=config_file)
    assert new_config.config == {
        "Vault 1": {
            "path": str(fake_vault),
            "exclude_paths": [".git", ".obsidian"],
            "insert_location": "BOTTOM",
        }
    }
