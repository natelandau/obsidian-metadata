# type: ignore
"""Test inline metadata from metadata.py."""
import pytest

from obsidian_metadata.models.exceptions import InlineMetadataError
from obsidian_metadata.models.metadata import InlineMetadata

FRONTMATTER_CONTENT: str = """
---
tags:
  - tag_1
  - tag_2
  -
  - 📅/tag_3
frontmatter_Key1: "frontmatter_Key1_value"
frontmatter_Key2: ["note", "article"]
shared_key1: "shared_key1_value"
---
more content

---
horizontal: rule
---
"""

INLINE_CONTENT = """\
key1:: value1
key1:: value2
key1:: value3
key2:: value1
Paragraph of text with an [inline_key:: value1] and [inline_key:: value2] and [inline_key:: value3] which should do it.
> blockquote_key:: value1
> blockquote_key:: value2

- list_key:: value1
- list_key:: value2

1. list_key:: value1
2. list_key:: value2
"""


def test__grab_inline_metadata_1():
    """Test grab inline metadata.

    GIVEN content that has no inline metadata
    WHEN grab_inline_metadata is called
    THEN an empty dict is returned

    """
    content = """
---
frontmatter_key1: frontmatter_key1_value
---
not_a_key: not_a_value
```
key:: in_codeblock
```
    """
    inline = InlineMetadata(content)
    assert inline.dict == {}


def test__grab_inline_metadata_2():
    """Test grab inline metadata.

    GIVEN content that has inline metadata
    WHEN grab_inline_metadata is called
    THEN the inline metadata is parsed and returned as a dict

    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.dict == {
        "blockquote_key": ["value1", "value2"],
        "inline_key": ["value1", "value2", "value3"],
        "key1": ["value1", "value2", "value3"],
        "key2": ["value1"],
        "list_key": ["value1", "value2", "value1", "value2"],
    }


def test__grab_inline_metadata_3(mocker):
    """Test grab inline metadata.

    GIVEN content that has inline metadata
    WHEN an error occurs parsing the inline metadata
    THEN raise an InlineMetadataError and pass the error message
    """
    mocker.patch(
        "obsidian_metadata.models.metadata.inline_metadata_from_string",
        return_value=[("key")],
    )
    with pytest.raises(InlineMetadataError, match=r"Error parsing inline metadata: \['key'\]"):
        InlineMetadata("")


def test_add_1():
    """Test InlineMetadata add() method.

    GIVEN a InlineMetadata object
    WHEN the add() method is called with an existing key
    THEN return False
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.add("key1") is False


def test_add_2():
    """Test InlineMetadata add() method.

    GIVEN a InlineMetadata object
    WHEN the add() method is called with an existing key and existing value
    THEN return False
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.add("key1", "value1") is False


def test_add_3():
    """Test InlineMetadata add() method.

    GIVEN a InlineMetadata object
    WHEN the add() method is called with a new key
    THEN return True and add the key to the dict
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.add("added_key") is True
    assert "added_key" in inline.dict


def test_add_4():
    """Test InlineMetadata add() method.

    GIVEN a InlineMetadata object
    WHEN the add() method is called with a new key and a new value
    THEN return True and add the key and the value to the dict
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.add("added_key", "added_value") is True
    assert inline.dict["added_key"] == ["added_value"]


def test_add_5():
    """Test InlineMetadata add() method.

    GIVEN a InlineMetadata object
    WHEN the add() method is called with an existing key and a new value
    THEN return True and add the value to the dict
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.add("key1", "new_value") is True
    assert inline.dict["key1"] == ["value1", "value2", "value3", "new_value"]


def test_add_6():
    """Test InlineMetadata add() method.

    GIVEN a InlineMetadata object
    WHEN the add() method is called with an existing key and a list of new values
    THEN return True and add the values to the dict
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.add("key2", ["new_value", "new_value2"]) is True
    assert inline.dict["key2"] == ["new_value", "new_value2", "value1"]


def test_add_7():
    """Test InlineMetadata add() method.

    GIVEN a InlineMetadata object
    WHEN the add() method is called with an existing key and a list of values including an existing value
    THEN return True and add the new values to the dict
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.add("key1", ["value1", "new_value", "new_value2"]) is True
    assert inline.dict["key1"] == ["new_value", "new_value2", "value1", "value2", "value3"]


def test_add_8():
    """Test InlineMetadata add() method.

    GIVEN a InlineMetadata object
    WHEN the add() method is called with a new key and a list of values
    THEN return True and add the new values to the dict
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.add("new_key", ["value1", "new_value", "new_value2"]) is True
    assert inline.dict["new_key"] == ["value1", "new_value", "new_value2"]


def test_contains_1():
    """Test InlineMetadata contains() method.

    GIVEN a InlineMetadata object
    WHEN the contains() method is called with a key
    THEN return True if the key is found
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.contains("key1") is True


def test_contains_2():
    """Test InlineMetadata contains() method.

    GIVEN a InlineMetadata object
    WHEN the contains() method is called with a key
    THEN return False if the key is not found
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.contains("no_key") is False


def test_contains_3():
    """Test InlineMetadata contains() method.

    GIVEN a InlineMetadata object
    WHEN the contains() method is called with a key and a value
    THEN return True if the key and value is found
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.contains("key1", "value1") is True


def test_contains_4():
    """Test InlineMetadata contains() method.

    GIVEN a InlineMetadata object
    WHEN the contains() method is called with a key and a value
    THEN return False if the key and value is not found
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.contains("key1", "no value") is False


def test_contains_5():
    """Test InlineMetadata contains() method.

    GIVEN a InlineMetadata object
    WHEN the contains() method is called with a key regex
    THEN return True if a key matches the regex
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.contains(r"\d$", is_regex=True) is True


def test_contains_6():
    """Test InlineMetadata contains() method.

    GIVEN a InlineMetadata object
    WHEN the contains() method is called with a key regex
    THEN return False if no key matches the regex
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.contains(r"^\d", is_regex=True) is False


def test_contains_7():
    """Test InlineMetadata contains() method.

    GIVEN a InlineMetadata object
    WHEN the contains() method is called with a key and value regex
    THEN return True if a value matches the regex
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.contains(r"key\d", r"\w\d", is_regex=True) is True


def test_contains_8():
    """Test InlineMetadata contains() method.

    GIVEN a InlineMetadata object
    WHEN the contains() method is called with a key and value regex
    THEN return False if a value does not match the regex
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.contains("key1", r"_\d", is_regex=True) is False


def test_delete_1():
    """Test InlineMetadata delete() method.

    GIVEN a InlineMetadata object
    WHEN the delete() method is called with a key that does not exist
    THEN return False
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.delete("no key") is False


def test_delete_2():
    """Test InlineMetadata delete() method.

    GIVEN a InlineMetadata object
    WHEN the delete() method is called with an existing key and a value that does not exist
    THEN return False
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.delete("key1", "no value") is False


def test_delete_3():
    """Test InlineMetadata delete() method.

    GIVEN a InlineMetadata object
    WHEN the delete() method is called with a regex that does not match any keys
    THEN return False
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.delete(r"\d{3}", is_regex=True) is False


def test_delete_4():
    """Test InlineMetadata delete() method.

    GIVEN a InlineMetadata object
    WHEN the delete() method is called with an existing key and a regex that does not match any values
    THEN return False
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.delete("key1", r"\d{5}", is_regex=True) is False


def test_delete_5():
    """Test InlineMetadata delete() method.

    GIVEN a InlineMetadata object
    WHEN the delete() method is called with an existing key and an existing value
    THEN return True and delete the value from the dict
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.delete("key1", "value1") is True
    assert "value1" not in inline.dict["key1"]
    assert "key1" in inline.dict


def test_delete_6():
    """Test InlineMetadata delete() method.

    GIVEN a InlineMetadata object
    WHEN the delete() method is called with an existing key
    THEN return True and delete the key from the dict
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.delete("key1") is True
    assert "key1" not in inline.dict


def test_delete_7():
    """Test InlineMetadata delete() method.

    GIVEN a InlineMetadata object
    WHEN the delete() method is called with a regex that matches a key
    THEN return True and delete the matching keys from the dict
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.delete(r"key\w+", is_regex=True) is True
    assert "key1" not in inline.dict
    assert "key2" not in inline.dict


def test_delete_8():
    """Test InlineMetadata delete() method.

    GIVEN a InlineMetadata object
    WHEN the delete() method is called with an existing key and a regex that matches values
    THEN return True and delete the matching values
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.delete("key1", r"\w+\d", is_regex=True) is True
    assert "value1" not in inline.dict["key1"]
    assert "value2" not in inline.dict["key1"]
    assert "value3" not in inline.dict["key1"]


def test_has_changes_1():
    """Test InlineMetadata has_changes() method.

    GIVEN a InlineMetadata object
    WHEN no changes have been made to the object
    THEN return False
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.has_changes() is False


def test_has_changes_2():
    """Test InlineMetadata has_changes() method.

    GIVEN a InlineMetadata object
    WHEN changes have been made to the object
    THEN return True
    """
    inline = InlineMetadata(INLINE_CONTENT)
    inline.dict["new key"] = ["new value"]
    assert inline.has_changes() is True


def test_rename_1():
    """Test InlineMetadata rename() method.

    GIVEN a InlineMetadata object
    WHEN the rename() method is called with a key
    THEN return False if the key is not found
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.rename("no key", "new key") is False


def test_rename_2():
    """Test InlineMetadata rename() method.

    GIVEN a InlineMetadata object
    WHEN the rename() method is called with an existing key and non-existing value
    THEN return False
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.rename("key1", "no value", "new value") is False


def test_rename_3():
    """Test InlineMetadata rename() method.

    GIVEN a InlineMetadata object
    WHEN the rename() method is called with an existing key
    THEN return True and rename the key
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.rename("key1", "new key") is True
    assert "key1" not in inline.dict
    assert inline.dict["new key"] == ["value1", "value2", "value3"]


def test_rename_4():
    """Test InlineMetadata rename() method.

    GIVEN a InlineMetadata object
    WHEN the rename() method is called with an existing key and value
    THEN return True and rename the value
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.rename("key1", "value1", "new value") is True
    assert "value1" not in inline.dict["key1"]
    assert "new value" in inline.dict["key1"]


def test_rename_5():
    """Test InlineMetadata rename() method.

    GIVEN a InlineMetadata object
    WHEN the rename() method is called with an existing key and value and the new value already exists
    THEN return True and remove the old value leaving one instance of the new value
    """
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.rename("key1", "value1", "value2") is True
    assert inline.dict["key1"] == ["value2", "value3"]
