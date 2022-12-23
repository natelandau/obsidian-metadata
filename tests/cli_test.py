# type: ignore
"""Test obsidian-metadata CLI."""

from typer.testing import CliRunner

from obsidian_metadata.cli import app
from tests.helpers import Regex

runner = CliRunner()


def test_version() -> None:
    """Test printing version and then exiting."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output == Regex(r"obsidian_metadata: v\d+\.\d+\.\d+$")
