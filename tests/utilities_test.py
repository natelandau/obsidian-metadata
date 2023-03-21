# type: ignore
"""Test the utilities module."""

import pytest
import typer

from obsidian_metadata._utils import (
    clean_dictionary,
    delete_from_dict,
    dict_contains,
    dict_keys_to_lower,
    dict_values_to_lists_strings,
    remove_markdown_sections,
    rename_in_dict,
    validate_csv_bulk_imports,
)
from tests.helpers import Regex, remove_ansi


def test_delete_from_dict_1():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values
    WHEN the delete_from_dict() function is called with a key that exists
    THEN the key should be deleted from the dictionary and the original dictionary should not be modified
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert delete_from_dict(dictionary=test_dict, key="key1") == {
        "key2": ["value2", "value3"],
        "key3": "value4",
    }
    assert test_dict == {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}


def test_delete_from_dict_2():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values
    WHEN the delete_from_dict() function is called with a key that does not exist
    THEN the dictionary should not be modified
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert delete_from_dict(dictionary=test_dict, key="key5") == test_dict


def test_delete_from_dict_3():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values in a list
    WHEN the delete_from_dict() function is called with a key and value that exists
    THEN the value should be deleted from the specified key in dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert delete_from_dict(dictionary=test_dict, key="key2", value="value3") == {
        "key1": ["value1"],
        "key2": ["value2"],
        "key3": "value4",
    }


def test_delete_from_dict_4():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values as strings
    WHEN the delete_from_dict() function is called with a key and value that exists
    THEN the value and key should be deleted from the dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert delete_from_dict(dictionary=test_dict, key="key3", value="value4") == {
        "key1": ["value1"],
        "key2": ["value2", "value3"],
    }


def test_delete_from_dict_5():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values as strings
    WHEN the delete_from_dict() function is called with a key and value that does not exist
    THEN the dictionary should not be modified
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert delete_from_dict(dictionary=test_dict, key="key3", value="value5") == test_dict


def test_delete_from_dict_6():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values as strings
    WHEN the delete_from_dict() function is called with a key regex that matches
    THEN the matching keys should be deleted from the dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert delete_from_dict(dictionary=test_dict, key="key[23]", is_regex=True) == {
        "key1": ["value1"]
    }


def test_delete_from_dict_7():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values as strings
    WHEN the delete_from_dict() function is called with a key regex that does not match
    THEN no keys should be deleted from the dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert delete_from_dict(dictionary=test_dict, key=r"key\d\d", is_regex=True) == test_dict


def test_delete_from_dict_8():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values as strings
    WHEN the delete_from_dict() function is called with a key and value regex that matches
    THEN the matching keys should be deleted from the dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert delete_from_dict(dictionary=test_dict, key="key2", value=r"\w+", is_regex=True) == {
        "key1": ["value1"],
        "key2": [],
        "key3": "value4",
    }


def test_delete_from_dict_9():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values as strings
    WHEN the delete_from_dict() function is called with a key and value regex that does not match
    THEN no keys should be deleted from the dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert (
        delete_from_dict(dictionary=test_dict, key=r"key2", value=r"^\d", is_regex=True)
        == test_dict
    )


def test_delete_from_dict_10():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values as strings
    WHEN the delete_from_dict() function is called with a key and value regex that matches
    THEN the matching keys should be deleted from the dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert delete_from_dict(dictionary=test_dict, key="key3", value=r"\w+", is_regex=True) == {
        "key1": ["value1"],
        "key2": ["value2", "value3"],
    }


def test_delete_from_dict_11():
    """Test delete_from_dict() function.

    GIVEN a dictionary with values as strings
    WHEN the delete_from_dict() function is called with a key regex that matches multiple and values that match
    THEN the values matching the associated keys should be deleted from the dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"], "key3": "value4"}

    assert delete_from_dict(
        dictionary=test_dict, key=r"key[23]", value=r"\w+[34]$", is_regex=True
    ) == {"key1": ["value1"], "key2": ["value2"]}


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


def test_rename_in_dict_1():
    """Test rename_in_dict() function.

    GIVEN a dictionary with values as a list
    WHEN the rename_in_dict() function is called with a key that does not exist
    THEN no keys should be renamed in the dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"]}

    assert rename_in_dict(dictionary=test_dict, key="key4", value_1="key5") == test_dict


def test_rename_in_dict_2():
    """Test rename_in_dict() function.

    GIVEN a dictionary with values as a list
    WHEN the rename_in_dict() function is called with a key that exists and a new value for the key
    THEN the key should be renamed in the returned dictionary and the original dictionary should not be modified
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"]}

    assert rename_in_dict(dictionary=test_dict, key="key2", value_1="new_key") == {
        "key1": ["value1"],
        "new_key": ["value2", "value3"],
    }
    assert test_dict == {"key1": ["value1"], "key2": ["value2", "value3"]}


def test_rename_in_dict_3():
    """Test rename_in_dict() function.

    GIVEN a dictionary with values as a list
    WHEN the rename_in_dict() function is called with a key that exists value that does not exist
    THEN the dictionary should not be modified
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"]}

    assert (
        rename_in_dict(dictionary=test_dict, key="key2", value_1="no_value", value_2="new_value")
        == test_dict
    )


def test_rename_in_dict_4():
    """Test rename_in_dict() function.

    GIVEN a dictionary with values as a list
    WHEN the rename_in_dict() function is called with a key that exists and a new value for a value
    THEN update the specified value in the dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"]}

    assert rename_in_dict(
        dictionary=test_dict, key="key2", value_1="value2", value_2="new_value"
    ) == {"key1": ["value1"], "key2": ["new_value", "value3"]}


def test_rename_in_dict_5():
    """Test rename_in_dict() function.

    GIVEN a dictionary with values as a list
    WHEN the rename_in_dict() function is called with a key that exists and a an existing value for a renamed value
    THEN only one instance of the new value should be in the key
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"]}

    assert rename_in_dict(dictionary=test_dict, key="key2", value_1="value2", value_2="value3") == {
        "key1": ["value1"],
        "key2": ["value3"],
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
note1.md,frontmatter,key,value"""
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
note1.md,frontmatter,key,value"""
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
note1.md,frontmatter,key,value"""
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
note1.md,frontmatter,key,value"""
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


def test_validate_csv_bulk_imports_6(tmp_path):
    """Test the validate_csv_bulk_imports function.

    GIVEN a valid csv file
    WHEN a path is given that does not exist in the vault
    THEN show the user a warning
    """
    csv_path = tmp_path / "test.csv"
    csv_content = """\
path,type,key,value
note1.md,frontmatter,key,value
note1.md,tag,key,value
note1.md,inline_metadata,key,value
note1.md,inline_metadata,key2,value
note1.md,inline_metadata,key2,value2
note2.md,frontmatter,key,value
note2.md,tag,key,value
note2.md,inline_metadata,key,value
note2.md,inline_metadata,key2,value
note2.md,inline_metadata,key2,value2
"""
    csv_path.write_text(csv_content)

    with pytest.raises(typer.BadParameter):
        validate_csv_bulk_imports(csv_path=csv_path, note_paths=["note1.md"])


def test_validate_csv_bulk_imports_7(tmp_path):
    """Test the validate_csv_bulk_imports function.

    GIVEN a valid csv file
    WHEN if a type is not 'frontmatter' or 'inline_metadata', 'tag'
    THEN exit the program
    """
    csv_path = tmp_path / "test.csv"
    csv_content = """\
path,type,key,value
note1.md,frontmatter,key,value
note2.md,notvalid,key,value
"""
    csv_path.write_text(csv_content)
    with pytest.raises(typer.BadParameter):
        validate_csv_bulk_imports(csv_path=csv_path, note_paths=["note1.md", "note2.md"])


def test_validate_csv_bulk_imports_8(tmp_path):
    """Test the validate_csv_bulk_imports function.

    GIVEN a valid csv file
    WHEN more than one row has the same path
    THEN add the row to the list of rows for that path
    """
    csv_path = tmp_path / "test.csv"
    csv_content = """\
path,type,key,value
note1.md,frontmatter,key,value
note1.md,tag,key,value
note1.md,inline_metadata,key,value
note1.md,inline_metadata,key2,value
note1.md,inline_metadata,key2,value2
note2.md,frontmatter,key,value
note2.md,tag,key,value
note2.md,inline_metadata,key,value
note2.md,inline_metadata,key2,value
note2.md,inline_metadata,key2,value2
"""
    csv_path.write_text(csv_content)
    csv_dict = validate_csv_bulk_imports(csv_path=csv_path, note_paths=["note1.md", "note2.md"])
    assert csv_dict == {
        "note1.md": [
            {"key": "key", "type": "frontmatter", "value": "value"},
            {"key": "key", "type": "tag", "value": "value"},
            {"key": "key", "type": "inline_metadata", "value": "value"},
            {"key": "key2", "type": "inline_metadata", "value": "value"},
            {"key": "key2", "type": "inline_metadata", "value": "value2"},
        ],
        "note2.md": [
            {"key": "key", "type": "frontmatter", "value": "value"},
            {"key": "key", "type": "tag", "value": "value"},
            {"key": "key", "type": "inline_metadata", "value": "value"},
            {"key": "key2", "type": "inline_metadata", "value": "value"},
            {"key": "key2", "type": "inline_metadata", "value": "value2"},
        ],
    }
