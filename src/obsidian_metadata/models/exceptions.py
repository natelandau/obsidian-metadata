"""Custom exceptions for the obsidian_metadata package."""


class ObsidianMetadataError(Exception):
    """Base exception for the obsidian_metadata package."""


class FrontmatterError(ObsidianMetadataError):
    """Exception for errors in the frontmatter."""


class InlineMetadataError(ObsidianMetadataError):
    """Exception for errors in the inlined metadata."""


class InlineTagError(ObsidianMetadataError):
    """Exception for errors in the inline tags."""
