"""Utility functions."""
from typing import Any


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
        obj.__doc__ = obj.__doc__.format(*sub)
        return obj

    return dec
