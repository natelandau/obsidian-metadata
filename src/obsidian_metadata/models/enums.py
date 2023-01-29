"""Enum classes for the obsidian_metadata package."""

from enum import Enum


class MetadataType(Enum):
    """Enum class for the type of metadata."""

    FRONTMATTER = "Frontmatter"
    INLINE = "Inline Metadata"
    TAGS = "Inline Tags"
