# type: ignore
"""Test the InlineField class."""

import pytest

from obsidian_metadata.models.enums import MetadataType, Wrapping
from obsidian_metadata.models.metadata import InlineField, dict_to_yaml


def test_dict_to_yaml_1():
    """Test dict_to_yaml() function.

    GIVEN a dictionary
    WHEN values contain lists
    THEN confirm the output is not sorted
    """
    test_dict = {"k2": ["v1", "v2"], "k1": ["v1", "v2"]}
    assert dict_to_yaml(test_dict) == "k2:\n  - v1\n  - v2\nk1:\n  - v1\n  - v2\n"


def test_dict_to_yaml_2():
    """Test dict_to_yaml() function.

    GIVEN a dictionary
    WHEN values contain lists and sort_keys is True
    THEN confirm the output is sorted
    """
    test_dict = {"k2": ["v1", "v2"], "k1": ["v1", "v2"]}
    assert dict_to_yaml(test_dict, sort_keys=True) == "k1:\n  - v1\n  - v2\nk2:\n  - v1\n  - v2\n"


def test_dict_to_yaml_3():
    """Test dict_to_yaml() function.

    GIVEN a dictionary
    WHEN values contain a list with a single value
    THEN confirm single-value lists are converted to strings
    """
    test_dict = {"k2": ["v1"], "k1": ["v1", "v2"]}
    assert dict_to_yaml(test_dict, sort_keys=True) == "k1:\n  - v1\n  - v2\nk2: v1\n"


def test_init_1():
    """Test creating an InlineField object.

    GIVEN an inline tag
    WHEN an InlineField object is created
    THEN confirm the object's attributes match the expected values
    """
    obj = InlineField(
        meta_type=MetadataType.TAGS,
        key=None,
        value="tag1",
    )
    assert obj.meta_type == MetadataType.TAGS
    assert obj.key is None
    assert obj.value == "tag1"
    assert obj.normalized_value == "tag1"
    assert obj.wrapping == Wrapping.NONE
    assert obj.clean_key is None
    assert obj.normalized_key is None
    assert not obj.key_open
    assert not obj.key_close
    assert obj.is_changed is False


def test_init_2():
    """Test creating an InlineField object.

    GIVEN an inline key/value pair
    WHEN an InlineField object is created
    THEN confirm the object's attributes match the expected values
    """
    obj = InlineField(meta_type=MetadataType.INLINE, key="key", value="value")
    assert obj.meta_type == MetadataType.INLINE
    assert obj.key == "key"
    assert obj.value == "value"
    assert obj.normalized_value == "value"
    assert obj.wrapping == Wrapping.NONE
    assert obj.clean_key == "key"
    assert obj.normalized_key == "key"
    assert not obj.key_open
    assert not obj.key_close
    assert obj.is_changed is False

    obj = InlineField(
        meta_type=MetadataType.INLINE,
        key="key",
        value="value",
        wrapping=Wrapping.PARENS,
    )
    assert obj.meta_type == MetadataType.INLINE
    assert obj.key == "key"
    assert obj.value == "value"
    assert obj.normalized_value == "value"
    assert obj.wrapping == Wrapping.PARENS
    assert obj.clean_key == "key"
    assert obj.normalized_key == "key"
    assert not obj.key_open
    assert not obj.key_close
    assert obj.is_changed is False

    obj = InlineField(
        meta_type=MetadataType.INLINE,
        key="**key**",
        value="value",
        wrapping=Wrapping.BRACKETS,
    )
    assert obj.meta_type == MetadataType.INLINE
    assert obj.key == "**key**"
    assert obj.value == "value"
    assert obj.normalized_value == "value"
    assert obj.wrapping == Wrapping.BRACKETS
    assert obj.clean_key == "key"
    assert obj.normalized_key == "key"
    assert obj.key_open == "**"
    assert obj.key_close == "**"
    assert obj.is_changed is False


@pytest.mark.parametrize(
    (
        "original",
        "cleaned",
        "normalized",
        "key_open",
        "key_close",
    ),
    [
        ("foo", "foo", "foo", "", ""),
        ("🌱/🌿", "🌱/🌿", "🌱/🌿", "", ""),
        ("FOO 1", "FOO 1", "foo-1", "", ""),
        ("**key foo**", "key foo", "key-foo", "**", "**"),
        ("## KEY", "KEY", "key", "## ", ""),
    ],
)
def test_init_3(original, cleaned, normalized, key_open, key_close):
    """Test creating an InlineField object.

    GIVEN an InlineField object is created
    WHEN the key needs to be normalized
    THEN confirm clean_key() returns the expected value
    """
    obj = InlineField(meta_type=MetadataType.INLINE, key=original, value="value")
    assert obj.clean_key == cleaned
    assert obj.normalized_key == normalized
    assert obj.key_open == key_open
    assert obj.key_close == key_close


@pytest.mark.parametrize(
    ("original", "normalized"),
    [("foo", "foo"), ("🌱/🌿", "🌱/🌿"), (" value ", "value"), ("   ", "-"), ("", "-")],
)
def test_init_4(original, normalized):
    """Test creating an InlineField object.

    GIVEN an InlineField object is created
    WHEN the value needs to be normalized
    THEN create the normalized_value attribute
    """
    obj = InlineField(meta_type=MetadataType.INLINE, key="key", value=original)
    assert obj.value == original
    assert obj.normalized_value == normalized


def test_inline_field_init_5():
    """Test updating the is_changed attribute.

    GIVEN creating an object
    WHEN is_changed set to True at init
    THEN confirm is_changed is True
    """
    obj = InlineField(meta_type=MetadataType.TAGS, key="key", value="tag1", is_changed=True)
    assert obj.is_changed is True


def test_inline_field_init_6():
    """Test updating the is_changed attribute.

    GIVEN creating an object
    WHEN is_changed set to True at after init
    THEN confirm is_changed is True
    """
    obj = InlineField(meta_type=MetadataType.TAGS, key="key", value="tag1", is_changed=False)
    assert obj.is_changed is False
    obj.is_changed = True
    assert obj.is_changed is True


def test_inline_field_init_4():
    """Test updating the is_changed attribute.

    GIVEN creating an object
    WHEN key_open and key_close are set after init
    THEN confirm they are set correctly
    """
    obj = InlineField(
        meta_type=MetadataType.INLINE,
        key="_key_",
        value="value",
        is_changed=False,
    )
    assert obj.key_open == "_"
    assert obj.key_close == "_"
    obj.key_open = "**"
    obj.key_close = "**"
    assert obj.key_open == "**"
    assert obj.key_close == "**"
