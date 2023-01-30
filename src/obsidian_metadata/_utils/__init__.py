"""Shared utilities."""

from obsidian_metadata._utils import alerts
from obsidian_metadata._utils.alerts import LoggerManager
from obsidian_metadata._utils.utilities import (
    clean_dictionary,
    clear_screen,
    dict_contains,
    dict_values_to_lists_strings,
    docstring_parameter,
    remove_markdown_sections,
    version_callback,
)

__all__ = [
    "alerts",
    "clean_dictionary",
    "clear_screen",
    "dict_contains",
    "dict_values_to_lists_strings",
    "docstring_parameter",
    "LoggerManager",
    "remove_markdown_sections",
    "vault_validation",
    "version_callback",
]
