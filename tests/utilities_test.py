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
    merge_dictionaries,
    remove_markdown_sections,
    rename_in_dict,
    validate_csv_bulk_imports,
)
from tests.helpers import Regex, remove_ansi


def test_clean_dictionary_1():
    """Test clean_dictionary() function.

    GIVEN a dictionary passed to clean_dictionary()
    WHEN the dictionary is empty
    THEN return an empty dictionary
    """
    assert clean_dictionary({}) == {}


def test_clean_dictionary_2():
    """Test clean_dictionary() function.

    GIVEN a dictionary passed to clean_dictionary()
    WHEN keys contain leading/trailing spaces
    THEN remove the spaces from the keys
    """
    assert clean_dictionary({" key 1 ": "value 1"}) == {"key 1": "value 1"}


def test_clean_dictionary_3():
    """Test clean_dictionary() function.

    GIVEN a dictionary passed to clean_dictionary()
    WHEN values contain leading/trailing spaces
    THEN remove the spaces from the values
    """
    assert clean_dictionary({"key 1": " value 1 "}) == {"key 1": "value 1"}


def test_clean_dictionary_4():
    """Test clean_dictionary() function.

    GIVEN a dictionary passed to clean_dictionary()
    WHEN keys or values contain leading/trailing asterisks
    THEN remove the asterisks from the keys or values
    """
    assert clean_dictionary({"**key_1**": ["**value 1**", "value 2"]}) == {
        "key_1": ["value 1", "value 2"]
    }


def test_clean_dictionary_5():
    """Test clean_dictionary() function.

    GIVEN a dictionary passed to clean_dictionary()
    WHEN keys or values contain leading/trailing brackets
    THEN remove the brackets from the keys and values
    """
    assert clean_dictionary({"[[key_1]]": ["[[value 1]]", "[value 2]"]}) == {
        "key_1": ["value 1", "value 2"]
    }


def test_clean_dictionary_6():
    """Test clean_dictionary() function.

    GIVEN a dictionary passed to clean_dictionary()
    WHEN keys or values contain leading/trailing hashtags
    THEN remove the hashtags from the keys and values
    """
    assert clean_dictionary({"#key_1": ["#value 1", "value 2#"]}) == {
        "key_1": ["value 1", "value 2"]
    }


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


def test_dict_contains_1():
    """Test dict_contains() function.

    GIVEN calling dict_contains() with a dictionary
    WHEN the dictionary is empty
    THEN the function should return False
    """
    assert dict_contains({}, "key1") is False


def test_dict_contains_2():
    """Test dict_contains() function.

    GIVEN calling dict_contains() with a dictionary
    WHEN when the key is not in the dictionary
    THEN the function should return False
    """
    assert dict_contains({"key1": "value1"}, "key2") is False


def test_dict_contains_3():
    """Test dict_contains() function.

    GIVEN calling dict_contains() with a dictionary
    WHEN when the key is in the dictionary
    THEN the function should return True
    """
    assert dict_contains({"key1": "value1"}, "key1") is True


def test_dict_contains_4():
    """Test dict_contains() function.

    GIVEN calling dict_contains() with a dictionary
    WHEN when the key and value are in the dictionary
    THEN the function should return True
    """
    assert dict_contains({"key1": "value1"}, "key1", "value1") is True


def test_dict_contains_5():
    """Test dict_contains() function.

    GIVEN calling dict_contains() with a dictionary
    WHEN when the key and value are not in the dictionary
    THEN the function should return False
    """
    assert dict_contains({"key1": "value1"}, "key1", "value2") is False


def test_dict_contains_6():
    """Test dict_contains() function.

    GIVEN calling dict_contains() with a dictionary
    WHEN a regex is used for the key and the key is in the dictionary
    THEN the function should return True
    """
    assert dict_contains({"key1": "value1"}, r"key\d", is_regex=True) is True


def test_dict_contains_7():
    """Test dict_contains() function.

    GIVEN calling dict_contains() with a dictionary
    WHEN a regex is used for the key and the key is not in the dictionary
    THEN the function should return False
    """
    assert dict_contains({"key1": "value1"}, r"key\d\d", is_regex=True) is False


def test_dict_contains_8():
    """Test dict_contains() function.

    GIVEN calling dict_contains() with a dictionary
    WHEN a regex is used for a value and the value is in the dictionary
    THEN the function should return True
    """
    assert dict_contains({"key1": "value1"}, "key1", r"\w+", is_regex=True) is True


def test_dict_contains_9():
    """Test dict_contains() function.

    GIVEN calling dict_contains() with a dictionary
    WHEN a regex is used for a value and the value is not in the dictionary
    THEN the function should return False
    """
    assert dict_contains({"key1": "value1"}, "key1", r"\d{2}", is_regex=True) is False


def test_dict_keys_to_lower() -> None:
    """Test the dict_keys_to_lower() function.

    GIVEN a dictionary with mixed case keys
    WHEN the dict_keys_to_lower() function is called
    THEN the dictionary keys should be converted to lowercase
    """
    test_dict = {"Key1": "Value1", "KEY2": "Value2", "key3": "Value3"}
    assert dict_keys_to_lower(test_dict) == {"key1": "Value1", "key2": "Value2", "key3": "Value3"}


def test_dict_values_to_lists_strings_1():
    """Test the dict_values_to_lists_strings() function.

    GIVEN a dictionary passed to the dict_values_to_lists_strings() function
    WHEN the dictionary is empty
    THEN the function should return an empty dictionary
    """
    assert dict_values_to_lists_strings({}) == {}
    assert dict_values_to_lists_strings({}, strip_null_values=True) == {}


def test_dict_values_to_lists_strings_2():
    """Test the dict_values_to_lists_strings() function.

    GIVEN a dictionary passed to the dict_values_to_lists_strings() function
    WHEN the dictionary values are already lists of strings
    THEN the function should return the dictionary
    """
    test_dict = {"key1": ["value1"], "key2": ["value2", "value3"]}
    assert dict_values_to_lists_strings(test_dict) == {
        "key1": ["value1"],
        "key2": ["value2", "value3"],
    }
    assert dict_values_to_lists_strings(test_dict, strip_null_values=True) == {
        "key1": ["value1"],
        "key2": ["value2", "value3"],
    }


def test_dict_values_to_lists_strings_3():
    """Test the dict_values_to_lists_strings() function.

    GIVEN a dictionary passed to the dict_values_to_lists_strings() function
    WHEN the a value is None and strip_null_values is False
    THEN then convert None to an empty string
    """
    test_dict = {"key1": None, "key2": ["value", None]}
    assert dict_values_to_lists_strings(test_dict) == {"key1": [""], "key2": ["", "value"]}


def test_dict_values_to_lists_strings_4():
    """Test the dict_values_to_lists_strings() function.

    GIVEN a dictionary passed to the dict_values_to_lists_strings() function
    WHEN the a value is None and strip_null_values is True
    THEN remove null values
    """
    test_dict = {"key1": None, "key2": ["value", None]}
    assert dict_values_to_lists_strings(test_dict, strip_null_values=True) == {
        "key1": [],
        "key2": ["value"],
    }


def test_dict_values_to_lists_strings_5():
    """Test the dict_values_to_lists_strings() function.

    GIVEN a dictionary passed to the dict_values_to_lists_strings() function
    WHEN the a value is a string "None" and strip_null_values is True or False
    THEN ensure the value is not removed
    """
    test_dict = {"key1": "None", "key2": [None, "None"]}
    assert dict_values_to_lists_strings(test_dict) == {"key1": ["None"], "key2": ["", "None"]}
    assert dict_values_to_lists_strings(test_dict, strip_null_values=True) == {
        "key1": [],
        "key2": ["None"],
    }


def test_dict_values_to_lists_strings_6():
    """Test the dict_values_to_lists_strings() function.

    GIVEN a dictionary passed to the dict_values_to_lists_strings() function
    WHEN the a value is another dictionary
    THEN ensure the values in the inner dictionary are converted to lists of strings
    """
    test_dict = {"key1": {"key2": "value2", "key3": ["value3", None]}}
    assert dict_values_to_lists_strings(test_dict) == {
        "key1": {"key2": ["value2"], "key3": ["", "value3"]}
    }
    assert dict_values_to_lists_strings(test_dict, strip_null_values=True) == {
        "key1": {"key2": ["value2"], "key3": ["value3"]}
    }


def test_merge_dictionaries_1():
    """Test merge_dictionaries() function.

    GIVEN two dictionaries supplied to the merge_dictionaries() function
    WHEN a value in dict1 is not a list
    THEN raise a TypeError
    """
    test_dict_1 = {"key1": "value1", "key2": "value2"}
    test_dict_2 = {"key3": ["value3"], "key4": ["value4"]}

    with pytest.raises(TypeError, match=r"key.*is not a list"):
        merge_dictionaries(test_dict_1, test_dict_2)


def test_merge_dictionaries_2():
    """Test merge_dictionaries() function.

    GIVEN two dictionaries supplied to the merge_dictionaries() function
    WHEN a value in dict2 is not a list
    THEN raise a TypeError
    """
    test_dict_1 = {"key3": ["value3"], "key4": ["value4"]}
    test_dict_2 = {"key1": "value1", "key2": "value2"}

    with pytest.raises(TypeError, match=r"key.*is not a list"):
        merge_dictionaries(test_dict_1, test_dict_2)


def test_merge_dictionaries_3():
    """Test merge_dictionaries() function.

    GIVEN two dictionaries supplied to the merge_dictionaries() function
    WHEN keys and values in both dictionaries are unique
    THEN return a dictionary with the keys and values from both dictionaries
    """
    test_dict_1 = {"key1": ["value1"], "key2": ["value2"]}
    test_dict_2 = {"key3": ["value3"], "key4": ["value4"]}

    assert merge_dictionaries(test_dict_1, test_dict_2) == {
        "key1": ["value1"],
        "key2": ["value2"],
        "key3": ["value3"],
        "key4": ["value4"],
    }


def test_merge_dictionaries_4():
    """Test merge_dictionaries() function.

    GIVEN two dictionaries supplied to the merge_dictionaries() function
    WHEN keys in both dictionaries are not unique
    THEN return a dictionary with the merged keys and values from both dictionaries
    """
    test_dict_1 = {"key1": ["value1"], "key2": ["value2"]}
    test_dict_2 = {"key1": ["value3"], "key2": ["value4"]}

    assert merge_dictionaries(test_dict_1, test_dict_2) == {
        "key1": ["value1", "value3"],
        "key2": ["value2", "value4"],
    }


def test_merge_dictionaries_5():
    """Test merge_dictionaries() function.

    GIVEN two dictionaries supplied to the merge_dictionaries() function
    WHEN keys and values both dictionaries are not unique
    THEN return a dictionary with the merged keys and values from both dictionaries
    """
    test_dict_1 = {"key1": ["a", "c"], "key2": ["a", "b"]}
    test_dict_2 = {"key1": ["a", "b"], "key2": ["a", "c"]}

    assert merge_dictionaries(test_dict_1, test_dict_2) == {
        "key1": ["a", "b", "c"],
        "key2": ["a", "b", "c"],
    }


def test_merge_dictionaries_6():
    """Test merge_dictionaries() function.

    GIVEN two dictionaries supplied to the merge_dictionaries() function
    WHEN one of the dictionaries is empty
    THEN return a dictionary the other dictionary
    """
    test_dict_1 = {"key1": ["a", "c"], "key2": ["a", "b"]}
    test_dict_2 = {}

    assert merge_dictionaries(test_dict_1, test_dict_2) == {"key1": ["a", "c"], "key2": ["a", "b"]}

    test_dict_1 = {}
    test_dict_2 = {"key1": ["a", "c"], "key2": ["a", "b"]}
    assert merge_dictionaries(test_dict_1, test_dict_2) == {"key1": ["a", "c"], "key2": ["a", "b"]}


def test_merge_dictionaries_7():
    """Test merge_dictionaries() function.

    GIVEN two dictionaries supplied to the merge_dictionaries() function
    WHEN keys and values both dictionaries are not unique
    THEN ensure the original dictionaries objects are not modified
    """
    test_dict_1 = {"key1": ["a", "c"], "key2": ["a", "b"]}
    test_dict_2 = {"key1": ["a", "b"], "key2": ["a", "c"]}

    assert merge_dictionaries(test_dict_1, test_dict_2) == {
        "key1": ["a", "b", "c"],
        "key2": ["a", "b", "c"],
    }
    assert test_dict_1 == {"key1": ["a", "c"], "key2": ["a", "b"]}
    assert test_dict_2 == {"key1": ["a", "b"], "key2": ["a", "c"]}


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


def test_remove_markdown_sections_1():
    """Test remove_markdown_sections() function.

    GIVEN a string with markdown sections
    WHEN the remove_markdown_sections() function is called with the default arguments
    THEN return the string without removing any markdown sections
    """
    text: str = """
---
key: value
---

# heading

```bash
echo "Hello world"
```

Lorem ipsum `inline_code` lorem ipsum.
```
echo "foo bar"
```

---
dd
---
    """

    assert remove_markdown_sections(text) == text


def test_remove_markdown_sections_2():
    """Test remove_markdown_sections() function.

    GIVEN a string with markdown sections
    WHEN the remove_markdown_sections() function is called with strip_codeblocks set to True
    THEN return the string without the codeblocks
    """
    text: str = """
---
key: value
---

# heading

```bash
echo "Hello world"
```

Lorem ipsum `inline_code` lorem ipsum.
```
echo "foo bar"
```

---
dd
---
    """
    result = remove_markdown_sections(text, strip_codeblocks=True)
    assert "inline_code" in result
    assert "```bash" not in result
    assert "```" not in result
    assert "foo" not in result
    assert "world" not in result
    assert "key: value" in result
    assert "heading" in result
    assert "Lorem ipsum" in result
    assert "---\n" in result
    assert "dd" in result


def test_remove_markdown_sections_3():
    """Test remove_markdown_sections() function.

    GIVEN a string with markdown sections
    WHEN the remove_markdown_sections() function is called with strip_inlinecode set to True
    THEN return the string without the inline code
    """
    text: str = """
---
key: value
---

# heading

```bash
echo "Hello world"
```

Lorem ipsum `inline_code` lorem ipsum.
```
echo "foo bar"
```

---
dd
---
    """
    result = remove_markdown_sections(text, strip_inlinecode=True)
    assert "`inline_code`" not in result
    assert "```bash" in result
    assert "```" in result
    assert "foo" in result
    assert "world" in result
    assert "key: value" in result
    assert "heading" in result
    assert "Lorem ipsum" in result
    assert "---\n" in result
    assert "dd" in result


def test_remove_markdown_sections_4():
    """Test remove_markdown_sections() function.

    GIVEN a string with markdown sections
    WHEN the remove_markdown_sections() function is called with strip_frontmatter set to True
    THEN return the string without the frontmatter
    """
    text: str = """
---
key: value
---

# heading

```bash
echo "Hello world"
```

Lorem ipsum `inline_code` lorem ipsum.
```
echo "foo bar"
```

---
dd
---
    """
    result = remove_markdown_sections(text, strip_frontmatter=True)
    assert "`inline_code`" in result
    assert "```bash" in result
    assert "```" in result
    assert "foo" in result
    assert "world" in result
    assert "key: value" not in result
    assert "heading" in result
    assert "Lorem ipsum" in result
    assert "---\n" in result
    assert "dd" in result


def test_remove_markdown_sections_5():
    """Test remove_markdown_sections() function.

    GIVEN a string with markdown sections
    WHEN the remove_markdown_sections() function is called with all arguments set to True
    THEN return the string without the frontmatter, inline code, and codeblocks
    """
    text: str = """
---
key: value
---

# heading

```bash
echo "Hello world"
```

Lorem ipsum `inline_code` lorem ipsum.
```
echo "foo bar"
```

---
dd
---
    """
    result = remove_markdown_sections(
        text, strip_frontmatter=True, strip_inlinecode=True, strip_codeblocks=True
    )
    assert "`inline_code`" not in result
    assert "bash" not in result
    assert "```" not in result
    assert "foo" not in result
    assert "world" not in result
    assert "key: value" not in result
    assert "heading" in result
    assert "Lorem ipsum" in result
    assert "---\n" in result
    assert "dd" in result


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
