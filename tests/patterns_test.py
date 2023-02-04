# type: ignore
"""Tests for the regex module."""

import pytest

from obsidian_metadata.models.patterns import Patterns

TAG_CONTENT: str = "#1 #2 **#3** [[#4]] [[#5|test]] #6#notag #7_8 #9/10 #11-12 #13; #14, #15. #16: #17* #18(#19) #20[#21] #22\\ #23& #24# #25 **#26** #📅/tag [link](#no_tag) https://example.com/somepage.html_#no_url_tags"
INLINE_METADATA: str = """
**1:: 1**
2_2:: [[2_2]] | 2
asdfasdf [3:: 3] asdfasdf [7::7] asdf
[4:: 4] [5:: 5]
> 6:: 6
**8**:: **8**
10::
📅11:: 11/📅/11
emoji_📅_key:: 📅emoji_📅_key_value
    """
FRONTMATTER_CONTENT: str = """
---
tags:
  - tag_1
  - tag_2
  -
  - 📅/tag_3
frontmatter_Key1: "frontmatter_Key1_value"
frontmatter_Key2: ["note", "article"]
shared_key1: 'shared_key1_value'
---
more content

---
horizontal: rule
---
"""
CORRECT_FRONTMATTER_WITH_SEPARATORS: str = """---
tags:
  - tag_1
  - tag_2
  -
  - 📅/tag_3
frontmatter_Key1: "frontmatter_Key1_value"
frontmatter_Key2: ["note", "article"]
shared_key1: 'shared_key1_value'
---"""
CORRECT_FRONTMATTER_NO_SEPARATORS: str = """
tags:
  - tag_1
  - tag_2
  -
  - 📅/tag_3
frontmatter_Key1: "frontmatter_Key1_value"
frontmatter_Key2: ["note", "article"]
shared_key1: 'shared_key1_value'
"""


def test_top_of_note():
    """Test identifying the top of a note."""
    pattern = Patterns()

    no_fm_or_header = """


Lorem ipsum dolor sit amet.

# header 1
---
horizontal: rule
---
Lorem ipsum dolor sit amet.
"""
    fm_and_header: str = """
---
tags:
  - tag_1
  - tag_2
  -
  - 📅/tag_3
frontmatter_Key1: "frontmatter_Key1_value"
frontmatter_Key2: ["note", "article"]
shared_key1: 'shared_key1_value'
---

# Header 1
more content

---
horizontal: rule
---
"""
    fm_and_header_result = """---
tags:
  - tag_1
  - tag_2
  -
  - 📅/tag_3
frontmatter_Key1: "frontmatter_Key1_value"
frontmatter_Key2: ["note", "article"]
shared_key1: 'shared_key1_value'
---

# Header 1"""
    no_fm = """

    ### Header's number 3 [📅] "+$2.00" 🤷
    ---
    horizontal: rule
    ---
    """
    no_fm_result = '### Header\'s number 3 [📅] "+$2.00" 🤷'

    assert pattern.top_of_note.search(no_fm_or_header).group("top") == ""
    assert pattern.top_of_note.search(fm_and_header).group("top") == fm_and_header_result
    assert pattern.top_of_note.search(no_fm).group("top") == no_fm_result


def test_find_inline_tags():
    """Test find_inline_tags regex."""
    pattern = Patterns()
    assert pattern.find_inline_tags.findall(TAG_CONTENT) == [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7_8",
        "9/10",
        "11-12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "📅/tag",
    ]


def test_find_inline_metadata():
    """Test find_inline_metadata regex."""
    pattern = Patterns()

    result = pattern.find_inline_metadata.findall(INLINE_METADATA)
    assert result == [
        ("", "", "1", "1**"),
        ("", "", "2_2", "[[2_2]] | 2"),
        ("3", "3", "", ""),
        ("7", "7", "", ""),
        ("", "", "4", "4] [5:: 5]"),
        ("", "", "8**", "**8**"),
        ("", "", "11", "11/📅/11"),
        ("", "", "emoji_📅_key", "📅emoji_📅_key_value"),
    ]


def test_find_frontmatter():
    """Test regexes."""
    pattern = Patterns()
    found = pattern.frontmatter_block.search(FRONTMATTER_CONTENT).group("frontmatter")
    assert found == CORRECT_FRONTMATTER_WITH_SEPARATORS

    found = pattern.frontmatt_block_strip_separators.search(FRONTMATTER_CONTENT).group(
        "frontmatter"
    )
    assert found == CORRECT_FRONTMATTER_NO_SEPARATORS

    with pytest.raises(AttributeError):
        pattern.frontmatt_block_strip_separators.search(TAG_CONTENT).group("frontmatter")


def test_validators():
    """Test validators."""
    pattern = Patterns()

    assert pattern.validate_tag_text.search("test_tag") is None
    assert pattern.validate_tag_text.search("#asdf").group(0) == "#"
    assert pattern.validate_tag_text.search("#asdf").group(0) == "#"
