# type: ignore
"""Tests for the regex module."""

import pytest

from obsidian_metadata.models.patterns import Patterns

TAG_CONTENT: str = "#1 #2 **#3** [[#4]] [[#5|test]] #6#notag #7_8 #9/10 #11-12 #13; #14, #15. #16: #17* #18(#19) #20[#21] #22\\ #23& #24# #25 **#26** #📅/tag"
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


def test_regex():
    """Test regexes."""
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

    found = pattern.frontmatt_block_with_separators.search(FRONTMATTER_CONTENT).group("frontmatter")
    assert found == CORRECT_FRONTMATTER_WITH_SEPARATORS

    found = pattern.frontmatt_block_no_separators.search(FRONTMATTER_CONTENT).group("frontmatter")
    assert found == CORRECT_FRONTMATTER_NO_SEPARATORS

    with pytest.raises(AttributeError):
        pattern.frontmatt_block_no_separators.search(TAG_CONTENT).group("frontmatter")

    assert pattern.validate_tag_text.search("test_tag") is None
    assert pattern.validate_tag_text.search("#asdf").group(0) == "#"
