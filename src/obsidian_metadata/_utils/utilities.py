"""Utility functions."""
import csv
import re
from os import name, system
from pathlib import Path
from typing import Any

import typer

from obsidian_metadata.__version__ import __version__
from obsidian_metadata._utils import alerts
from obsidian_metadata._utils.alerts import logger as log
from obsidian_metadata._utils.console import console


def clean_dictionary(dictionary: dict[str, Any]) -> dict[str, Any]:
    """Clean up a dictionary by markdown formatting from keys and values.

    Args:
        dictionary (dict): Dictionary to clean

    Returns:
        dict: Cleaned dictionary
    """
    new_dict = {key.strip(): value for key, value in dictionary.items()}
    new_dict = {key.strip("*[]#"): value for key, value in new_dict.items()}
    for key, value in new_dict.items():
        new_dict[key] = [s.strip("*[]#") for s in value if isinstance(value, list)]

    return new_dict


def clear_screen() -> None:  # pragma: no cover
    """Clear the screen."""
    # for windows
    _ = system("cls") if name == "nt" else system("clear")


def dict_contains(
    dictionary: dict[str, list[str]], key: str, value: str = None, is_regex: bool = False
) -> bool:
    """Check if a dictionary contains a key or if a specified key contains a value.

    Args:
        dictionary (dict): Dictionary to check
        key (str): Key to check for
        value (str, optional): Value to check for. Defaults to None.
        is_regex (bool, optional): Whether the key is a regex. Defaults to False.

    Returns:
        bool: Whether the dictionary contains the key
    """
    if value is None:
        if is_regex:
            return any(re.search(key, str(_key)) for _key in dictionary)
        return key in dictionary

    if is_regex:
        found_keys = []
        for _key in dictionary:
            if re.search(key, str(_key)):
                found_keys.append(
                    any(re.search(value, _v) for _v in dictionary[_key]),
                )
        return any(found_keys)

    return key in dictionary and value in dictionary[key]


def dict_keys_to_lower(dictionary: dict) -> dict:
    """Convert all keys in a dictionary to lowercase.

    Args:
        dictionary (dict): Dictionary to convert

    Returns:
        dict: Dictionary with all keys converted to lowercase
    """
    return {key.lower(): value for key, value in dictionary.items()}


def dict_values_to_lists_strings(
    dictionary: dict,
    strip_null_values: bool = False,
) -> dict:
    """Convert all values in a dictionary to lists of strings.

    Args:
        dictionary (dict): Dictionary to convert
        strip_null_values (bool): Whether to strip null values

    Returns:
        dict: Dictionary with all values converted to lists of strings

        {key: sorted(new_dict[key]) for key in sorted(new_dict)}
    """
    new_dict = {}

    if strip_null_values:
        for key, value in dictionary.items():
            if isinstance(value, list):
                new_dict[key] = sorted([str(item) for item in value if item is not None])
            elif isinstance(value, dict):
                new_dict[key] = dict_values_to_lists_strings(value)  # type: ignore[assignment]
            elif value is None or value == "None" or not value:
                new_dict[key] = []
            else:
                new_dict[key] = [str(value)]

        return new_dict

    for key, value in dictionary.items():
        if isinstance(value, list):
            new_dict[key] = sorted([str(item) for item in value])
        elif isinstance(value, dict):
            new_dict[key] = dict_values_to_lists_strings(value)  # type: ignore[assignment]
        else:
            new_dict[key] = [str(value)]

    return new_dict


def docstring_parameter(*sub: Any) -> Any:
    """Replace variables within docstrings.

    Args:
        sub (Any): Replacement variables

    Usage:
        @docstring_parameter("foo", "bar")
        def foo():
            '''This is a {0} docstring with {1} variables.'''

    """

    def dec(obj: Any) -> Any:
        """Format object."""
        obj.__doc__ = obj.__doc__.format(*sub)
        return obj

    return dec


def merge_dictionaries(dict1: dict, dict2: dict) -> dict:
    """Merge two dictionaries. When the values are lists, they are merged and sorted.

    Args:
        dict1 (dict): First dictionary.
        dict2 (dict): Second dictionary.

    Returns:
        dict: Merged dictionary.
    """
    for k, v in dict2.items():
        if k in dict1:
            if isinstance(v, list):
                dict1[k].extend(v)
        else:
            dict1[k] = v

    for k, v in dict1.items():
        if isinstance(v, list):
            dict1[k] = sorted(set(v))
        elif isinstance(v, dict):  # pragma: no cover
            for kk, vv in v.items():
                if isinstance(vv, list):
                    v[kk] = sorted(set(vv))

    return dict(sorted(dict1.items()))


def remove_markdown_sections(
    text: str,
    strip_codeblocks: bool = False,
    strip_inlinecode: bool = False,
    strip_frontmatter: bool = False,
) -> str:
    """Strip markdown sections from text.

    Args:
        text (str): Text to remove code blocks from
        strip_codeblocks (bool, optional): Strip code blocks. Defaults to False.
        strip_inlinecode (bool, optional): Strip inline code. Defaults to False.
        strip_frontmatter (bool, optional): Strip frontmatter. Defaults to False.

    Returns:
        str: Text without code blocks
    """
    if strip_codeblocks:
        text = re.sub(r"`{3}.*?`{3}", "", text, flags=re.DOTALL)

    if strip_inlinecode:
        text = re.sub(r"`.*?`", "", text)

    if strip_frontmatter:
        text = re.sub(r"^\s*---.*?---", "", text, flags=re.DOTALL)

    return text


def validate_csv_bulk_imports(csv_path: Path, note_paths: list) -> dict[str, list[dict[str, str]]]:
    """Validate the bulk import CSV file.

    Args:
        csv_path (dict): Dictionary to validate
        note_paths (list): List of paths to all notes in vault

    Returns:
        dict: Validated dictionary
    """
    csv_dict: dict[str, Any] = {}
    with csv_path.expanduser().open("r") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        row_num = 0
        for row in csv_reader:
            if row_num == 0:
                if "path" not in row:
                    raise typer.BadParameter("Missing 'path' column in CSV file")
                if "type" not in row:
                    raise typer.BadParameter("Missing 'type' column in CSV file")
                if "key" not in row:
                    raise typer.BadParameter("Missing 'key' column in CSV file")
                if "value" not in row:
                    raise typer.BadParameter("Missing 'value' column in CSV file")
            row_num += 1

            if row["path"] not in csv_dict:
                csv_dict[row["path"]] = []

            csv_dict[row["path"]].append(
                {"type": row["type"], "key": row["key"], "value": row["value"]}
            )

        if row_num == 0 or row_num == 1:
            raise typer.BadParameter("Empty CSV file")

        paths_to_remove = [x for x in csv_dict if x not in note_paths]

        for _path in paths_to_remove:
            alerts.warning(f"'{_path}' does not exist in vault. Skipping...")
            del csv_dict[_path]

        if len(csv_dict) == 0:
            log.error("No paths in the CSV file matched paths in the vault")
            raise typer.Exit(1)

    return csv_dict


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"{__package__.split('.')[0]}: v{__version__}")
        raise typer.Exit()
