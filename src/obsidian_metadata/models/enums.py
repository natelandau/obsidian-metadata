"""Enum classes for the obsidian_metadata package."""

from enum import Enum


class InsertLocation(Enum):
    """Location to add metadata to notes.

    TOP:            Directly after frontmatter.
    AFTER_TITLE:    After a header following frontmatter.
    BOTTOM:         The bottom of the note

    """

    TOP = "Top"
    AFTER_TITLE = "After title"
    BOTTOM = "Bottom"


class MetadataType(Enum):
    """Enum class for the type of metadata."""

    ALL = "Inline, Frontmatter, and Tags"
    FRONTMATTER = "Frontmatter"
    INLINE = "Inline Metadata"
    KEYS = "Metadata Keys Only"
    META = "Inline and Frontmatter. No Tags"
    TAGS = "Inline Tags"


class Wrapping(Enum):
    """Wrapping for inline metadata within a block of text."""

    BRACKETS = "Brackets"
    PARENS = "Parentheses"
    NONE = None
