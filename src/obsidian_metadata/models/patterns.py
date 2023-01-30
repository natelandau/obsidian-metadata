"""Regexes for parsing frontmatter and note content."""

import re
from dataclasses import dataclass
from typing import Pattern


@dataclass
class Patterns:
    """Regex patterns for parsing frontmatter and note content."""

    find_inline_tags: Pattern[str] = re.compile(
        r"""
        (?:^|[ \|_,;:\*\(\)\[\]\\\.])     # Before tag is start of line or separator
        \#([^ \|,;:\*\(\)\[\]\\\.\n#&]+)  # Match tag until separator or end of line
        """,
        re.MULTILINE | re.X,
    )

    find_inline_metadata: Pattern[str] = re.compile(
        r"""                                    # First look for in-text key values
        (?:^\[| \[)                             # Find key with starting bracket
        ([-_\w\d\/\*\u263a-\U0001f645]+?)::[ ]?                  # Find key
        (.*?)\]                                 # Find value until closing bracket
        |                                       # Else look for key values at start of line
        (?:^|[^ \w\d]+| \[)                     # Any non-word or non-digit character
        ([-_\w\d\/\*\u263a-\U0001f645]+?)::(?!\n)(?:[ ](?!\n))?  # Capture the key if not a new line
        (.*?)$                                  # Capture the value
        """,
        re.X | re.MULTILINE,
    )

    frontmatt_block_with_separators: Pattern[str] = re.compile(
        r"^\s*(?P<frontmatter>---.*?---)", flags=re.DOTALL
    )
    frontmatt_block_no_separators: Pattern[str] = re.compile(
        r"^\s*---(?P<frontmatter>.*?)---", flags=re.DOTALL
    )
    # This pattern will return a tuple of 4 values, two will be empty and will need to be stripped before processing further

    validate_key_text: Pattern[str] = re.compile(r"[^-_\w\d\/\*\u263a-\U0001f645]")
    validate_tag_text: Pattern[str] = re.compile(r"[ \|,;:\*\(\)\[\]\\\.\n#&]")
