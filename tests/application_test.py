# type: ignore
"""Tests for the application module."""


from obsidian_metadata._config import Config
from obsidian_metadata.models.application import Application


def test_load_vault(test_vault) -> None:
    """Test application."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    app = Application(config=vault_config, dry_run=False)
    app.load_vault()

    assert app.dry_run is False
    assert app.config == vault_config
    assert app.vault.num_notes() == 3
