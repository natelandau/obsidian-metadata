# type: ignore
"""Test notes.py."""

import re
from pathlib import Path

import pytest
import typer

from obsidian_metadata.models.enums import InsertLocation, MetadataType
from obsidian_metadata.models.notes import Note
from tests.helpers import Regex


def test_note_not_exists() -> None:
    """Test target not found.

    GIVEN a path to a non-existent file
    WHEN a Note object is created pointing to that file
    THEN a typer.Exit exception is raised
    """
    with pytest.raises(typer.Exit):
        Note(note_path="nonexistent_file.md")


def test_create_note_1(sample_note):
    """Test creating a note object.

    GIVEN a path to a markdown file
    WHEN a Note object is created pointing to that file
    THEN the Note object is created
    """
    note = Note(note_path=sample_note, dry_run=True)
    assert note.note_path == Path(sample_note)
    assert note.dry_run is True
    assert "Lorem ipsum dolor" in note.file_content
    assert note.frontmatter.dict == {
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
        "intext_key": ["intext_value"],
        "key📅": ["📅_key_value"],
        "shared_key1": ["shared_key1_value", "shared_key1_value2"],
        "shared_key2": ["shared_key2_value2"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value_as_link"],
    }

    with sample_note.open():
        content = sample_note.read_text()

    assert note.file_content == content
    assert note.original_file_content == content


def test_create_note_2() -> None:
    """Test creating a note object.

    GIVEN a text file with invalid frontmatter
    WHEN the note is initialized
    THEN a typer exit is raised
    """
    broken_fm = Path("tests/fixtures/broken_frontmatter.md")
    with pytest.raises(typer.Exit):
        Note(note_path=broken_fm)


def test_add_metadata_method_1(short_notes):
    """Test adding metadata.

    GIVEN calling the add_metadata method
    WHEN a key is passed without a value
    THEN the key is added to to the InlineMetadata object and the file content
    """
    note = Note(note_path=short_notes[0])
    assert note.inline_metadata.dict == {}

    assert (
        note.add_metadata(MetadataType.INLINE, location=InsertLocation.BOTTOM, key="new_key1")
        is True
    )
    assert note.inline_metadata.dict == {"new_key1": []}
    assert "new_key1::" in note.file_content.strip()


def test_add_metadata_method_2(short_notes):
    """Test adding metadata.

    GIVEN calling the add_metadata method
    WHEN a key is passed with a value
    THEN the key and value is added to to the InlineMetadata object and the file content
    """
    note = Note(note_path=short_notes[0])
    assert note.inline_metadata.dict == {}

    assert (
        note.add_metadata(
            MetadataType.INLINE, key="new_key2", value="new_value1", location=InsertLocation.TOP
        )
        is True
    )
    assert note.inline_metadata.dict == {"new_key2": ["new_value1"]}
    assert "new_key2:: new_value1" in note.file_content


def test_add_metadata_method_3(short_notes):
    """Test adding metadata.

    GIVEN calling the add_metadata method
    WHEN a key is passed that already exists
    THEN the the method returns False
    """
    note = Note(note_path=short_notes[0])
    note.inline_metadata.dict = {"new_key1": []}
    assert (
        note.add_metadata(MetadataType.INLINE, location=InsertLocation.BOTTOM, key="new_key1")
        is False
    )


def test_add_metadata_method_4(short_notes):
    """Test adding metadata.

    GIVEN calling the add_metadata method
    WHEN a key is passed with a value that already exists
    THEN the the method returns False
    """
    note = Note(note_path=short_notes[0])
    note.inline_metadata.dict = {"new_key2": ["new_value1"]}
    assert (
        note.add_metadata(
            MetadataType.INLINE, key="new_key2", value="new_value1", location=InsertLocation.TOP
        )
        is False
    )


def test_add_metadata_method_5(sample_note):
    """Test add_metadata() method.

    GIVEN a note with frontmatter
    WHEN add_metadata() is called with a key or value that already exists in the frontmatter
    THEN the method returns False
    """
    note = Note(note_path=sample_note)
    assert note.add_metadata(MetadataType.FRONTMATTER, "frontmatter_Key1") is False
    assert note.add_metadata(MetadataType.FRONTMATTER, "shared_key1", "shared_key1_value") is False


def test_add_metadata_method_6(sample_note):
    """Test add_metadata() method.

    GIVEN a note with frontmatter
    WHEN add_metadata() is called with a new key
    THEN the key is added to the frontmatter
    """
    note = Note(note_path=sample_note)
    assert "new_key1" not in note.frontmatter.dict
    assert note.add_metadata(MetadataType.FRONTMATTER, "new_key1") is True
    assert "new_key1" in note.frontmatter.dict


def test_add_metadata_method_7(sample_note):
    """Test add_metadata() method.

    GIVEN a note with frontmatter
    WHEN add_metadata() is called with a new key and value
    THEN the key and value is added to the frontmatter
    """
    note = Note(note_path=sample_note)
    assert "new_key" not in note.frontmatter.dict
    assert note.add_metadata(MetadataType.FRONTMATTER, "new_key", "new_value") is True
    assert note.frontmatter.dict["new_key"] == ["new_value"]


def test_add_metadata_method_8(sample_note):
    """Test add_metadata() method.

    GIVEN a note with frontmatter
    WHEN add_metadata() is called with an existing key and new value
    THEN the new value is appended to the existing key
    """
    note = Note(note_path=sample_note)
    assert "new_key" not in note.frontmatter.dict
    assert note.add_metadata(MetadataType.FRONTMATTER, "new_key", "new_value") is True
    assert note.frontmatter.dict["new_key"] == ["new_value"]
    assert note.add_metadata(MetadataType.FRONTMATTER, "new_key", "new_value2") is True
    assert note.frontmatter.dict["new_key"] == ["new_value", "new_value2"]


def test_add_metadata_method_9(sample_note):
    """Test add_metadata() method.

    GIVEN a note object
    WHEN add_metadata() is with an existing tag
    THEN the method returns False
    """
    note = Note(note_path=sample_note)
    assert (
        note.add_metadata(MetadataType.TAGS, value="shared_tag", location=InsertLocation.TOP)
        is False
    )


def test_add_metadata_method_10(sample_note):
    """Test add_metadata() method.

    GIVEN a note object
    WHEN add_metadata() is with a new tag
    THEN the tag is added to the InlineTags object and the file content
    """
    note = Note(note_path=sample_note)
    assert "new_tag" not in note.inline_tags.list
    assert (
        note.add_metadata(MetadataType.TAGS, value="new_tag", location=InsertLocation.TOP) is True
    )
    assert "new_tag" in note.inline_tags.list
    assert "#new_tag" in note.file_content


def test_commit_1(sample_note, tmp_path) -> None:
    """Test commit() method.

    GIVEN a note object with commit() called
    WHEN the note is modified
    THEN the updated note is committed to the file system
    """
    note = Note(note_path=sample_note)
    note.sub(pattern="Heading 1", replacement="Heading 2")

    note.commit()
    note = Note(note_path=sample_note)
    assert "Heading 2" in note.file_content
    assert "Heading 1" not in note.file_content

    new_path = Path(tmp_path / "new_note.md")
    note.commit(new_path)
    note2 = Note(note_path=new_path)
    assert "Heading 2" in note2.file_content
    assert "Heading 1" not in note2.file_content


def test_commit_2(sample_note, tmp_path) -> None:
    """Test commit() method.

    GIVEN a note object with commit() called
    WHEN the note is modified and dry_run is True
    THEN the note is not committed to the file system
    """
    note = Note(note_path=sample_note, dry_run=True)
    note.sub(pattern="Heading 1", replacement="Heading 2")

    note.commit()
    note = Note(note_path=sample_note)
    assert "Heading 1" in note.file_content


def test_contains_inline_tag(sample_note) -> None:
    """Test contains_inline_tag method.

    GIVEN a note object
    WHEN contains_inline_tag() is called
    THEN the method returns True if the tag is found and False if not

    """
    note = Note(note_path=sample_note)
    assert note.contains_inline_tag("intext_tag1") is True
    assert note.contains_inline_tag("nonexistent_tag") is False
    assert note.contains_inline_tag(r"\d$", is_regex=True) is True
    assert note.contains_inline_tag(r"^\d", is_regex=True) is False


def test_contains_metadata(sample_note) -> None:
    """Test contains_metadata method.

    GIVEN a note object
    WHEN contains_metadata() is called
    THEN the method returns True if the key and/or value are found and False if not

    """
    note = Note(note_path=sample_note)

    assert note.contains_metadata("no key") is False
    assert note.contains_metadata("frontmatter_Key2") is True
    assert note.contains_metadata(r"^\d", is_regex=True) is False
    assert note.contains_metadata(r"^[\w_]+\d", is_regex=True) is True
    assert note.contains_metadata("frontmatter_Key2", "no value") is False
    assert note.contains_metadata("frontmatter_Key2", "article") is True
    assert note.contains_metadata("bottom_key1", "bottom_key1_value") is True
    assert note.contains_metadata(r"bottom_key\d$", r"bottom_key\d_value", is_regex=True) is True


def test_delete_inline_tag(sample_note) -> None:
    """Test delete_inline_tag method.

    GIVEN a note object
    WHEN delete_inline_tag() is called
    THEN the method returns True if the tag is found and deleted and False if not
    """
    note = Note(note_path=sample_note)
    assert note.delete_inline_tag("not_a_tag") is False
    assert note.delete_inline_tag("intext_tag[1]") is True
    assert "intext_tag1" not in note.inline_tags.list
    assert note.file_content == Regex("consequat.  Duis")


def test_delete_metadata_1(sample_note):
    """Test delete_metadata() method.

    GIVEN a note object
    WHEN delete_metadata() is called with a keys or values that do not exist
    THEN the method returns False
    """
    note = Note(note_path=sample_note)
    assert note.delete_metadata("nonexistent_key") is False
    assert note.delete_metadata("frontmatter_Key1", "no value") is False


def test_delete_metadata_2(sample_note):
    """Test delete_metadata() method.

    GIVEN a note object
    WHEN delete_metadata() is called with a frontmatter key and no value
    THEN the entire key and all values are deleted
    """
    note = Note(note_path=sample_note)
    assert "frontmatter_Key1" in note.frontmatter.dict
    assert note.delete_metadata("frontmatter_Key1") is True
    assert "frontmatter_Key1" not in note.frontmatter.dict


def test_delete_metadata_3(sample_note):
    """Test delete_metadata() method.

    GIVEN a note object
    WHEN delete_metadata() is called with a frontmatter key and value
    THEN the value is deleted from the key
    """
    note = Note(note_path=sample_note)
    assert note.frontmatter.dict["frontmatter_Key2"] == ["article", "note"]
    assert note.delete_metadata("frontmatter_Key2", "article") is True
    assert note.frontmatter.dict["frontmatter_Key2"] == ["note"]


def test_delete_metadata_4(sample_note):
    """Test delete_metadata() method.

    GIVEN a note object
    WHEN delete_metadata() is called with an inline key and value
    THEN the value is deleted from the InlineMetadata object and the file content
    """
    note = Note(note_path=sample_note)
    assert note.inline_metadata.dict["bottom_key1"] == ["bottom_key1_value"]
    assert note.file_content == Regex(r"bottom_key1:: bottom_key1_value\n")
    assert note.delete_metadata("bottom_key1", "bottom_key1_value") is True
    assert note.inline_metadata.dict["bottom_key1"] == []
    assert note.file_content == Regex(r"bottom_key1::\n")


def test_delete_metadata_5(sample_note):
    """Test delete_metadata() method.

    GIVEN a note object
    WHEN delete_metadata() is called with an inline key and no value
    THEN the key and all values are deleted from the InlineMetadata object and the file content
    """
    note = Note(note_path=sample_note)
    assert note.inline_metadata.dict["bottom_key2"] == ["bottom_key2_value"]
    assert note.delete_metadata("bottom_key2") is True
    assert "bottom_key2" not in note.inline_metadata.dict
    assert note.file_content != Regex(r"bottom_key2")


def test_delete_metadata_6(sample_note):
    """Test delete_metadata() method.

    GIVEN a note object
    WHEN delete_metadata() is called with an inline key and a single value
    THEN the specified value is removed from the InlineMetadata object and the file content and remaining values are untouched
    """
    note = Note(note_path=sample_note)
    assert note.inline_metadata.dict["shared_key1"] == ["shared_key1_value", "shared_key1_value2"]
    assert (
        note.delete_metadata("shared_key1", "shared_key1_value2", area=MetadataType.INLINE) is True
    )
    assert note.inline_metadata.dict["shared_key1"] == ["shared_key1_value"]
    assert note.file_content == Regex(r"shared_key1_value")
    assert note.file_content != Regex(r"shared_key1_value2")


def test_has_changes(sample_note) -> None:
    """Test has_changes() method.

    GIVEN a note object
    WHEN has_changes() is called
    THEN the method returns True if the note has changes and False if not
    """
    note = Note(note_path=sample_note)
    assert note.has_changes() is False
    note.write_string("This is a test string.", location=InsertLocation.BOTTOM)
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


def test_print_diff(sample_note, capsys) -> None:
    """Test print_diff() method.

    GIVEN a note object
    WHEN print_diff() is called
    THEN the note's diff is printed to stdout
    """
    note = Note(note_path=sample_note)

    note.write_string("This is a test string.", location=InsertLocation.BOTTOM)
    note.print_diff()
    captured = capsys.readouterr()
    assert "+ This is a test string." in captured.out

    note.sub("The quick brown fox", "The quick brown hedgehog")
    note.print_diff()
    captured = capsys.readouterr()
    assert "- The quick brown fox" in captured.out
    assert "+ The quick brown hedgehog" in captured.out


def test_print_note(sample_note, capsys) -> None:
    """Test print_note() method.

    GIVEN a note object
    WHEN print_note() is called
    THEN the note's new content is printed to stdout
    """
    note = Note(note_path=sample_note)
    note.print_note()
    captured = capsys.readouterr()
    assert "```python" in captured.out
    assert "---" in captured.out
    assert "#shared_tag" in captured.out


def test_rename_inline_tag_1(sample_note) -> None:
    """Test rename_inline_tag() method.

    GIVEN a note object
    WHEN rename_inline_tag() is called with a tag that does not exist
    THEN the method returns False
    """
    note = Note(note_path=sample_note)
    assert note.rename_inline_tag("no_note_tag", "intext_tag2") is False


def test_rename_inline_tag_2(sample_note) -> None:
    """Test rename_inline_tag() method.

    GIVEN a note object
    WHEN rename_inline_tag() is called with a tag exists
    THEN the tag is renamed in the InlineTags object and the file content
    """
    note = Note(note_path=sample_note)
    assert "intext_tag1" in note.inline_tags.list
    assert note.rename_inline_tag("intext_tag1", "intext_tag26") is True
    assert "intext_tag1" not in note.inline_tags.list
    assert "intext_tag26" in note.inline_tags.list
    assert note.file_content == Regex(r"#intext_tag26")
    assert note.file_content != Regex(r"#intext_tag1")


def test_rename_metadata_1(sample_note) -> None:
    """Test rename_metadata() method.

    GIVEN a note object
    WHEN rename_metadata() is called with a key and/or value that does not exist
    THEN the method returns False
    """
    note = Note(note_path=sample_note)
    assert note.rename_metadata("nonexistent_key", "new_key") is False
    assert note.rename_metadata("frontmatter_Key1", "nonexistent_value", "article") is False


def test_rename_metadata_2(sample_note) -> None:
    """Test rename_metadata() method.

    GIVEN a note object
    WHEN rename_metadata() is called with key that matches a frontmatter key
    THEN the key is renamed in the Frontmatter object and the file content
    """
    note = Note(note_path=sample_note)
    assert note.frontmatter.dict["frontmatter_Key1"] == ["author name"]
    assert note.rename_metadata("frontmatter_Key1", "new_key") is True
    assert "frontmatter_Key1" not in note.frontmatter.dict
    assert "new_key" in note.frontmatter.dict
    assert note.frontmatter.dict["new_key"] == ["author name"]
    assert note.file_content == Regex(r"new_key: author name")


def test_rename_metadata_3(sample_note) -> None:
    """Test rename_metadata() method.

    GIVEN a note object
    WHEN rename_metadata() is called with key/value that matches a frontmatter key/value
    THEN the key/value is renamed in the Frontmatter object and the file content
    """
    note = Note(note_path=sample_note)
    assert note.frontmatter.dict["frontmatter_Key2"] == ["article", "note"]
    assert note.rename_metadata("frontmatter_Key2", "article", "new_key") is True
    assert note.frontmatter.dict["frontmatter_Key2"] == ["new_key", "note"]
    assert note.file_content == Regex(r"  - new_key")
    assert note.file_content != Regex(r"  - article")


def test_rename_metadata_4(sample_note) -> None:
    """Test rename_metadata() method.

    GIVEN a note object
    WHEN rename_metadata() is called with key that matches an inline key
    THEN the key is renamed in the InlineMetada object and the file content
    """
    note = Note(note_path=sample_note)
    assert note.rename_metadata("bottom_key1", "new_key") is True
    assert "bottom_key1" not in note.inline_metadata.dict
    assert "new_key" in note.inline_metadata.dict
    assert note.file_content == Regex(r"new_key:: bottom_key1_value")


def test_rename_metadata_5(sample_note) -> None:
    """Test rename_metadata() method.

    GIVEN a note object
    WHEN rename_metadata() is called with key/value that matches an inline key/value
    THEN the key/value is renamed in the InlineMetada object and the file content
    """
    note = Note(note_path=sample_note)
    assert note.rename_metadata("bottom_key1", "bottom_key1_value", "new_value") is True
    assert note.inline_metadata.dict["bottom_key1"] == ["new_value"]
    assert note.file_content == Regex(r"bottom_key1:: new_value")


def test_sub(sample_note) -> None:
    """Test the sub() method.

    GIVEN a note object
    WHEN sub() is called with a string that exists in the note
    THEN the string is replaced in the note's file content
    """
    note = Note(note_path=sample_note)
    note.sub("#shared_tag", "#unshared_tags", is_regex=True)
    assert note.file_content != Regex(r"#shared_tag")
    assert note.file_content == Regex(r"#unshared_tags")

    note.sub(" ut ", "")
    assert note.file_content != Regex(r" ut ")
    assert note.file_content == Regex(r"laboriosam, nisialiquid ex ea")


def test_transpose_metadata_1(sample_note):
    """Test transpose_metadata() method.

    GIVEN a note object with transpose_metadata() is called
    WHEN a metadata object is empty
    THEN the method returns False
    """
    note = Note(note_path=sample_note)
    note.frontmatter.dict = {}
    assert note.transpose_metadata(begin=MetadataType.FRONTMATTER, end=MetadataType.INLINE) is False

    note = Note(note_path=sample_note)
    note.inline_metadata.dict = {}
    assert note.transpose_metadata(begin=MetadataType.INLINE, end=MetadataType.FRONTMATTER) is False


def test_transpose_metadata_2(sample_note):
    """Test transpose_metadata() method.

    GIVEN a note object with transpose_metadata() is called
    WHEN a specified key and/or value does not exist
    THEN the method returns False
    """
    note = Note(note_path=sample_note)
    assert (
        note.transpose_metadata(
            begin=MetadataType.FRONTMATTER,
            end=MetadataType.INLINE,
            key="not_a_key",
        )
        is False
    )
    assert (
        note.transpose_metadata(
            begin=MetadataType.FRONTMATTER,
            end=MetadataType.INLINE,
            key="frontmatter_Key2",
            value="not_a_value",
        )
        is False
    )
    assert (
        note.transpose_metadata(
            begin=MetadataType.FRONTMATTER,
            end=MetadataType.INLINE,
            key="frontmatter_Key2",
            value=["not_a_value", "not_a_value2"],
        )
        is False
    )


def test_transpose_metadata_3(sample_note):
    """Test transpose_metadata() method.

    GIVEN a note object with transpose_metadata() is called
    WHEN FRONTMATTER to INLINE and no key or value is specified
    THEN all frontmatter is removed and added to the inline metadata object and the file content
    """
    note = Note(note_path=sample_note)
    assert note.transpose_metadata(begin=MetadataType.FRONTMATTER, end=MetadataType.INLINE) is True
    assert note.frontmatter.dict == {}
    assert note.inline_metadata.dict == {
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
        "shared_key2": ["shared_key2_value2", "shared_key2_value1"],
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


def test_transpose_metadata_4(sample_note):
    """Test transpose_metadata() method.

    GIVEN a note object with transpose_metadata() is called
    WHEN INLINE to FRONTMATTER and no key or value is specified
    THEN all inline metadata is removed and added to the frontmatter object and the file content
    """
    note = Note(note_path=sample_note)
    assert note.transpose_metadata(begin=MetadataType.INLINE, end=MetadataType.FRONTMATTER) is True
    assert note.inline_metadata.dict == {}
    assert note.frontmatter.dict == {
        "bottom_key1": ["bottom_key1_value"],
        "bottom_key2": ["bottom_key2_value"],
        "date_created": ["2022-12-22"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_value"],
        "key📅": ["📅_key_value"],
        "shared_key1": [
            "shared_key1_value",
            "shared_key1_value3",
            "shared_key1_value",
            "shared_key1_value2",
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


def test_transpose_metadata_5(sample_note):
    """Test transpose_metadata() method.

    GIVEN a note object with transpose_metadata() is called
    WHEN a key exists in both frontmatter and inline metadata
    THEN the values for the key are merged in the specified metadata object
    """
    note = Note(note_path=sample_note)
    assert note.frontmatter.dict["shared_key1"] == ["shared_key1_value", "shared_key1_value3"]
    assert note.inline_metadata.dict["shared_key1"] == ["shared_key1_value", "shared_key1_value2"]
    assert (
        note.transpose_metadata(
            begin=MetadataType.FRONTMATTER,
            end=MetadataType.INLINE,
            key="shared_key1",
        )
        is True
    )
    assert "shared_key1" not in note.frontmatter.dict
    assert note.inline_metadata.dict["shared_key1"] == [
        "shared_key1_value",
        "shared_key1_value2",
        "shared_key1_value3",
    ]


def test_transpose_metadata_6(sample_note):
    """Test transpose_metadata() method.

    GIVEN a note object with transpose_metadata() is called
    WHEN a specified key with no value is specified
    THEN the key is removed from the specified metadata object and added to the target metadata object
    """
    note = Note(note_path=sample_note)
    assert "top_key1" not in note.frontmatter.dict
    assert "top_key1" in note.inline_metadata.dict
    assert (
        note.transpose_metadata(
            begin=MetadataType.INLINE,
            end=MetadataType.FRONTMATTER,
            key="top_key1",
        )
        is True
    )
    assert "top_key1" not in note.inline_metadata.dict
    assert note.frontmatter.dict["top_key1"] == ["top_key1_value"]


def test_transpose_metadata_7(sample_note):
    """Test transpose_metadata() method.

    GIVEN a note object with transpose_metadata() is called
    WHEN a specified value is a list
    THEN the key/value is removed from the specified metadata object and added to the target metadata object
    """
    note = Note(note_path=sample_note)
    assert (
        note.transpose_metadata(
            begin=MetadataType.FRONTMATTER,
            end=MetadataType.INLINE,
            key="frontmatter_Key2",
            value=["article", "note"],
        )
        is True
    )
    assert "frontmatter_Key2" not in note.frontmatter.dict
    assert note.inline_metadata.dict["frontmatter_Key2"] == ["article", "note"]


def test_transpose_metadata_8(sample_note):
    """Test transpose_metadata() method.

    GIVEN a note object with transpose_metadata() is called
    WHEN a specified value is a string
    THEN the key/value is removed from the specified metadata object and added to the target metadata object
    """
    note = Note(note_path=sample_note)
    assert (
        note.transpose_metadata(
            begin=MetadataType.FRONTMATTER,
            end=MetadataType.INLINE,
            key="frontmatter_Key2",
            value="note",
        )
        is True
    )
    assert note.frontmatter.dict["frontmatter_Key2"] == ["article"]
    assert note.inline_metadata.dict["frontmatter_Key2"] == ["note"]


def test_write_delete_inline_metadata_1(sample_note) -> None:
    """Twrite_delete_inline_metadata() method.

    GIVEN a note object with write_delete_inline_metadata() called
    WHEN a key is specified that is not in the inline metadata
    THEN the file content is not changed

    """
    note = Note(note_path=sample_note)
    note.write_delete_inline_metadata("nonexistent_key")
    assert note.file_content == note.original_file_content
    note.write_delete_inline_metadata("frontmatter_Key1")
    assert note.file_content == note.original_file_content


def test_write_delete_inline_metadata_2(sample_note) -> None:
    """Twrite_delete_inline_metadata() method.

    GIVEN a note object with write_delete_inline_metadata() called
    WHEN a key is specified that is within a body of text
    THEN the key and all associated values are removed from the note content

    """
    note = Note(note_path=sample_note)
    note.write_delete_inline_metadata("intext_key")
    assert note.file_content == Regex(r"dolore eu  fugiat", re.DOTALL)


def test_write_delete_inline_metadata_3(sample_note) -> None:
    """Twrite_delete_inline_metadata() method.

    GIVEN a note object with write_delete_inline_metadata() called
    WHEN a key is specified that is not within a body of text
    THEN the key/value is removed from the note content
    """
    note = Note(note_path=sample_note)
    note.write_delete_inline_metadata("bottom_key2", "bottom_key2_value")
    assert note.file_content != Regex(r"bottom_key2_value")
    assert note.file_content == Regex(r"bottom_key2::")
    note.write_delete_inline_metadata("bottom_key1")
    assert note.file_content != Regex(r"bottom_key1::")


def test_write_delete_inline_metadata_4(sample_note) -> None:
    """Twrite_delete_inline_metadata() method.

    GIVEN a note object with write_delete_inline_metadata() called
    WHEN no key or value is specified
    THEN all inline metadata is removed from the note content
    """
    note = Note(note_path=sample_note)
    note.write_delete_inline_metadata()
    assert note.file_content == Regex(r"codeblock_key::")
    assert note.file_content != Regex(r"key📅::")
    assert note.file_content != Regex(r"top_key1::")
    assert note.file_content != Regex(r"top_key3::")
    assert note.file_content != Regex(r"intext_key::")
    assert note.file_content != Regex(r"shared_key1::")
    assert note.file_content != Regex(r"shared_key2::")
    assert note.file_content != Regex(r"bottom_key1::")
    assert note.file_content != Regex(r"bottom_key2::")


def test_write_frontmatter_1(sample_note) -> None:
    """Test writing frontmatter.

    GIVEN a note with frontmatter
    WHEN the frontmatter object is different
    THEN the old frontmatter is replaced with the new frontmatter
    """
    note = Note(note_path=sample_note)

    assert note.rename_metadata("frontmatter_Key1", "author name", "some_new_key_here") is True
    assert note.write_frontmatter() is True
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
shared_key1:
  - shared_key1_value
  - shared_key1_value3
shared_key2: shared_key2_value1
---"""
    assert new_frontmatter in note.file_content
    assert "# Heading 1" in note.file_content
    assert "```python" in note.file_content


def test_write_frontmatter_2() -> None:
    """Test replacing frontmatter.

    GIVEN a note with no frontmatter
    WHEN the frontmatter object has values
    THEN the frontmatter is added to the note
    """
    note = Note(note_path="tests/fixtures/test_vault/no_metadata.md")

    note.frontmatter.dict = {"key1": "value1", "key2": "value2"}
    assert note.write_frontmatter() is True
    new_frontmatter = """---
key1: value1
key2: value2
---"""
    assert new_frontmatter in note.file_content
    assert "Lorem ipsum dolor sit amet" in note.file_content


def test_write_frontmatter_3(sample_note) -> None:
    """Test replacing frontmatter.

    GIVEN a note with frontmatter
    WHEN the frontmatter object is empty
    THEN the frontmatter is removed from the note
    """
    note = Note(note_path=sample_note)

    note.frontmatter.dict = {}
    assert note.write_frontmatter() is True
    assert "---" not in note.file_content
    assert note.file_content != Regex("date_created:")
    assert "Lorem ipsum dolor sit amet" in note.file_content


def test_write_frontmatter_4() -> None:
    """Test replacing frontmatter.

    GIVEN a note with no frontmatter
    WHEN the frontmatter object is empty
    THEN the frontmatter is not added to the note
    """
    note = Note(note_path="tests/fixtures/test_vault/no_metadata.md")
    note.frontmatter.dict = {}
    assert note.write_frontmatter() is False
    assert "---" not in note.file_content
    assert "Lorem ipsum dolor sit amet" in note.file_content


def test_write_all_inline_metadata_1(sample_note) -> None:
    """Test write_all_inline_metadata() method.

    GIVEN a note object with write_metadata_all() called
    WHEN the note has inline metadata
    THEN the inline metadata is written to the note
    """
    note = Note(note_path=sample_note)
    metadata_block = """
bottom_key1:: bottom_key1_value
bottom_key2:: bottom_key2_value
intext_key:: intext_value
key📅:: 📅_key_value
shared_key1:: shared_key1_value
shared_key1:: shared_key1_value2
shared_key2:: shared_key2_value2
top_key1:: top_key1_value
top_key2:: top_key2_value
top_key3:: top_key3_value_as_link"""
    assert metadata_block not in note.file_content
    assert note.write_all_inline_metadata(location=InsertLocation.BOTTOM) is True
    assert metadata_block in note.file_content


def test_write_all_inline_metadata_2(sample_note) -> None:
    """Test write_all_inline_metadata() method.

    GIVEN a note object with write_metadata_all() called
    WHEN the note has no inline metadata
    THEN write_all_inline_metadata returns False
    """
    note = Note(note_path=sample_note)
    note.inline_metadata.dict = {}
    assert note.write_all_inline_metadata(location=InsertLocation.BOTTOM) is False


def test_write_inline_metadata_change_1(sample_note):
    """Test write_inline_metadata_change() method.

    GIVEN a note object with write_inline_metadata_change() called
    WHEN the key and/or value is not in the note
    THEN the key and/or value is not added to the note
    """
    note = Note(note_path=sample_note)

    note.write_inline_metadata_change("nonexistent_key", "new_key")
    assert note.file_content == note.original_file_content
    note.write_inline_metadata_change("bottom_key1", "no_value", "new_value")
    assert note.file_content == note.original_file_content


def test_write_inline_metadata_change_2(sample_note):
    """Test write_inline_metadata_change() method.

    GIVEN a note object with write_inline_metadata_change() called
    WHEN the key is in the note
    THEN the key is changed to the new key
    """
    note = Note(note_path=sample_note)

    note.write_inline_metadata_change("bottom_key1", "new_key")
    assert note.file_content != Regex(r"bottom_key1::")
    assert note.file_content == Regex(r"new_key:: bottom_key1_value")


def test_write_inline_metadata_change_3(sample_note):
    """Test write_inline_metadata_change() method.

    GIVEN a note object with write_inline_metadata_change() called
    WHEN the key and value is in the note
    THEN the value is changed
    """
    note = Note(note_path=sample_note)
    note.write_inline_metadata_change("key📅", "📅_key_value", "new_value")
    assert note.file_content != Regex(r"key📅:: ?📅_key_value")
    assert note.file_content == Regex(r"key📅:: ?new_value")


def test_write_string_1(short_notes) -> None:
    """Test the write_string() method.

    GIVEN a note object with write_string() called
    WHEN the specified location is BOTTOM
    THEN the string is written to the bottom of the note
    """
    path1, path2 = short_notes
    note = Note(note_path=str(path1))
    note2 = Note(note_path=str(path2))

    string1 = "This is a test string."
    string2 = "This is"

    correct_content = """
---
key: value
---

# header 1

Lorem ipsum dolor sit amet.

This is a test string.
    """
    correct_content2 = """
---
key: value
---

# header 1

Lorem ipsum dolor sit amet.

This is a test string.
This is
    """
    correct_content3 = """
Lorem ipsum dolor sit amet.

This is a test string.
    """
    note.write_string(new_string=string1, location=InsertLocation.BOTTOM)
    assert note.file_content == correct_content.strip()

    note.write_string(new_string=string2, location=InsertLocation.BOTTOM)
    assert note.file_content == correct_content.strip()

    note.write_string(new_string=string2, allow_multiple=True, location=InsertLocation.BOTTOM)
    assert note.file_content == correct_content2.strip()

    note2.write_string(new_string=string1, location=InsertLocation.BOTTOM)
    assert note2.file_content == correct_content3.strip()


def test_write_string_2(short_notes) -> None:
    """Test the write_string() method.

    GIVEN a note object with write_string() called
    WHEN the specified location is TOP
    THEN the string is written to the top of the note
    """
    path1, path2 = short_notes
    note = Note(note_path=str(path1))
    note2 = Note(note_path=str(path2))

    string1 = "This is a test string."
    string2 = "This is"
    correct_content = """
---
key: value
---
This is a test string.

# header 1

Lorem ipsum dolor sit amet.
    """

    correct_content2 = """
---
key: value
---
This is
This is a test string.

# header 1

Lorem ipsum dolor sit amet.
    """
    correct_content3 = """
This is a test string.
Lorem ipsum dolor sit amet.
    """

    note.write_string(new_string=string1, location=InsertLocation.TOP)
    assert note.file_content.strip() == correct_content.strip()

    note.write_string(new_string=string2, allow_multiple=True, location=InsertLocation.TOP)
    assert note.file_content.strip() == correct_content2.strip()

    note2.write_string(new_string=string1, location=InsertLocation.TOP)
    assert note2.file_content.strip() == correct_content3.strip()


def test_write_string_3(short_notes) -> None:
    """Test the write_string() method.

    GIVEN a note object with write_string() called
    WHEN the specified location is AFTER_TITLE
    THEN the string is written after the title of the note
    """
    path1, path2 = short_notes
    note = Note(note_path=str(path1))
    note2 = Note(note_path=str(path2))

    string1 = "This is a test string."
    string2 = "This is"
    correct_content = """
---
key: value
---

# header 1
This is a test string.

Lorem ipsum dolor sit amet.
    """

    correct_content2 = """
---
key: value
---

# header 1
This is
This is a test string.

Lorem ipsum dolor sit amet.
    """
    correct_content3 = """
This is a test string.
Lorem ipsum dolor sit amet.
    """

    note.write_string(new_string=string1, location=InsertLocation.AFTER_TITLE)
    assert note.file_content.strip() == correct_content.strip()

    note.write_string(new_string=string2, allow_multiple=True, location=InsertLocation.AFTER_TITLE)
    assert note.file_content.strip() == correct_content2.strip()

    note2.write_string(new_string=string1, location=InsertLocation.AFTER_TITLE)
    assert note2.file_content.strip() == correct_content3.strip()
