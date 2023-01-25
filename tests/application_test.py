# type: ignore
"""Tests for the application module.

How mocking works in this test suite:

1. The main_app() method is mocked using a side effect iterable. This allows us to pass a value in the first run, and then a KeyError in the second run to exit the loop.
2. All questions are mocked using return_value. This allows us to pass in a value to the question and then the method will return that value. This is useful for testing questionary prompts without user input.
"""

import re

import pytest

from tests.helpers import Regex


def test_instantiate_application(test_application) -> None:
    """Test application."""
    app = test_application
    app.load_vault()

    assert app.dry_run is False
    assert app.config.name == "command_line_vault"
    assert app.config.exclude_paths == [".git", ".obsidian"]
    assert app.dry_run is False
    assert app.vault.num_notes() == 13


def test_abort(test_application, mocker, capsys) -> None:
    """Test renaming a key."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        return_value="abort",
    )

    app.main_app()
    captured = capsys.readouterr()
    assert "Vault Info" in captured.out
    assert "Done!" in captured.out


def test_list_notes(test_application, mocker, capsys) -> None:
    """Test renaming a key."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["list_notes", KeyError],
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert "04 no metadata/no_metadata_1.md" in captured.out
    assert "02 inline/inline 2.md" in captured.out
    assert "+inbox/Untitled.md" in captured.out
    assert "00 meta/templates/data sample.md" in captured.out


def test_all_metadata(test_application, mocker, capsys) -> None:
    """Test renaming a key."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["all_metadata", KeyError],
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    expected = re.escape("┃ Keys               ┃ Values")
    assert captured.out == Regex(expected)
    expected = re.escape("Inline Tags        │ breakfast")
    assert captured.out == Regex(expected)


def test_filter_notes(test_application, mocker, capsys) -> None:
    """Test renaming a key."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["filter_notes", "list_notes", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_filter_path",
        return_value="inline",
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert "04 no metadata/no_metadata_1.md" not in captured.out
    assert "02 inline/inline 1.md" in captured.out
    assert "02 inline/inline 2.md" in captured.out
    assert "+inbox/Untitled.md" not in captured.out
    assert "00 meta/templates/data sample.md" not in captured.out


def test_rename_key_success(test_application, mocker, capsys) -> None:
    """Test renaming a key."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["rename_key", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_key",
        return_value="tags",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_new_key",
        return_value="new_tags",
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"Renamed.*tags.*to.*new_tags.*in.*\d+.*notes", re.DOTALL)


def test_rename_key_fail(test_application, mocker, capsys) -> None:
    """Test renaming a key."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["rename_key", KeyError],
    )

    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_key",
        return_value="tag",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_new_key",
        return_value="new_tags",
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert "WARNING  | No notes were changed" in captured.out


def test_rename_inline_tag_success(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["rename_inline_tag", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_inline_tag",
        return_value="breakfast",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_new_tag",
        return_value="new_tag",
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"Renamed.*breakfast.*to.*new_tag.*in.*\d+.*notes", re.DOTALL)


def test_rename_inline_tag_fail(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["rename_inline_tag", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_inline_tag",
        return_value="not_a_tag",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_new_tag",
        return_value="new_tag",
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"WARNING +\| No notes were changed", re.DOTALL)


def test_delete_inline_tag_success(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["delete_inline_tag", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_inline_tag",
        return_value="breakfast",
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"SUCCESS +\| Deleted.*\d+.*notes", re.DOTALL)


def test_delete_inline_tag_fail(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["delete_inline_tag", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_inline_tag",
        return_value="not_a_tag_in_vault",
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"WARNING +\| No notes were changed", re.DOTALL)


def test_delete_key_success(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["delete_key", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_keys_regex",
        return_value=r"d\w+",
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(
        r"SUCCESS +\|.*Deleted.*keys.*matching:.*d\\w\+.*from.*10", re.DOTALL
    )


def test_delete_key_fail(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["delete_key", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_keys_regex",
        return_value=r"\d{7}",
    )

    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"WARNING +\| No notes found with a.*key.*matching", re.DOTALL)


def test_rename_value_success(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["rename_value", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_key",
        return_value="area",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_value",
        return_value="frontmatter",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_new_value",
        return_value="new_key",
    )
    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(
        r"SUCCESS  | Renamed 'area:frontmatter' to 'area:new_key'", re.DOTALL
    )
    assert captured.out == Regex(r".*in.*\d+.*notes.*", re.DOTALL)


def test_rename_value_fail(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["rename_value", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_key",
        return_value="area",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_value",
        return_value="not_exists",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_new_value",
        return_value="new_key",
    )
    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"WARNING +\| No notes were changed", re.DOTALL)


def test_delete_value_success(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["delete_value", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_key",
        return_value="area",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_value_regex",
        return_value=r"^front\w+$",
    )
    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(
        r"SUCCESS +\| Deleted value.*\^front\\w\+\$.*from.*key.*area.*in.*\d+.*notes", re.DOTALL
    )


def test_delete_value_fail(test_application, mocker, capsys) -> None:
    """Test renaming an inline tag."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["delete_value", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_key",
        return_value="area",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_value_regex",
        return_value=r"\d{7}",
    )
    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"WARNING +\| No notes found matching:", re.DOTALL)


def test_review_no_changes(test_application, mocker, capsys) -> None:
    """Review changes when no changes to vault."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["review_changes", KeyError],
    )
    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"INFO +\| No changes to review", re.DOTALL)


def test_review_changes(test_application, mocker, capsys) -> None:
    """Review changes when no changes to vault."""
    app = test_application
    app.load_vault()
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_main_application",
        side_effect=["delete_key", "review_changes", KeyError],
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_existing_keys_regex",
        return_value=r"d\w+",
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_confirm",
        return_value=True,
    )
    mocker.patch(
        "obsidian_metadata.models.application.Questions.ask_for_selection",
        side_effect=[1, "return"],
    )
    with pytest.raises(KeyError):
        app.main_app()
    captured = capsys.readouterr()
    assert captured.out == Regex(r".*Found.*\d+.*changed notes in the vault.*", re.DOTALL)
    assert "- date_created: 2022-12-22" in captured.out
    assert "+   - breakfast" in captured.out
