# type: ignore
"""Helper functions for tests."""

import re


class KeyInputs:
    """Key inputs for testing."""

    DOWN = "\x1b[B"
    UP = "\x1b[A"
    LEFT = "\x1b[D"
    RIGHT = "\x1b[C"
    ENTER = "\r"
    ESCAPE = "\x1b"
    CONTROLC = "\x03"
    BACK = "\x7f"
    SPACE = " "
    TAB = "\x09"
    ONE = "1"
    TWO = "2"
    THREE = "3"


def remove_ansi(text) -> str:
    """Remove ANSI escape sequences from a string.

    Args:
        text (str): String to remove ANSI escape sequences from.

    Returns:
        str: String without ANSI escape sequences.
    """
    ansi_chars = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_chars.sub("", text)


class Regex:
    """Assert that a given string meets some expectations.

    Usage:
        from tests.helpers import Regex

        assert caplog.text == Regex(r"^.*$", re.I)
    """

    def __init__(self, pattern, flags=0):
        self._regex = re.compile(pattern, flags)

    def __eq__(self, actual):
        """Define equality.

        Args:
            actual (str): String to be matched to the regex

        Returns:
            bool: True if the actual string matches the regex, False otherwise.
        """
        return bool(self._regex.search(actual))

    def __repr__(self):
        """Error printed on failed tests."""
        return f"Regex: '{self._regex.pattern}'"
