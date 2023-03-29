"""Utility functions."""
import copy
import csv
import re
from os import name, system
from pathlib import Path
from typing import Any

import typer

from obsidian_metadata.__version__ import __version__
from obsidian_metadata._utils.console import console


def clean_dictionary(dictionary: dict[str, Any]) -> dict[str, Any]:
    """Clean up a dictionary by markdown formatting from keys and values.

    Args:
        dictionary (dict): Dictionary to clean

    Returns:
        dict: Cleaned dictionary
    """
    new_dict = copy.deepcopy(dictionary)
    new_dict = {key.strip("*[]# "): value for key, value in new_dict.items()}
    for key, value in new_dict.items():
        if isinstance(value, list):
            new_dict[key] = [s.strip("*[]# ") for s in value if isinstance(value, list)]
        elif isinstance(value, str):
            new_dict[key] = value.strip("*[]# ")

    return new_dict


def clear_screen() -> None:  # pragma: no cover
    """Clear the screen."""
    _ = system("cls") if name == "nt" else system("clear")


def dict_contains(
    dictionary: dict[str, list[str]], key: str, value: str = None, is_regex: bool = False
) -> bool:
    """Check if a dictionary contains a key or if a key contains a value.

    Args:
        dictionary (dict): Dictionary to check
        key (str): Key to check for
        value (str, optional): Value to check for. Defaults to None.
        is_regex (bool, optional): Whether the key is a regex. Defaults to False.

    Returns:
        bool: Whether the dictionary contains the key or value
    """
    if value is None:
        if is_regex:
            return any(re.search(key, str(_key)) for _key in dictionary)
        return key in dictionary

    if is_regex:
        for _key in dictionary:
            if re.search(key, str(_key)) and any(re.search(value, _v) for _v in dictionary[_key]):
                return True

        return False

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
    dictionary = copy.deepcopy(dictionary)
    new_dict = {}

    if strip_null_values:
        for key, value in dictionary.items():
            if isinstance(value, list):
                new_dict[key] = sorted([str(item) for item in value if item is not None])
            elif isinstance(value, dict):
                new_dict[key] = dict_values_to_lists_strings(value, strip_null_values=True)  # type: ignore[assignment]
            elif value is None or value == "None" or not value:
                new_dict[key] = []
            else:
                new_dict[key] = [str(value)]

        return new_dict

    for key, value in dictionary.items():
        if isinstance(value, list):
            new_dict[key] = sorted([str(item) if item is not None else "" for item in value])
        elif isinstance(value, dict):
            new_dict[key] = dict_values_to_lists_strings(value)  # type: ignore[assignment]
        else:
            new_dict[key] = [str(value) if value is not None else ""]

    return new_dict


def delete_from_dict(  # noqa: C901
    dictionary: dict, key: str, value: str = None, is_regex: bool = False
) -> dict:
    """Delete a key or a value from a dictionary.

    Args:
        dictionary (dict): Dictionary to delete from
        is_regex (bool, optional): Whether the key is a regex. Defaults to False.
        key (str): Key to delete
        value (str, optional): Value to delete. Defaults to None.

    Returns:
        dict: Dictionary without the key
    """
    dictionary = copy.deepcopy(dictionary)

    if value is None:
        if is_regex:
            return {k: v for k, v in dictionary.items() if not re.search(key, str(k))}

        return {k: v for k, v in dictionary.items() if k != key}

    if is_regex:
        keys_to_delete = []
        for _key in dictionary:
            if re.search(key, str(_key)):
                if isinstance(dictionary[_key], list):
                    dictionary[_key] = [v for v in dictionary[_key] if not re.search(value, v)]
                elif isinstance(dictionary[_key], str) and re.search(value, dictionary[_key]):
                    keys_to_delete.append(_key)

        for key in keys_to_delete:
            dictionary.pop(key)

    elif key in dictionary and isinstance(dictionary[key], list):
        dictionary[key] = [v for v in dictionary[key] if v != value]
    elif key in dictionary and dictionary[key] == value:
        dictionary.pop(key)

    return dictionary


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


def inline_metadata_from_string(string: str) -> list[tuple[Any, ...]]:
    """Search for inline metadata in a string and return a list tuples containing (key, value).

    Args:
        string (str): String to get metadata from

    Returns:
        tuple[str]: (key, value)
    """
    from obsidian_metadata.models import Patterns

    results = Patterns().find_inline_metadata.findall(string)
    return [tuple(filter(None, x)) for x in results]


def merge_dictionaries(dict1: dict, dict2: dict) -> dict:
    """Merge two dictionaries. When the values are lists, they are merged and sorted.

    Args:
        dict1 (dict): First dictionary.
        dict2 (dict): Second dictionary.

    Returns:
        dict: Merged dictionary.
    """
    d1 = copy.deepcopy(dict1)
    d2 = copy.deepcopy(dict2)

    for _key in d1:
        if not isinstance(d1[_key], list):
            raise TypeError(f"Key {_key} is not a list.")
    for _key in d2:
        if not isinstance(d2[_key], list):
            raise TypeError(f"Key {_key} is not a list.")

    for k, v in d2.items():
        if k in d1:
            d1[k].extend(v)
            d1[k] = sorted(set(d1[k]))
        else:
            d1[k] = sorted(set(v))

    return dict(sorted(d1.items()))


def rename_in_dict(
    dictionary: dict[str, list[str]], key: str, value_1: str, value_2: str = None
) -> dict:
    """Rename a key or a value in a dictionary who's values are lists of strings.

    Args:
        dictionary (dict): Dictionary to rename in.
        key (str): Key to check.
        value_1 (str): `With value_2` this is the value to rename. If `value_2` is None this is the renamed key
        value_2 (str, Optional): New value.

    Returns:
        dict: Dictionary with renamed key or value
    """
    dictionary = copy.deepcopy(dictionary)

    if value_2 is None:
        if key in dictionary and value_1 not in dictionary:
            dictionary[value_1] = dictionary.pop(key)
    elif key in dictionary and value_1 in dictionary[key]:
        dictionary[key] = sorted({value_2 if x == value_1 else x for x in dictionary[key]})

    return dictionary


def remove_markdown_sections(
    text: str,
    strip_codeblocks: bool = False,
    strip_inlinecode: bool = False,
    strip_frontmatter: bool = False,
) -> str:
    """Strip unwanted markdown sections from text. This is used to remove code blocks and frontmatter from the body of notes before tags and inline metadata are processed.

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
        text = re.sub(r"(?<!`{2})`[^`]+?`", "", text)

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

            if row_num > 0 and row["type"] not in ["tag", "frontmatter", "inline_metadata"]:
                raise typer.BadParameter(
                    f"Invalid type '{row['type']}' in CSV file. Must be one of 'tag', 'frontmatter', 'inline_metadata'"
                )

            if row["path"] not in csv_dict:
                csv_dict[row["path"]] = []

            csv_dict[row["path"]].append(
                {"type": row["type"], "key": row["key"], "value": row["value"]}
            )

        if row_num == 0 or row_num == 1:
            raise typer.BadParameter("Empty CSV file")

        paths_to_remove = [x for x in csv_dict if x not in note_paths]

        for _path in paths_to_remove:
            raise typer.BadParameter(
                f"'{_path}' in CSV does not exist in vault. Ensure all paths are relative to the vault root."
            )

    return csv_dict


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"{__package__.split('.')[0]}: v{__version__}")
        raise typer.Exit(0)
