# type: ignore
"""Test inline tags from metadata.py."""

from obsidian_metadata.models.metadata import InlineTags

CONTENT = """\
#tag1 #tag2
> #tag3
**#tag4**
I am a sentence with #tag5 and #tag6 in the middle
#tag🙈7
#tag/8
#tag/👋/9
"""


def test__grab_inline_tags_1() -> None:
    """Test _grab_inline_tags() method.

    GIVEN a string with a codeblock
    WHEN the method is called
    THEN the codeblock is ignored
    """
    content = """
some text

```python
#tag1
#tag2
```

```
#tag3
#tag4
```
    """
    tags = InlineTags(content)
    assert tags.list == []
    assert tags.list_original == []


def test__grab_inline_tags_2() -> None:
    """Test _grab_inline_tags() method.

    GIVEN a string with tags
    WHEN the method is called
    THEN the tags are extracted
    """
    tags = InlineTags(CONTENT)
    assert tags.list == [
        "tag/8",
        "tag/👋/9",
        "tag1",
        "tag2",
        "tag3",
        "tag4",
        "tag5",
        "tag6",
        "tag🙈7",
    ]
    assert tags.list_original == [
        "tag/8",
        "tag/👋/9",
        "tag1",
        "tag2",
        "tag3",
        "tag4",
        "tag5",
        "tag6",
        "tag🙈7",
    ]


def test_add_1():
    """Test add() method.

    GIVEN a InlineTag object
    WHEN the add() method is called with a tag that exists in the list
    THEN return False
    """
    tags = InlineTags(CONTENT)
    assert tags.add("tag1") is False


def test_add_2():
    """Test add() method.

    GIVEN a InlineTag object
    WHEN the add() method is called with a new tag
    THEN return True and add the tag to the list
    """
    tags = InlineTags(CONTENT)
    assert tags.add("new_tag") is True
    assert "new_tag" in tags.list


def test_add_3():
    """Test add() method.

    GIVEN a InlineTag object
    WHEN the add() method is called with a list of new tags
    THEN return True and add the tags to the list
    """
    tags = InlineTags(CONTENT)
    new_tags = ["new_tag1", "new_tag2"]
    assert tags.add(new_tags) is True
    assert "new_tag1" in tags.list
    assert "new_tag2" in tags.list


def test_add_4():
    """Test add() method.

    GIVEN a InlineTag object
    WHEN the add() method is called with a list of tags, some of which already exist
    THEN return True and add only the new tags to the list
    """
    tags = InlineTags(CONTENT)
    new_tags = ["new_tag1", "new_tag2", "tag1", "tag2"]
    assert tags.add(new_tags) is True
    assert tags.list == [
        "new_tag1",
        "new_tag2",
        "tag/8",
        "tag/👋/9",
        "tag1",
        "tag2",
        "tag3",
        "tag4",
        "tag5",
        "tag6",
        "tag🙈7",
    ]


def test_add_5():
    """Test add() method.

    GIVEN a InlineTag object
    WHEN the add() method is called with a list of tags which are already in the list
    THEN return False
    """
    tags = InlineTags(CONTENT)
    new_tags = ["tag1", "tag2"]
    assert tags.add(new_tags) is False
    assert "tag1" in tags.list
    assert "tag2" in tags.list


def test_add_6():
    """Test add() method.

    GIVEN a InlineTag object
    WHEN the add() method is called with a list of tags which have a # in the name
    THEN strip the # from the tag name
    """
    tags = InlineTags(CONTENT)
    new_tags = ["#tag1", "#tag2", "#new_tag"]
    assert tags.add(new_tags) is True
    assert tags.list == [
        "new_tag",
        "tag/8",
        "tag/👋/9",
        "tag1",
        "tag2",
        "tag3",
        "tag4",
        "tag5",
        "tag6",
        "tag🙈7",
    ]


def test_add_7():
    """Test add() method.

    GIVEN a InlineTag object
    WHEN the add() method is called with a tag which has a # in the name
    THEN strip the # from the tag name
    """
    tags = InlineTags(CONTENT)
    assert tags.add("#tag1") is False
    assert tags.add("#new_tag") is True
    assert "new_tag" in tags.list


def test_contains_1():
    """Test contains() method.

    GIVEN a InlineTag object
    WHEN the contains() method is called with a tag that exists in the list
    THEN return True
    """
    tags = InlineTags(CONTENT)
    assert tags.contains("tag1") is True


def test_contains_2():
    """Test contains() method.

    GIVEN a InlineTag object
    WHEN the contains() method is called with a tag that does not exist in the list
    THEN return False
    """
    tags = InlineTags(CONTENT)
    assert tags.contains("no_tag") is False


def test_contains_3():
    """Test contains() method.

    GIVEN a InlineTag object
    WHEN the contains() method is called with a regex that matches a tag in the list
    THEN return True
    """
    tags = InlineTags(CONTENT)
    assert tags.contains(r"tag\d", is_regex=True) is True


def test_contains_4():
    """Test contains() method.

    GIVEN a InlineTag object
    WHEN the contains() method is called with a regex that does not match any tags in the list
    THEN return False
    """
    tags = InlineTags(CONTENT)
    assert tags.contains(r"tag\d\d", is_regex=True) is False


def test_delete_1():
    """Test delete() method.

    GIVEN a InlineTag object
    WHEN the delete() method is called with a tag that exists in the list
    THEN return True and remove the tag from the list
    """
    tags = InlineTags(CONTENT)
    assert tags.delete("tag1") is True
    assert "tag1" not in tags.list


def test_delete_2():
    """Test delete() method.

    GIVEN a InlineTag object
    WHEN the delete() method is called with a tag that does not exist in the list
    THEN return False
    """
    tags = InlineTags(CONTENT)
    assert tags.delete("no_tag") is False


def test_delete_3():
    """Test delete() method.

    GIVEN a InlineTag object
    WHEN the delete() method is called with a regex that matches a tag in the list
    THEN return True and remove the tag from the list
    """
    tags = InlineTags(CONTENT)
    assert tags.delete(r"tag\d") is True
    assert tags.list == ["tag/8", "tag/👋/9", "tag🙈7"]


def test_delete_4():
    """Test delete() method.

    GIVEN a InlineTag object
    WHEN the delete() method is called with a regex that does not match any tags in the list
    THEN return False
    """
    tags = InlineTags(CONTENT)
    assert tags.delete(r"tag\d\d") is False


def test_has_changes_1():
    """Test has_changes() method.

    GIVEN a InlineTag object
    WHEN the has_changes() method is called
    THEN return False
    """
    tags = InlineTags(CONTENT)
    assert tags.has_changes() is False


def test_has_changes_2():
    """Test has_changes() method.

    GIVEN a InlineTag object
    WHEN the has_changes() method after the list has been updated
    THEN return True
    """
    tags = InlineTags(CONTENT)
    tags.list = ["new_tag"]
    assert tags.has_changes() is True


def test_rename_1():
    """Test rename() method.

    GIVEN a InlineTag object
    WHEN the rename() method is called with a tag that exists in the list
    THEN return True and rename the tag in the list
    """
    tags = InlineTags(CONTENT)
    assert tags.rename("tag1", "new_tag") is True
    assert "tag1" not in tags.list
    assert "new_tag" in tags.list


def test_rename_2():
    """Test rename() method.

    GIVEN a InlineTag object
    WHEN the rename() method is called with a tag that does not exist in the list
    THEN return False
    """
    tags = InlineTags(CONTENT)
    assert tags.rename("no_tag", "new_tag") is False
    assert "new_tag" not in tags.list


def test_rename_3():
    """Test rename() method.

    GIVEN a InlineTag object
    WHEN the rename() method is called with a tag that exists and the new tag name already exists in the list
    THEN return True and ensure the new tag name is only in the list once
    """
    tags = InlineTags(CONTENT)
    assert tags.rename(r"tag1", "tag2") is True
    assert tags.list == [
        "tag/8",
        "tag/👋/9",
        "tag2",
        "tag3",
        "tag4",
        "tag5",
        "tag6",
        "tag🙈7",
    ]


def test_rename_4():
    """Test rename() method.

    GIVEN a InlineTag object
    WHEN the rename() method is called with a new tag value that is None
    THEN return False
    """
    tags = InlineTags(CONTENT)
    assert tags.rename("tag1", None) is False
    assert "tag1" in tags.list


def test_rename_5():
    """Test rename() method.

    GIVEN a InlineTag object
    WHEN the rename() method is called with a new tag value that is empty
    THEN return False
    """
    tags = InlineTags(CONTENT)
    assert tags.rename("tag1", "") is False
    assert "tag1" in tags.list
