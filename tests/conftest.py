# type: ignore
"""Fixtures for tests."""

import shutil
from pathlib import Path

import pytest

from obsidian_metadata._config import Config
from obsidian_metadata.models.application import Application


def remove_all(root: Path):
    """Remove all files and directories in a directory."""
    for path in root.iterdir():
        if path.is_file():
            print(f"Deleting the file: {path}")
            path.unlink()
        else:
            remove_all(path)
    print(f"Deleting the empty dir: {root}")
    root.rmdir()


@pytest.fixture()
def sample_note(tmp_path) -> Path:
    """Fixture which creates a temporary note file."""
    source_file: Path = Path("tests/fixtures/test_vault/test1.md")
    if not source_file.exists():
        raise FileNotFoundError(f"Original file not found: {source_file}")

    dest_file: Path = Path(tmp_path / source_file.name)
    shutil.copy(source_file, dest_file)
    yield dest_file

    # after test - remove fixtures
    dest_file.unlink()


@pytest.fixture()
def short_notes(tmp_path) -> Path:
    """Fixture which creates two temporary note files.

    Yields:
        Tuple[Path, Path]: Tuple of two temporary note files.
            1. Very short note with frontmatter
            2. Very short note without any frontmatter
    """
    source_file1: Path = Path("tests/fixtures/short_textfile.md")
    source_file2: Path = Path("tests/fixtures/no_metadata.md")
    if not source_file1.exists():
        raise FileNotFoundError(f"Original file not found: {source_file1}")
    if not source_file2.exists():
        raise FileNotFoundError(f"Original file not found: {source_file2}")

    dest_file1: Path = Path(tmp_path / source_file1.name)
    dest_file2: Path = Path(tmp_path / source_file2.name)
    shutil.copy(source_file1, dest_file1)
    shutil.copy(source_file2, dest_file2)
    yield dest_file1, dest_file2

    # after test - remove fixtures
    dest_file1.unlink()
    dest_file2.unlink()


@pytest.fixture()
def sample_vault(tmp_path) -> Path:
    """Fixture which creates a sample vault."""
    source_dir = Path(__file__).parent / "fixtures" / "sample_vault"
    dest_dir = Path(tmp_path / "vault")
    backup_dir = Path(f"{dest_dir}.bak")

    if not source_dir.exists():
        raise FileNotFoundError(f"Sample vault not found: {source_dir}")

    shutil.copytree(source_dir, dest_dir)
    yield dest_dir

    # after test - remove fixtures
    shutil.rmtree(dest_dir)

    if backup_dir.exists():
        shutil.rmtree(backup_dir)


@pytest.fixture()
def test_vault(tmp_path) -> Path:
    """Fixture which creates a sample vault."""
    source_dir = Path(__file__).parent / "fixtures" / "test_vault"
    dest_dir = Path(tmp_path / "vault")
    backup_dir = Path(f"{dest_dir}.bak")

    if not source_dir.exists():
        raise FileNotFoundError(f"Sample vault not found: {source_dir}")

    shutil.copytree(source_dir, dest_dir)
    yield dest_dir

    # after test - remove fixtures
    shutil.rmtree(dest_dir)

    if backup_dir.exists():
        shutil.rmtree(backup_dir)


@pytest.fixture()
def test_application(tmp_path) -> Application:
    """Fixture which creates a sample vault."""
    source_dir = Path(__file__).parent / "fixtures" / "sample_vault"
    dest_dir = Path(tmp_path / "application")
    backup_dir = Path(f"{dest_dir}.bak")

    if not source_dir.exists():
        raise FileNotFoundError(f"Sample vault not found: {source_dir}")

    shutil.copytree(source_dir, dest_dir)
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=dest_dir)
    vault_config = config.vaults[0]
    app = Application(config=vault_config, dry_run=False)

    yield app

    # after test - remove fixtures
    shutil.rmtree(dest_dir)

    if backup_dir.exists():
        shutil.rmtree(backup_dir)
