# type: ignore
"""Test notes.py."""

from pathlib import Path

import pytest
import typer

from obsidian_metadata.models.enums import MetadataType
from obsidian_metadata.models.exceptions import FrontmatterError
from obsidian_metadata.models.metadata import InlineField
from obsidian_metadata.models.notes import Note


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
    assert note.encoding == "utf_8"
    assert len(note.metadata) == 22

    with sample_note.open():
        content = sample_note.read_text()

    assert note.file_content == content
    assert note.original_file_content == content


def test_create_note_2(tmp_path) -> None:
    """Test creating a note object.

    GIVEN a text file with invalid frontmatter
    WHEN the note is initialized
    THEN a typer exit is raised
    """
    note_path = Path(tmp_path) / "broken_frontmatter.md"
    note_path.touch()
    note_path.write_text(
        """---
tags:
invalid = = "content"
---
"""
    )
    with pytest.raises(typer.Exit):
        Note(note_path=note_path)


def test_create_note_3(tmp_path) -> None:
    """Test creating a note object.

    GIVEN a text file with invalid frontmatter
    WHEN the note is initialized
    THEN a typer exit is raised
    """
    note_path = Path(tmp_path) / "broken_frontmatter.md"
    note_path.touch()
    note_path.write_text(
        """---
nested1:
    nested2: "content"
    nested3:
        - "content"
        - "content"
---
"""
    )
    with pytest.raises(typer.Exit):
        Note(note_path=note_path)


def test_create_note_6(tmp_path):
    """Test creating a note object.

    GIVEN a text file
    WHEN there is no content in the file
    THEN a note is returned with no metadata or content
    """
    note_path = Path(tmp_path) / "empty_file.md"
    note_path.touch()
    note = Note(note_path=note_path)
    assert note.note_path == note_path
    assert not note.file_content
    assert not note.original_file_content
    assert note.metadata == []


def test__grab_metadata_1(tmp_path):
    """Test the _grab_metadata method.

    GIVEN a text file
    WHEN there is frontmatter
    THEN the frontmatter is returned in the metadata list
    """
    note_path = Path(tmp_path) / "test_file.md"
    note_path.touch()
    note_path.write_text(
        """
---
key1: value1
key2: 2022-12-22
key3:
    - value3
    - value4
key4:
key5: "value5"
---
    """
    )
    note = Note(note_path=note_path)
    assert sorted(note.metadata, key=lambda x: (x.key, x.value)) == [
        InlineField(meta_type=MetadataType.FRONTMATTER, key="key1", value="value1"),
        InlineField(meta_type=MetadataType.FRONTMATTER, key="key2", value="2022-12-22"),
        InlineField(meta_type=MetadataType.FRONTMATTER, key="key3", value="value3"),
        InlineField(meta_type=MetadataType.FRONTMATTER, key="key3", value="value4"),
        InlineField(meta_type=MetadataType.FRONTMATTER, key="key4", value="None"),
        InlineField(meta_type=MetadataType.FRONTMATTER, key="key5", value="value5"),
    ]


def test__grab_metadata_2(tmp_path):
    """Test the _grab_metadata method.

    GIVEN a text file
    WHEN there is inline metadata
    THEN the inline metadata is returned in the metadata list
    """
    note_path = Path(tmp_path) / "test_file.md"
    note_path.touch()
    note_path.write_text(
        """

key1::value1
key2::2022-12-22
foo [key3::value3] bar
key4::value4
foo (key4::value) bar
key5::value5
key6:: `value6`
`key7::value7`
`key8`::`value8`

    """
    )
    note = Note(note_path=note_path)
    assert sorted(note.metadata, key=lambda x: (x.key, x.value)) == [
        InlineField(meta_type=MetadataType.INLINE, key="`key7", value="value7`"),
        InlineField(meta_type=MetadataType.INLINE, key="`key8`", value="`value8`"),
        InlineField(meta_type=MetadataType.INLINE, key="key1", value="value1"),
        InlineField(meta_type=MetadataType.INLINE, key="key2", value="2022-12-22"),
        InlineField(meta_type=MetadataType.INLINE, key="key3", value="value3"),
        InlineField(meta_type=MetadataType.INLINE, key="key4", value="value"),
        InlineField(meta_type=MetadataType.INLINE, key="key4", value="value4"),
        InlineField(meta_type=MetadataType.INLINE, key="key5", value="value5"),
        InlineField(meta_type=MetadataType.INLINE, key="key6", value=" `value6`"),
    ]


def test__grab_metadata_3(tmp_path):
    """Test the _grab_metadata method.

    GIVEN a text file
    WHEN there are tags
    THEN the tags are returned in the metadata list
    """
    note_path = Path(tmp_path) / "test_file.md"
    note_path.touch()
    note_path.write_text("#tag1\n#tag2")
    note = Note(note_path=note_path)
    assert sorted(note.metadata, key=lambda x: x.value) == [
        InlineField(meta_type=MetadataType.TAGS, key=None, value="tag1"),
        InlineField(meta_type=MetadataType.TAGS, key=None, value="tag2"),
    ]


def test__grab_metadata_4(tmp_path):
    """Test the _grab_metadata method.

    GIVEN a text file
    WHEN there are tags, frontmatter, and inline metadata
    THEN all metadata is returned
    """
    note_path = Path(tmp_path) / "test_file.md"
    note_path.touch()
    note_path.write_text(
        """\
---
key1: value1
---
key2::value2
#tag1\n#tag2"""
    )
    note = Note(note_path=note_path)
    assert sorted(note.metadata, key=lambda x: x.value) == [
        InlineField(meta_type=MetadataType.TAGS, key=None, value="tag1"),
        InlineField(meta_type=MetadataType.TAGS, key=None, value="tag2"),
        InlineField(meta_type=MetadataType.FRONTMATTER, key="key1", value="value1"),
        InlineField(meta_type=MetadataType.INLINE, key="key2", value="value2"),
    ]


def test__grab_metadata_5(tmp_path):
    """Test the _grab_metadata method.

    GIVEN a text file
    WHEN invalid metadata is present
    THEN raise a FrontmatterError
    """
    note_path = Path(tmp_path) / "broken_frontmatter.md"
    note_path.touch()
    note_path.write_text(
        """---
tags:
invalid = = "content"
---
"""
    )
    with pytest.raises(typer.Exit):
        Note(note_path=note_path)
