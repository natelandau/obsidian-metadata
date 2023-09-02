# type: ignore
"""Tests for the Vault module."""

import re
from pathlib import Path

import pytest
import typer

from obsidian_metadata._config import Config
from obsidian_metadata._utils.console import console
from obsidian_metadata.models import Vault, VaultFilter
from obsidian_metadata.models.enums import InsertLocation, MetadataType
from tests.helpers import Regex, strip_ansi


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
    assert vault.frontmatter == {
        "date_created": ["2022-12-22"],
        "french1": [
            "Voix ambiguë d'un cœur qui, au zéphyr, préfère les jattes de kiwis",
        ],
        "frontmatter1": ["foo"],
        "frontmatter2": ["bar", "baz", "qux"],
        "tags": ["bar", "foo"],
        "🌱": ["🌿"],
    }
    assert vault.inline_meta == {
        "french2": [
            "Voix ambiguë d'un cœur qui, au zéphyr, préfère les jattes de kiwis.",
        ],
        "inline1": ["bar baz", "foo"],
        "inline2": ["[[foo]]"],
        "inline3": ["value"],
        "inline4": ["foo"],
        "inline5": [],
        "intext1": ["foo"],
        "intext2": ["foo"],
        "key with space": ["foo"],
        "🌱": ["🌿"],
    }
    assert vault.tags == ["tag1", "tag2"]
    assert vault.exclude_paths == [
        tmp_path / "vault" / ".git",
        tmp_path / "vault" / ".obsidian",
        tmp_path / "vault" / "ignore_folder",
    ]
    assert vault.filters == []
    assert len(vault.all_note_paths) == 2
    assert len(vault.notes_in_scope) == 2


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


@pytest.mark.parametrize(
    ("meta_type", "key", "value", "expected"),
    [
        (MetadataType.FRONTMATTER, "new_key", "new_value", 2),
        (MetadataType.FRONTMATTER, "frontmatter1", "new_value", 2),
        (MetadataType.INLINE, "new_key", "new_value", 2),
        (MetadataType.INLINE, "inline5", "new_value", 2),
        (MetadataType.INLINE, "inline1", "foo", 1),
        (MetadataType.TAGS, None, "new_value", 2),
        (MetadataType.TAGS, None, "tag1", 1),
    ],
)
def test_add_metadata(test_vault, meta_type, key, value, expected):
    """Test add_metadata method.

    GIVEN a vault object
    WHEN metadata is added
    THEN add the metadata and return the number of notes updated
    """
    vault = Vault(config=test_vault)
    assert vault.add_metadata(meta_type, key, value) == expected

    if meta_type == MetadataType.FRONTMATTER:
        assert value in vault.frontmatter[key]

    if meta_type == MetadataType.INLINE:
        assert value in vault.inline_meta[key]

    if meta_type == MetadataType.TAGS:
        assert value in vault.tags


def test_backup_1(test_vault, capsys):
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


@pytest.mark.parametrize(
    ("meta_type", "key", "value", "is_regex", "expected"),
    [
        (MetadataType.FRONTMATTER, "frontmatter1", None, False, True),
        (MetadataType.FRONTMATTER, "frontmatter1", "foo", False, True),
        (MetadataType.FRONTMATTER, "no_key", None, False, False),
        (MetadataType.FRONTMATTER, "frontmatter1", "no_value", False, False),
        (MetadataType.FRONTMATTER, r"f\w+\d", None, True, True),
        (MetadataType.FRONTMATTER, r"f\w+\d", r"\w+", True, True),
        (MetadataType.FRONTMATTER, r"^\d+", None, True, False),
        (MetadataType.FRONTMATTER, r"frontmatter1", r"^\d+", True, False),
        (MetadataType.INLINE, "intext1", None, False, True),
        (MetadataType.INLINE, "intext1", "foo", False, True),
        (MetadataType.INLINE, "no_key", None, False, False),
        (MetadataType.INLINE, "intext1", "no_value", False, False),
        (MetadataType.INLINE, r"i\w+\d", None, True, True),
        (MetadataType.INLINE, r"i\w+\d", r"\w+", True, True),
        (MetadataType.INLINE, r"^\d+", None, True, False),
        (MetadataType.INLINE, r"intext1", r"^\d+", True, False),
        (MetadataType.TAGS, None, "tag1", False, True),
        (MetadataType.TAGS, None, "no tag", False, False),
        (MetadataType.TAGS, None, r"^\w+\d", True, True),
        (MetadataType.TAGS, None, r"^\d", True, False),
        ##############3
        (MetadataType.META, "frontmatter1", None, False, True),
        (MetadataType.META, "frontmatter1", "foo", False, True),
        (MetadataType.META, "no_key", None, False, False),
        (MetadataType.META, "frontmatter1", "no_value", False, False),
        (MetadataType.META, r"f\w+\d", None, True, True),
        (MetadataType.META, r"f\w+\d", r"\w+", True, True),
        (MetadataType.META, r"^\d+", None, True, False),
        (MetadataType.META, r"frontmatter1", r"^\d+", True, False),
        (MetadataType.META, r"i\w+\d", None, True, True),
        (MetadataType.ALL, None, "tag1", False, True),
        (MetadataType.ALL, None, "no tag", False, False),
        (MetadataType.ALL, None, r"^\w+\d", True, True),
        (MetadataType.ALL, None, r"^\d", True, False),
        (MetadataType.ALL, "frontmatter1", "foo", False, True),
        (MetadataType.ALL, r"i\w+\d", None, True, True),
    ],
)
def test_contains_metadata(test_vault, meta_type, key, value, is_regex, expected):
    """Test the contains_metadata method.

    GIVEN a vault object
    WHEN the contains_metadata method is called
    THEN the method returns True if the metadata is found
    """
    vault = Vault(config=test_vault)
    assert vault.contains_metadata(meta_type, key, value, is_regex) == expected


def test_commit_changes_1(test_vault, tmp_path):
    """Test committing changes to content in the vault.

    GIVEN a vault object
    WHEN the commit_changes method is called
    THEN the changes are committed to the vault
    """
    vault = Vault(config=test_vault)

    content = Path(f"{tmp_path}/vault/sample_note.md").read_text()
    assert "new_key: new_key_value" not in content
    vault.add_metadata(MetadataType.FRONTMATTER, "new_key", "new_key_value")
    vault.commit_changes()
    committed_content = Path(f"{tmp_path}/vault/sample_note.md").read_text()
    assert "new_key: new_key_value" in committed_content


def test_commit_changes_2(test_vault, tmp_path):
    """Test committing changes to content in the vault in dry run mode.

    GIVEN a vault object
    WHEN dry_run is set to True
    THEN no changes are committed to the vault
    """
    vault = Vault(config=test_vault, dry_run=True)
    content = Path(f"{tmp_path}/vault/sample_note.md").read_text()
    assert "new_key: new_key_value" not in content

    vault.add_metadata(MetadataType.FRONTMATTER, "new_key", "new_key_value")
    vault.commit_changes()
    committed_content = Path(f"{tmp_path}/vault/sample_note.md").read_text()
    assert "new_key: new_key_value" not in committed_content


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


@pytest.mark.parametrize(
    ("tag_to_delete", "expected"),
    [
        ("tag1", 1),
        ("tag2", 1),
        ("tag3", 0),
    ],
)
def test_delete_tag(test_vault, tag_to_delete, expected):
    """Test delete_tag method.

    GIVEN a vault object
    WHEN the delete_tag method is called
    THEN delete tags if found and return the number of notes updated
    """
    vault = Vault(config=test_vault)

    assert vault.delete_tag(tag_to_delete) == expected
    assert tag_to_delete not in vault.tags


@pytest.mark.parametrize(
    ("meta_type", "key_to_delete", "value_to_delete", "expected"),
    [
        (MetadataType.FRONTMATTER, "frontmatter1", "foo", 1),
        (MetadataType.FRONTMATTER, "frontmatter1", None, 1),
        (MetadataType.FRONTMATTER, "frontmatter1", "bar", 0),
        (MetadataType.FRONTMATTER, "frontmatter2", "bar", 1),
        (MetadataType.META, "frontmatter1", "foo", 1),
        (MetadataType.INLINE, "frontmatter1", "foo", 0),
        (MetadataType.INLINE, "inline1", "foo", 1),
        (MetadataType.INLINE, "inline1", None, 1),
    ],
)
def test_delete_metadata(test_vault, meta_type, key_to_delete, value_to_delete, expected):
    """Test delete_metadata method.

    GIVEN a vault object
    WHEN the delete_metadata method is called
    THEN delete metadata if found and return the number of notes updated
    """
    vault = Vault(config=test_vault)
    assert (
        vault.delete_metadata(meta_type=meta_type, key=key_to_delete, value=value_to_delete)
        == expected
    )

    if meta_type == MetadataType.FRONTMATTER or meta_type == MetadataType.META:
        if value_to_delete is None:
            assert key_to_delete not in vault.frontmatter
        elif key_to_delete in vault.frontmatter:
            assert value_to_delete not in vault.frontmatter[key_to_delete]

    if meta_type == MetadataType.INLINE or meta_type == MetadataType.META:
        if value_to_delete is None:
            assert key_to_delete not in vault.inline_meta
        elif key_to_delete in vault.inline_meta:
            assert value_to_delete not in vault.inline_meta[key_to_delete]


def test_export_csv_1(tmp_path, test_vault):
    """Test exporting the vault to a CSV file.

    GIVEN a vault object
    WHEN the export_metadata method is called with a path and export_format of csv
    THEN the vault metadata is exported to a CSV file
    """
    vault = Vault(config=test_vault)
    export_file = tmp_path / "export.csv"

    vault.export_metadata(path=export_file, export_format="csv")
    assert export_file.exists() is True
    result = export_file.read_text()
    assert "Metadata Type,Key,Value" in result
    assert "frontmatter,date_created,2022-12-22" in result
    assert "inline_metadata,🌱,🌿" in result
    assert "inline_metadata,inline5,\n" in result
    assert "tags,,tag1" in result


def test_export_csv_2(tmp_path, test_vault):
    """Test exporting the vault to a CSV file.

    GIVEN a vault object
    WHEN the export_metadata method is called with a path that does not exist and export_format of csv
    THEN an error is raised
    """
    vault = Vault(config=test_vault)
    export_file = tmp_path / "does_not_exist" / "export.csv"

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
    export_file = tmp_path / "export.json"

    vault.export_metadata(path=export_file, export_format="json")
    assert export_file.exists() is True
    result = export_file.read_text()
    assert '"frontmatter": {' in result
    assert '"inline_metadata": {' in result
    assert '"tags": [' in result


def test_export_notes_to_csv_1(tmp_path, test_vault):
    """Test export_notes_to_csv() method.

    GIVEN a vault object
    WHEN the export_notes_to_csv method is called with a path
    THEN the notes are exported to a CSV file
    """
    vault = Vault(config=test_vault)
    export_file = tmp_path / "export.csv"
    vault.export_notes_to_csv(path=export_file)
    assert export_file.exists() is True
    result = export_file.read_text()
    assert "path,type,key,value" in result
    assert "sample_note.md,FRONTMATTER,date_created,2022-12-22" in result
    assert "sample_note.md,FRONTMATTER,🌱,🌿" in result
    assert "sample_note.md,INLINE,inline2,[[foo]]" in result
    assert "sample_note.md,INLINE,inline1,bar baz" in result
    assert "sample_note.md,TAGS,,tag1" in result
    assert "sample_note.md,INLINE,inline5,\n" in result


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
    assert len(vault.notes_in_scope) == 0


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


def test_get_changed_notes(test_vault, tmp_path):
    """Test get_changed_notes() method.

    GIVEN a vault object
    WHEN the get_changed_notes method is called
    THEN the changed notes are returned
    """
    vault = Vault(config=test_vault)
    assert vault.get_changed_notes() == []
    vault.delete_metadata(key="frontmatter1", meta_type=MetadataType.FRONTMATTER)
    changed_notes = vault.get_changed_notes()
    assert len(changed_notes) == 1
    assert changed_notes[0].note_path == tmp_path / "vault" / "sample_note.md"


def test_info(test_vault, capsys):
    """Test info() method.

    GIVEN a vault object
    WHEN the info method is called
    THEN the vault info is printed
    """
    vault = Vault(config=test_vault)

    vault.info()

    captured = strip_ansi(capsys.readouterr().out)
    assert captured == Regex(r"Vault +\│ /[\d\w]+")
    assert captured == Regex(r"Notes in scope +\│ \d+")
    assert captured == Regex(r"Backup +\│ None")


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
    assert captured.out == Regex(r"\d +sample_note\.md")


def test_move_inline_metadata_1(test_vault) -> None:
    """Test move_inline_metadata() method.

    GIVEN a vault with inline metadata.
    WHEN the move_inline_metadata() method is called.
    THEN the inline metadata is moved to the top of the file.
    """
    vault = Vault(config=test_vault)

    assert vault.move_inline_metadata(location=InsertLocation.TOP) == 1


@pytest.mark.parametrize(
    ("meta_type", "expected_regex"),
    [
        (
            MetadataType.ALL,
            r"All metadata.*Keys +┃ Values +┃.*frontmatter1 +│ foo.*inline1 +│ bar baz.*tags +│ bar.*All inline tags.*#tag1.*#tag2",
        ),
        (
            MetadataType.FRONTMATTER,
            r"All frontmatter.*Keys +┃ Values +┃.*frontmatter1 +│ foo.*tags +│ bar",
        ),
        (
            MetadataType.INLINE,
            r"All inline metadata.*Keys +┃ Values +┃.*inline2 +│ \[\[foo\]\]",
        ),
        (
            MetadataType.TAGS,
            r"All inline tags.*#tag1.*#tag2",
        ),
    ],
)
def test_print_metadata(test_vault, capsys, meta_type, expected_regex) -> None:
    """Test print_metadata() method.

    GIVEN a vault object
    WHEN the print_metadata() method is called
    THEN the metadata is printed
    """
    vault = Vault(config=test_vault)
    vault.print_metadata(meta_type=meta_type)
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == Regex(expected_regex, re.DOTALL)


def test_rename_tag_1(test_vault) -> None:
    """Test rename_tag() method.

    GIVEN a vault object
    WHEN the rename_tag() method is called with a tag that is found
    THEN the inline tag is renamed
    """
    vault = Vault(config=test_vault)

    assert vault.rename_tag("tag1", "new_tag") == 1
    assert "tag1" not in vault.tags
    assert "new_tag" in vault.tags


def test_rename_tag_2(test_vault) -> None:
    """Test rename_tag() method.

    GIVEN a vault object
    WHEN the rename_tag() method is called with a tag that is not found
    THEN the inline tag is not renamed
    """
    vault = Vault(config=test_vault)

    assert vault.rename_tag("no tag", "new_tag") == 0
    assert "new_tag" not in vault.tags


@pytest.mark.parametrize(
    ("key", "value1", "value2", "expected"),
    [
        ("no key", "new_value", None, 0),
        ("frontmatter1", "no_value", "new_value", 0),
        ("frontmatter1", "foo", "new_value", 1),
        ("inline1", "foo", "new_value", 1),
        ("frontmatter1", "new_key", None, 1),
        ("inline1", "new_key", None, 1),
    ],
)
def test_rename_metadata(test_vault, key, value1, value2, expected) -> None:
    """Test rename_metadata() method.

    GIVEN a vault object
    WHEN the rename_metadata() method is called with a key or key/value that is found
    THEN the metadata is not renamed
    """
    vault = Vault(config=test_vault)

    assert vault.rename_metadata(key, value1, value2) == expected

    if expected > 0 and value2 is None:
        assert key not in vault.frontmatter
        assert key not in vault.inline_meta

    if expected > 0 and value2:
        if key in vault.frontmatter:
            assert value1 not in vault.frontmatter[key]
            assert value2 in vault.frontmatter[key]
        if key in vault.inline_meta:
            assert value1 not in vault.inline_meta[key]
            assert value2 in vault.inline_meta[key]


@pytest.mark.parametrize(
    ("begin", "end", "key", "value", "expected"),
    [
        # no matches
        (MetadataType.INLINE, MetadataType.FRONTMATTER, "no key", None, 0),
        (MetadataType.INLINE, MetadataType.FRONTMATTER, "no key", "new_value", 0),
        (MetadataType.INLINE, MetadataType.FRONTMATTER, "inline1", "new_value", 0),
        (MetadataType.FRONTMATTER, MetadataType.INLINE, "no key", None, 0),
        (MetadataType.FRONTMATTER, MetadataType.INLINE, "no key", "new_value", 0),
        (MetadataType.FRONTMATTER, MetadataType.INLINE, "frontmatter1", "new_value", 0),
        # entire keys
        (MetadataType.FRONTMATTER, MetadataType.INLINE, "frontmatter1", None, 1),
        (MetadataType.FRONTMATTER, MetadataType.INLINE, "frontmatter2", None, 1),
        (MetadataType.INLINE, MetadataType.FRONTMATTER, "inline1", None, 1),
        # specific values
        (MetadataType.FRONTMATTER, MetadataType.INLINE, "frontmatter1", "foo", 1),
        (MetadataType.INLINE, MetadataType.FRONTMATTER, "inline1", "bar baz", 1),
        (MetadataType.INLINE, MetadataType.FRONTMATTER, "inline2", "[[foo]]", 1),
    ],
)
def test_transpose_metadata_1(test_vault, begin, end, key, value, expected) -> None:
    """Test transpose_metadata() method.

    GIVEN a vault object
    WHEN the transpose_metadata() method is called
    THEN the number of notes with transposed metadata is returned and the vault metadata is updated
    """
    vault = Vault(config=test_vault)

    assert vault.transpose_metadata(begin=begin, end=end, key=key, value=value) == expected

    if expected > 0:
        if begin == MetadataType.INLINE and value is None:
            assert key not in vault.inline_meta
            assert key in vault.frontmatter
        elif begin == MetadataType.FRONTMATTER and value is None:
            assert key not in vault.frontmatter
            assert key in vault.inline_meta
        elif begin == MetadataType.INLINE and value:
            assert value in vault.frontmatter[key]
        elif begin == MetadataType.FRONTMATTER and value:
            assert value in vault.inline_meta[key]


def test_update_from_dict_1(test_vault):
    """Test update_from_dict() method.

    GIVEN a vault object and an update dictionary
    WHEN no dictionary keys match paths in the vault
    THEN no notes are updated and 0 is returned
    """
    update_dict = {
        "path1": {"type": "frontmatter", "key": "new_key", "value": "new_value"},
        "path2": {"type": "frontmatter", "key": "new_key", "value": "new_value"},
    }
    vault = Vault(config=test_vault)

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
        "sample_note.md": [
            {"type": "frontmatter", "key": "new_key", "value": "new_value"},
            {"type": "inline_metadata", "key": "new_key2", "value": "new_value"},
            {"type": "tag", "key": "", "value": "new_tag"},
        ]
    }
    assert vault.update_from_dict(update_dict) == 1

    note = vault.get_changed_notes()[0]

    assert note.note_path.name == "sample_note.md"
    assert len(note.metadata) == 3
    assert vault.frontmatter == {"new_key": ["new_value"]}
    assert vault.inline_meta == {"new_key2": ["new_value"]}
    assert vault.tags == ["new_tag"]
