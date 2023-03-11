# type: ignore
"""Tests for the application module.

How mocking works in this test suite:

1. The application_main() method is mocked using a side effect iterable. This allows us to pass a value in the first run, and then a KeyError in the second run to exit the loop.
2. All questions are mocked using return_value. This allows us to pass in a value to the question and then the method will return that value. This is useful for testing questionary prompts without user input.
"""

import re
from pathlib import Path

import pytest

from obsidian_metadata.models.enums import MetadataType
from tests.helpers import Regex, remove_ansi


def test_instantiate_application(test_application) -> None:
    """Test application."""
    app = test_application
    app._load_vault()

    assert app.dry_run is False
    assert app.config.name == "command_line_vault"
    assert app.config.exclude_paths == [".git", ".obsidian"]
    assert app.dry_run is False
    assert len(app.vault.all_notes) == 13


def test_abort(test_application, mocker, capsys) -> None:
    """Test renaming a key."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        return_value="abort",
    )

    app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert "Done!" in captured


def test_add_metadata_frontmatter(test_application, mocker, capsys) -> None:
    """Test adding new metadata to the vault."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["add_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_area",
        return_value=MetadataType.FRONTMATTER,
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_key",
        return_value="new_key",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_value",
        return_value="new_key_value",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r"SUCCESS +\| Added metadata to \d+ notes", re.DOTALL)


def test_add_metadata_inline(test_application, mocker, capsys) -> None:
    """Test adding new metadata to the vault."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["add_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_area",
        return_value=MetadataType.INLINE,
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_key",
        return_value="new_key",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_value",
        return_value="new_key_value",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r"SUCCESS +\| Added metadata to \d+ notes", re.DOTALL)


def test_add_metadata_tag(test_application, mocker, capsys) -> None:
    """Test adding new metadata to the vault."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["add_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_area",
        return_value=MetadataType.TAGS,
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_tag",
        return_value="new_tag",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r"SUCCESS +\| Added metadata to \d+ notes", re.DOTALL)


def test_delete_inline_tag(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["delete_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["delete_inline_tag", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_inline_tag",
        return_value="not_a_tag_in_vault",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert "WARNING  | No notes were changed" in captured

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["delete_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["delete_inline_tag", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_inline_tag",
        return_value="breakfast",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r"SUCCESS +\| Deleted inline tag: breakfast in \d+ notes", re.DOTALL)


def test_delete_key(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["delete_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["delete_key", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_keys_regex",
        return_value=r"\d{7}",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert r"WARNING  | No notes found with a key matching: \d{7}" in captured

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["delete_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["delete_key", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_keys_regex",
        return_value=r"d\w+",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r"SUCCESS  \| Deleted keys matching: d\\w\+ from \d+ notes", re.DOTALL)


def test_delete_value(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["delete_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["delete_value", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_key",
        return_value="area",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_value_regex",
        return_value=r"\d{7}",
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert r"WARNING  | No notes found matching: area: \d{7}" in captured

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["delete_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["delete_value", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_key",
        return_value="area",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_value_regex",
        return_value=r"^front\w+$",
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert r"SUCCESS  | Deleted value ^front\w+$ from key area in 4 notes" in captured


def test_filter_notes(test_application, mocker, capsys) -> None:
    """Test renaming a key."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["filter_notes", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["apply_path_filter", "list_notes", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_filter_path",
        return_value="inline",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r"SUCCESS +\| Loaded \d+ notes from \d+ total", re.DOTALL)
    assert "02 inline/inline 2.md" in captured
    assert "03 mixed/mixed 1.md" not in captured

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["filter_notes", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["apply_metadata_filter", "list_notes", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_key",
        return_value="on_one_note",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_value",
        return_value="",
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"SUCCESS +\| Loaded.*1.*notes from.*\d+.*total", re.DOTALL)
    assert "02 inline/inline 2.md" in captured.out
    assert "03 mixed/mixed 1.md" not in captured.out


def test_filter_clear(test_application, mocker, capsys) -> None:
    """Test clearing filters."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["filter_notes", "filter_notes", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["apply_metadata_filter", "list_filters", "list_notes", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_key",
        return_value="on_one_note",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_value",
        return_value="",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_number",
        return_value="1",
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert "02 inline/inline 2.md" in captured
    assert "03 mixed/mixed 1.md" in captured
    assert "01 frontmatter/frontmatter 4.md" in captured
    assert "04 no metadata/no_metadata_1.md " in captured


def test_inspect_metadata_all(test_application, mocker, capsys) -> None:
    """Test backing up a vault."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["inspect_metadata", KeyError],
    )

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["all_metadata", "back"],
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r"type +│ article", re.DOTALL)


def test_rename_inline_tag(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["rename_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["rename_inline_tag", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_inline_tag",
        return_value="not_a_tag",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_tag",
        return_value="new_tag",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert "No notes were changed" in captured

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["rename_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["rename_inline_tag", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_inline_tag",
        return_value="breakfast",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_tag",
        return_value="new_tag",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r"Renamed breakfast to new_tag in \d+ notes", re.DOTALL)


def test_rename_key(test_application, mocker, capsys) -> None:
    """Test renaming a key."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["rename_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["rename_key", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_key",
        return_value="tag",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_key",
        return_value="new_tags",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert "WARNING  | No notes were changed" in captured

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["rename_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["rename_key", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_key",
        return_value="tags",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_key",
        return_value="new_tags",
    )

    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r"Renamed tags to new_tags in \d+ notes", re.DOTALL)


def test_rename_value_fail(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["rename_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["rename_value", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_key",
        return_value="area",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_value",
        return_value="not_exists",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_value",
        return_value="new_key",
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert "WARNING  | No notes were changed" in captured

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["rename_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["rename_value", "back"],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_key",
        return_value="area",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_value",
        return_value="frontmatter",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_value",
        return_value="new_key",
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(
        r"SUCCESS +\| Renamed 'area:frontmatter' to 'area:new_key' in \d+ notes", re.DOTALL
    )


def test_review_no_changes(test_application, mocker, capsys) -> None:
    """Review changes when no changes to vault."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["review_changes", KeyError],
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert "INFO     | No changes to review" in captured


def test_review_changes(test_application, mocker, capsys) -> None:
    """Review changes when no changes to vault."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["rename_metadata", "review_changes", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_existing_key",
        return_value="tags",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_new_key",
        return_value="new_tags",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["rename_key", 1, "return"],
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r".*Found \d+ changed notes in the vault", re.DOTALL)
    assert "- tags:" in captured
    assert "+ new_tags:" in captured


def test_transpose_metadata(test_application, mocker, capsys) -> None:
    """Transpose metadata."""
    app = test_application
    app._load_vault()

    assert app.vault.metadata.inline_metadata["inline_key"] == ["inline_key_value"]
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["transpose_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["inline_to_frontmatter", "transpose_all"],
    )
    with pytest.raises(KeyError):
        app.application_main()
    assert app.vault.metadata.inline_metadata == {}
    assert app.vault.metadata.frontmatter["inline_key"] == ["inline_key_value"]
    captured = remove_ansi(capsys.readouterr().out)
    assert "SUCCESS  | Transposed Inline Metadata to Frontmatter in 5 notes" in captured

    app = test_application
    app._load_vault()

    assert app.vault.metadata.frontmatter["date_created"] == ["2022-12-21", "2022-12-22"]
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["transpose_metadata", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["frontmatter_to_inline", "transpose_all"],
    )
    with pytest.raises(KeyError):
        app.application_main()
    assert app.vault.metadata.inline_metadata["date_created"] == ["2022-12-21", "2022-12-22"]
    assert app.vault.metadata.frontmatter == {}


def test_vault_backup(test_application, mocker, capsys) -> None:
    """Test backing up a vault."""
    app = test_application
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["vault_actions", KeyError],
    )

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["backup_vault", "back"],
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(
        r"SUCCESS +\| Vault backed up to:[-\w\d\/\s]+application\.bak", re.DOTALL
    )


def test_vault_delete(test_application, mocker, capsys, tmp_path) -> None:
    """Test backing up a vault."""
    app = test_application
    backup_path = Path(tmp_path / "application.bak")
    backup_path.mkdir()
    app._load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_application_main",
        side_effect=["vault_actions", KeyError],
    )

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_selection",
        side_effect=["delete_backup", "back"],
    )
    with pytest.raises(KeyError):
        app.application_main()
    captured = remove_ansi(capsys.readouterr().out)
    assert captured == Regex(r"SUCCESS +\| Backup deleted", re.DOTALL)
