# type: ignore
"""Test VaultMetadata object from metadata.py."""
import pytest

from obsidian_metadata.models.enums import MetadataType
from obsidian_metadata.models.metadata import (
    VaultMetadata,
)
from tests.helpers import Regex, remove_ansi


def test_vault_metadata__init_1() -> None:
    """Test VaultMetadata class."""
    vm = VaultMetadata()
    assert vm.dict == {}
    assert vm.frontmatter == {}
    assert vm.inline_metadata == {}
    assert vm.tags == []


def test_index_metadata_1():
    """Test index_metadata() method.

    GIVEN a dictionary to add
    WHEN the target area is FRONTMATTER and the old dictionary is empty
    THEN the new dictionary is added to the target area
    """
    vm = VaultMetadata()
    new_dict = {"key1": ["value1"], "key2": ["value2", "value3"]}
    vm.index_metadata(area=MetadataType.FRONTMATTER, metadata=new_dict)
    assert vm.dict == new_dict
    assert vm.frontmatter == new_dict


def test_index_metadata_2():
    """Test index_metadata() method.

    GIVEN a dictionary to add
    WHEN the target area is FRONTMATTER and the old dictionary is not empty
    THEN the new dictionary is merged with the old dictionary
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"], "other_key": ["value1"]}
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}

    new_dict = {"key1": ["value1"], "key2": ["value1", "value3"], "key3": ["value1"]}

    vm.index_metadata(area=MetadataType.FRONTMATTER, metadata=new_dict)
    assert vm.dict == {
        "key1": ["value1"],
        "key2": ["value1", "value2", "value3"],
        "key3": ["value1"],
        "other_key": ["value1"],
    }
    assert vm.frontmatter == {
        "key1": ["value1"],
        "key2": ["value1", "value2", "value3"],
        "key3": ["value1"],
    }


def test_index_metadata_3():
    """Test index_metadata() method.

    GIVEN a dictionary to add
    WHEN the target area is INLINE and the old dictionary is empty
    THEN the new dictionary is added to the target area
    """
    vm = VaultMetadata()
    new_dict = {"key1": ["value1"], "key2": ["value2", "value3"]}
    vm.index_metadata(area=MetadataType.INLINE, metadata=new_dict)
    assert vm.dict == new_dict
    assert vm.inline_metadata == new_dict


def test_index_metadata_4():
    """Test index_metadata() method.

    GIVEN a dictionary to add
    WHEN the target area is INLINE and the old dictionary is not empty
    THEN the new dictionary is merged with the old dictionary
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"], "other_key": ["value1"]}
    vm.inline_metadata = {"key1": ["value1"], "key2": ["value1", "value2"]}

    new_dict = {"key1": ["value1"], "key2": ["value1", "value3"], "key3": ["value1"]}

    vm.index_metadata(area=MetadataType.INLINE, metadata=new_dict)
    assert vm.dict == {
        "key1": ["value1"],
        "key2": ["value1", "value2", "value3"],
        "key3": ["value1"],
        "other_key": ["value1"],
    }
    assert vm.inline_metadata == {
        "key1": ["value1"],
        "key2": ["value1", "value2", "value3"],
        "key3": ["value1"],
    }


def test_index_metadata_5():
    """Test index_metadata() method.

    GIVEN a dictionary to add
    WHEN the target area is TAGS and the old list is empty
    THEN the new list is added to the target area
    """
    vm = VaultMetadata()
    new_list = ["tag1", "tag2", "tag3"]
    vm.index_metadata(area=MetadataType.TAGS, metadata=new_list)
    assert vm.dict == {}
    assert vm.tags == new_list


def test_index_metadata_6():
    """Test index_metadata() method.

    GIVEN a dictionary to add
    WHEN the target area is TAGS and the old list is not empty
    THEN the new list is merged with the old list
    """
    vm = VaultMetadata()
    vm.tags = ["tag1", "tag2", "tag3"]
    new_list = ["tag1", "tag2", "tag4", "tag5"]

    vm.index_metadata(area=MetadataType.TAGS, metadata=new_list)
    assert vm.dict == {}
    assert vm.tags == ["tag1", "tag2", "tag3", "tag4", "tag5"]


def test_contains_1():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN FRONTMATTER is checked for a key that exists
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.FRONTMATTER, key="key1") is True


def test_contains_2():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN FRONTMATTER is checked for a key that does not exist
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.FRONTMATTER, key="key3") is False


def test_contains_3():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN FRONTMATTER is checked for a key and value that exists
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.FRONTMATTER, key="key2", value="value1") is True


def test_contains_4():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN FRONTMATTER is checked for a key and value that does not exist
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.FRONTMATTER, key="key2", value="value3") is False


def test_contains_5():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN FRONTMATTER is checked for a key that exists with regex
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.FRONTMATTER, key=r"\w+\d", is_regex=True) is True


def test_contains_6():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN FRONTMATTER is checked for a key that does not exist with regex
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.FRONTMATTER, key=r"^\d", is_regex=True) is False


def test_contains_7():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN FRONTMATTER is checked for a key and value that exists with regex
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert (
        vm.contains(area=MetadataType.FRONTMATTER, key="key2", value=r"\w\d", is_regex=True) is True
    )


def test_contains_8():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN FRONTMATTER is checked for a key and value that does not exist with regex
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert (
        vm.contains(area=MetadataType.FRONTMATTER, key="key2", value=r"^\d", is_regex=True) is False
    )


def test_contains_9():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN FRONTMATTER is checked with a key is None
    THEN raise a ValueError
    """
    vm = VaultMetadata()
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    with pytest.raises(ValueError, match="Key must be provided"):
        vm.contains(area=MetadataType.FRONTMATTER, value="value1")


def test_contains_10():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN INLINE is checked for a key that exists
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.inline_metadata = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.INLINE, key="key1") is True


def test_contains_11():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN INLINE is checked for a key that does not exist
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.inline_metadata = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.INLINE, key="key3") is False


def test_contains_12():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN INLINE is checked for a key and value that exists
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.inline_metadata = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.INLINE, key="key2", value="value1") is True


def test_contains_13():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN INLINE is checked for a key and value that does not exist
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.inline_metadata = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.INLINE, key="key2", value="value3") is False


def test_contains_14():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN INLINE is checked for a key that exists with regex
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.inline_metadata = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.INLINE, key=r"\w+\d", is_regex=True) is True


def test_contains_15():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN INLINE is checked for a key that does not exist with regex
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.inline_metadata = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.INLINE, key=r"^\d", is_regex=True) is False


def test_contains_16():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN INLINE is checked for a key and value that exists with regex
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.inline_metadata = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.INLINE, key="key2", value=r"\w\d", is_regex=True) is True


def test_contains_17():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN INLINE is checked for a key and value that does not exist with regex
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.inline_metadata = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.INLINE, key="key2", value=r"^\d", is_regex=True) is False


def test_contains_18():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN INLINE is checked with a key is None
    THEN raise a ValueError
    """
    vm = VaultMetadata()
    vm.inline_metadata = {"key1": ["value1"], "key2": ["value1", "value2"]}
    with pytest.raises(ValueError, match="Key must be provided"):
        vm.contains(area=MetadataType.INLINE, value="value1")


def test_contains_19():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN TAGS is checked for a key but not a value
    THEN raise a ValueError
    """
    vm = VaultMetadata()
    vm.tags = ["tag1", "tag2", "tag3"]
    with pytest.raises(ValueError, match="Value must be provided"):
        vm.contains(area=MetadataType.TAGS, key="key1")


def test_contains_20():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN TAGS is checked for a value that exists
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.tags = ["tag1", "tag2", "tag3"]
    assert vm.contains(area=MetadataType.TAGS, value="tag1") is True


def test_contains_21():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN TAGS is checked for a value that does not exist
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.tags = ["tag1", "tag2", "tag3"]
    assert vm.contains(area=MetadataType.TAGS, value="value1") is False


def test_contains_22():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN TAGS is checked for a key regex but no value
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.tags = ["tag1", "tag2", "tag3"]
    with pytest.raises(ValueError, match="Value must be provided"):
        vm.contains(area=MetadataType.TAGS, key=r"\w", is_regex=True)


def test_contains_23():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN TAGS is checked for a value that does not exist with regex
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.tags = ["tag1", "tag2", "tag3"]
    assert vm.contains(area=MetadataType.TAGS, value=r"^\d", is_regex=True) is False


def test_contains_24():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN TAGS is checked for a value that exists with regex
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.tags = ["tag1", "tag2", "tag3"]
    assert vm.contains(area=MetadataType.TAGS, value=r"^tag\d", is_regex=True) is True


def test_contains_25():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN ALL is checked for a key that exists
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.ALL, key="key1") is True


def test_contains_26():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN ALL is checked for a key that does not exist
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.ALL, key="key3") is False


def test_contains_27():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN ALL is checked for a key and value that exists
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.ALL, key="key2", value="value1") is True


def test_contains_28():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN ALL is checked for a key and value that does not exist
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.ALL, key="key2", value="value3") is False


def test_contains_29():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN ALL is checked for a key that exists with regex
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.ALL, key=r"\w+\d", is_regex=True) is True


def test_contains_30():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN ALL is checked for a key that does not exist with regex
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.ALL, key=r"^\d", is_regex=True) is False


def test_contains_31():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN ALL is checked for a key and value that exists with regex
    THEN True is returned
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.ALL, key="key2", value=r"\w\d", is_regex=True) is True


def test_contains_32():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN ALL is checked for a key and value that does not exist with regex
    THEN False is returned
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.contains(area=MetadataType.ALL, key="key2", value=r"^\d", is_regex=True) is False


def test_contains_33():
    """Test contains() method.

    GIVEN a VaultMetadata object
    WHEN ALL is checked with a key is None
    THEN raise a ValueError
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    with pytest.raises(ValueError, match="Key must be provided"):
        vm.contains(area=MetadataType.ALL, value="value1")


def test_delete_1():
    """Test delete() method.

    GIVEN a VaultMetadata object
    WHEN a key is deleted
    THEN return True and the key is removed
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.delete(key="key1") is True
    assert vm.dict == {"key2": ["value1", "value2"]}


def test_delete_2():
    """Test delete() method.

    GIVEN a VaultMetadata object
    WHEN a key is deleted that does not exist
    THEN return False and the key is not removed
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.delete(key="key3") is False
    assert vm.dict == {"key1": ["value1"], "key2": ["value1", "value2"]}


def test_delete_3():
    """Test delete() method.

    GIVEN a VaultMetadata object
    WHEN a key and value are specified
    THEN return True and remove the value
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.delete(key="key2", value_to_delete="value1") is True
    assert vm.dict == {"key1": ["value1"], "key2": ["value2"]}


def test_delete_4():
    """Test delete() method.

    GIVEN a VaultMetadata object
    WHEN a key and nonexistent value are specified
    THEN return False
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.delete(key="key2", value_to_delete="value11") is False
    assert vm.dict == {"key1": ["value1"], "key2": ["value1", "value2"]}


def test_rename_1():
    """Test VaultMetadata rename() method.

    GIVEN a VaultMetadata object
    WHEN the rename() method is called with a key
    THEN return False if the key is not found
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.rename("no key", "new key") is False


def test_rename_2():
    """Test VaultMetadata rename() method.

    GIVEN a VaultMetadata object
    WHEN the rename() method is called with an existing key and non-existing value
    THEN return False
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.rename("key1", "no value", "new value") is False


def test_rename_3():
    """Test VaultMetadata rename() method.

    GIVEN a VaultMetadata object
    WHEN the rename() method is called with an existing key
    THEN return True and rename the key
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.rename("key1", "new key") is True
    assert vm.dict == {"key2": ["value1", "value2"], "new key": ["value1"]}


def test_rename_4():
    """Test VaultMetadata rename() method.

    GIVEN a VaultMetadata object
    WHEN the rename() method is called with an existing key and value
    THEN return True and rename the value
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.rename("key1", "value1", "new value") is True
    assert vm.dict == {"key1": ["new value"], "key2": ["value1", "value2"]}


def test_rename_5():
    """Test VaultMetadata rename() method.

    GIVEN a VaultMetadata object
    WHEN the rename() method is called with an existing key and value and the new value already exists
    THEN return True and remove the old value leaving one instance of the new value
    """
    vm = VaultMetadata()
    vm.dict = {"key1": ["value1"], "key2": ["value1", "value2"]}
    assert vm.rename("key2", "value1", "value2") is True
    assert vm.dict == {"key1": ["value1"], "key2": ["value2"]}


def test_print_metadata_1(capsys):
    """Test print_metadata() method.

    GIVEN calling print_metadata() with a VaultMetadata object
    WHEN ALL is specified
    THEN print all the metadata
    """
    vm = VaultMetadata()
    vm.dict = {
        "key1": ["value1", "value2"],
        "key2": ["value1", "value2"],
        "key3": ["value1"],
        "key4": ["value1", "value2"],
    }
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    vm.inline_metadata = {
        "key1": ["value1", "value2"],
        "key3": ["value1"],
        "key4": ["value1", "value2"],
    }
    vm.tags = ["tag1", "tag2", "tag3"]

    vm.print_metadata(area=MetadataType.ALL)
    captured = remove_ansi(capsys.readouterr().out)
    assert "All metadata" in captured
    assert captured == Regex("┃ Keys +┃ Values +┃")
    assert captured == Regex("│ key1 +│ value1 +│")
    assert captured == Regex("│ key2 +│ value1 +│")
    assert captured == Regex("│ key4 +│ value1 +│")
    assert "All inline tags" in captured
    assert captured == Regex("#tag1 +#tag2")


def test_print_metadata_2(capsys):
    """Test print_metadata() method.

    GIVEN calling print_metadata() with a VaultMetadata object
    WHEN FRONTMATTER is specified
    THEN print all the metadata
    """
    vm = VaultMetadata()
    vm.dict = {
        "key1": ["value1", "value2"],
        "key2": ["value1", "value2"],
        "key3": ["value1"],
        "key4": ["value1", "value2"],
    }
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    vm.inline_metadata = {
        "key1": ["value1", "value2"],
        "key3": ["value1"],
        "key4": ["value1", "value2"],
    }
    vm.tags = ["tag1", "tag2", "tag3"]

    vm.print_metadata(area=MetadataType.FRONTMATTER)
    captured = remove_ansi(capsys.readouterr().out)
    assert "All frontmatter" in captured
    assert captured == Regex("┃ Keys +┃ Values +┃")
    assert captured == Regex("│ key1 +│ value1 +│")
    assert captured == Regex("│ key2 +│ value1 +│")
    assert captured != Regex("│ key4 +│ value1 +│")
    assert "All inline tags" not in captured
    assert captured != Regex("#tag1 +#tag2")


def test_print_metadata_3(capsys):
    """Test print_metadata() method.

    GIVEN calling print_metadata() with a VaultMetadata object
    WHEN INLINE is specified
    THEN print all the metadata
    """
    vm = VaultMetadata()
    vm.dict = {
        "key1": ["value1", "value2"],
        "key2": ["value1", "value2"],
        "key3": ["value1"],
        "key4": ["value1", "value2"],
    }
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    vm.inline_metadata = {
        "key1": ["value1", "value2"],
        "key3": ["value1"],
        "key4": ["value1", "value2"],
    }
    vm.tags = ["tag1", "tag2", "tag3"]

    vm.print_metadata(area=MetadataType.INLINE)
    captured = remove_ansi(capsys.readouterr().out)
    assert "All inline" in captured
    assert captured == Regex("┃ Keys +┃ Values +┃")
    assert captured == Regex("│ key1 +│ value1 +│")
    assert captured != Regex("│ key2 +│ value1 +│")
    assert captured == Regex("│ key4 +│ value1 +│")
    assert "All inline tags" not in captured
    assert captured != Regex("#tag1 +#tag2")


def test_print_metadata_4(capsys):
    """Test print_metadata() method.

    GIVEN calling print_metadata() with a VaultMetadata object
    WHEN TAGS is specified
    THEN print all the tags
    """
    vm = VaultMetadata()
    vm.dict = {
        "key1": ["value1", "value2"],
        "key2": ["value1", "value2"],
        "key3": ["value1"],
        "key4": ["value1", "value2"],
    }
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    vm.inline_metadata = {
        "key1": ["value1", "value2"],
        "key3": ["value1"],
        "key4": ["value1", "value2"],
    }
    vm.tags = ["tag1", "tag2", "tag3"]

    vm.print_metadata(area=MetadataType.TAGS)
    captured = remove_ansi(capsys.readouterr().out)
    assert "All inline tags" in captured
    assert captured != Regex("┃ Keys +┃ Values +┃")
    assert captured != Regex("│ key1 +│ value1 +│")
    assert captured != Regex("│ key2 +│ value1 +│")
    assert captured != Regex("│ key4 +│ value1 +│")
    assert captured == Regex("#tag1 +#tag2 +#tag3")


def test_print_metadata_5(capsys):
    """Test print_metadata() method.

    GIVEN calling print_metadata() with a VaultMetadata object
    WHEN KEYS is specified
    THEN print all the tags
    """
    vm = VaultMetadata()
    vm.dict = {
        "key1": ["value1", "value2"],
        "key2": ["value1", "value2"],
        "key3": ["value1"],
        "key4": ["value1", "value2"],
    }
    vm.frontmatter = {"key1": ["value1"], "key2": ["value1", "value2"]}
    vm.inline_metadata = {
        "key1": ["value1", "value2"],
        "key3": ["value1"],
        "key4": ["value1", "value2"],
    }
    vm.tags = ["tag1", "tag2", "tag3"]

    vm.print_metadata(area=MetadataType.KEYS)
    captured = remove_ansi(capsys.readouterr().out)
    assert "All Keys" in captured
    assert captured != Regex("┃ Keys +┃ Values +┃")
    assert captured != Regex("│ key1 +│ value1 +│")
    assert captured != Regex("│ key2 +│ value1 +│")
    assert captured != Regex("│ key4 +│ value1 +│")
    assert captured != Regex("#tag1 +#tag2 +#tag3")
    assert captured == Regex("key1 +key2 +key3 +key4")
