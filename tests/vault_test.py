# type: ignore
"""Tests for the Vault module."""

from pathlib import Path

from obsidian_metadata._config import Config
from obsidian_metadata.models import Vault, VaultFilter
from obsidian_metadata.models.enums import MetadataType
from tests.helpers import Regex


def test_vault_creation(test_vault):
    """Test creating a Vault object."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

    assert vault.vault_path == vault_path
    assert vault.backup_path == Path(f"{vault_path}.bak")
    assert vault.dry_run is False
    assert str(vault.exclude_paths[0]) == Regex(r".*\.git")
    assert len(vault.all_notes) == 3

    assert vault.metadata.dict == {
        "Inline Tags": [
            "ignored_file_tag2",
            "inline_tag_bottom1",
            "inline_tag_bottom2",
            "inline_tag_top1",
            "inline_tag_top2",
            "intext_tag1",
            "intext_tag2",
            "shared_tag",
        ],
        "author": ["author name"],
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "date_created": ["2022-12-22"],
        "emoji_📅_key": ["emoji_📅_key_value"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "ignored_frontmatter": ["ignore_me"],
        "intext_key": ["intext_value"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value1", "shared_key2_value2"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "frontmatter_tag3",
            "ignored_file_tag1",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value_as_link"],
        "type": ["article", "note"],
    }


def test_get_filtered_notes(sample_vault) -> None:
    """Test filtering notes."""
    vault_path = sample_vault
    config = Config(config_path="tests/fixtures/sample_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]

    filters = [VaultFilter(path_filter="front")]
    vault = Vault(config=vault_config, filters=filters)
    assert len(vault.all_notes) == 13
    assert len(vault.notes_in_scope) == 4

    filters = [VaultFilter(path_filter="mixed")]
    vault = Vault(config=vault_config, filters=filters)
    assert len(vault.all_notes) == 13
    assert len(vault.notes_in_scope) == 1

    filters = [VaultFilter(key_filter="on_one_note")]
    vault = Vault(config=vault_config, filters=filters)
    assert len(vault.all_notes) == 13
    assert len(vault.notes_in_scope) == 1

    filters = [VaultFilter(key_filter="type", value_filter="book")]
    vault = Vault(config=vault_config, filters=filters)
    assert len(vault.all_notes) == 13
    assert len(vault.notes_in_scope) == 10

    filters = [VaultFilter(tag_filter="brunch")]
    vault = Vault(config=vault_config, filters=filters)
    assert len(vault.all_notes) == 13
    assert len(vault.notes_in_scope) == 1

    filters = [VaultFilter(tag_filter="brunch"), VaultFilter(path_filter="inbox")]
    vault = Vault(config=vault_config, filters=filters)
    assert len(vault.all_notes) == 13
    assert len(vault.notes_in_scope) == 0


def test_backup(test_vault, capsys):
    """Test backing up the vault."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

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
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config, dry_run=True)

    print(f"vault.dry_run: {vault.dry_run}")
    vault.backup()

    captured = capsys.readouterr()
    assert vault.backup_path.exists() is False
    assert captured.out == Regex(r"DRYRUN +| Backup up vault to")


def test_delete_backup(test_vault, capsys):
    """Test deleting the vault backup."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

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
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config, dry_run=True)

    Path.mkdir(vault.backup_path)
    vault.delete_backup()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"DRYRUN +| Delete backup")
    assert vault.backup_path.exists() is True


def test_info(test_vault, capsys):
    """Test printing vault information."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

    vault.info()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Vault +\│ /[\d\w]+")
    assert captured.out == Regex(r"Notes in scope +\│ \d+")
    assert captured.out == Regex(r"Backup +\│ None")


def test_list_editable_notes(test_vault, capsys) -> None:
    """Test listing editable notes."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

    vault.list_editable_notes()
    captured = capsys.readouterr()
    assert captured.out == Regex("Notes in current scope")
    assert captured.out == Regex(r"1 +test1\.md")


def test_contains_inline_tag(test_vault) -> None:
    """Test if the vault contains an inline tag."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

    assert vault.contains_inline_tag("tag") is False
    assert vault.contains_inline_tag("intext_tag2") is True


def test_add_metadata(test_vault) -> None:
    """Test adding metadata to the vault."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

    assert vault.add_metadata(MetadataType.FRONTMATTER, "new_key") == 3
    assert vault.metadata.dict == {
        "Inline Tags": [
            "ignored_file_tag2",
            "inline_tag_bottom1",
            "inline_tag_bottom2",
            "inline_tag_top1",
            "inline_tag_top2",
            "intext_tag1",
            "intext_tag2",
            "shared_tag",
        ],
        "author": ["author name"],
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "date_created": ["2022-12-22"],
        "emoji_📅_key": ["emoji_📅_key_value"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "ignored_frontmatter": ["ignore_me"],
        "intext_key": ["intext_value"],
        "new_key": [],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value1", "shared_key2_value2"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "frontmatter_tag3",
            "ignored_file_tag1",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value_as_link"],
        "type": ["article", "note"],
    }
    assert vault.add_metadata(MetadataType.FRONTMATTER, "new_key2", "new_key2_value") == 3
    assert vault.metadata.dict == {
        "Inline Tags": [
            "ignored_file_tag2",
            "inline_tag_bottom1",
            "inline_tag_bottom2",
            "inline_tag_top1",
            "inline_tag_top2",
            "intext_tag1",
            "intext_tag2",
            "shared_tag",
        ],
        "author": ["author name"],
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "date_created": ["2022-12-22"],
        "emoji_📅_key": ["emoji_📅_key_value"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "ignored_frontmatter": ["ignore_me"],
        "intext_key": ["intext_value"],
        "new_key": [],
        "new_key2": ["new_key2_value"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value1", "shared_key2_value2"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "frontmatter_tag3",
            "ignored_file_tag1",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value_as_link"],
        "type": ["article", "note"],
    }


def test_contains_metadata(test_vault) -> None:
    """Test if the vault contains a metadata key."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

    assert vault.contains_metadata("key") is False
    assert vault.contains_metadata("top_key1") is True
    assert vault.contains_metadata("top_key1", "no_value") is False
    assert vault.contains_metadata("top_key1", "top_key1_value") is True


def test_delete_inline_tag(test_vault) -> None:
    """Test deleting an inline tag."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

    assert vault.delete_inline_tag("no tag") == 0
    assert vault.delete_inline_tag("intext_tag2") == 2
    assert vault.metadata.dict["Inline Tags"] == [
        "ignored_file_tag2",
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
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

    assert vault.delete_metadata("no key") == 0
    assert vault.delete_metadata("top_key1", "no_value") == 0

    assert vault.delete_metadata("top_key1", "top_key1_value") == 2
    assert vault.metadata.dict["top_key1"] == []

    assert vault.delete_metadata("top_key2") == 2
    assert "top_key2" not in vault.metadata.dict


def test_rename_inline_tag(test_vault) -> None:
    """Test renaming an inline tag."""
    vault_path = test_vault
    config = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

    assert vault.rename_inline_tag("no tag", "new_tag") == 0
    assert vault.rename_inline_tag("intext_tag2", "new_tag") == 2
    assert vault.metadata.dict["Inline Tags"] == [
        "ignored_file_tag2",
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
    vault_config = config.vaults[0]
    vault = Vault(config=vault_config)

    assert vault.rename_metadata("no key", "new_key") == 0
    assert vault.rename_metadata("tags", "nonexistent_value", "new_vaule") == 0

    assert vault.rename_metadata("tags", "frontmatter_tag1", "new_vaule") == 2
    assert vault.metadata.dict["tags"] == [
        "frontmatter_tag2",
        "frontmatter_tag3",
        "ignored_file_tag1",
        "new_vaule",
        "shared_tag",
        "📅/frontmatter_tag3",
    ]

    assert vault.rename_metadata("tags", "new_key") == 2
    assert "tags" not in vault.metadata.dict
    assert vault.metadata.dict["new_key"] == [
        "frontmatter_tag2",
        "frontmatter_tag3",
        "ignored_file_tag1",
        "new_vaule",
        "shared_tag",
        "📅/frontmatter_tag3",
    ]
