"""Work with metadata items."""

import re
from io import StringIO

from rich import print
from rich.columns import Columns
from rich.console import Console
from rich.table import Table
from ruamel.yaml import YAML

from obsidian_metadata._utils import (
    clean_dictionary,
    dict_contains,
    dict_values_to_lists_strings,
    remove_markdown_sections,
)
from obsidian_metadata.models import Patterns  # isort: ignore

PATTERNS = Patterns()
INLINE_TAG_KEY: str = "Inline Tags"


class VaultMetadata:
    """Representation of all Metadata in the Vault."""

    def __init__(self) -> None:
        self.dict: dict[str, list[str]] = {}

    def __repr__(self) -> str:
        """Representation of all metadata."""
        return str(self.dict)

    def add_metadata(self, metadata: dict[str, list[str]]) -> None:
        """Add metadata to the vault. Takes a dictionary as input and merges it with the existing metadata.  Does not overwrite existing keys.

        Args:
            metadata (dict): Metadata to add.
        """
        existing_metadata = self.dict

        new_metadata = clean_dictionary(metadata)

        for k, v in new_metadata.items():
            if k in existing_metadata:
                if isinstance(v, list):
                    existing_metadata[k].extend(v)
            else:
                existing_metadata[k] = v

        for k, v in existing_metadata.items():
            if isinstance(v, list):
                existing_metadata[k] = sorted(set(v))
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    if isinstance(vv, list):
                        v[kk] = sorted(set(vv))

        self.dict = dict(sorted(existing_metadata.items()))

    def contains(self, key: str, value: str = None, is_regex: bool = False) -> bool:
        """Check if a key and/or a value exists in the metadata.

        Args:
            key (str): Key to check.
            value (str, optional): Value to check.
            is_regex (bool, optional): Use regex to check. Defaults to False.

        Returns:
            bool: True if the key exists.
        """
        return dict_contains(self.dict, key, value, is_regex)

    def delete(self, key: str, value_to_delete: str = None) -> bool:
        """Delete a key or a key's value from the metadata. Regex is supported to allow deleting more than one key or value.

        Args:
            key (str): Key to check.
            value_to_delete (str, optional): Value to delete.

        Returns:
            bool: True if a value was deleted
        """
        new_dict = self.dict.copy()

        if value_to_delete is None:
            for _k in list(new_dict):
                if re.search(key, _k):
                    del new_dict[_k]
        else:
            for _k, _v in new_dict.items():
                if re.search(key, _k):
                    new_values = [x for x in _v if not re.search(value_to_delete, x)]
                    new_dict[_k] = sorted(new_values)

        if new_dict != self.dict:
            self.dict = dict(new_dict)
            return True

        return False

    def print_keys(self) -> None:
        """Print all metadata keys."""
        columns = Columns(
            sorted(self.dict.keys()),
            equal=True,
            expand=True,
            title="All metadata keys in Obsidian vault",
        )
        print(columns)

    def print_metadata(self) -> None:
        """Print all metadata."""
        table = Table(show_footer=False, show_lines=True)
        table.add_column("Keys")
        table.add_column("Values")
        for key, value in sorted(self.dict.items()):
            values: str | dict[str, list[str]] = (
                "\n".join(sorted(value)) if isinstance(value, list) else value
            )
            table.add_row(f"[bold]{key}[/]", str(values))
        Console().print(table)

    def print_tags(self) -> None:
        """Print all tags."""
        columns = Columns(
            sorted(self.dict["tags"]),
            equal=True,
            expand=True,
            title="All tags in Obsidian vault",
        )
        print(columns)

    def rename(self, key: str, value_1: str, value_2: str = None) -> bool:
        """Replace a value in the frontmatter.

        Args:
            key (str): Key to check.
            value_1 (str): `With value_2` this is the value to rename. If `value_2` is None this is the renamed key
            value_2 (str, Optional): New value.
            bypass_check (bool, optional): Bypass the check if the key exists. Defaults to False.

        Returns:
            bool: True if a value was renamed
        """
        if value_2 is None:
            if key in self.dict and value_1 not in self.dict:
                self.dict[value_1] = self.dict.pop(key)
                return True
            return False

        if key in self.dict and value_1 in self.dict[key]:
            self.dict[key] = sorted({value_2 if x == value_1 else x for x in self.dict[key]})
            return True

        return False


class Frontmatter:
    """Representation of frontmatter metadata."""

    def __init__(self, file_content: str):

        self.dict: dict[str, list[str]] = self._grab_note_frontmatter(file_content)
        self.dict_original: dict[str, list[str]] = self.dict.copy()

    def __repr__(self) -> str:  # pragma: no cover
        """Representation of the frontmatter.

        Returns:
            str: frontmatter
        """
        return f"Frontmatter(frontmatter={self.dict})"

    def _grab_note_frontmatter(self, file_content: str) -> dict:
        """Grab metadata from a note.

        Args:
            note_path (Path): Path to the note file.

        Returns:
            dict: Metadata from the note.
        """
        try:
            frontmatter_block: str = PATTERNS.frontmatt_block_no_separators.search(
                file_content
            ).group("frontmatter")
        except AttributeError:
            return {}

        yaml = YAML(typ="safe")
        frontmatter: dict = yaml.load(frontmatter_block)

        for k in frontmatter:
            if frontmatter[k] is None:
                frontmatter[k] = []

        return dict_values_to_lists_strings(frontmatter, strip_null_values=True)

    def add(self, key: str, value: str | list[str] = None) -> bool:
        """Add a key and value to the frontmatter.

        Args:
            key (str): Key to add.
            value (str, optional): Value to add.

        Returns:
            bool: True if the metadata was added
        """
        if value is None:
            if key not in self.dict:
                self.dict[key] = []
                return True
            return False

        if key not in self.dict:
            if isinstance(value, list):
                self.dict[key] = value
                return True

            self.dict[key] = [value]
            return True

        if key in self.dict and value not in self.dict[key]:
            if isinstance(value, list):
                self.dict[key].extend(value)
                return True

            self.dict[key].append(value)
            return True

        return False

    def contains(self, key: str, value: str = None, is_regex: bool = False) -> bool:
        """Check if a key or value exists in the metadata.

        Args:
            key (str): Key to check.
            value (str, optional): Value to check.
            is_regex (bool, optional): Use regex to check. Defaults to False.

        Returns:
            bool: True if the key exists.
        """
        return dict_contains(self.dict, key, value, is_regex)

    def delete(self, key: str, value_to_delete: str = None) -> bool:
        """Delete a value or key in the frontmatter.  Regex is supported to allow deleting more than one key or value.

        Args:
            key (str): If no value, key to delete. If value, key containing the value.
            value_to_delete (str, optional): Value to delete.

        Returns:
            bool: True if a value was deleted
        """
        new_dict = dict(self.dict)

        if value_to_delete is None:
            for _k in list(new_dict):
                if re.search(key, _k):
                    del new_dict[_k]
        else:
            for _k, _v in new_dict.items():
                if re.search(key, _k):
                    new_values = [x for x in _v if not re.search(value_to_delete, x)]
                    new_dict[_k] = sorted(new_values)

        if new_dict != self.dict:
            self.dict = dict(new_dict)
            return True

        return False

    def has_changes(self) -> bool:
        """Check if the frontmatter has changes.

        Returns:
            bool: True if the frontmatter has changes.
        """
        return self.dict != self.dict_original

    def rename(self, key: str, value_1: str, value_2: str = None) -> bool:
        """Replace a value in the frontmatter.

        Args:
            key (str): Key to check.
            value_1 (str): `With value_2` this is the value to rename. If `value_2` is None this is the renamed key
            value_2 (str, Optional): New value.

        Returns:
            bool: True if a value was renamed
        """
        if value_2 is None:
            if key in self.dict and value_1 not in self.dict:
                self.dict[value_1] = self.dict.pop(key)
                return True
            return False

        if key in self.dict and value_1 in self.dict[key]:
            self.dict[key] = sorted({value_2 if x == value_1 else x for x in self.dict[key]})
            return True

        return False

    def to_yaml(self, sort_keys: bool = False) -> str:
        """Return the frontmatter as a YAML string.

        Returns:
            str: Frontmatter as a YAML string.
            sort_keys (bool, optional): Sort the keys. Defaults to False.
        """
        dict_to_dump = self.dict.copy()
        for k in dict_to_dump:
            if dict_to_dump[k] == []:
                dict_to_dump[k] = None
            if isinstance(dict_to_dump[k], list) and len(dict_to_dump[k]) == 1:
                new_val = dict_to_dump[k][0]
                dict_to_dump[k] = new_val  # type: ignore [assignment]

        # Converting stream to string from https://stackoverflow.com/questions/47614862/best-way-to-use-ruamel-yaml-to-dump-yaml-to-string-not-to-stream/63179923#63179923

        if sort_keys:
            dict_to_dump = dict(sorted(dict_to_dump.items()))

        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        string_stream = StringIO()
        yaml.dump(dict_to_dump, string_stream)
        yaml_value = string_stream.getvalue()
        string_stream.close()
        return yaml_value


class InlineMetadata:
    """Representation of inline metadata in the form of `key:: value`."""

    def __init__(self, file_content: str):

        self.dict: dict[str, list[str]] = self._grab_inline_metadata(file_content)
        self.dict_original: dict[str, list[str]] = self.dict.copy()

    def __repr__(self) -> str:  # pragma: no cover
        """Representation of inline metadata.

        Returns:
            str: inline metadata
        """
        return f"InlineMetadata(inline_metadata={self.dict})"

    def _grab_inline_metadata(self, file_content: str) -> dict[str, list[str]]:
        """Grab inline metadata from a note.

        Returns:
            dict[str, str]: Inline metadata from the note.
        """
        content = remove_markdown_sections(
            file_content,
            strip_codeblocks=True,
            strip_inlinecode=True,
            strip_frontmatter=True,
        )
        all_results = PATTERNS.find_inline_metadata.findall(content)
        stripped_null_values = [tuple(filter(None, x)) for x in all_results]

        inline_metadata: dict[str, list[str]] = {}
        for (k, v) in stripped_null_values:
            if k in inline_metadata:
                inline_metadata[k].append(str(v))
            else:
                inline_metadata[k] = [str(v)]

        return clean_dictionary(inline_metadata)

    def add(self, key: str, value: str | list[str] = None) -> bool:
        """Add a key and value to the frontmatter.

        Args:
            key (str): Key to add.
            value (str, optional): Value to add.

        Returns:
            bool: True if the metadata was added
        """
        # TODO: implement adding to inline metadata which requires knowing where in the note the metadata is to be added.  In addition, unlike frontmatter, it is not possible to have multiple values for a key.
        pass

    def contains(self, key: str, value: str = None, is_regex: bool = False) -> bool:
        """Check if a key or value exists in the inline metadata.

        Args:
            key (str): Key to check.
            value (str, Optional): Value to check.
            is_regex (bool, optional): If True, key and value are treated as regex. Defaults to False.

        Returns:
            bool: True if the key exists.
        """
        return dict_contains(self.dict, key, value, is_regex)

    def delete(self, key: str, value_to_delete: str = None) -> bool:
        """Delete a value or key in the inline metadata. Regex is supported to allow deleting more than one key or value.

        Args:
            key (str): If no value, key to delete. If value, key containing the value.
            value_to_delete (str, optional): Value to delete.

        Returns:
            bool: True if a value was deleted
        """
        new_dict = dict(self.dict)

        if value_to_delete is None:
            for _k in list(new_dict):
                if re.search(key, _k):
                    del new_dict[_k]
        else:
            for _k, _v in new_dict.items():
                if re.search(key, _k):
                    new_values = [x for x in _v if not re.search(value_to_delete, x)]
                    new_dict[_k] = sorted(new_values)

        if new_dict != self.dict:
            self.dict = dict(new_dict)
            return True

        return False

    def has_changes(self) -> bool:
        """Check if the metadata has changes.

        Returns:
            bool: True if the metadata has changes.
        """
        return self.dict != self.dict_original

    def rename(self, key: str, value_1: str, value_2: str = None) -> bool:
        """Replace a value in the inline metadata.

        Args:
            key (str): Key to check.
            value_1 (str): `With value_2` this is the value to rename. If `value_2` is None this is the renamed key
            value_2 (str, Optional): New value.

        Returns:
            bool: True if a value was renamed
        """
        if value_2 is None:
            if key in self.dict and value_1 not in self.dict:
                self.dict[value_1] = self.dict.pop(key)
                return True
            return False

        if key in self.dict and value_1 in self.dict[key]:
            self.dict[key] = sorted({value_2 if x == value_1 else x for x in self.dict[key]})
            return True

        return False


class InlineTags:
    """Representation of inline tags."""

    def __init__(self, file_content: str):

        self.metadata_key = INLINE_TAG_KEY
        self.list: list[str] = self._grab_inline_tags(file_content)
        self.list_original: list[str] = self.list.copy()

    def __repr__(self) -> str:  # pragma: no cover
        """Representation of the inline tags.

        Returns:
            str: inline tags
        """
        return f"InlineTags(tags={self.list})"

    def _grab_inline_tags(self, file_content: str) -> list[str]:
        """Grab inline tags from a note.

        Args:
            file_content (str): Total contents of the note file (frontmatter and content).

        Returns:
            list[str]: Inline tags from the note.
        """
        return sorted(
            PATTERNS.find_inline_tags.findall(
                remove_markdown_sections(
                    file_content,
                    strip_codeblocks=True,
                    strip_inlinecode=True,
                )
            )
        )

    def contains(self, tag: str, is_regex: bool = False) -> bool:
        """Check if a tag exists in the metadata.

        Args:
            tag (str): Tag to check.
            is_regex (bool, optional): If True, tag is treated as regex. Defaults to False.

        Returns:
            bool: True if the tag exists.
        """
        if is_regex is True:
            return any(re.search(tag, _t) for _t in self.list)

        if tag in self.list:
            return True

        return False

    def delete(self, tag_to_delete: str) -> bool:
        """Delete a specified inline tag. Regex is supported to allow deleting more than one tag.

        Args:
            tag_to_delete (str, optional): Value to delete.

        Returns:
            bool: True if a value was deleted
        """
        new_list = sorted([x for x in self.list if re.search(tag_to_delete, x) is None])

        if new_list != self.list:
            self.list = new_list
            return True
        return False

    def has_changes(self) -> bool:
        """Check if the metadata has changes.

        Returns:
            bool: True if the metadata has changes.
        """
        return self.list != self.list_original

    def rename(self, old_tag: str, new_tag: str) -> bool:
        """Replace an inline tag with another string.

        Args:
            old_tag (str): `With value_2` this is the value to rename. If `value_2` is None this is the renamed key
            new_tag (str, Optional): New value.

        Returns:
            bool: True if a value was renamed
        """
        if old_tag in self.list:
            self.list = sorted([new_tag if i == old_tag else i for i in self.list])
            return True
        return False
