# type: ignore
"""Test metadata.py."""
from pathlib import Path

import pytest

from obsidian_metadata.models.enums import MetadataType
from obsidian_metadata.models.metadata import (
    InlineTags,
    VaultMetadata,
)
from tests.helpers import Regex, remove_ansi

FILE_CONTENT: str = Path("tests/fixtures/test_vault/test1.md").read_text()
TAG_LIST: list[str] = ["tag 1", "tag 2", "tag 3"]
METADATA: dict[str, list[str]] = {
    "frontmatter_Key1": ["author name"],
    "frontmatter_Key2": ["note", "article"],
    "shared_key1": ["shared_key1_value"],
    "shared_key2": ["shared_key2_value"],
    "tags": ["tag 2", "tag 1", "tag 3"],
    "top_key1": ["top_key1_value"],
    "top_key2": ["top_key2_value"],
    "top_key3": ["top_key3_value"],
    "intext_key": ["intext_key_value"],
}
METADATA_2: dict[str, list[str]] = {"key1": ["value1"], "key2": ["value2", "value3"]}
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


def test_inline_tags_add() -> None:
    """Test inline tags add."""
    tags = InlineTags(INLINE_CONTENT)

    assert tags.add("bold_tag") is False
    assert tags.add("new_tag") is True
    assert tags.list == [
        "bold_tag",
        "in_text_tag",
        "inline_tag_top1",
        "inline_tag_top2",
        "new_tag",
        "tag_key_value",
    ]


def test_inline_tags_contains() -> None:
    """Test inline tags contains."""
    tags = InlineTags(INLINE_CONTENT)
    assert tags.contains("bold_tag") is True
    assert tags.contains("no tag") is False

    assert tags.contains(r"\w_\w", is_regex=True) is True
    assert tags.contains(r"\d_\d", is_regex=True) is False


def test_inline_tags_create() -> None:
    """Test inline tags creation."""
    tags = InlineTags(FRONTMATTER_CONTENT)
    tags.metadata_key
    assert tags.list == []

    tags = InlineTags(INLINE_CONTENT)
    assert tags.list == [
        "bold_tag",
        "in_text_tag",
        "inline_tag_top1",
        "inline_tag_top2",
        "tag_key_value",
    ]
    assert tags.list_original == [
        "bold_tag",
        "in_text_tag",
        "inline_tag_top1",
        "inline_tag_top2",
        "tag_key_value",
    ]


def test_inline_tags_delete() -> None:
    """Test inline tags delete."""
    tags = InlineTags(INLINE_CONTENT)
    assert tags.list == [
        "bold_tag",
        "in_text_tag",
        "inline_tag_top1",
        "inline_tag_top2",
        "tag_key_value",
    ]

    assert tags.delete("no tag") is False
    assert tags.has_changes() is False
    assert tags.delete("bold_tag") is True
    assert tags.list == [
        "in_text_tag",
        "inline_tag_top1",
        "inline_tag_top2",
        "tag_key_value",
    ]
    assert tags.has_changes() is True
    assert tags.delete(r"\d{3}") is False
    assert tags.delete(r"inline_tag_top\d") is True
    assert tags.list == ["in_text_tag", "tag_key_value"]


def test_inline_tags_rename() -> None:
    """Test inline tags rename."""
    tags = InlineTags(INLINE_CONTENT)
    assert tags.list == [
        "bold_tag",
        "in_text_tag",
        "inline_tag_top1",
        "inline_tag_top2",
        "tag_key_value",
    ]

    assert tags.rename("no tag", "new tag") is False
    assert tags.has_changes() is False
    assert tags.rename("bold_tag", "new tag") is True
    assert tags.list == [
        "in_text_tag",
        "inline_tag_top1",
        "inline_tag_top2",
        "new tag",
        "tag_key_value",
    ]
    assert tags.has_changes() is True


def test_vault_metadata() -> None:
    """Test VaultMetadata class."""
    vm = VaultMetadata()
    assert vm.dict == {}

    vm.index_metadata(area=MetadataType.FRONTMATTER, metadata=METADATA)
    vm.index_metadata(area=MetadataType.INLINE, metadata=METADATA_2)
    vm.index_metadata(area=MetadataType.TAGS, metadata=TAG_LIST)
    assert vm.dict == {
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_key_value"],
        "key1": ["value1"],
        "key2": ["value2", "value3"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value"],
        "tags": ["tag 1", "tag 2", "tag 3"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value"],
    }
    assert vm.frontmatter == {
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_key_value"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value"],
        "tags": ["tag 1", "tag 2", "tag 3"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value"],
    }
    assert vm.inline_metadata == {"key1": ["value1"], "key2": ["value2", "value3"]}
    assert vm.tags == ["tag 1", "tag 2", "tag 3"]

    new_metadata = {"added_key": ["added_value"], "frontmatter_Key2": ["new_value"]}
    new_tags = ["tag 4", "tag 5"]
    vm.index_metadata(area=MetadataType.FRONTMATTER, metadata=new_metadata)
    vm.index_metadata(area=MetadataType.TAGS, metadata=new_tags)
    assert vm.dict == {
        "added_key": ["added_value"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "new_value", "note"],
        "intext_key": ["intext_key_value"],
        "key1": ["value1"],
        "key2": ["value2", "value3"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value"],
        "tags": ["tag 1", "tag 2", "tag 3"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value"],
    }
    assert vm.frontmatter == {
        "added_key": ["added_value"],
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "new_value", "note"],
        "intext_key": ["intext_key_value"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value"],
        "tags": ["tag 1", "tag 2", "tag 3"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value"],
    }
    assert vm.inline_metadata == {"key1": ["value1"], "key2": ["value2", "value3"]}
    assert vm.tags == ["tag 1", "tag 2", "tag 3", "tag 4", "tag 5"]


def test_vault_metadata_print(capsys) -> None:
    """Test print_metadata method."""
    vm = VaultMetadata()
    vm.index_metadata(area=MetadataType.FRONTMATTER, metadata=METADATA)
    vm.index_metadata(area=MetadataType.INLINE, metadata=METADATA_2)
    vm.index_metadata(area=MetadataType.TAGS, metadata=TAG_LIST)

    vm.print_metadata(area=MetadataType.ALL)
    captured = remove_ansi(capsys.readouterr().out)
    assert "All metadata" in captured
    assert "All inline tags" in captured
    assert "┃ Keys             ┃ Values            ┃" in captured
    assert "│ shared_key1      │ shared_key1_value │" in captured
    assert captured == Regex("#tag 1 +#tag 2")

    vm.print_metadata(area=MetadataType.FRONTMATTER)
    captured = remove_ansi(capsys.readouterr().out)
    assert "All frontmatter" in captured
    assert "┃ Keys             ┃ Values            ┃" in captured
    assert "│ shared_key1      │ shared_key1_value │" in captured
    assert "value1" not in captured

    vm.print_metadata(area=MetadataType.INLINE)
    captured = remove_ansi(capsys.readouterr().out)
    assert "All inline" in captured
    assert "┃ Keys ┃ Values ┃" in captured
    assert "shared_key1" not in captured
    assert "│ key1 │ value1 │" in captured

    vm.print_metadata(area=MetadataType.TAGS)
    captured = remove_ansi(capsys.readouterr().out)
    assert "All inline tags " in captured
    assert "┃ Keys             ┃ Values            ┃" not in captured
    assert captured == Regex("#tag 1 +#tag 2")

    vm.print_metadata(area=MetadataType.KEYS)
    captured = remove_ansi(capsys.readouterr().out)
    assert "All Keys " in captured
    assert "┃ Keys             ┃ Values            ┃" not in captured
    assert captured != Regex("#tag 1 +#tag 2")
    assert captured == Regex("frontmatter_Key1 +frontmatter_Key2")


def test_vault_metadata_contains() -> None:
    """Test contains method."""
    vm = VaultMetadata()
    vm.index_metadata(area=MetadataType.FRONTMATTER, metadata=METADATA)
    vm.index_metadata(area=MetadataType.INLINE, metadata=METADATA_2)
    vm.index_metadata(area=MetadataType.TAGS, metadata=TAG_LIST)
    assert vm.dict == {
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_key_value"],
        "key1": ["value1"],
        "key2": ["value2", "value3"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value"],
        "tags": ["tag 1", "tag 2", "tag 3"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value"],
    }
    assert vm.frontmatter == {
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_key_value"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value"],
        "tags": ["tag 1", "tag 2", "tag 3"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value"],
    }
    assert vm.inline_metadata == {"key1": ["value1"], "key2": ["value2", "value3"]}
    assert vm.tags == ["tag 1", "tag 2", "tag 3"]

    with pytest.raises(ValueError):
        vm.contains(area=MetadataType.ALL, value="key1")

    assert vm.contains(area=MetadataType.ALL, key="no_key") is False
    assert vm.contains(area=MetadataType.ALL, key="key1") is True
    assert vm.contains(area=MetadataType.ALL, key="frontmatter_Key2", value="article") is True
    assert vm.contains(area=MetadataType.ALL, key="frontmatter_Key2", value="none") is False
    assert vm.contains(area=MetadataType.ALL, key="1$", is_regex=True) is True
    assert vm.contains(area=MetadataType.ALL, key=r"\d\d", is_regex=True) is False

    assert vm.contains(area=MetadataType.FRONTMATTER, key="no_key") is False
    assert vm.contains(area=MetadataType.FRONTMATTER, key="frontmatter_Key1") is True
    assert (
        vm.contains(area=MetadataType.FRONTMATTER, key="frontmatter_Key2", value="article") is True
    )
    assert vm.contains(area=MetadataType.FRONTMATTER, key="frontmatter_Key2", value="none") is False
    assert vm.contains(area=MetadataType.FRONTMATTER, key="1$", is_regex=True) is True
    assert vm.contains(area=MetadataType.FRONTMATTER, key=r"\d\d", is_regex=True) is False

    assert vm.contains(area=MetadataType.INLINE, key="no_key") is False
    assert vm.contains(area=MetadataType.INLINE, key="key1") is True
    assert vm.contains(area=MetadataType.INLINE, key="key2", value="value3") is True
    assert vm.contains(area=MetadataType.INLINE, key="key2", value="none") is False
    assert vm.contains(area=MetadataType.INLINE, key="1$", is_regex=True) is True
    assert vm.contains(area=MetadataType.INLINE, key=r"\d\d", is_regex=True) is False

    assert vm.contains(area=MetadataType.TAGS, value="no_tag") is False
    assert vm.contains(area=MetadataType.TAGS, value="tag 1") is True
    assert vm.contains(area=MetadataType.TAGS, value=r"\w+ \d$", is_regex=True) is True
    assert vm.contains(area=MetadataType.TAGS, value=r"\w+ \d\d$", is_regex=True) is False
    with pytest.raises(ValueError):
        vm.contains(area=MetadataType.TAGS, key="key1")


def test_vault_metadata_delete() -> None:
    """Test delete method."""
    vm = VaultMetadata()
    vm.index_metadata(area=MetadataType.FRONTMATTER, metadata=METADATA)
    assert vm.dict == {
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_key_value"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value"],
        "tags": ["tag 1", "tag 2", "tag 3"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value"],
    }

    assert vm.delete("no key") is False
    assert vm.delete("tags", "no value") is False
    assert vm.delete("tags", "tag 2") is True
    assert vm.dict["tags"] == ["tag 1", "tag 3"]
    assert vm.delete("tags") is True
    assert "tags" not in vm.dict


def test_vault_metadata_rename() -> None:
    """Test rename method."""
    vm = VaultMetadata()
    vm.index_metadata(area=MetadataType.FRONTMATTER, metadata=METADATA)
    assert vm.dict == {
        "frontmatter_Key1": ["author name"],
        "frontmatter_Key2": ["article", "note"],
        "intext_key": ["intext_key_value"],
        "shared_key1": ["shared_key1_value"],
        "shared_key2": ["shared_key2_value"],
        "tags": ["tag 1", "tag 2", "tag 3"],
        "top_key1": ["top_key1_value"],
        "top_key2": ["top_key2_value"],
        "top_key3": ["top_key3_value"],
    }

    assert vm.rename("no key", "new key") is False
    assert vm.rename("tags", "no tag", "new key") is False
    assert vm.rename("tags", "tag 2", "new tag") is True
    assert vm.dict["tags"] == ["new tag", "tag 1", "tag 3"]
    assert vm.rename("tags", "old_tags") is True
    assert vm.dict["old_tags"] == ["new tag", "tag 1", "tag 3"]
    assert "tags" not in vm.dict
