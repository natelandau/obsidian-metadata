"""Shared utilities."""

from obsidian_metadata._utils import alerts
from obsidian_metadata._utils.alerts import LoggerManager
from obsidian_metadata._utils.utilities import (
    clean_dictionary,
    clear_screen,
    delete_from_dict,
    dict_contains,
    dict_keys_to_lower,
    dict_values_to_lists_strings,
    docstring_parameter,
    inline_metadata_from_string,
    merge_dictionaries,
    remove_markdown_sections,
    rename_in_dict,
    validate_csv_bulk_imports,
    version_callback,
)

__all__ = [
    "alerts",
    "clean_dictionary",
    "clear_screen",
    "delete_from_dict",
    "dict_contains",
    "dict_keys_to_lower",
    "dict_values_to_lists_strings",
    "docstring_parameter",
    "LoggerManager",
    "inline_metadata_from_string",
    "merge_dictionaries",
    "rename_in_dict",
    "remove_markdown_sections",
    "validate_csv_bulk_imports",
    "version_callback",
]
