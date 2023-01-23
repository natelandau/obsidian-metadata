# type: ignore
"""Test obsidian-metadata CLI."""

from typer.testing import CliRunner

from obsidian_metadata.cli import app

from .helpers import KeyInputs, Regex  # noqa: F401

runner = CliRunner()


def test_version() -> None:
    """Test printing version and then exiting."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output == Regex(r"obsidian_metadata: v\d+\.\d+\.\d+$")


def test_application(test_vault, tmp_path) -> None:
    """Test the application."""
    vault_path = test_vault
    config_path = tmp_path / "config.toml"
    result = runner.invoke(
        app,
        ["--vault-path", vault_path, "--config-file", config_path],
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
