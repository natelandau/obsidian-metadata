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
