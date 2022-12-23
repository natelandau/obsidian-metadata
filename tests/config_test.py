# type: ignore
"""Tests for the configuration module."""

import re
from pathlib import Path

from obsidian_metadata._config import Config


def test_first_run(tmp_path):
    """Test creating a config on first run."""
    config_file = Path(tmp_path / "config.toml")
    vault_path = Path(tmp_path / "vault/")
    vault_path.mkdir()

    config = Config(config_path=config_file, vault_path=vault_path)

    assert config_file.exists() is True
    config.write_config_value("vault", str(vault_path))
    content = config_file.read_text()
    assert config.vault_path == vault_path
    assert re.search(str(vault_path), content) is not None


def test_parse_config():
    """Test parsing a config file."""
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=None)
    assert config.vault_path == Path(Path.cwd() / "tests/fixtures/test_vault")
