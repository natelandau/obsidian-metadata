# type: ignore
"""Tests for the Vault module."""

from pathlib import Path

from obsidian_frontmatter._utils import Vault
from tests.helpers import Regex


def test_vault_info(sample_vault, capsys):
    """Test printing vault information."""
    vault_path = sample_vault

    vault = Vault(vault=vault_path)
    vault.info()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Vault +\│ /[\d\w]+")
    assert captured.out == Regex(r"Number of notes +\│ \d+")
    assert captured.out == Regex(r"Backup +\│ None")


def test_vault_backup(sample_vault, capsys):
    """Test backing up the vault."""
    vault_path = sample_vault

    vault = Vault(vault=vault_path)
    vault.backup()

    captured = capsys.readouterr()
    assert Path(f"{vault_path}.bak").exists() is True
    assert captured.out == Regex(r"Vault backed up to:[\s ]+/[\d\w]+")

    vault.info()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Vault +\│ /[\d\w]+")
    assert captured.out == Regex(r"Number of notes +\│ \d+")
    assert captured.out == Regex(r"Backup path +\│[\s ]+/[\d\w]+")


def test_vault_delete_backup(sample_vault, capsys):
    """Test deleting the vault backup."""
    vault_path = sample_vault

    vault = Vault(vault=vault_path)
    vault.backup()
    vault.delete_backup()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Backup deleted")
    assert Path(f"{vault_path}.bak").exists() is False

    vault.info()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Vault +\│ /[\d\w]+")
    assert captured.out == Regex(r"Number of notes +\│ \d+")
    assert captured.out == Regex(r"Backup +\│ None")
