"""Parsers for Obsidian metadata files."""

from dataclasses import dataclass

import emoji
import regex as re

from obsidian_metadata.models.enums import Wrapping


@dataclass
class Parser:
    """Regex parsers for Obsidian metadata files.

    All methods return a list of matches
    """

    # Reusable regex patterns
    internal_link = r"\[\[[^\[\]]*?\]\]"  # An Obsidian link of the form [[<link>]]
    chars_not_in_tags = r"\u2000-\u206F\u2E00-\u2E7F'!\"#\$%&\(\)\*+,\.:;<=>?@\^`\{\|\}~\[\]\\\s"

    # Compiled regex patterns
    tag = re.compile(
        r"""
        (?:
            (?:^|\s|\\{2}) # If tarts with newline, space, or "\\""
                (?P<tag>\#[^\u2000-\u206F\u2E00-\u2E7F'!\"\#\$%&\(\)\*+,\.:;<=>?@\^`\{\|\}~\[\]\\\s]+) # capture tag
                | # Else
                (?:(?<=
                    \#[^\u2000-\u206F\u2E00-\u2E7F'!\"\#\$%&\(\)\*+,\.:;<=>?@\^`\{\|\}~\[\]\\\s]+
                )) # if lookbehind is a tag
                    (?P<tag>\#[^\u2000-\u206F\u2E00-\u2E7F'!\"\#\$%&\(\)\*+,\.:;<=>?@\^`\{\|\}~\[\]\\\s]+) # capture tag
                    | # Else
                    (*FAIL)
        )
        """,
        re.X,
    )
    frontmatter_complete = re.compile(r"^\s*(?P<frontmatter>---.*?---)", flags=re.DOTALL)
    frontmatter_data = re.compile(
        r"(?P<open>^\s*---)(?P<frontmatter>.*?)(?P<close>---)", flags=re.DOTALL
    )
    code_block = re.compile(r"```.*?```", flags=re.DOTALL)
    inline_code = re.compile(r"(?<!`{2})`[^`]+?` ?")
    inline_metadata = re.compile(
        r"""
        (?: # Conditional
            (?= # If opening wrapper is a bracket or parenthesis
                (
                    (?<!\[)\[(?!\[) # Single bracket
                    |               # Or
                    (?<!\()\((?!\() # Single parenthesis
                    )
                )
                (?: # Conditional
                    (?= # If opening wrapper is a bracket
                        (?<!\[)\[(?!\[) # Single bracket
                    )
                        (?<!\[)(?P<open>\[)(?!\[)           # Open bracket
                        (?P<key>[0-9\p{Letter}\w\s_/-;\*\~`]+?)  # Find key
                        (?<!:)::(?!:)                       # Separator
                        (?P<value>.*?)                      # Value
                        (?<!\])(?P<close>\])(?!\])          # Close bracket
                    | # Else if opening wrapper is a parenthesis
                        (?<!\()(?P<open>\()(?!\()           # Open parens
                        (?P<key>[0-9\p{Letter}\w\s_/-;\*\~`]+?)  # Find key
                        (?<!:)::(?!:)                       # Separator
                        (?P<value>.*?)                      # Value
                        (?<!\))(?P<close>\))(?!\))          # Close parenthesis
                )
                | # Else grab entire line
                (?P<key>[0-9\p{Letter}\w\s_/-;\*\~`]+?)          # Find key
                (?<!:)::(?!:)                               # Separator
                (?P<value>.*)                               # Value
        )

    """,
        re.X | re.I,
    )
    top_with_header = re.compile(
        r"""^\s*                                        # Start of note
        (?P<top>                                        # Capture the top of the note
            .*                                         # Anything above the first header
            \#+[ ].*?[\r\n]                           # Full header, if it exists
        )                                               # End capture group
        """,
        flags=re.DOTALL | re.X,
    )
    validate_key_text = re.compile(r"[^-_\w\d\/\*\u263a-\U0001f999]")
    validate_tag_text = re.compile(r"[ \|,;:\*\(\)\[\]\\\.\n#&]")

    def return_inline_metadata(self, line: str) -> list[tuple[str, str, Wrapping]] | None:
        """Return a list of metadata matches for a single line.

        Args:
            line (str): The text to search.

        Returns:
            list[tuple[str, str, Wrapping]] | None: A list of tuples containing the key, value, and wrapping type.
        """
        sep = r"(?<!:)::(?!:)"
        if not re.search(sep, line):
            return None

        # Replace emoji with text
        line = emoji.demojize(line, delimiters=(";", ";"))

        matches = []
        for match in self.inline_metadata.finditer(line):
            match match.group("open"):
                case "[":
                    wrapper = Wrapping.BRACKETS
                case "(":
                    wrapper = Wrapping.PARENS
                case _:
                    wrapper = Wrapping.NONE

            matches.append(
                (
                    emoji.emojize(match.group("key"), delimiters=(";", ";")),
                    emoji.emojize(match.group("value"), delimiters=(";", ";")),
                    wrapper,
                )
            )

        return matches

    def return_frontmatter(self, text: str, data_only: bool = False) -> str | None:
        """Return a list of metadata matches.

        Args:
            text (str): The text to search.
            data_only (bool, optional): If True, only return the frontmatter data and strip the "---" lines from the returned string. Defaults to False

        Returns:
            str | None: The frontmatter block, or None if no frontmatter is found.
        """
        if data_only:
            result = self.frontmatter_data.search(text)
        else:
            result = self.frontmatter_complete.search(text)

        if result:
            return result.group("frontmatter").strip()
        return None

    def return_tags(self, text: str) -> list[str]:
        """Return a list of tags.

        Args:
            text (str): The text to search.

        Returns:
            list[str]: A list of tags.
        """
        return [
            t.group("tag")
            for t in self.tag.finditer(text)
            if not re.match(r"^#[0-9]+$", t.group("tag"))
        ]

    def return_top_with_header(self, text: str) -> str:
        """Returns the top content of a string until the end of the first markdown header found.

        Args:
            text (str): The text to search.

        Returns:
            str: The top content of the string.
        """
        result = self.top_with_header.search(text)
        if result:
            return result.group("top")
        return None

    def strip_frontmatter(self, text: str, data_only: bool = False) -> str:
        """Strip frontmatter from a string.

        Args:
            text (str): The text to search.
            data_only (bool, optional): If True, only strip the frontmatter data and leave the '---' lines. Defaults to False
        """
        if data_only:
            return self.frontmatter_data.sub(r"\g<open>\n\g<close>", text)

        return self.frontmatter_complete.sub("", text)

    def strip_code_blocks(self, text: str) -> str:
        """Strip code blocks from a string."""
        return self.code_block.sub("", text)

    def strip_inline_code(self, text: str) -> str:
        """Strip inline code from a string."""
        return self.inline_code.sub("", text)
