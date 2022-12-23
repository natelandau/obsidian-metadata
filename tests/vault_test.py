# type: ignore
"""Tests for the Vault module."""

from pathlib import Path

from obsidian_metadata._config import Config
from obsidian_metadata.models import Vault
from tests.helpers import Regex


def test_vault_creation(test_vault):
    """Test creating a Vault object."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config)

    assert vault.vault_path == vault_path
    assert vault.backup_path == Path(f"{vault_path}.bak")
    assert vault.new_vault_path == Path(f"{vault_path}.new")
    assert vault.dry_run is False
    assert str(vault.exclude_paths[0]) == Regex(r".*\.git")
    assert vault.num_notes() == 2

    assert vault.metadata.dict == {
        "Inline Tags": [
            "inline_tag_bottom1",
            "inline_tag_bottom2",
            "inline_tag_top1",
            "inline_tag_top2",
            "intext_tag1",
            "intext_tag2",
            "shared_tag",
        ],
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "date_created": ["2022-12-22"],
        "emoji_📅_key": ["emoji_📅_key_value"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_value"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value1", "shared_key2_value2"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value_as_link"],
    }


def test_get_filtered_notes(sample_vault) -> None:
    """Test filtering notes."""
    vault_path = sample_vault
    config = Config(config_path="tests/fixtures/sample_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config, path_filter="front")

    assert vault.num_notes() == 4

    vault_path = sample_vault
    config = Config(config_path="tests/fixtures/sample_vault_config.toml", vault_path=vault_path)
    vault2 = Vault(config=config, path_filter="mixed")

    assert vault2.num_notes() == 1


def test_backup(test_vault, capsys):
    """Test backing up the vault."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config, dry_run=False)

    vault.backup()

    captured = capsys.readouterr()
    assert Path(f"{vault_path}.bak").exists() is True
    assert captured.out == Regex(r"SUCCESS +| backed up to")

    vault.info()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Backup path +\│[\s ]+/[\d\w]+")


def test_backup_dryrun(test_vault, capsys):
    """Test backing up the vault."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config, dry_run=True)

    print(f"vault.dry_run: {vault.dry_run}")
    vault.backup()

    captured = capsys.readouterr()
    assert vault.backup_path.exists() is False
    assert captured.out == Regex(r"DRYRUN +| Backup up vault to")


def test_delete_backup(test_vault, capsys):
    """Test deleting the vault backup."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config, dry_run=False)

    vault.backup()
    vault.delete_backup()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Backup deleted")
    assert vault.backup_path.exists() is False

    vault.info()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Backup +\│ None")


def test_delete_backup_dryrun(test_vault, capsys):
    """Test deleting the vault backup."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config, dry_run=True)

    Path.mkdir(vault.backup_path)
    vault.delete_backup()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"DRYRUN +| Delete backup")
    assert vault.backup_path.exists() is True


def test_info(test_vault, capsys):
    """Test printing vault information."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config)

    vault.info()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Vault +\│ /[\d\w]+")
    assert captured.out == Regex(r"Notes being edited +\│ \d+")
    assert captured.out == Regex(r"Backup +\│ None")


def test_contains_inline_tag(test_vault) -> None:
    """Test if the vault contains an inline tag."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config)

    assert vault.contains_inline_tag("tag") is False
    assert vault.contains_inline_tag("intext_tag2") is True


def test_contains_metadata(test_vault) -> None:
    """Test if the vault contains a metadata key."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config)

    assert vault.contains_metadata("key") is False
    assert vault.contains_metadata("top_key1") is True
    assert vault.contains_metadata("top_key1", "no_value") is False
    assert vault.contains_metadata("top_key1", "top_key1_value") is True


def test_delete_inline_tag(test_vault) -> None:
    """Test deleting an inline tag."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config)

    assert vault.delete_inline_tag("no tag") is False
    assert vault.delete_inline_tag("intext_tag2") is True
    assert vault.metadata.dict["Inline Tags"] == [
        "inline_tag_bottom1",
        "inline_tag_bottom2",
        "inline_tag_top1",
        "inline_tag_top2",
        "intext_tag1",
        "shared_tag",
    ]


def test_delete_metadata(test_vault) -> None:
    """Test deleting a metadata key/value."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config)

    assert vault.delete_metadata("no key") == 0
    assert vault.delete_metadata("top_key1", "no_value") == 0

    assert vault.delete_metadata("top_key1", "top_key1_value") == 1
    assert vault.metadata.dict["top_key1"] == []

    assert vault.delete_metadata("top_key2") == 1
    assert "top_key2" not in vault.metadata.dict


def test_rename_inline_tag(test_vault) -> None:
    """Test renaming an inline tag."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config)

    assert vault.rename_inline_tag("no tag", "new_tag") is False
    assert vault.rename_inline_tag("intext_tag2", "new_tag") is True
    assert vault.metadata.dict["Inline Tags"] == [
        "inline_tag_bottom1",
        "inline_tag_bottom2",
        "inline_tag_top1",
        "inline_tag_top2",
        "intext_tag1",
        "new_tag",
        "shared_tag",
    ]


def test_rename_metadata(test_vault) -> None:
    """Test renaming a metadata key/value."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault = Vault(config=config)

    assert vault.rename_metadata("no key", "new_key") is False
    assert vault.rename_metadata("tags", "nonexistent_value", "new_vaule") is False

    assert vault.rename_metadata("tags", "frontmatter_tag1", "new_vaule") is True
    assert vault.metadata.dict["tags"] == [
        "frontmatter_tag2",
        "new_vaule",
        "shared_tag",
        "📅/frontmatter_tag3",
    ]

    assert vault.rename_metadata("tags", "new_key") is True
    assert "tags" not in vault.metadata.dict
    assert vault.metadata.dict["new_key"] == [
        "frontmatter_tag2",
        "new_vaule",
        "shared_tag",
        "📅/frontmatter_tag3",
    ]
