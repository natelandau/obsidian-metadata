# type: ignore
"""Tests for the Vault module."""

from pathlib import Path

import pytest
import typer
from rich import print

from obsidian_metadata._config import Config
from obsidian_metadata.models import Vault, VaultFilter
from obsidian_metadata.models.enums import InsertLocation, MetadataType
from tests.helpers import Regex


def test_vault_creation(test_vault, tmp_path):
    """Test creating a Vault object.

    GIVEN a Config object
    WHEN a Vault object is created
    THEN the Vault object is created with the correct attributes.
    """
    vault = Vault(config=test_vault)

    assert vault.name == "vault"
    assert vault.insert_location == InsertLocation.TOP
    assert vault.backup_path == Path(tmp_path, "vault.bak")
    assert vault.dry_run is False
    assert str(vault.exclude_paths[0]) == Regex(r".*\.git")
    assert len(vault.all_notes) == 2

    assert vault.metadata.dict == {
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_value"],
        "key📅": ["📅_key_value"],
        "shared_key1": [
            "shared_key1_value",
            "shared_key1_value2",
            "shared_key1_value3",
        ],
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

    assert vault.metadata.tags == [
        "inline_tag_bottom1",
        "inline_tag_bottom2",
        "inline_tag_top1",
        "inline_tag_top2",
        "intext_tag1",
        "intext_tag2",
        "shared_tag",
    ]
    assert vault.metadata.inline_metadata == {
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "intext_key": ["intext_value"],
        "key📅": ["📅_key_value"],
        "shared_key1": ["shared_key1_value", "shared_key1_value2"],
        "shared_key2": ["shared_key2_value2"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value_as_link"],
    }
    assert vault.metadata.frontmatter == {
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value", "shared_key1_value3"],
        "shared_key2": ["shared_key2_value1"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
    }


def set_insert_location(test_vault):
    """Test setting a new insert location.

    GIVEN a vault object
    WHEN the insert location is changed
    THEN the insert location is changed
    """
    vault = Vault(config=test_vault)

    assert vault.name == "vault"
    assert vault.insert_location == InsertLocation.TOP
    vault.insert_location = InsertLocation.BOTTOM
    assert vault.insert_location == InsertLocation.BOTTOM


def test_add_metadata_1(test_vault) -> None:
    """Test adding metadata to the vault.

    GIVEN a vault object
    WHEN a new metadata key is added
    THEN the metadata is added to the vault
    """
    vault = Vault(config=test_vault)

    assert vault.add_metadata(MetadataType.FRONTMATTER, "new_key") == 2
    assert vault.metadata.dict == {
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_value"],
        "key📅": ["📅_key_value"],
        "new_key": [],
        "shared_key1": [
            "shared_key1_value",
            "shared_key1_value2",
            "shared_key1_value3",
        ],
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
    assert vault.metadata.frontmatter == {
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "new_key": [],
        "shared_key1": ["shared_key1_value", "shared_key1_value3"],
        "shared_key2": ["shared_key2_value1"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
    }


def test_add_metadata_2(test_vault) -> None:
    """Test adding metadata to the vault.

    GIVEN a vault object
    WHEN a new metadata key and value is added
    THEN the metadata is added to the vault
    """
    vault = Vault(config=test_vault)
    assert vault.add_metadata(MetadataType.FRONTMATTER, "new_key2", "new_key2_value") == 2
    assert vault.metadata.dict == {
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_value"],
        "key📅": ["📅_key_value"],
        "new_key2": ["new_key2_value"],
        "shared_key1": [
            "shared_key1_value",
            "shared_key1_value2",
            "shared_key1_value3",
        ],
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
    assert vault.metadata.frontmatter == {
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "new_key2": ["new_key2_value"],
        "shared_key1": ["shared_key1_value", "shared_key1_value3"],
        "shared_key2": ["shared_key2_value1"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
    }


def test_commit_changes_1(test_vault, tmp_path):
    """Test committing changes to content in the vault.

    GIVEN a vault object
    WHEN the commit_changes method is called
    THEN the changes are committed to the vault
    """
    vault = Vault(config=test_vault)

    content = Path(f"{tmp_path}/vault/test1.md").read_text()
    assert "new_key: new_key_value" not in content
    vault.add_metadata(MetadataType.FRONTMATTER, "new_key", "new_key_value")
    vault.commit_changes()
    committed_content = Path(f"{tmp_path}/vault/test1.md").read_text()
    assert "new_key: new_key_value" in committed_content


def test_commit_changes_2(test_vault, tmp_path):
    """Test committing changes to content in the vault in dry run mode.

    GIVEN a vault object
    WHEN dry_run is set to True
    THEN no changes are committed to the vault
    """
    vault = Vault(config=test_vault, dry_run=True)
    content = Path(f"{tmp_path}/vault/test1.md").read_text()
    assert "new_key: new_key_value" not in content

    vault.add_metadata(MetadataType.FRONTMATTER, "new_key", "new_key_value")
    vault.commit_changes()
    committed_content = Path(f"{tmp_path}/vault/test1.md").read_text()
    assert "new_key: new_key_value" not in committed_content


def test_backup_1(test_vault, tmp_path, capsys):
    """Test the backup method.

    GIVEN a vault object
    WHEN the backup method is called
    THEN the vault is backed up
    """
    vault = Vault(config=test_vault)

    vault.backup()

    captured = capsys.readouterr()
    assert vault.backup_path.exists() is True
    assert captured.out == Regex(r"SUCCESS +| backed up to")

    vault.info()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Backup path +\│[\s ]+/[\d\w]+")


def test_backup_2(test_vault, capsys):
    """Test the backup method.

    GIVEN a vault object
    WHEN dry_run is set to True and the backup method is called
    THEN the vault is not backed up
    """
    vault = Vault(config=test_vault, dry_run=True)

    vault.backup()

    captured = capsys.readouterr()
    assert vault.backup_path.exists() is False
    assert captured.out == Regex(r"DRYRUN +| Backup up vault to")


def test_delete_backup_1(test_vault, capsys):
    """Test deleting the vault backup.

    GIVEN a vault object
    WHEN the delete_backup method is called
    THEN the backup is deleted
    """
    vault = Vault(config=test_vault)

    vault.backup()
    vault.delete_backup()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Backup deleted")
    assert vault.backup_path.exists() is False

    vault.info()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Backup +\│ None")


def test_delete_backup_2(test_vault, capsys):
    """Test delete_backup method in dry run mode.

    GIVEN a vault object
    WHEN the dry_run is True and the delete_backup method is called
    THEN the backup is not deleted
    """
    vault = Vault(config=test_vault, dry_run=True)

    Path.mkdir(vault.backup_path)
    vault.delete_backup()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"DRYRUN +| Delete backup")
    assert vault.backup_path.exists() is True


def test_delete_inline_tag_1(test_vault) -> None:
    """Test delete_inline_tag() method.

    GIVEN a vault object
    WHEN the delete_inline_tag method is called
    THEN the inline tag is deleted
    """
    vault = Vault(config=test_vault)

    assert vault.delete_inline_tag("intext_tag2") == 1
    assert vault.metadata.tags == [
        "inline_tag_bottom1",
        "inline_tag_bottom2",
        "inline_tag_top1",
        "inline_tag_top2",
        "intext_tag1",
        "shared_tag",
    ]


def test_delete_inline_tag_2(test_vault) -> None:
    """Test delete_inline_tag() method.

    GIVEN a vault object
    WHEN the delete_inline_tag method is called with a tag that does not exist
    THEN no changes are made
    """
    vault = Vault(config=test_vault)

    assert vault.delete_inline_tag("no tag") == 0


def test_delete_metadata_1(test_vault) -> None:
    """Test deleting a metadata key/value.

    GIVEN a vault object
    WHEN the delete_metadata method is called with a key and value
    THEN the specified metadata key/value is deleted
    """
    vault = Vault(config=test_vault)

    assert vault.delete_metadata("top_key1", "top_key1_value") == 1
    assert vault.metadata.dict["top_key1"] == []


def test_delete_metadata_2(test_vault) -> None:
    """Test deleting a metadata key/value.

    GIVEN a vault object
    WHEN the delete_metadata method is called with a key
    THEN the specified metadata key is deleted
    """
    vault = Vault(config=test_vault)

    assert vault.delete_metadata("top_key2") == 1
    assert "top_key2" not in vault.metadata.dict


def test_delete_metadata_3(test_vault) -> None:
    """Test deleting a metadata key/value.

    GIVEN a vault object
    WHEN the delete_metadata method is called with a key and/or value that does not exist
    THEN no changes are made
    """
    vault = Vault(config=test_vault)

    assert vault.delete_metadata("no key") == 0
    assert vault.delete_metadata("top_key1", "no_value") == 0


def test_export_csv_1(tmp_path, test_vault):
    """Test exporting the vault to a CSV file.

    GIVEN a vault object
    WHEN the export_metadata method is called with a path and export_format of csv
    THEN the vault metadata is exported to a CSV file
    """
    vault = Vault(config=test_vault)
    export_file = Path(f"{tmp_path}/export.csv")

    vault.export_metadata(path=export_file, export_format="csv")
    assert export_file.exists() is True
    assert "frontmatter,date_created,2022-12-22" in export_file.read_text()


def test_export_csv_2(tmp_path, test_vault):
    """Test exporting the vault to a CSV file.

    GIVEN a vault object
    WHEN the export_metadata method is called with a path that does not exist and export_format of csv
    THEN an error is raised
    """
    vault = Vault(config=test_vault)
    export_file = Path(f"{tmp_path}/does_not_exist/export.csv")

    with pytest.raises(typer.Exit):
        vault.export_metadata(path=export_file, export_format="csv")
    assert export_file.exists() is False


def test_export_json(tmp_path, test_vault):
    """Test exporting the vault to a JSON file.

    GIVEN a vault object
    WHEN the export_metadata method is called with a path and export_format of csv
    THEN the vault metadata is exported to a JSON file
    """
    vault = Vault(config=test_vault)
    export_file = Path(f"{tmp_path}/export.json")

    vault.export_metadata(path=export_file, export_format="json")
    assert export_file.exists() is True
    assert '"frontmatter": {' in export_file.read_text()


def test_export_notes_to_csv_1(tmp_path, test_vault):
    """Test export_notes_to_csv() method.

    GIVEN a vault object
    WHEN the export_notes_to_csv method is called with a path
    THEN the notes are exported to a CSV file
    """
    vault = Vault(config=test_vault)
    export_file = Path(f"{tmp_path}/export.csv")
    vault.export_notes_to_csv(path=export_file)
    assert export_file.exists() is True
    assert "path,type,key,value" in export_file.read_text()
    assert "test1.md,frontmatter,shared_key1,shared_key1_value" in export_file.read_text()
    assert "test1.md,inline_metadata,shared_key1,shared_key1_value" in export_file.read_text()
    assert "test1.md,tag,,shared_tag" in export_file.read_text()
    assert "test1.md,frontmatter,tags,📅/frontmatter_tag3" in export_file.read_text()
    assert "test1.md,inline_metadata,key📅,📅_key_value" in export_file.read_text()


def test_export_notes_to_csv_2(test_vault):
    """Test export_notes_to_csv() method.

    GIVEN a vault object
    WHEN the export_notes_to_csv method is called with a path where the parent directory does not exist
    THEN an error is raised
    """
    vault = Vault(config=test_vault)
    export_file = Path("/I/do/not/exist/export.csv")
    with pytest.raises(typer.Exit):
        vault.export_notes_to_csv(path=export_file)


def test_get_filtered_notes_1(sample_vault) -> None:
    """Test filtering notes.

    GIVEN a vault object
    WHEN the get_filtered_notes method is called with a path filter
    THEN the notes in scope are filtered
    """
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


def test_get_filtered_notes_2(sample_vault) -> None:
    """Test filtering notes.

    GIVEN a vault object
    WHEN the get_filtered_notes method is called with a key filter
    THEN the notes in scope are filtered
    """
    vault_path = sample_vault
    config = Config(config_path="tests/fixtures/sample_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]

    filters = [VaultFilter(key_filter="on_one_note")]
    vault = Vault(config=vault_config, filters=filters)
    assert len(vault.all_notes) == 13
    assert len(vault.notes_in_scope) == 1


def test_get_filtered_notes_3(sample_vault) -> None:
    """Test filtering notes.

    GIVEN a vault object
    WHEN the get_filtered_notes method is called with a key and a value filter
    THEN the notes in scope are filtered
    """
    vault_path = sample_vault
    config = Config(config_path="tests/fixtures/sample_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    filters = [VaultFilter(key_filter="type", value_filter="book")]
    vault = Vault(config=vault_config, filters=filters)
    assert len(vault.all_notes) == 13
    assert len(vault.notes_in_scope) == 10


def test_get_filtered_notes_4(sample_vault) -> None:
    """Test filtering notes.

    GIVEN a vault object
    WHEN the get_filtered_notes method is called with a tag filter
    THEN the notes in scope are filtered
    """
    vault_path = sample_vault
    config = Config(config_path="tests/fixtures/sample_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    filters = [VaultFilter(tag_filter="brunch")]
    vault = Vault(config=vault_config, filters=filters)
    assert len(vault.all_notes) == 13
    assert len(vault.notes_in_scope) == 1


def test_get_filtered_notes_5(sample_vault) -> None:
    """Test filtering notes.

    GIVEN a vault object
    WHEN the get_filtered_notes method is called with a tag and a path filter
    THEN the notes in scope are filtered
    """
    vault_path = sample_vault
    config = Config(config_path="tests/fixtures/sample_vault_config.toml", vault_path=vault_path)
    vault_config = config.vaults[0]
    filters = [VaultFilter(tag_filter="brunch"), VaultFilter(path_filter="inbox")]
    vault = Vault(config=vault_config, filters=filters)
    assert len(vault.all_notes) == 13
    assert len(vault.notes_in_scope) == 0


def test_info(test_vault, capsys):
    """Test info() method.

    GIVEN a vault object
    WHEN the info method is called
    THEN the vault info is printed
    """
    vault = Vault(config=test_vault)

    vault.info()

    captured = capsys.readouterr()
    assert captured.out == Regex(r"Vault +\│ /[\d\w]+")
    assert captured.out == Regex(r"Notes in scope +\│ \d+")
    assert captured.out == Regex(r"Backup +\│ None")


def test_list_editable_notes(test_vault, capsys) -> None:
    """Test list_editable_notes() method.

    GIVEN a vault object
    WHEN the list_editable_notes() method is called
    THEN the editable notes in scope are printed
    """
    vault = Vault(config=test_vault)

    vault.list_editable_notes()
    captured = capsys.readouterr()
    assert captured.out == Regex("Notes in current scope")
    assert captured.out == Regex(r"\d +test1\.md")


def test_move_inline_metadata_1(test_vault) -> None:
    """Test move_inline_metadata() method.

    GIVEN a vault with inline metadata.
    WHEN the move_inline_metadata() method is called.
    THEN the inline metadata is moved to the top of the file.
    """
    vault = Vault(config=test_vault)

    assert vault.move_inline_metadata(location=InsertLocation.TOP) == 1


def test_rename_inline_tag_1(test_vault) -> None:
    """Test rename_inline_tag() method.

    GIVEN a vault object
    WHEN the rename_inline_tag() method is called with a tag that is found
    THEN the inline tag is renamed
    """
    vault = Vault(config=test_vault)

    assert vault.rename_inline_tag("intext_tag2", "new_tag") == 1
    assert vault.metadata.tags == [
        "inline_tag_bottom1",
        "inline_tag_bottom2",
        "inline_tag_top1",
        "inline_tag_top2",
        "intext_tag1",
        "new_tag",
        "shared_tag",
    ]


def test_rename_inline_tag_2(test_vault) -> None:
    """Test rename_inline_tag() method.

    GIVEN a vault object
    WHEN the rename_inline_tag() method is called with a tag that is not found
    THEN the inline tag is not renamed
    """
    vault = Vault(config=test_vault)

    assert vault.rename_inline_tag("no tag", "new_tag") == 0


def test_rename_metadata_1(test_vault) -> None:
    """Test rename_metadata() method.

    GIVEN a vault object
    WHEN the rename_metadata() method is called with a key or key/value that is found
    THEN the metadata is not renamed
    """
    vault = Vault(config=test_vault)

    assert vault.rename_metadata("no key", "new_key") == 0
    assert vault.rename_metadata("tags", "nonexistent_value", "new_vaule") == 0


def test_rename_metadata_2(test_vault) -> None:
    """Test rename_metadata() method.

    GIVEN a vault object
    WHEN the rename_metadata() method with a key and no value
    THEN the metadata key is renamed
    """
    vault = Vault(config=test_vault)

    assert vault.rename_metadata("tags", "new_key") == 1
    assert "tags" not in vault.metadata.dict
    assert vault.metadata.dict["new_key"] == [
        "frontmatter_tag1",
        "frontmatter_tag2",
        "shared_tag",
        "📅/frontmatter_tag3",
    ]


def test_rename_metadata_3(test_vault) -> None:
    """Test rename_metadata() method.

    GIVEN a vault object
    WHEN the rename_metadata() method is called with a key and value
    THEN the metadata key/value is renamed
    """
    vault = Vault(config=test_vault)

    assert vault.rename_metadata("tags", "frontmatter_tag1", "new_vaule") == 1
    assert vault.metadata.dict["tags"] == [
        "frontmatter_tag2",
        "new_vaule",
        "shared_tag",
        "📅/frontmatter_tag3",
    ]


def test_transpose_metadata(test_vault) -> None:
    """Test transpose_metadata() method.

    GIVEN a vault object
    WHEN the transpose_metadata() method is called
    THEN the metadata is transposed
    """
    vault = Vault(config=test_vault)

    assert vault.transpose_metadata(begin=MetadataType.INLINE, end=MetadataType.FRONTMATTER) == 1

    assert vault.metadata.inline_metadata == {}
    assert vault.metadata.frontmatter == {
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_value"],
        "key📅": ["📅_key_value"],
        "shared_key1": [
            "shared_key1_value",
            "shared_key1_value2",
            "shared_key1_value3",
        ],
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

    assert (
        vault.transpose_metadata(
            begin=MetadataType.INLINE, end=MetadataType.FRONTMATTER, location=InsertLocation.TOP
        )
        == 0
    )


def test_update_from_dict_1(test_vault):
    """Test update_from_dict() method.

    GIVEN a vault object and an update dictionary
    WHEN no dictionary keys match paths in the vault
    THEN no notes are updated and 0 is returned
    """
    vault = Vault(config=test_vault)
    update_dict = {
        "path1": {"type": "frontmatter", "key": "new_key", "value": "new_value"},
        "path2": {"type": "frontmatter", "key": "new_key", "value": "new_value"},
    }

    assert vault.update_from_dict(update_dict) == 0
    assert vault.get_changed_notes() == []


def test_update_from_dict_2(test_vault):
    """Test update_from_dict() method.

    GIVEN a vault object and an update dictionary
    WHEN the dictionary is empty
    THEN no notes are updated and 0 is returned
    """
    vault = Vault(config=test_vault)
    update_dict = {}

    assert vault.update_from_dict(update_dict) == 0
    assert vault.get_changed_notes() == []


def test_update_from_dict_3(test_vault):
    """Test update_from_dict() method.

    GIVEN a vault object and an update dictionary
    WHEN a dictionary key matches a path in the vault
    THEN the note is updated to match the dictionary values
    """
    vault = Vault(config=test_vault)

    update_dict = {
        "test1.md": [
            {"type": "frontmatter", "key": "new_key", "value": "new_value"},
            {"type": "inline_metadata", "key": "new_key2", "value": "new_value"},
            {"type": "tags", "key": "", "value": "new_tag"},
        ]
    }
    assert vault.update_from_dict(update_dict) == 1
    assert vault.get_changed_notes()[0].note_path.name == "test1.md"
    assert vault.get_changed_notes()[0].frontmatter.dict == {"new_key": ["new_value"]}
    assert vault.get_changed_notes()[0].inline_metadata.dict == {"new_key2": ["new_value"]}
    assert vault.get_changed_notes()[0].inline_tags.list == ["new_tag"]
    assert vault.metadata.frontmatter == {"new_key": ["new_value"]}
    assert vault.metadata.inline_metadata == {"new_key2": ["new_value"]}
    assert vault.metadata.tags == ["new_tag"]
