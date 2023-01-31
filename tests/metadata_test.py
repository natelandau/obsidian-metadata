# type: ignore
"""Test metadata.py."""
from pathlib import Path

from obsidian_metadata.models.metadata import (
    Frontmatter,
    InlineMetadata,
    InlineTags,
    VaultMetadata,
)
from tests.helpers import Regex

FILE_CONTENT: str = Path("tests/fixtures/test_vault/test1.md").read_text()
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


def test_vault_metadata(capsys) -> None:
    """Test VaultMetadata class."""
    vm = VaultMetadata()
    assert vm.dict == {}

    vm.index_metadata(METADATA)
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

    vm.print_keys()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"frontmatter_Key1 +frontmatter_Key2 +intext_key")

    vm.print_tags()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"tag 1 +tag 2 +tag 3")

    vm.print_metadata()
    captured = capsys.readouterr()
    assert captured.out == Regex(r"┃ Keys +┃ Values +┃")
    assert captured.out == Regex(r"│ +│ tag 3 +│")
    assert captured.out == Regex(r"│ frontmatter_Key1 +│ author name +│")

    new_metadata = {"added_key": ["added_value"], "frontmatter_Key2": ["new_value"]}
    vm.index_metadata(new_metadata)
    assert vm.dict == {
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


def test_vault_metadata_contains() -> None:
    """Test contains method."""
    vm = VaultMetadata()
    vm.index_metadata(METADATA)
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

    assert vm.contains("frontmatter_Key1") is True
    assert vm.contains("frontmatter_Key2", "article") is True
    assert vm.contains("frontmatter_Key3") is False
    assert vm.contains("frontmatter_Key2", "no value") is False
    assert vm.contains("1$", is_regex=True) is True
    assert vm.contains("5$", is_regex=True) is False
    assert vm.contains("tags", r"\d", is_regex=True) is True
    assert vm.contains("tags", r"^\d", is_regex=True) is False


def test_vault_metadata_delete() -> None:
    """Test delete method."""
    vm = VaultMetadata()
    vm.index_metadata(METADATA)
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
    vm.index_metadata(METADATA)
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


def test_frontmatter_create() -> None:
    """Test frontmatter creation."""
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


def test_frontmatter_contains() -> None:
    """Test frontmatter contains."""
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)

    assert frontmatter.contains("frontmatter_Key1") is True
    assert frontmatter.contains("frontmatter_Key2", "article") is True
    assert frontmatter.contains("frontmatter_Key3") is False
    assert frontmatter.contains("frontmatter_Key2", "no value") is False

    assert frontmatter.contains(r"\d$", is_regex=True) is True
    assert frontmatter.contains(r"^\d", is_regex=True) is False
    assert frontmatter.contains("key", r"_\d", is_regex=True) is False
    assert frontmatter.contains("key", r"\w\d_", is_regex=True) is True


def test_frontmatter_add() -> None:
    """Test frontmatter add."""
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)

    assert frontmatter.add("frontmatter_Key1") is False
    assert frontmatter.add("added_key") is True
    assert frontmatter.dict == {
        "added_key": [],
        "frontmatter_Key1": ["frontmatter_Key1_value"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "tags": ["tag_1", "tag_2", "📅/tag_3"],
    }

    assert frontmatter.add("added_key", "added_value") is True
    assert frontmatter.dict == {
        "added_key": ["added_value"],
        "frontmatter_Key1": ["frontmatter_Key1_value"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "tags": ["tag_1", "tag_2", "📅/tag_3"],
    }

    assert frontmatter.add("added_key", "added_value_2") is True
    assert frontmatter.dict == {
        "added_key": ["added_value", "added_value_2"],
        "frontmatter_Key1": ["frontmatter_Key1_value"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "tags": ["tag_1", "tag_2", "📅/tag_3"],
    }

    assert frontmatter.add("added_key", ["added_value_3", "added_value_4"]) is True
    assert frontmatter.dict == {
        "added_key": ["added_value", "added_value_2", "added_value_3", "added_value_4"],
        "frontmatter_Key1": ["frontmatter_Key1_value"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "tags": ["tag_1", "tag_2", "📅/tag_3"],
    }

    assert frontmatter.add("added_key2", ["added_value_1", "added_value_2"]) is True
    assert frontmatter.dict == {
        "added_key": ["added_value", "added_value_2", "added_value_3", "added_value_4"],
        "added_key2": ["added_value_1", "added_value_2"],
        "frontmatter_Key1": ["frontmatter_Key1_value"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "tags": ["tag_1", "tag_2", "📅/tag_3"],
    }

    assert frontmatter.add("added_key3", "added_value_1") is True
    assert frontmatter.dict == {
        "added_key": ["added_value", "added_value_2", "added_value_3", "added_value_4"],
        "added_key2": ["added_value_1", "added_value_2"],
        "added_key3": ["added_value_1"],
        "frontmatter_Key1": ["frontmatter_Key1_value"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "tags": ["tag_1", "tag_2", "📅/tag_3"],
    }

    assert frontmatter.add("added_key3", "added_value_1") is False


def test_frontmatter_rename() -> None:
    """Test frontmatter rename."""
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.dict == {
        "frontmatter_Key1": ["frontmatter_Key1_value"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "tags": ["tag_1", "tag_2", "📅/tag_3"],
    }

    assert frontmatter.rename("no key", "new key") is False
    assert frontmatter.rename("tags", "no tag", "new key") is False

    assert frontmatter.has_changes() is False
    assert frontmatter.rename("tags", "tag_2", "new tag") is True

    assert frontmatter.dict["tags"] == ["new tag", "tag_1", "📅/tag_3"]
    assert frontmatter.rename("tags", "old_tags") is True
    assert frontmatter.dict["old_tags"] == ["new tag", "tag_1", "📅/tag_3"]
    assert "tags" not in frontmatter.dict

    assert frontmatter.has_changes() is True


def test_frontmatter_delete() -> None:
    """Test Frontmatter delete method."""
    frontmatter = Frontmatter(FRONTMATTER_CONTENT)
    assert frontmatter.dict == {
        "frontmatter_Key1": ["frontmatter_Key1_value"],
        "frontmatter_Key2": ["article", "note"],
        "shared_key1": ["shared_key1_value"],
        "tags": ["tag_1", "tag_2", "📅/tag_3"],
    }

    assert frontmatter.delete("no key") is False
    assert frontmatter.delete("tags", "no value") is False
    assert frontmatter.delete(r"\d{3}") is False
    assert frontmatter.has_changes() is False
    assert frontmatter.delete("tags", "tag_2") is True
    assert frontmatter.dict["tags"] == ["tag_1", "📅/tag_3"]
    assert frontmatter.delete("tags") is True
    assert "tags" not in frontmatter.dict
    assert frontmatter.has_changes() is True
    assert frontmatter.delete("shared_key1", r"\w+") is True
    assert frontmatter.dict["shared_key1"] == []
    assert frontmatter.delete(r"\w.tter") is True
    assert frontmatter.dict == {"shared_key1": []}


def test_frontmatter_yaml_conversion():
    """Test Frontmatter to_yaml method."""
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
    assert frontmatter.to_yaml() == new_frontmatter
    assert frontmatter.to_yaml(sort_keys=True) == new_frontmatter_sorted


def test_inline_metadata_create() -> None:
    """Test inline metadata creation."""
    inline = InlineMetadata(FRONTMATTER_CONTENT)
    assert inline.dict == {}
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.dict == {
        "bold_key1": ["bold_key1_value"],
        "bold_key2": ["bold_key2_value"],
        "emoji_📅_key": ["emoji_📅_key_value"],
        "in_text_key1": ["in_text_key1_value"],
        "in_text_key2": ["in_text_key2_value"],
        "link_key": ["link_key_value"],
        "repeated_key": ["repeated_key_value1", "repeated_key_value2"],
        "tag_key": ["tag_key_value"],
    }
    assert inline.dict_original == {
        "bold_key1": ["bold_key1_value"],
        "bold_key2": ["bold_key2_value"],
        "emoji_📅_key": ["emoji_📅_key_value"],
        "in_text_key1": ["in_text_key1_value"],
        "in_text_key2": ["in_text_key2_value"],
        "link_key": ["link_key_value"],
        "repeated_key": ["repeated_key_value1", "repeated_key_value2"],
        "tag_key": ["tag_key_value"],
    }


def test_inline_contains() -> None:
    """Test inline metadata contains method."""
    inline = InlineMetadata(INLINE_CONTENT)

    assert inline.contains("bold_key1") is True
    assert inline.contains("bold_key2", "bold_key2_value") is True
    assert inline.contains("bold_key3") is False
    assert inline.contains("bold_key2", "no value") is False

    assert inline.contains(r"\w{4}_key", is_regex=True) is True
    assert inline.contains(r"^\d", is_regex=True) is False
    assert inline.contains("1$", r"\d_value", is_regex=True) is True
    assert inline.contains("key", r"^\d_value", is_regex=True) is False


def test_inline_metadata_rename() -> None:
    """Test inline metadata rename."""
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.dict == {
        "bold_key1": ["bold_key1_value"],
        "bold_key2": ["bold_key2_value"],
        "emoji_📅_key": ["emoji_📅_key_value"],
        "in_text_key1": ["in_text_key1_value"],
        "in_text_key2": ["in_text_key2_value"],
        "link_key": ["link_key_value"],
        "repeated_key": ["repeated_key_value1", "repeated_key_value2"],
        "tag_key": ["tag_key_value"],
    }

    assert inline.rename("no key", "new key") is False
    assert inline.rename("repeated_key", "no value", "new key") is False
    assert inline.has_changes() is False
    assert inline.rename("repeated_key", "repeated_key_value1", "new value") is True
    assert inline.dict["repeated_key"] == ["new value", "repeated_key_value2"]
    assert inline.rename("repeated_key", "old_key") is True
    assert inline.dict["old_key"] == ["new value", "repeated_key_value2"]
    assert "repeated_key" not in inline.dict
    assert inline.has_changes() is True


def test_inline_metadata_delete() -> None:
    """Test inline metadata delete."""
    inline = InlineMetadata(INLINE_CONTENT)
    assert inline.dict == {
        "bold_key1": ["bold_key1_value"],
        "bold_key2": ["bold_key2_value"],
        "emoji_📅_key": ["emoji_📅_key_value"],
        "in_text_key1": ["in_text_key1_value"],
        "in_text_key2": ["in_text_key2_value"],
        "link_key": ["link_key_value"],
        "repeated_key": ["repeated_key_value1", "repeated_key_value2"],
        "tag_key": ["tag_key_value"],
    }

    assert inline.delete("no key") is False
    assert inline.delete("repeated_key", "no value") is False
    assert inline.has_changes() is False
    assert inline.delete("repeated_key", "repeated_key_value1") is True
    assert inline.dict["repeated_key"] == ["repeated_key_value2"]
    assert inline.delete("repeated_key") is True
    assert "repeated_key" not in inline.dict
    assert inline.has_changes() is True
    assert inline.delete(r"\d{3}") is False
    assert inline.delete(r"bold_key\d") is True
    assert inline.dict == {
        "emoji_📅_key": ["emoji_📅_key_value"],
        "in_text_key1": ["in_text_key1_value"],
        "in_text_key2": ["in_text_key2_value"],
        "link_key": ["link_key_value"],
        "tag_key": ["tag_key_value"],
    }
    assert inline.delete("emoji_📅_key", ".*📅.*") is True
    assert inline.dict == {
        "emoji_📅_key": [],
        "in_text_key1": ["in_text_key1_value"],
        "in_text_key2": ["in_text_key2_value"],
        "link_key": ["link_key_value"],
        "tag_key": ["tag_key_value"],
    }


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


def test_inline_tags_contains() -> None:
    """Test inline tags contains."""
    tags = InlineTags(INLINE_CONTENT)
    assert tags.contains("bold_tag") is True
    assert tags.contains("no tag") is False

    assert tags.contains(r"\w_\w", is_regex=True) is True
    assert tags.contains(r"\d_\d", is_regex=True) is False


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
