"""Regexes for parsing frontmatter and note content."""

from dataclasses import dataclass

import regex as re
from regex import Pattern


@dataclass
class Patterns:
    """Regex patterns for parsing frontmatter and note content."""

    find_inline_tags: Pattern[str] = re.compile(
        r"""
        (?:^|[ \|_,;:\*\)\[\]\\\.]|(?<!\])\()   # Before tag is start of line or separator
        (?<!\/\/[\w\d_\.\(\)\/&_-]+)            # Before tag is not a link
        \#([^ \|,;:\*\(\)\[\]\\\.\n#&]+)        # Match tag until separator or end of line
        """,
        re.MULTILINE | re.X,
    )

    find_inline_metadata: Pattern[str] = re.compile(
        r"""                                    # First look for in-text key values
        (?:^\[| \[)                             # Find key with starting bracket
        ([-_\w\d\/\*\u263a-\U0001f999]+?)::[ ]? # Find key
        (.*?)\]                                 # Find value until closing bracket
        |                                       # Else look for key values at start of line
        (?:^|[^ \w\d]+| \[)                     # Any non-word or non-digit character
        ([-_\w\d\/\*\u263a-\U0001f9995]+?)::(?!\n)(?:[ ](?!\n))?  # Capture the key if not a new line
        (.*?)$                                  # Capture the value
        """,
        re.X | re.MULTILINE,
    )

    frontmatter_block: Pattern[str] = re.compile(r"^\s*(?P<frontmatter>---.*?---)", flags=re.DOTALL)
    frontmatt_block_strip_separators: Pattern[str] = re.compile(
        r"^\s*---(?P<frontmatter>.*?)---", flags=re.DOTALL
    )
    # This pattern will return a tuple of 4 values, two will be empty and will need to be stripped before processing further

    top_with_header: Pattern[str] = re.compile(
        r"""^\s*                                        # Start of note
        (?P<top>                                        # Capture the top of the note
            (---.*?---)?                                # Frontmatter, if it exists
            \s*                                         # Any whitespace
            (                                           # Full header, if it exists
                \#+[ ]                                  # Match start of any header level
                (                                       # Text of header
                    [\w\d]+                             # Word or digit
                    |                                   # Or
                    [\[\]\(\)\+\{\}\"'\-\.\/\*\$\| ]+   # Special characters
                    |                                   # Or
                    [\u263a-\U0001f999]+                # Emoji
                )+                                      # End of header text
            )?                                          # End of full header
        )                                               # End capture group
        """,
        flags=re.DOTALL | re.X,
    )

    validate_key_text: Pattern[str] = re.compile(r"[^-_\w\d\/\*\u263a-\U0001f999]")
    validate_tag_text: Pattern[str] = re.compile(r"[ \|,;:\*\(\)\[\]\\\.\n#&]")
