# type: ignore
"""Test the utilities module."""

import pytest
import typer

from obsidian_metadata._utils import (
    clean_dictionary,
    dict_contains,
    dict_keys_to_lower,
    dict_values_to_lists_strings,
    remove_markdown_sections,
    validate_csv_bulk_imports,
)
from tests.helpers import Regex, remove_ansi


def test_dict_contains() -> None:
    """Test dict_contains."""
    d = {"key1": ["value1", "value2"], "key2": ["value3", "value4"], "key3": ["value5", "value6"]}

    assert dict_contains(d, "key1") is True
    assert dict_contains(d, "key5") is False
    assert dict_contains(d, "key1", "value1") is True
    assert dict_contains(d, "key1", "value5") is False
    assert dict_contains(d, "key[1-2]", is_regex=True) is True
    assert dict_contains(d, "^1", is_regex=True) is False
    assert dict_contains(d, r"key\d", r"value\d", is_regex=True) is True
    assert dict_contains(d, "key1$", "^alue", is_regex=True) is False
    assert dict_contains(d, r"key\d", "value5", is_regex=True) is True


def test_dict_keys_to_lower() -> None:
    """Test the dict_keys_to_lower() function.

    GIVEN a dictionary with mixed case keys
    WHEN the dict_keys_to_lower() function is called
    THEN the dictionary keys should be converted to lowercase
    """
    test_dict = {"Key1": "Value1", "KEY2": "Value2", "key3": "Value3"}
    assert dict_keys_to_lower(test_dict) == {"key1": "Value1", "key2": "Value2", "key3": "Value3"}


def test_dict_values_to_lists_strings():
    """Test converting dictionary values to lists of strings."""
    dictionary = {
        "key1": "value1",
        "key2": ["value2", "value3", None],
        "key3": {"key4": "value4"},
        "key5": {"key6": {"key7": "value7"}},
        "key6": None,
        "key8": [1, 3, None, 4],
        "key9": [None, "", "None"],
        "key10": "None",
        "key11": "",
    }

    result = dict_values_to_lists_strings(dictionary)
    assert result == {
        "key1": ["value1"],
        "key10": ["None"],
        "key11": [""],
        "key2": ["None", "value2", "value3"],
        "key3": {"key4": ["value4"]},
        "key5": {"key6": {"key7": ["value7"]}},
        "key6": ["None"],
        "key8": ["1", "3", "4", "None"],
        "key9": ["", "None", "None"],
    }

    result = dict_values_to_lists_strings(dictionary, strip_null_values=True)
    assert result == {
        "key1": ["value1"],
        "key10": [],
        "key11": [],
        "key2": ["value2", "value3"],
        "key3": {"key4": ["value4"]},
        "key5": {"key6": {"key7": ["value7"]}},
        "key6": [],
        "key8": ["1", "3", "4"],
        "key9": ["", "None"],
    }


def test_remove_markdown_sections():
    """Test removing markdown sections."""
    text: str = """
---
key: value
---

Lorem ipsum `dolor sit` amet.

```bash
    echo "Hello World"
```
---
dd
---
    """
    result = remove_markdown_sections(
        text,
        strip_codeblocks=True,
        strip_frontmatter=True,
        strip_inlinecode=True,
    )
    assert "```bash" not in result
    assert "`dolor sit`" not in result
    assert "---\nkey: value" not in result
    assert "`" not in result

    result = remove_markdown_sections(text)
    assert "```bash" in result
    assert "`dolor sit`" in result
    assert "---\nkey: value" in result
    assert "`" in result


def test_clean_dictionary():
    """Test cleaning a dictionary."""
    dictionary = {" *key* ": ["**value**", "[[value2]]", "#value3"]}

    new_dict = clean_dictionary(dictionary)
    assert new_dict == {"key": ["value", "value2", "value3"]}


def test_validate_csv_bulk_imports_1(tmp_path):
    """Test the validate_csv_bulk_imports function.

    GIVEN a csv file missing the `path` column
    WHEN the validate_csv_bulk_imports function is called
    THEN an exception should be raised
    """
    csv_path = tmp_path / "test.csv"
    csv_content = """\
PATH,type,key,value
note1.md,type,key,value"""
    csv_path.write_text(csv_content)

    with pytest.raises(typer.BadParameter):
        validate_csv_bulk_imports(csv_path=csv_path, note_paths=[])


def test_validate_csv_bulk_imports_2(tmp_path):
    """Test the validate_csv_bulk_imports function.

    GIVEN a csv file missing the `type` column
    WHEN the validate_csv_bulk_imports function is called
    THEN an exception should be raised
    """
    csv_path = tmp_path / "test.csv"
    csv_content = """\
path,Type,key,value
note1.md,type,key,value"""
    csv_path.write_text(csv_content)

    with pytest.raises(typer.BadParameter):
        validate_csv_bulk_imports(csv_path=csv_path, note_paths=[])


def test_validate_csv_bulk_imports_3(tmp_path):
    """Test the validate_csv_bulk_imports function.

    GIVEN a csv file missing the `key` column
    WHEN the validate_csv_bulk_imports function is called
    THEN an exception should be raised
    """
    csv_path = tmp_path / "test.csv"
    csv_content = """\
path,type,value
note1.md,type,key,value"""
    csv_path.write_text(csv_content)

    with pytest.raises(typer.BadParameter):
        validate_csv_bulk_imports(csv_path=csv_path, note_paths=[])


def test_validate_csv_bulk_imports_4(tmp_path):
    """Test the validate_csv_bulk_imports function.

    GIVEN a csv file missing the `value` column
    WHEN the validate_csv_bulk_imports function is called
    THEN an exception should be raised
    """
    csv_path = tmp_path / "test.csv"
    csv_content = """\
path,type,key,values
note1.md,type,key,value"""
    csv_path.write_text(csv_content)

    with pytest.raises(typer.BadParameter):
        validate_csv_bulk_imports(csv_path=csv_path, note_paths=[])


def test_validate_csv_bulk_imports_5(tmp_path):
    """Test the validate_csv_bulk_imports function.

    GIVEN a csv file with only headers
    WHEN the validate_csv_bulk_imports function is called
    THEN an exception should be raised
    """
    csv_path = tmp_path / "test.csv"
    csv_content = "path,type,key,value"
    csv_path.write_text(csv_content)

    with pytest.raises(typer.BadParameter):
        validate_csv_bulk_imports(csv_path=csv_path, note_paths=[])


def test_validate_csv_bulk_imports_6(tmp_path, capsys):
    """Test the validate_csv_bulk_imports function.

    GIVEN a valid csv file
    WHEN a path is given that does not exist in the vault
    THEN show the user a warning
    """
    csv_path = tmp_path / "test.csv"
    csv_content = """\
path,type,key,value
note1.md,type,key,value
note2.md,type,key,value
"""
    csv_path.write_text(csv_content)

    csv_dict = validate_csv_bulk_imports(csv_path=csv_path, note_paths=["note1.md"])
    captured = remove_ansi(capsys.readouterr().out)
    assert "WARNING  | 'note2.md' does not exist in vault." in captured
    assert csv_dict == {"note1.md": [{"key": "key", "type": "type", "value": "value"}]}


def test_validate_csv_bulk_imports_7(tmp_path):
    """Test the validate_csv_bulk_imports function.

    GIVEN a valid csv file
    WHEN no paths match paths in the vault
    THEN exit the program
    """
    csv_path = tmp_path / "test.csv"
    csv_content = """\
path,type,key,value
note1.md,type,key,value
note2.md,type,key,value
"""
    csv_path.write_text(csv_content)
    with pytest.raises(typer.Exit):
        validate_csv_bulk_imports(csv_path=csv_path, note_paths=[])
