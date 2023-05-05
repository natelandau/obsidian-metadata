"""Work with metadata items."""


import re
from io import StringIO

import rich.repr
from ruamel.yaml import YAML

from obsidian_metadata.models.enums import MetadataType, Wrapping


def dict_to_yaml(dictionary: dict[str, list[str]], sort_keys: bool = False) -> str:
    """Return the a dictionary of {key: [values]} as a YAML string.

    Args:
        dictionary (dict[str, list[str]]): Dictionary of {key: [values]}.
        sort_keys (bool, optional): Sort the keys. Defaults to False.

    Returns:
        str: Frontmatter as a YAML string.
        sort_keys (bool, optional): Sort the keys. Defaults to False.
    """
    if sort_keys:
        dictionary = dict(sorted(dictionary.items()))

    for key, value in dictionary.items():
        if len(value) == 1:
            dictionary[key] = value[0]  # type: ignore [assignment]

    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    string_stream = StringIO()
    yaml.dump(dictionary, string_stream)
    yaml_value = string_stream.getvalue()
    string_stream.close()
    if yaml_value == "{}\n":
        return ""
    return yaml_value


@rich.repr.auto
class InlineField:
    """Representation of a single inline field.

    Attributes:
        meta_type (MetadataType): Metadata category.
        clean_key (str): Cleaned key - Key without surround markdown
        key (str): Metadata key - Complete key found in note
        key_close (str): Closing key markdown.
        key_open (str): Opening key markdown.
        normalized_key (str): Key converted to lowercase w. spaces replaced with dashes
        normalized_value (str): Value stripped of leading and trailing whitespace.
        value (str): Metadata value - Complete value found in note.
        wrapping (Wrapping): Inline metadata may be wrapped with [] or ().
    """

    def __init__(
        self,
        meta_type: MetadataType,
        key: str,
        value: str,
        wrapping: Wrapping = Wrapping.NONE,
        is_changed: bool = False,
    ) -> None:
        self.meta_type = meta_type
        self.key = key
        self.value = value
        self.wrapping = wrapping
        self.is_changed = is_changed

        # Clean keys of surrounding markdown and convert to lowercase
        self.clean_key, self.normalized_key, self.key_open, self.key_close = (
            self._clean_key(self.key) if self.key else (None, None, "", "")
        )

        # Normalize value for display
        self.normalized_value = "-" if re.match(r"^\s*$", self.value) else self.value.strip()

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover
        """Rich representation of the inline field."""
        yield "clean_key", self.clean_key
        yield "is_changed", self.is_changed
        yield "key_close", self.key_close
        yield "key_open", self.key_open
        yield "key", self.key
        yield "meta_type", self.meta_type.value
        yield "normalized_key", self.normalized_key
        yield "normalized_value", self.normalized_value
        yield "value", self.value
        yield "wrapping", self.wrapping.value

    def __eq__(self, other: object) -> bool:
        """Compare two InlineField objects."""
        if not isinstance(other, InlineField):
            return NotImplemented
        return (
            self.key == other.key
            and self.value == other.value
            and self.meta_type == other.meta_type
        )

    def __hash__(self) -> int:
        """Hash the InlineField object."""
        return hash((self.key, self.value, self.meta_type))

    def _clean_key(self, text: str) -> tuple[str, str, str, str]:
        """Remove markdown from the key.

            Creates the following attributes:

                clean_key     : The key stripped of opening and closing markdown
                normalized_key: The key converted to lowercase with spaces replaced with dashes
                key_open      : The opening markdown
                key_close     : The closing markdown.

        Args:
            text (str): Key to clean.

        Returns:
            tuple[str, str, str, str]: Cleaned key, normalized key, opening markdown, closing markdown.
        """
        cleaned = text
        if tmp := re.search(r"^([\*#_ `~]+)", text):
            key_open = tmp.group(0)
            cleaned = re.sub(rf"^{re.escape(key_open)}", "", text)
        else:
            key_open = ""

        if tmp := re.search(r"([\*#_ `~]+)$", text):
            key_close = tmp.group(0)
            cleaned = re.sub(rf"{re.escape(key_close)}$", "", cleaned)
        else:
            key_close = ""

        normalized = cleaned.replace(" ", "-").lower()

        return cleaned, normalized, key_open, key_close
