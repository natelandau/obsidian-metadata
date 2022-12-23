# type: ignore
"""Test the utilities module."""


from obsidian_metadata._utils import (
    clean_dictionary,
    dict_contains,
    dict_values_to_lists_strings,
    remove_markdown_sections,
    vault_validation,
)


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


def test_vault_validation():
    """Test vault validation."""
    assert vault_validation("tests/") is True
    assert "Path is not a directory" in vault_validation("pyproject.toml")
    assert "Path does not exist" in vault_validation("tests/vault2")


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
