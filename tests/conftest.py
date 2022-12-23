# type: ignore
"""Fixtures for tests."""

import shutil
from pathlib import Path

import pytest


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
