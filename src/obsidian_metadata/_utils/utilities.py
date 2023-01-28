"""Utility functions."""
import re
from os import name, system
from typing import Any

import typer

from obsidian_metadata.__version__ import __version__


def dict_values_to_lists_strings(dictionary: dict, strip_null_values: bool = False) -> dict:
    """Converts all values in a dictionary to lists of strings.

    Args:
        dictionary (dict): Dictionary to convert
        strip_null (bool): Whether to strip null values

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
            elif value is None or value == "None" or value == "":
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

    return text  # noqa: RET504


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        print(f"{__package__.split('.')[0]}: v{__version__}")
        raise typer.Exit()


def docstring_parameter(*sub: Any) -> Any:
    """Decorator to replace variables within docstrings.

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
    """Check if a dictionary contains a key.

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
