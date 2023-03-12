# type: ignore
"""Test obsidian-metadata CLI."""

import shutil
from pathlib import Path

from typer.testing import CliRunner

from obsidian_metadata.cli import app

from .helpers import KeyInputs, Regex  # noqa: F401

runner = CliRunner()


def test_version() -> None:
    """Test printing version and then exiting."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output == Regex(r"obsidian_metadata: v\d+\.\d+\.\d+$")


def test_application(tmp_path) -> None:
    """Test the application."""
    source_dir = Path(__file__).parent / "fixtures" / "test_vault"
    dest_dir = Path(tmp_path / "vault")

    if not source_dir.exists():
        raise FileNotFoundError(f"Sample vault not found: {source_dir}")

    shutil.copytree(source_dir, dest_dir)

    config_path = tmp_path / "config.toml"
    result = runner.invoke(
        app,
        ["--vault-path", dest_dir, "--config-file", config_path],
        # input=KeyInputs.DOWN + KeyInputs.DOWN + KeyInputs.DOWN + KeyInputs.ENTER, # noqa: ERA001
    )

    banner = r"""
   ___  _         _     _ _
  / _ \| |__  ___(_) __| (_) __ _ _ __
 | | | | '_ \/ __| |/ _` | |/ _` | '_ \
 | |_| | |_) \__ \ | (_| | | (_| | | | |
  \___/|_.__/|___/_|\__,_|_|\__,_|_| |_|
 |  \/  | ___| |_ __ _  __| | __ _| |_ __ _
 | |\/| |/ _ \ __/ _` |/ _` |/ _` | __/ _` |
 | |  | |  __/ || (_| | (_| | (_| | || (_| |
 |_|  |_|\___|\__\__,_|\__,_|\__,_|\__\__,_|
"""

    assert banner in result.output
    assert result.exit_code == 1
