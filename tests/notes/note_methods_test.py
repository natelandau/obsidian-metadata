# type: ignore
"""Test for metadata methods within Note class."""
from pathlib import Path

import pytest
import typer
from tests.helpers import Regex

from obsidian_metadata._utils.console import console
from obsidian_metadata.models.enums import InsertLocation, MetadataType
from obsidian_metadata.models.notes import Note


@pytest.mark.parametrize(
    ("content", "new_content"),
    [
        ("foo bar\nkey:: value", "foo bar\n"),
        ("foo\nkey:: value\nbar", "foo\nbar"),
        ("foo\n     key:: value    \nbar\nbaz", "foo\nbar\nbaz"),
        ("> blockquote\n> key:: value\n > blockquote2", "> blockquote\n> blockquote2"),
        ("foo (**key**:: value) bar", "foo bar"),
        ("foo [**key**:: value] bar", "foo bar"),
    ],
)
def test__delete_inline_metadata_1(tmp_path, content, new_content):
    """Test _edit_inline_metadata() method.

    GIVEN a note object with inline metadata
    WHEN changing a key and value in the inline metadata
    THEN the metadata object and the content is updated
    """
    note_path = Path(tmp_path) / "note.md"
    note_path.touch()
    note_path.write_text(content)
    note = Note(note_path=note_path)
    source_field = note.metadata[0]
    assert note._delete_inline_metadata(source_field) is True
    assert note.file_content == new_content


@pytest.mark.parametrize(
    ("content", "new_key", "new_content"),
    [
        ("key:: value", "new_key", "new_key:: value"),
        ("key::value", "🌱", "🌱:: value"),
        ("foo (**key**:: value) bar", "new_key", "foo (**new_key**:: value) bar"),
        ("foo [key:: value] bar", "new_key", "foo [new_key:: value] bar"),
    ],
)
def test__edit_inline_metadata_1(tmp_path, content, new_key, new_content):
    """Test _edit_inline_metadata() method.

    GIVEN a note object with inline metadata
    WHEN changing a key in the inline metadata
    THEN the metadata object and the content is updated
    """
    note_path = Path(tmp_path) / "note.md"
    note_path.touch()
    note_path.write_text(content)
    note = Note(note_path=note_path)
    source_field = note.metadata[0]
    new_field = note._edit_inline_metadata(source=source_field, new_key=new_key)
    assert new_content in note.file_content
    assert len(note.metadata) == 1
    assert new_field in note.metadata


@pytest.mark.parametrize(
    ("content", "new_key", "new_value", "new_content"),
    [
        ("key:: value", "new_key", "", "new_key::"),
        ("key::value", "🌱", "new_value", "🌱:: new_value"),
        ("foo (**key**:: value) bar", "key", "new value", "foo (**key**:: new value) bar"),
        ("foo [key:: value] bar", "new_key", "new value", "foo [new_key:: new value] bar"),
    ],
)
def test__edit_inline_metadata_2(tmp_path, content, new_key, new_value, new_content):
    """Test _edit_inline_metadata() method.

    GIVEN a note object with inline metadata
    WHEN changing a key and value in the inline metadata
    THEN the metadata object and the content is updated
    """
    note_path = Path(tmp_path) / "note.md"
    note_path.touch()
    note_path.write_text(content)
    note = Note(note_path=note_path)
    source_field = note.metadata[0]
    new_field = note._edit_inline_metadata(
        source=source_field, new_key=new_key, new_value=new_value
    )
    assert new_content in note.file_content
    assert len(note.metadata) == 1
    assert new_field in note.metadata


@pytest.mark.parametrize(
    ("meta_type", "key", "value", "is_regex", "expected"),
    [
        (MetadataType.FRONTMATTER, None, None, False, 8),
        (MetadataType.FRONTMATTER, None, None, True, 8),
        (MetadataType.FRONTMATTER, "frontmatter1", None, False, 1),
        (MetadataType.FRONTMATTER, r"\w+2", None, True, 3),
        (MetadataType.FRONTMATTER, "frontmatter1", "foo", False, 1),
        (MetadataType.FRONTMATTER, "frontmatter1", r"\w+", True, 1),
        (MetadataType.FRONTMATTER, r"\w+1", "foo", True, 1),
        (MetadataType.FRONTMATTER, "frontmatter1", "XXX", False, 0),
        (MetadataType.FRONTMATTER, "frontmatterXX", None, False, 0),
        (MetadataType.FRONTMATTER, r"^\d", "XXX", False, 0),
        (MetadataType.FRONTMATTER, "frontmatterXX", r"^\d+", False, 0),
        (MetadataType.INLINE, None, None, False, 10),
        (MetadataType.INLINE, None, None, True, 10),
        (MetadataType.INLINE, "inline1", None, False, 2),
        (MetadataType.INLINE, r"\w+2", None, True, 2),
        (MetadataType.INLINE, "inline1", "foo", False, 1),
        (MetadataType.INLINE, "inline1", r"\w+", True, 2),
        (MetadataType.INLINE, r"\w+1", "foo", True, 2),
        (MetadataType.INLINE, "inline1", "XXX", False, 0),
        (MetadataType.INLINE, "inlineXX", None, False, 0),
        (MetadataType.INLINE, r"^\d", "XXX", False, 0),
        (MetadataType.INLINE, "frontmatterXX", r"^\d+", False, 0),
        (MetadataType.TAGS, None, None, False, 2),
        (MetadataType.TAGS, None, None, True, 2),
        (MetadataType.TAGS, None, r"^\w+", True, 2),
        (MetadataType.TAGS, None, "tag1", False, 1),
        (MetadataType.TAGS, None, "XXX", False, 0),
        (MetadataType.TAGS, None, r"^\d+", True, 0),
    ],
)
def test__find_matching_fields_1(sample_note, meta_type, key, value, is_regex, expected):
    """Test _find_matching_fields() method.

    GIVEN a note object
    WHEN searching for matching fields
    THEN return a list of matching fields
    """
    note = Note(note_path=sample_note)
    assert (
        len(
            note._find_matching_fields(meta_type=meta_type, key=key, value=value, is_regex=is_regex)
        )
        == expected
    )


@pytest.mark.parametrize(
    ("meta_type"),
    [(MetadataType.META), (MetadataType.FRONTMATTER), (MetadataType.TAGS)],
)
def test__update_inline_metadata_1(sample_note, meta_type):
    """Test _update_inline_metadata() method.

    GIVEN a note object
    WHEN updating inline metadata with invalid metadata type
    THEN raise an error
    """
    note = Note(note_path=sample_note)
    source_field = [x for x in note.metadata][0]
    source_field.meta_type = meta_type

    with pytest.raises(typer.Exit):
        note._update_inline_metadata(source_field, new_key="inline1", new_value="new value")


def test__update_inline_metadata_2(sample_note):
    """Test _update_inline_metadata() method.

    GIVEN a note object
    WHEN updating inline metadata without a new key or value
    THEN raise an error
    """
    note = Note(note_path=sample_note)
    source_field = [x for x in note.metadata][0]
    source_field.meta_type = MetadataType.INLINE

    with pytest.raises(typer.Exit):
        note._update_inline_metadata(source_field, new_key=None, new_value=None)


@pytest.mark.parametrize(
    ("orig_key", "orig_value", "new_key", "new_value", "new_content"),
    [
        ("inline2", None, "NEW_KEY", None, "**NEW_KEY**:: [[foo]]"),
        (None, "value", None, "NEW_VALUE", "_inline3_:: NEW_VALUE"),
        ("intext2", "foo", "NEW_KEY", "NEW_VALUE", "(NEW_KEY:: NEW_VALUE)"),
        ("intext1", None, "NEW_KEY", None, "[NEW_KEY:: foo]"),
    ],
)
def test__update_inline_metadata_3(
    sample_note, orig_key, orig_value, new_key, new_value, new_content
):
    """Test _update_inline_metadata() method.

    GIVEN a note object
    WHEN updating inline metadata with a new key
    THEN update the content of the note and the metadata object
    """
    note = Note(note_path=sample_note)

    if orig_key is None:
        source_inlinefield = [
            x
            for x in note.metadata
            if x.meta_type == MetadataType.INLINE and x.normalized_value == orig_value
        ][0]
        assert (
            note._update_inline_metadata(source_inlinefield, new_key=new_key, new_value=new_value)
            is True
        )
        assert source_inlinefield.normalized_value == new_value

    elif orig_value is None:
        source_inlinefield = [
            x
            for x in note.metadata
            if x.meta_type == MetadataType.INLINE and x.normalized_key == orig_key
        ][0]
        assert (
            note._update_inline_metadata(source_inlinefield, new_key=new_key, new_value=new_value)
            is True
        )
        assert source_inlinefield.normalized_key == new_key.lower()

    else:
        source_inlinefield = [
            x
            for x in note.metadata
            if x.meta_type == MetadataType.INLINE
            if x.normalized_key == orig_key
            if x.normalized_value == orig_value
        ][0]
        assert (
            note._update_inline_metadata(source_inlinefield, new_key=new_key, new_value=new_value)
            is True
        )
        assert source_inlinefield.normalized_key == new_key.lower()
        assert source_inlinefield.normalized_value == new_value

    assert new_content in note.file_content
    assert source_inlinefield.is_changed is True


def test_add_metadata_1(sample_note):
    """Test add_metadata() method.

    GIVEN a note object
    WHEN when adding invalid metadata types
    THEN raise an error
    """
    note = Note(note_path=sample_note)

    with pytest.raises(typer.Exit):
        note.add_metadata(meta_type=MetadataType.META, added_key="foo", added_value="bar")


@pytest.mark.parametrize(
    ("meta_type", "key", "value"),
    [
        (MetadataType.FRONTMATTER, "frontmatter1", "foo"),
        (MetadataType.INLINE, "inline1", "foo"),
        (MetadataType.TAGS, None, "tag1"),
    ],
)
def test_add_metadata_2(sample_note, meta_type, key, value):
    """Test add_metadata() method.

    GIVEN a note object
    WHEN when adding metadata which already exists
    THEN return False
    """
    note = Note(note_path=sample_note)
    assert note.add_metadata(meta_type=meta_type, added_key=key, added_value=value) is False


def test_add_metadata_3(sample_note):
    """Test add_metadata() method.

    GIVEN a note object
    WHEN when adding a blank tag
    THEN raise an error
    """
    note = Note(note_path=sample_note)
    with pytest.raises(typer.Exit):
        note.add_metadata(meta_type=MetadataType.TAGS, added_key=None, added_value="")


def test_add_metadata_4(sample_note):
    """Test add_metadata() method.

    GIVEN a note object
    WHEN when adding an invalid tag
    THEN raise an error
    """
    note = Note(note_path=sample_note)
    with pytest.raises(typer.Exit):
        note.add_metadata(meta_type=MetadataType.TAGS, added_key=None, added_value="[*")


def test_add_metadata_5(sample_note):
    """Test add_metadata() method.

    GIVEN a note object
    WHEN when adding an empty key
    THEN raise an error
    """
    note = Note(note_path=sample_note)

    with pytest.raises(typer.Exit):
        note.add_metadata(meta_type=MetadataType.FRONTMATTER, added_key=" ", added_value="bar")


def test_add_metadata_6(sample_note):
    """Test add_metadata() method.

    GIVEN a note object
    WHEN when adding no key but a value
    THEN raise an error
    """
    note = Note(note_path=sample_note)

    with pytest.raises(typer.Exit):
        note.add_metadata(meta_type=MetadataType.FRONTMATTER, added_key=None, added_value="bar")


@pytest.mark.parametrize(
    ("metatype", "key", "value", "expected"),
    [
        (MetadataType.FRONTMATTER, "test", "value", "test: value"),
        (MetadataType.INLINE, "test", "value", "test:: value"),
        (MetadataType.TAGS, None, "testtag", "#testtag"),
        (MetadataType.TAGS, None, "#testtag", "#testtag"),
    ],
)
def test_add_metadata_7(sample_note, metatype, key, value, expected):
    """Test add_metadata() method.

    GIVEN a note object
    WHEN when adding metadata
    THEN the metadata is added to the note
    """
    note = Note(note_path=sample_note)
    assert note.contains_metadata(meta_type=metatype, search_key=key, search_value=value) is False
    assert expected not in note.file_content
    assert (
        note.add_metadata(
            meta_type=metatype, added_key=key, added_value=value, location=InsertLocation.TOP
        )
        is True
    )
    assert note.contains_metadata(meta_type=metatype, search_key=key, search_value=value) is True
    assert expected in note.file_content


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


def test_commit_2(sample_note) -> None:
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


@pytest.mark.parametrize(
    ("meta_type", "key", "value", "is_regex", "expected"),
    [
        # Key does not match
        (MetadataType.META, "not_a_key", None, False, False),
        (MetadataType.META, r"^\d+", None, True, False),
        (MetadataType.TAGS, "tag1", None, False, False),
        (MetadataType.TAGS, r"^f\w+1", None, True, False),
        (MetadataType.INLINE, "frontamtter1", None, False, False),
        (MetadataType.INLINE, r"^f\w+1", None, True, False),
        (MetadataType.FRONTMATTER, "inline1", None, False, False),
        (MetadataType.FRONTMATTER, r"^i\w+1", None, True, False),
        # Key matches, no value provided
        (MetadataType.META, "frontmatter1", None, False, True),
        (MetadataType.META, r"^f\w+2", None, True, True),
        (MetadataType.FRONTMATTER, "frontmatter1", None, False, True),
        (MetadataType.FRONTMATTER, r"^f\w+2", None, True, True),
        (MetadataType.INLINE, "inline1", None, False, True),
        (MetadataType.INLINE, r"^i\w+1", None, True, True),
        # Key matches, value does not match
        (MetadataType.META, "frontmatter1", "not_a_value", False, False),
        (MetadataType.META, r"^f\w+1", r"^\d+", True, False),
        (MetadataType.FRONTMATTER, "frontmatter1", "not_a_value", False, False),
        (MetadataType.FRONTMATTER, r"^f\w+1", r"^\d+", True, False),
        (MetadataType.INLINE, "inline1", "not_a_value", False, False),
        (MetadataType.INLINE, r"^i\w+1", r"^\d+", True, False),
        (MetadataType.TAGS, None, "not_a_value", False, False),
        (MetadataType.TAGS, None, r"^\d+", True, False),
        # Key and values match
        (MetadataType.META, "frontmatter1", "foo", False, True),
        (MetadataType.META, r"^f\w+1", r"[a-z]{3}", True, True),
        (MetadataType.FRONTMATTER, "frontmatter1", "foo", False, True),
        (MetadataType.FRONTMATTER, r"^f\w+1", r"[a-z]{3}", True, True),
        (MetadataType.INLINE, "inline1", "foo", False, True),
        (MetadataType.INLINE, r"^i\w+1", r"[a-z]{3}", True, True),
        (MetadataType.TAGS, None, "#tag1", False, True),
        (MetadataType.TAGS, None, r"^\w+1", True, True),
        # Confirm MetaType.ALL works
        (MetadataType.ALL, "not_a_key", None, False, False),
        (MetadataType.ALL, r"^\d+", None, True, False),
        (MetadataType.ALL, "frontmatter1", None, False, True),
        (MetadataType.ALL, r"^i\w+1", None, True, True),
        (MetadataType.ALL, "not_a_key", r"\w+", True, False),
        (MetadataType.ALL, "frontmatter1", "not_a_value", False, False),
        (MetadataType.ALL, r"^f\w+1", r"^\d+", True, False),
        (MetadataType.ALL, "inline1", "not_a_value", False, False),
        (MetadataType.ALL, r"^i\w+1", r"^\d+", True, False),
        (MetadataType.ALL, None, "not_a_value", False, False),
        (MetadataType.ALL, None, r"^\d+", True, False),
        (MetadataType.ALL, "frontmatter1", "foo", False, True),
        (MetadataType.ALL, r"^f\w+1", r"[a-z]{3}", True, True),
        (MetadataType.ALL, "frontmatter1", "foo", False, True),
        (MetadataType.ALL, r"^f\w+1", r"[a-z]{3}", True, True),
        (MetadataType.ALL, "inline1", "foo", False, True),
        (MetadataType.ALL, r"^i\w+1", r"[a-z]{3}", True, True),
        (MetadataType.ALL, None, "#tag1", False, True),
        (MetadataType.ALL, None, r"^\w+1", True, True),
    ],
)
def test_contains_metadata_1(sample_note, meta_type, key, value, is_regex, expected):
    """Test contains_metadata() method.

    GIVEN a note object containing metadata
    WHEN the contains_metadata method is called
    THEN return the correct value
    """
    note = Note(note_path=sample_note)
    assert (
        note.contains_metadata(
            meta_type=meta_type, search_key=key, search_value=value, is_regex=is_regex
        )
        is expected
    )


@pytest.mark.parametrize(
    ("meta_type", "key", "value"),
    [
        (MetadataType.META, "", "foo"),
        (MetadataType.FRONTMATTER, "", "foo"),
        (MetadataType.INLINE, "", "foo"),
        (MetadataType.TAGS, "foo", ""),
        (MetadataType.META, None, "foo"),
        (MetadataType.FRONTMATTER, None, "foo"),
        (MetadataType.INLINE, None, "foo"),
        (MetadataType.TAGS, "foo", None),
    ],
)
def test_delete_metadata_1(
    sample_note,
    meta_type,
    key,
    value,
):
    """Test delete_metadata() method.

    GIVEN a note object
    WHEN when deleting invalid metadata types
    THEN raise an error
    """
    note = Note(note_path=sample_note)

    with pytest.raises(typer.Exit):
        note.delete_metadata(meta_type=meta_type, key=key, value=value)


@pytest.mark.parametrize(
    ("meta_type", "key", "value", "is_regex"),
    [
        (MetadataType.META, "frontmatter1", None, False),
        (MetadataType.FRONTMATTER, "frontmatter1", None, False),
        (MetadataType.INLINE, "inline1", None, False),
        (MetadataType.META, "inline1", None, False),
        (MetadataType.META, "frontmatter1", "foo", False),
        (MetadataType.FRONTMATTER, "frontmatter1", "foo", False),
        (MetadataType.INLINE, "inline1", "foo", False),
        (MetadataType.TAGS, None, "#tag1", False),
        (MetadataType.TAGS, None, "tag1", False),
        (MetadataType.META, r"\w\d", None, True),
        (MetadataType.FRONTMATTER, r"\w\d$", None, True),
        (MetadataType.INLINE, r"\w\d$", None, True),
        (MetadataType.META, r"\w\d$", None, True),
        (MetadataType.META, "frontmatter1", r"\w+", True),
        (MetadataType.FRONTMATTER, "frontmatter1", r"\w+", True),
        (MetadataType.INLINE, "inline1", r"\w+", True),
        (MetadataType.TAGS, None, r"\w\d$", True),
        (MetadataType.ALL, None, "#tag1", False),
        (MetadataType.ALL, None, r"\w\d$", True),
        (MetadataType.ALL, "inline1", r"\w+", True),
        (MetadataType.ALL, "frontmatter1", r"\w+", True),
        (MetadataType.ALL, "frontmatter1", "foo", False),
        (MetadataType.ALL, "inline1", None, False),
    ],
)
def test_delete_metadata_2(sample_note, meta_type, key, value, is_regex):
    """Test delete_metadata() method.

    GIVEN a note object
    WHEN when deleting metadata
    THEN the metadata is deleted from the note
    """
    note = Note(note_path=sample_note)
    assert (
        note.contains_metadata(
            meta_type=meta_type, search_key=key, search_value=value, is_regex=is_regex
        )
        is True
    )
    assert (
        note.delete_metadata(meta_type=meta_type, key=key, value=value, is_regex=is_regex) is True
    )

    assert (
        note.contains_metadata(
            meta_type=meta_type, search_key=key, search_value=value, is_regex=is_regex
        )
        is False
    )


@pytest.mark.parametrize(
    ("meta_type", "key", "value", "is_regex"),
    [
        (MetadataType.META, "frontmatterXXXX", None, False),
        (MetadataType.FRONTMATTER, "frontmatterXXXX", None, False),
        (MetadataType.INLINE, "inlineXXXX", None, False),
        (MetadataType.META, "inlineXXXX", None, False),
        (MetadataType.META, "frontmatter1", "XXXX", False),
        (MetadataType.FRONTMATTER, "frontmatter1", "XXXX", False),
        (MetadataType.INLINE, "inline1", "XXXX", False),
        (MetadataType.TAGS, None, "#not_existing", False),
        (MetadataType.TAGS, None, "XXXX", False),
        (MetadataType.META, r"\d{8}", None, True),
        (MetadataType.FRONTMATTER, r"\d{8}", None, True),
        (MetadataType.INLINE, r"\d{8}", None, True),
        (MetadataType.META, r"\d{8}", None, True),
        (MetadataType.META, "frontmatter1", r"\d{8}", True),
        (MetadataType.FRONTMATTER, "frontmatter1", r"\d{8}", True),
        (MetadataType.INLINE, "inline1", r"\d{8}", True),
        (MetadataType.TAGS, None, r"\d{8}", True),
    ],
)
def test_delete_metadata_3(sample_note, meta_type, key, value, is_regex):
    """Test delete_metadata() method.

    GIVEN a note object
    WHEN when deleting metadata that does not exist
    THEN return False
    """
    note = Note(note_path=sample_note)

    assert (
        note.delete_metadata(meta_type=meta_type, key=key, value=value, is_regex=is_regex) is False
    )


def test_delete_all_metadata_1(sample_note) -> None:
    """Test delete_all_metadata() method.

    GIVEN a note object
    WHEN when deleting all metadata
    THEN all metadata is deleted from the note
    """
    note = Note(note_path=sample_note)
    assert note.delete_all_metadata() is True
    assert note.metadata == []
    assert "inline1:: foo" not in note.file_content
    assert "#tag1" not in note.file_content
    assert "frontmatter1: foo" not in note.file_content


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
    note.delete_all_metadata()
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
    assert "#invalid" in captured.out
    assert note.file_content == Regex(r"\[\[link\]\]")


@pytest.mark.parametrize(
    ("key", "value1", "value2", "content", "result"),
    [
        ("frontmatter1", "NEW_KEY", None, "NEW_KEY: foo", True),
        ("inline1", "NEW_KEY", None, "NEW_KEY:: foo\nNEW_KEY::bar baz", True),
        ("intext1", "NEW_KEY", None, "[NEW_KEY:: foo]", True),
        ("frontmatter1", "foo", "NEW VALUE", "frontmatter1: NEW VALUE", True),
        ("inline1", "bar baz", "NEW VALUE", "inline1:: foo\ninline1:: NEW VALUE", True),
        ("intext1", "foo", "NEW VALUE", "[intext1:: NEW VALUE]", True),
        ("XXX", "NEW_KEY", None, "NEW_KEY: foo", False),
        ("frontmatter1", "XXX", "foo", "NEW_KEY: foo", False),
        ("intext1", "XXX", "foo", "NEW_KEY: foo", False),
    ],
)
def test_rename_metadata_1(sample_note, key, value1, value2, content, result) -> None:
    """Test rename_metadata() method.

    GIVEN a note object
    WHEN rename_metadata() is called
    THEN the metadata objects and note content are updated if the metadata exists and the method returns False if not
    """
    note = Note(note_path=sample_note)
    assert note.rename_metadata(key=key, value_1=value1, value_2=value2) is result

    if result:
        assert content in note.file_content
        if value2 is None:
            assert [x for x in note.metadata if x.clean_key == key] == []
            assert len([x for x in note.metadata if x.clean_key == value1]) > 0
        else:
            assert [
                x for x in note.metadata if x.clean_key == key and x.normalized_value == value1
            ] == []
            assert (
                len(
                    [
                        x
                        for x in note.metadata
                        if x.clean_key == key and x.normalized_value == value2
                    ]
                )
                > 0
            )

    else:
        assert note.has_changes() is False


def test_rename_tag_1(sample_note) -> None:
    """Test rename_tag() method.".

    GIVEN a note object
    WHEN rename_tag() is called
    THEN the tag is renamed in the note's file content
    """
    note = Note(note_path=sample_note)
    assert note.rename_tag(old_tag="#tag1", new_tag="#tag3") is True
    assert "#tag1" not in note.file_content
    assert "#tag3" in note.file_content
    assert (
        len([x for x in note.metadata if x.meta_type == MetadataType.TAGS and x.value == "tag1"])
        == 0
    )
    assert (
        len([x for x in note.metadata if x.meta_type == MetadataType.TAGS and x.value == "tag3"])
        == 1
    )


def test_rename_tag_2(sample_note) -> None:
    """Test rename_tag() method.".

    GIVEN a note object
    WHEN rename_tag() is called with a tag that does not exist
    THEN the method returns False
    """
    note = Note(note_path=sample_note)
    assert note.rename_tag(old_tag="not a tag", new_tag="#tag3") is False


def test_sub_1(sample_note) -> None:
    """Test the sub() method.

    GIVEN a note object
    WHEN sub() is called with a string that exists in the note
    THEN the string is replaced in the note's file content
    """
    note = Note(note_path=sample_note)
    note.sub(" Foo bar ", "")
    assert " Foo bar " not in note.file_content
    assert "#tag1#tag2" in note.file_content


def test_sub_2(sample_note) -> None:
    """Test the sub() method.

    GIVEN a note object
    WHEN sub() is called with a string that exists in the note using regex
    THEN the string is replaced in the note's file content
    """
    note = Note(note_path=sample_note)
    note.sub(r"\[.*\]", "", is_regex=True)
    assert "[intext1:: foo]" not in note.file_content


def test_sub_3(sample_note) -> None:
    """Test the sub() method.

    GIVEN a note object
    WHEN sub() is called and matches nothing
    THEN no changes are made to the note's file content
    """
    note = Note(note_path=sample_note)
    note2 = Note(note_path=sample_note)
    note.sub("nonexistent", "")
    assert note.file_content == note2.file_content


@pytest.mark.parametrize(
    ("begin", "end", "key", "value", "location"),
    [
        (MetadataType.FRONTMATTER, MetadataType.INLINE, "XXX", "XXX", InsertLocation.TOP),
        (MetadataType.INLINE, MetadataType.FRONTMATTER, "frontmatter1", "XXX", InsertLocation.TOP),
        (MetadataType.INLINE, MetadataType.FRONTMATTER, "XXX", "XXX", InsertLocation.TOP),
        (MetadataType.INLINE, MetadataType.FRONTMATTER, "intext2", "XXX", InsertLocation.TOP),
    ],
)
def test_transpose_metadata_1(sample_note, begin, end, key, value, location):
    """Test transpose_metadata() method.

    GIVEN a note object
    WHEN transpose_metadata() is called without matching metadata
    THEN the method returns False
    """
    note = Note(note_path=sample_note)
    assert not note.transpose_metadata(
        begin=begin, end=end, key=key, value=value, location=location
    )


@pytest.mark.parametrize(
    ("begin", "end", "key", "value", "location", "content"),
    [
        (
            MetadataType.FRONTMATTER,
            MetadataType.INLINE,
            "frontmatter2",
            None,
            InsertLocation.TOP,
            "---\nfrontmatter2:: bar\nfrontmatter2:: baz\nfrontmatter2:: qux",
        ),
        (
            MetadataType.INLINE,
            MetadataType.FRONTMATTER,
            "inline1",
            None,
            InsertLocation.TOP,
            "inline1:\n  - foo\n  - bar baz\n---",
        ),
        (
            MetadataType.INLINE,
            MetadataType.FRONTMATTER,
            "intext2",
            "foo",
            InsertLocation.TOP,
            "intext2: foo\n---",
        ),
        (
            MetadataType.INLINE,
            MetadataType.FRONTMATTER,
            "inline1",
            "foo",
            InsertLocation.TOP,
            "inline1: foo\n---",
        ),
        (
            MetadataType.INLINE,
            MetadataType.INLINE,
            None,
            None,
            InsertLocation.BOTTOM,
            "```\n\ninline1:: bar baz\ninline1:: foo\ninline2:: [[foo]]\ninline3:: value\ninline4:: foo\ninline5::\nintext1:: foo\nintext2:: foo\nkey with space:: foo\n🌱:: 🌿",
        ),
    ],
)
def test_transpose_metadata_2(sample_note, begin, end, key, value, location, content):
    """Test transpose_metadata() method.

    GIVEN a note object
    WHEN transpose_metadata() is called
    THEN the method returns True and all metadata with the specified keys & values is transposed
    """
    note = Note(note_path=sample_note)
    if value is None:
        original_fields = [x for x in note.metadata if x.key == key and x.meta_type == begin]
    else:
        original_fields = [
            x
            for x in note.metadata
            if x.key == key and x.normalized_value == value and x.meta_type == begin
        ]

    assert (
        note.transpose_metadata(begin=begin, end=end, key=key, value=value, location=location)
        is True
    )

    if value is None:
        new_fields = [x for x in note.metadata if x.key == key and x.meta_type == end]
    else:
        new_fields = [
            x
            for x in note.metadata
            if x.key == key
            and x.normalized_value == value
            and x.meta_type == end
            and x.is_changed is True
        ]

    assert len(new_fields) == len(original_fields)

    if value is None:
        assert len([x for x in note.metadata if x.key == key and x.meta_type == begin]) == 0
    else:
        assert (
            len(
                [
                    x
                    for x in note.metadata
                    if x.key == key and x.normalized_value == value and x.meta_type == begin
                ]
            )
            == 0
        )

    assert content in note.file_content


def test_transpose_metadata_3(sample_note):
    """Test transpose_metadata() method.

    GIVEN a note object
    WHEN transpose_metadata() is called with only Frontmatter
    THEN the method returns False
    """
    note = Note(note_path=sample_note)
    assert not note.transpose_metadata(
        begin=MetadataType.FRONTMATTER,
        end=MetadataType.FRONTMATTER,
        key="frontmatter1",
        value="foo",
    )


def test_write_frontmatter_1(tmp_path) -> None:
    """Test writing frontmatter.

    GIVEN a note with no frontmatter
    WHEN there are no frontmatter metadata objects
    THEN return False
    """
    note_path = Path(tmp_path) / "note.md"
    note_path.touch()
    note_path.write_text(
        """
# Header1
inline:: only
no frontmatter
"""
    )
    note = Note(note_path=note_path)
    assert note.write_frontmatter() is False


def test_write_frontmatter_2(tmp_path) -> None:
    """Test writing frontmatter.

    GIVEN a note with frontmatter
    WHEN there is no frontmatter to write
    THEN all frontmatter in the note is removed
    """
    note_path = Path(tmp_path) / "note.md"
    note_path.touch()
    note_path.write_text(
        """
---
key: value
---

# Header1
inline:: only
no frontmatter
"""
    )
    new_content = """

# Header1
inline:: only
no frontmatter
"""
    note = Note(note_path=note_path)
    note.metadata = []
    assert note.write_frontmatter() is True
    assert note.file_content == new_content


def test_write_frontmatter_3(tmp_path) -> None:
    """Test writing frontmatter.

    GIVEN a note with frontmatter
    WHEN there is new frontmatter to write and no frontmatter in the note content
    THEN new frontmatter is added
    """
    note_path = Path(tmp_path) / "note.md"
    note_path.touch()
    note_path.write_text(
        """
# Header1
inline:: only
no frontmatter
"""
    )
    new_note = """\
---
key: value
---

# Header1
inline:: only
no frontmatter
"""
    note = Note(note_path=note_path)
    note.add_metadata(meta_type=MetadataType.FRONTMATTER, added_key="key", added_value="value")
    assert note.write_frontmatter() is True
    assert note.file_content == new_note


def test_write_frontmatter_4(tmp_path) -> None:
    """Test writing frontmatter.

    GIVEN a note with frontmatter
    WHEN there is new frontmatter to write and existing frontmatter in the note
    THEN new frontmatter is added
    """
    note_path = Path(tmp_path) / "note.md"
    note_path.touch()
    note_path.write_text(
        """\
---
key: value
---

# Header1
inline:: only
no frontmatter
"""
    )
    new_note = """\
---
key: value
key2: value2
---

# Header1
inline:: only
no frontmatter
"""

    note = Note(note_path=note_path)
    note.add_metadata(meta_type=MetadataType.FRONTMATTER, added_key="key2", added_value="value2")
    assert note.write_frontmatter() is True
    assert note.file_content == new_note


@pytest.mark.parametrize(
    ("location"), [InsertLocation.TOP, InsertLocation.BOTTOM, InsertLocation.AFTER_TITLE]
)
def test_write_string_1(tmp_path, location) -> None:
    """Test write_string() method.

    GIVEN a note with no content
    WHEN a string is written to the note
    THEN the string is written to the note
    """
    note_path = Path(tmp_path) / "note.md"
    note_path.touch()
    note_path.write_text("")
    note = Note(note_path=note_path)

    note.write_string("foo", location=location)
    assert note.file_content.strip() == "foo"


@pytest.mark.parametrize(
    ("location", "result"),
    [
        (InsertLocation.TOP, "baz\n\n# Header1\nfoo bar"),
        (InsertLocation.BOTTOM, "# Header1\nfoo bar\nbaz"),
        (InsertLocation.AFTER_TITLE, "# Header1\nbaz\nfoo bar"),
    ],
)
def test_write_string_2(tmp_path, location, result) -> None:
    """Test write_string() method.

    GIVEN a note with no frontmatter
    WHEN a string is written to the note
    THEN the string is written to the correct location
    """
    note_path = Path(tmp_path) / "note.md"
    note_path.touch()
    note_path.write_text("\n# Header1\nfoo bar")
    note = Note(note_path=note_path)

    note.write_string("baz", location=location)
    assert note.file_content.strip() == result


@pytest.mark.parametrize(
    ("location", "result"),
    [
        (InsertLocation.TOP, "---\nkey: value\n---\nbaz\n# Header1\nfoo bar"),
        (InsertLocation.BOTTOM, "---\nkey: value\n---\n# Header1\nfoo bar\nbaz"),
        (InsertLocation.AFTER_TITLE, "---\nkey: value\n---\n# Header1\nbaz\nfoo bar"),
    ],
)
def test_write_string_3(tmp_path, location, result) -> None:
    """Test write_string() method.

    GIVEN a note with frontmatter
    WHEN a string is written to the note
    THEN the string is written to the correct location
    """
    note_path = Path(tmp_path) / "note.md"
    note_path.touch()
    note_path.write_text("---\nkey: value\n---\n# Header1\nfoo bar")
    note = Note(note_path=note_path)

    note.write_string("baz", location=location)
    assert note.file_content.strip() == result
