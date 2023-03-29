# type: ignore
"""Test the Frontmatter object from metadata.py."""

import pytest

from obsidian_metadata.models.exceptions import FrontmatterError
from obsidian_metadata.models.metadata import Frontmatter

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
repeated_key:: repeated_key_value1
#inline_tag_top1,#inline_tag_top2
**bold_key1**:: bold_key1_value
**bold_key2:: bold_key2_value**
link_key:: [[link_key_value]]
tag_key:: #tag_key_value
emoji_📅_key:: emoji_📅_key_value
**#bold_tag**

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. [in_text_key1:: in_text_key1_value] Ut enim ad minim veniam, quis nostrud exercitation [in_text_key2:: in_text_key2_value] ullamco laboris nisi ut aliquip ex ea commodo consequat. #in_text_tag Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

```python
#ffffff
# This is sample text [no_key:: value]with tags and metadata
#in_codeblock_tag1
#ffffff;
in_codeblock_key:: in_codeblock_value
The quick brown fox jumped over the #in_codeblock_tag2
```
repeated_key:: repeated_key_value2
"""


def test_create_1() -> None:
    """Test frontmatter creation.

    GIVEN valid frontmatter content
    WHEN a Frontmatter object is created
    THEN parse the YAML frontmatter and add it to the object
    """
    frontmatter = Frontmatter(INLINE_CONTENT)
    assert frontmatter.dict == {}

    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.dict == {
        "frontmatter_Key1": ["frontmatter_Key1_value"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "tags": ["tag_1", "tag_2", "📅/tag_3"],
    }
    assert frontmatter.dict_original == {
        "frontmatter_Key1": ["frontmatter_Key1_value"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "tags": ["tag_1", "tag_2", "📅/tag_3"],
    }


def test_create_2() -> None:
    """Test frontmatter creation error.

    GIVEN invalid frontmatter content
    WHEN a Frontmatter object is created
    THEN raise ValueError
    """
    fn = """---
tags: tag
invalid = = "content"
---
    """
    with pytest.raises(FrontmatterError):
        Frontmatter(fn)


def test_create_3():
    """Test frontmatter creation error.

    GIVEN empty frontmatter content
    WHEN a Frontmatter object is created
    THEN set the dict to an empty dict
    """
    content = "---\n\n---"
    frontmatter = Frontmatter(content)
    assert frontmatter.dict == {}


def test_create_4():
    """Test frontmatter creation error.

    GIVEN empty frontmatter content with a yaml marker
    WHEN a Frontmatter object is created
    THEN set the dict to an empty dict
    """
    content = "---\n-\n---"
    frontmatter = Frontmatter(content)
    assert frontmatter.dict == {}


def test_add_1():
    """Test frontmatter add() method.

    GIVEN a Frontmatter object
    WHEN the add() method is called with an existing key
    THEN return False
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)

    assert frontmatter.add("frontmatter_Key1") is False


def test_add_2():
    """Test frontmatter add() method.

    GIVEN a Frontmatter object
    WHEN the add() method is called with an existing key and existing value
    THEN return False
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.add("frontmatter_Key1", "frontmatter_Key1_value") is False


def test_add_3():
    """Test frontmatter add() method.

    GIVEN a Frontmatter object
    WHEN the add() method is called with a new key
    THEN return True and add the key to the dict
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.add("added_key") is True
    assert "added_key" in frontmatter.dict


def test_add_4():
    """Test frontmatter add() method.

    GIVEN a Frontmatter object
    WHEN the add() method is called with a new key and a new value
    THEN return True and add the key and the value to the dict
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.add("added_key", "added_value") is True
    assert frontmatter.dict["added_key"] == ["added_value"]


def test_add_5():
    """Test frontmatter add() method.

    GIVEN a Frontmatter object
    WHEN the add() method is called with an existing key and a new value
    THEN return True and add the value to the dict
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.add("frontmatter_Key1", "new_value") is True
    assert frontmatter.dict["frontmatter_Key1"] == ["frontmatter_Key1_value", "new_value"]


def test_add_6():
    """Test frontmatter add() method.

    GIVEN a Frontmatter object
    WHEN the add() method is called with an existing key and a list of new values
    THEN return True and add the values to the dict
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.add("frontmatter_Key1", ["new_value", "new_value2"]) is True
    assert frontmatter.dict["frontmatter_Key1"] == [
        "frontmatter_Key1_value",
        "new_value",
        "new_value2",
    ]


def test_add_7():
    """Test frontmatter add() method.

    GIVEN a Frontmatter object
    WHEN the add() method is called with an existing key and a list of values including an existing value
    THEN return True and add the new values to the dict
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert (
        frontmatter.add("frontmatter_Key1", ["frontmatter_Key1_value", "new_value", "new_value2"])
        is True
    )
    assert frontmatter.dict["frontmatter_Key1"] == [
        "frontmatter_Key1_value",
        "new_value",
        "new_value2",
    ]


def test_contains_1():
    """Test frontmatter contains() method.

    GIVEN a Frontmatter object
    WHEN the contains() method is called with a key
    THEN return True if the key is found
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.contains("frontmatter_Key1") is True


def test_contains_2():
    """Test frontmatter contains() method.

    GIVEN a Frontmatter object
    WHEN the contains() method is called with a key
    THEN return False if the key is not found
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.contains("no_key") is False


def test_contains_3():
    """Test frontmatter contains() method.

    GIVEN a Frontmatter object
    WHEN the contains() method is called with a key and a value
    THEN return True if the key and value is found
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.contains("frontmatter_Key2", "article") is True


def test_contains_4():
    """Test frontmatter contains() method.

    GIVEN a Frontmatter object
    WHEN the contains() method is called with a key and a value
    THEN return False if the key and value is not found
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.contains("frontmatter_Key2", "no value") is False


def test_contains_5():
    """Test frontmatter contains() method.

    GIVEN a Frontmatter object
    WHEN the contains() method is called with a key regex
    THEN return True if a key matches the regex
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.contains(r"\d$", is_regex=True) is True


def test_contains_6():
    """Test frontmatter contains() method.

    GIVEN a Frontmatter object
    WHEN the contains() method is called with a key regex
    THEN return False if no key matches the regex
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.contains(r"^\d", is_regex=True) is False


def test_contains_7():
    """Test frontmatter contains() method.

    GIVEN a Frontmatter object
    WHEN the contains() method is called with a key and value regex
    THEN return True if a value matches the regex
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.contains("key", r"\w\d_", is_regex=True) is True


def test_contains_8():
    """Test frontmatter contains() method.

    GIVEN a Frontmatter object
    WHEN the contains() method is called with a key and value regex
    THEN return False if a value does not match the regex
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.contains("key", r"_\d", is_regex=True) is False


def test_delete_1():
    """Test frontmatter delete() method.

    GIVEN a Frontmatter object
    WHEN the delete() method is called with a key that does not exist
    THEN return False
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.delete("no key") is False


def test_delete_2():
    """Test frontmatter delete() method.

    GIVEN a Frontmatter object
    WHEN the delete() method is called with an existing key and a value that does not exist
    THEN return False
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.delete("tags", "no value") is False


def test_delete_3():
    """Test frontmatter delete() method.

    GIVEN a Frontmatter object
    WHEN the delete() method is called with a regex that does not match any keys
    THEN return False
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.delete(r"\d{3}", is_regex=True) is False


def test_delete_4():
    """Test frontmatter delete() method.

    GIVEN a Frontmatter object
    WHEN the delete() method is called with an existing key and a regex that does not match any values
    THEN return False
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.delete("tags", r"\d{5}", is_regex=True) is False


def test_delete_5():
    """Test frontmatter delete() method.

    GIVEN a Frontmatter object
    WHEN the delete() method is called with an existing key and an existing value
    THEN return True and delete the value from the dict
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.delete("tags", "tag_2") is True
    assert "tag_2" not in frontmatter.dict["tags"]
    assert "tags" in frontmatter.dict


def test_delete_6():
    """Test frontmatter delete() method.

    GIVEN a Frontmatter object
    WHEN the delete() method is called with an existing key
    THEN return True and delete the key from the dict
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.delete("tags") is True
    assert "tags" not in frontmatter.dict


def test_delete_7():
    """Test frontmatter delete() method.

    GIVEN a Frontmatter object
    WHEN the delete() method is called with a regex that matches a key
    THEN return True and delete the matching keys from the dict
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.delete(r"front\w+", is_regex=True) is True
    assert "frontmatter_Key1" not in frontmatter.dict
    assert "frontmatter_Key2" not in frontmatter.dict


def test_delete_8():
    """Test frontmatter delete() method.

    GIVEN a Frontmatter object
    WHEN the delete() method is called with an existing key and a regex that matches values
    THEN return True and delete the matching values
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.delete("tags", r"\w+_[23]", is_regex=True) is True
    assert "tag_2" not in frontmatter.dict["tags"]
    assert "📅/tag_3" not in frontmatter.dict["tags"]
    assert "tag_1" in frontmatter.dict["tags"]


def test_delete_all():
    """Test Frontmatter delete_all method.

    GIVEN Frontmatter with multiple keys
    WHEN delete_all is called
    THEN all keys and values are deleted
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    frontmatter.delete_all()
    assert frontmatter.dict == {}


def test_has_changes_1():
    """Test frontmatter has_changes() method.

    GIVEN a Frontmatter object
    WHEN no changes have been made to the object
    THEN return False
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.has_changes() is False


def test_has_changes_2():
    """Test frontmatter has_changes() method.

    GIVEN a Frontmatter object
    WHEN changes have been made to the object
    THEN return True
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    frontmatter.dict["new key"] = ["new value"]
    assert frontmatter.has_changes() is True


def test_rename_1():
    """Test frontmatter rename() method.

    GIVEN a Frontmatter object
    WHEN the rename() method is called with a key
    THEN return False if the key is not found
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.rename("no key", "new key") is False


def test_rename_2():
    """Test frontmatter rename() method.

    GIVEN a Frontmatter object
    WHEN the rename() method is called with an existing key and non-existing value
    THEN return False
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.rename("tags", "no tag", "new key") is False


def test_rename_3():
    """Test frontmatter rename() method.

    GIVEN a Frontmatter object
    WHEN the rename() method is called with an existing key
    THEN return True and rename the key
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.rename("frontmatter_Key1", "new key") is True
    assert "frontmatter_Key1" not in frontmatter.dict
    assert frontmatter.dict["new key"] == ["frontmatter_Key1_value"]


def test_rename_4():
    """Test frontmatter rename() method.

    GIVEN a Frontmatter object
    WHEN the rename() method is called with an existing key and value
    THEN return True and rename the value
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.rename("tags", "tag_2", "new tag") is True
    assert "tag_2" not in frontmatter.dict["tags"]
    assert "new tag" in frontmatter.dict["tags"]


def test_rename_5():
    """Test frontmatter rename() method.

    GIVEN a Frontmatter object
    WHEN the rename() method is called with an existing key and value and the new value already exists
    THEN return True and remove the old value leaving one instance of the new value
    """
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.rename("tags", "tag_1", "tag_2") is True
    assert "tag_1" not in frontmatter.dict["tags"]
    assert frontmatter.dict["tags"] == ["tag_2", "📅/tag_3"]


def test_to_yaml_1():
    """Test Frontmatter to_yaml method.

    GIVEN a dictionary
    WHEN the to_yaml method is called
    THEN return a string with the yaml representation of the dictionary
    """
    new_frontmatter: str = """\
tags:
  - tag_1
  - tag_2
  - 📅/tag_3
frontmatter_Key1: frontmatter_Key1_value
frontmatter_Key2:
  - article
  - note
shared_key1: shared_key1_value
"""
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.to_yaml() == new_frontmatter


def test_to_yaml_2():
    """Test Frontmatter to_yaml method.

    GIVEN a dictionary
    WHEN the to_yaml method is called with sort_keys=True
    THEN return a string with the sorted yaml representation of the dictionary
    """
    new_frontmatter_sorted: str = """\
frontmatter_Key1: frontmatter_Key1_value
frontmatter_Key2:
  - article
  - note
shared_key1: shared_key1_value
tags:
  - tag_1
  - tag_2
  - 📅/tag_3
"""
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.to_yaml(sort_keys=True) == new_frontmatter_sorted
