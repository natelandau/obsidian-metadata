"""Enum classes for the obsidian_metadata package."""

from enum import Enum


class MetadataType(Enum):
    """Enum class for the type of metadata."""

    FRONTMATTER = "Frontmatter"
    INLINE = "Inline Metadata"
    TAGS = "Inline Tags"
    KEYS = "Metadata Keys Only"
    ALL = "All Metadata"


class InsertLocation(Enum):
    """Location to add metadata to notes.

    TOP:            Directly after frontmatter.
    AFTER_TITLE:    After a header following frontmatter.
    BOTTOM:         The bottom of the note

    """

    TOP = "Top"
    AFTER_TITLE = "Header"
    BOTTOM = "Bottom"
