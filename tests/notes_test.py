# type: ignore
"""Test notes.py."""

import re
from pathlib import Path

import pytest
import typer

from obsidian_metadata.models.enums import MetadataType
from obsidian_metadata.models.notes import Note
from tests.helpers import Regex


def test_note_not_exists() -> None:
    """Test target not found."""
    with pytest.raises(typer.Exit):
        note = Note(note_path="nonexistent_file.md")

        assert note.note_path == "tests/test_data/test_note.md"
        assert note.file_content == "This is a test note."
        assert note.frontmatter == {}
        assert note.inline_tags == []
        assert note.inline_metadata == {}
        assert note.dry_run is False


def test_note_create(sample_note) -> None:
    """Test creating note class."""
    note = Note(note_path=sample_note, dry_run=True)
    assert note.note_path == Path(sample_note)

    assert note.dry_run is True
    assert "Lorem ipsum dolor" in note.file_content
    assert note.frontmatter.dict == {
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value1"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
    }

    assert note.inline_tags.list == [
        "inline_tag_bottom1",
        "inline_tag_bottom2",
        "inline_tag_top1",
        "inline_tag_top2",
        "intext_tag1",
        "intext_tag2",
        "shared_tag",
    ]
    assert note.inline_metadata.dict == {
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "emoji_📅_key": ["emoji_📅_key_value"],
        "intext_key": ["intext_value"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value2"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value_as_link"],
    }

    with sample_note.open():
        content = sample_note.read_text()

    assert note.file_content == content
    assert note.original_file_content == content


def test_append(sample_note) -> None:
    """Test appending to note."""
    note = Note(note_path=sample_note)
    assert note.dry_run is False

    string = "This is a test string."
    string2 = "Lorem ipsum dolor sit"

    note.append(string_to_append=string)
    assert string in note.file_content
    assert len(re.findall(re.escape(string), note.file_content)) == 1

    note.append(string_to_append=string)
    assert string in note.file_content
    assert len(re.findall(re.escape(string), note.file_content)) == 1

    note.append(string_to_append=string, allow_multiple=True)
    assert string in note.file_content
    assert len(re.findall(re.escape(string), note.file_content)) == 2

    note.append(string_to_append=string2)
    assert string2 in note.file_content
    assert len(re.findall(re.escape(string2), note.file_content)) == 1

    note.append(string_to_append=string2, allow_multiple=True)
    assert string2 in note.file_content
    assert len(re.findall(re.escape(string2), note.file_content)) == 2


def test_add_metadata(sample_note) -> None:
    """Test adding metadata."""
    note = Note(note_path=sample_note)
    assert note.add_metadata(MetadataType.FRONTMATTER, "frontmatter_Key1") is False
    assert note.add_metadata(MetadataType.FRONTMATTER, "shared_key1", "shared_key1_value") is False
    assert note.add_metadata(MetadataType.FRONTMATTER, "new_key1") is True
    assert note.frontmatter.dict == {
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "new_key1": [],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value1"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
    }
    assert note.add_metadata(MetadataType.FRONTMATTER, "new_key2", "new_key2_value") is True
    assert note.frontmatter.dict == {
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "new_key1": [],
        "new_key2": ["new_key2_value"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value1"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
    }
    assert (
        note.add_metadata(
            MetadataType.FRONTMATTER, "new_key2", ["new_key2_value2", "new_key2_value3"]
        )
        is True
    )
    assert note.frontmatter.dict == {
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "new_key1": [],
        "new_key2": ["new_key2_value", "new_key2_value2", "new_key2_value3"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value1"],
        "tags": [
            "frontmatter_tag1",
            "frontmatter_tag2",
            "shared_tag",
            "📅/frontmatter_tag3",
        ],
    }


def test_contains_inline_tag(sample_note) -> None:
    """Test contains inline tag."""
    note = Note(note_path=sample_note)
    assert note.contains_inline_tag("intext_tag1") is True
    assert note.contains_inline_tag("nonexistent_tag") is False
    assert note.contains_inline_tag(r"\d$", is_regex=True) is True
    assert note.contains_inline_tag(r"^\d", is_regex=True) is False


def test_contains_metadata(sample_note) -> None:
    """Test contains metadata."""
    note = Note(note_path=sample_note)

    assert note.contains_metadata("no key") is False
    assert note.contains_metadata("frontmatter_Key2") is True
    assert note.contains_metadata(r"^\d", is_regex=True) is False
    assert note.contains_metadata(r"^[\w_]+\d", is_regex=True) is True
    assert note.contains_metadata("frontmatter_Key2", "no value") is False
    assert note.contains_metadata("frontmatter_Key2", "article") is True
    assert note.contains_metadata("bottom_key1", "bottom_key1_value") is True
    assert note.contains_metadata(r"bottom_key\d$", r"bottom_key\d_value", is_regex=True) is True


def test_delete_inline_metadata(sample_note) -> None:
    """Test deleting inline metadata."""
    note = Note(note_path=sample_note)

    note._delete_inline_metadata("nonexistent_key")
    assert note.file_content == note.original_file_content
    note._delete_inline_metadata("frontmatter_Key1")
    assert note.file_content == note.original_file_content

    note._delete_inline_metadata("intext_key")
    assert note.file_content == Regex(r"dolore eu  fugiat", re.DOTALL)

    note._delete_inline_metadata("bottom_key2", "bottom_key2_value")
    assert note.file_content != Regex(r"bottom_key2_value")
    assert note.file_content == Regex(r"bottom_key2::")
    note._delete_inline_metadata("bottom_key1")
    assert note.file_content != Regex(r"bottom_key1::")


def test_delete_inline_tag(sample_note) -> None:
    """Test deleting inline tags."""
    note = Note(note_path=sample_note)

    assert note.delete_inline_tag("not_a_tag") is False
    assert note.delete_inline_tag("intext_tag[1]") is True
    assert "intext_tag1" not in note.inline_tags.list
    assert note.file_content == Regex("consequat.  Duis")


def test_delete_metadata(sample_note) -> Note:
    """Test deleting metadata."""
    note = Note(note_path=sample_note)

    assert note.delete_metadata("nonexistent_key") is False
    assert note.delete_metadata("frontmatter_Key1", "no value") is False
    assert note.delete_metadata("frontmatter_Key1") is True
    assert "frontmatter_Key1" not in note.frontmatter.dict

    assert note.delete_metadata("frontmatter_Key2", "article") is True
    assert note.frontmatter.dict["frontmatter_Key2"] == ["note"]

    assert note.delete_metadata("bottom_key1", "bottom_key1_value") is True
    assert note.inline_metadata.dict["bottom_key1"] == []
    assert note.file_content == Regex(r"bottom_key1::\n")

    assert note.delete_metadata("bottom_key2") is True
    assert "bottom_key2" not in note.inline_metadata.dict
    assert note.file_content != Regex(r"bottom_key2")


def test_has_changes(sample_note) -> None:
    """Test has changes."""
    note = Note(note_path=sample_note)

    assert note.has_changes() is False
    note.append("This is a test string.")
    assert note.has_changes() is True

    note = Note(note_path=sample_note)
    assert note.has_changes() is False
    note.delete_metadata("frontmatter_Key1")
    assert note.has_changes() is True

    note = Note(note_path=sample_note)
    assert note.has_changes() is False
    note.delete_metadata("bottom_key2")
    assert note.has_changes() is True

    note = Note(note_path=sample_note)
    assert note.has_changes() is False
    note.delete_inline_tag("intext_tag1")
    assert note.has_changes() is True


def test_print_note(sample_note, capsys) -> None:
    """Test printing note."""
    note = Note(note_path=sample_note)
    note.print_note()
    captured = capsys.readouterr()
    assert "```python" in captured.out
    assert "---" in captured.out
    assert "#shared_tag" in captured.out


def test_print_diff(sample_note, capsys) -> None:
    """Test printing diff."""
    note = Note(note_path=sample_note)

    note.append("This is a test string.")
    note.print_diff()
    captured = capsys.readouterr()
    assert "+ This is a test string." in captured.out

    note.sub("The quick brown fox", "The quick brown hedgehog")
    note.print_diff()
    captured = capsys.readouterr()
    assert "- The quick brown fox" in captured.out
    assert "+ The quick brown hedgehog" in captured.out


def test_sub(sample_note) -> None:
    """Test substituting text in a note."""
    note = Note(note_path=sample_note)
    note.sub("#shared_tag", "#unshared_tags", is_regex=True)
    assert note.file_content != Regex(r"#shared_tag")
    assert note.file_content == Regex(r"#unshared_tags")

    note.sub(" ut ", "")
    assert note.file_content != Regex(r" ut ")
    assert note.file_content == Regex(r"laboriosam, nisialiquid ex ea")


def test_rename_inline_tag(sample_note) -> None:
    """Test renaming an inline tag."""
    note = Note(note_path=sample_note)

    assert note.rename_inline_tag("no_note_tag", "intext_tag2") is False
    assert note.rename_inline_tag("intext_tag1", "intext_tag26") is True
    assert note.inline_tags.list == [
        "inline_tag_bottom1",
        "inline_tag_bottom2",
        "inline_tag_top1",
        "inline_tag_top2",
        "intext_tag2",
        "intext_tag26",
        "shared_tag",
    ]
    assert note.file_content == Regex(r"#intext_tag26")
    assert note.file_content != Regex(r"#intext_tag1")


def test_rename_inline_metadata(sample_note) -> None:
    """Test renaming inline metadata."""
    note = Note(note_path=sample_note)

    note._rename_inline_metadata("nonexistent_key", "new_key")
    assert note.file_content == note.original_file_content
    note._rename_inline_metadata("bottom_key1", "no_value", "new_value")
    assert note.file_content == note.original_file_content

    note._rename_inline_metadata("bottom_key1", "new_key")
    assert note.file_content != Regex(r"bottom_key1::")
    assert note.file_content == Regex(r"new_key::")

    note._rename_inline_metadata("emoji_📅_key", "emoji_📅_key_value", "new_value")
    assert note.file_content != Regex(r"emoji_📅_key:: ?emoji_📅_key_value")
    assert note.file_content == Regex(r"emoji_📅_key:: ?new_value")


def test_rename_metadata(sample_note) -> None:
    """Test renaming metadata."""
    note = Note(note_path=sample_note)

    assert note.rename_metadata("nonexistent_key", "new_key") is False
    assert note.rename_metadata("frontmatter_Key1", "nonexistent_value", "article") is False

    assert note.rename_metadata("frontmatter_Key1", "new_key") is True
    assert "frontmatter_Key1" not in note.frontmatter.dict
    assert "new_key" in note.frontmatter.dict
    assert note.frontmatter.dict["new_key"] == ["author name"]
    assert note.file_content == Regex(r"new_key: author name")

    assert note.rename_metadata("frontmatter_Key2", "article", "new_key") is True
    assert note.frontmatter.dict["frontmatter_Key2"] == ["new_key", "note"]
    assert note.file_content == Regex(r"  - new_key")
    assert note.file_content != Regex(r"  - article")

    assert note.rename_metadata("bottom_key1", "new_key") is True
    assert "bottom_key1" not in note.inline_metadata.dict
    assert "new_key" in note.inline_metadata.dict
    assert note.file_content == Regex(r"new_key:: bottom_key1_value")

    assert note.rename_metadata("new_key", "bottom_key1_value", "new_value") is True
    assert note.inline_metadata.dict["new_key"] == ["new_value"]
    assert note.file_content == Regex(r"new_key:: new_value")


def test_replace_frontmatter(sample_note) -> None:
    """Test replacing frontmatter."""
    note = Note(note_path=sample_note)

    note.rename_metadata("frontmatter_Key1", "author name", "some_new_key_here")
    note.replace_frontmatter()
    new_frontmatter = """---
date_created: '2022-12-22'
tags:
  - frontmatter_tag1
  - frontmatter_tag2
  - shared_tag
  - 📅/frontmatter_tag3
frontmatter_Key1: some_new_key_here
frontmatter_Key2:
  - article
  - note
shared_key1: shared_key1_value
shared_key2: shared_key2_value1
---"""
    assert new_frontmatter in note.file_content
    assert "# Heading 1" in note.file_content
    assert "```python" in note.file_content

    note2 = Note(note_path="tests/fixtures/test_vault/no_metadata.md")
    note2.replace_frontmatter()
    note2.frontmatter.dict = {"key1": "value1", "key2": "value2"}
    note2.replace_frontmatter()
    new_frontmatter = """---
key1: value1
key2: value2
---"""
    assert new_frontmatter in note2.file_content
    assert "Lorem ipsum dolor sit amet" in note2.file_content


def test_write(sample_note, tmp_path) -> None:
    """Test writing note to file."""
    note = Note(note_path=sample_note)
    note.sub(pattern="Heading 1", replacement="Heading 2")

    note.write()
    note = Note(note_path=sample_note)
    assert "Heading 2" in note.file_content
    assert "Heading 1" not in note.file_content

    new_path = Path(tmp_path / "new_note.md")
    note.write(new_path)
    note2 = Note(note_path=new_path)
    assert "Heading 2" in note2.file_content
    assert "Heading 1" not in note2.file_content
