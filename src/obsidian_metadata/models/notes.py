"""Representation of notes and in the vault."""


import difflib
import re
from pathlib import Path
import copy
import rich.repr
import typer
from rich.console import Console
from rich.table import Table
from obsidian_metadata._utils import alerts
from obsidian_metadata._utils.alerts import logger as log
from obsidian_metadata.models import (
    Frontmatter,
    InlineMetadata,
    InlineTags,
    InsertLocation,
    MetadataType,
    Patterns,
)

PATTERNS = Patterns()


@rich.repr.auto
class Note:
    """Representation of a note in the vault.

    Args:
        note_path (Path): Path to the note file.

    Attributes:
        note_path (Path): Path to the note file.
        dry_run (bool): Whether to run in dry-run mode.
        file_content (str): Total contents of the note file (frontmatter and content).
        frontmatter (dict): Frontmatter of the note.
        inline_tags (list): List of inline tags in the note.
        inline_metadata (dict): Dictionary of inline metadata in the note.
    """

    def __init__(self, note_path: Path, dry_run: bool = False):
        log.trace(f"Creating Note object for {note_path}")
        self.note_path: Path = Path(note_path)
        self.dry_run: bool = dry_run

        try:
            with self.note_path.open():
                self.file_content: str = self.note_path.read_text()
        except FileNotFoundError as e:
            alerts.error(f"Note {self.note_path} not found. Exiting")
            raise typer.Exit(code=1) from e

        self.frontmatter: Frontmatter = Frontmatter(self.file_content)
        self.inline_tags: InlineTags = InlineTags(self.file_content)
        self.inline_metadata: InlineMetadata = InlineMetadata(self.file_content)
        self.original_file_content: str = self.file_content

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover
        """Define rich representation of Vault."""
        yield "note_path", self.note_path
        yield "dry_run", self.dry_run
        yield "frontmatter", self.frontmatter
        yield "inline_tags", self.inline_tags
        yield "inline_metadata", self.inline_metadata

    def _delete_inline_metadata(self, key: str, value: str = None) -> None:
        """Delete an inline metadata key/value pair from the text of the note. This method does not remove the key/value from the metadata attribute of the note.

        Args:
            key (str): Key to delete.
            value (str, optional): Value to delete.
        """
        all_results = PATTERNS.find_inline_metadata.findall(self.file_content)
        stripped_null_values = [tuple(filter(None, x)) for x in all_results]

        for _k, _v in stripped_null_values:
            if re.search(key, _k):
                if value is None:
                    _k = re.escape(_k)
                    _v = re.escape(_v)
                    self.sub(rf"\[?{_k}:: ?{_v}]?", "", is_regex=True)
                    return

                if re.search(value, _v):
                    _k = re.escape(_k)
                    _v = re.escape(_v)
                    self.sub(rf"({_k}::) ?{_v}", r"\1", is_regex=True)

    def _rename_inline_metadata(self, key: str, value_1: str, value_2: str = None) -> None:
        """Replace the inline metadata in the note with the current inline metadata object.

        Args:
            key (str): Key to rename.
            value_1 (str): Value to replace OR new key name (if value_2 is None).
            value_2 (str, optional): New value.

        """
        all_results = PATTERNS.find_inline_metadata.findall(self.file_content)
        stripped_null_values = [tuple(filter(None, x)) for x in all_results]

        for _k, _v in stripped_null_values:
            if re.search(key, _k):
                if value_2 is None:
                    if re.search(rf"{key}[^\w\d_-]+", _k):
                        key_text = re.split(r"[^\w\d_-]+$", _k)[0]
                        key_markdown = re.split(r"^[\w\d_-]+", _k)[1]
                        self.sub(
                            rf"{key_text}{key_markdown}::",
                            rf"{value_1}{key_markdown}::",
                        )
                    else:
                        self.sub(f"{_k}::", f"{value_1}::")
                else:
                    if re.search(key, _k) and re.search(value_1, _v):
                        _k = re.escape(_k)
                        _v = re.escape(_v)
                        self.sub(f"{_k}:: ?{_v}", f"{_k}:: {value_2}", is_regex=True)

    def add_metadata(
        self,
        area: MetadataType,
        key: str = None,
        value: str | list[str] = None,
        location: InsertLocation = None,
    ) -> bool:
        """Add metadata to the note if it does not already exist.

        Args:
            area (MetadataType): Area to add metadata to.
            key (str, optional): Key to add
            location (InsertLocation, optional): Location to add inline metadata and tags.
            value (str, optional): Value to add.

        Returns:
            bool: Whether the metadata was added.
        """
        match area:  # noqa: E999
            case MetadataType.FRONTMATTER if self.frontmatter.add(key, value):
                self.update_frontmatter()
                return True

            case MetadataType.INLINE:
                if value is None:
                    if self.inline_metadata.add(key):
                        line = f"{key}::"
                        self.insert(new_string=line, location=location)
                        return True

                new_values = []
                if isinstance(value, list):
                    new_values = [_v for _v in value if self.inline_metadata.add(key, _v)]
                else:
                    if self.inline_metadata.add(key, value):
                        new_values = [value]

                if new_values:
                    for value in new_values:
                        self.insert(new_string=f"{key}:: {value}", location=location)
                    return True

            case MetadataType.TAGS:
                new_values = []
                if isinstance(value, list):
                    new_values = [_v for _v in value if self.inline_tags.add(_v)]
                else:
                    if self.inline_tags.add(value):
                        new_values = [value]

                if new_values:
                    for value in new_values:
                        if value.startswith("#"):
                            value = value[1:]
                        self.insert(new_string=f"#{value}", location=location)
                    return True

            case _:
                return False

        return False

    def contains_inline_tag(self, tag: str, is_regex: bool = False) -> bool:
        """Check if a note contains the specified inline tag.

        Args:
            tag (str): Tag to check for.
            is_regex (bool, optional): Whether to use regex to match the tag.

        Returns:
            bool: Whether the note has inline tags.
        """
        return self.inline_tags.contains(tag, is_regex=is_regex)

    def contains_metadata(self, key: str, value: str = None, is_regex: bool = False) -> bool:
        """Check if a note has a key or a key-value pair in its metadata.

        Args:
            key (str): Key to check for.
            value (str, optional): Value to check for.
            is_regex (bool, optional): Whether to use regex to match the key/value.

        Returns:
            bool: Whether the note contains the key or key-value pair.
        """
        if value is None:
            if self.frontmatter.contains(key, is_regex=is_regex) or self.inline_metadata.contains(
                key, is_regex=is_regex
            ):
                return True
            return False

        if self.frontmatter.contains(
            key, value, is_regex=is_regex
        ) or self.inline_metadata.contains(key, value, is_regex=is_regex):
            return True

        return False

    def delete_inline_tag(self, tag: str) -> bool:
        """Delete an inline tag from the `inline_tags` attribute AND removes the tag from the text of the note if it exists.

        Args:
            tag (str): Tag to delete.

        Returns:
            bool: Whether the tag was deleted.
        """
        new_list = self.inline_tags.list.copy()

        for _t in new_list:
            if re.search(tag, _t):
                _t = re.escape(_t)
                self.sub(rf"#{_t}([ \|,;:\*\(\)\[\]\\\.\n#&])", r"\1", is_regex=True)
                self.inline_tags.delete(tag)

        if new_list != self.inline_tags.list:
            return True

        return False

    def delete_metadata(
        self, key: str, value: str = None, area: MetadataType = MetadataType.ALL
    ) -> bool:
        """Delete a key or key-value pair from the note's metadata. Regex is supported.

        If no value is provided, will delete an entire key.

        Args:
            key (str): Key to delete.
            value (str, optional): Value to delete.
            area (MetadataType, optional): Area to delete metadata from. Defaults to MetadataType.ALL.

        Returns:
            bool: Whether the key or key-value pair was deleted.
        """
        changed_value: bool = False

        if value is None:
            if (
                area == MetadataType.FRONTMATTER or area == MetadataType.ALL
            ) and self.frontmatter.delete(key):
                self.update_frontmatter()
                changed_value = True
            if (
                area == MetadataType.INLINE or area == MetadataType.ALL
            ) and self.inline_metadata.delete(key):
                self._delete_inline_metadata(key, value)
                changed_value = True
        else:
            if (
                area == MetadataType.FRONTMATTER or area == MetadataType.ALL
            ) and self.frontmatter.delete(key, value):
                self.update_frontmatter()
                changed_value = True
            if (
                area == MetadataType.INLINE or area == MetadataType.ALL
            ) and self.inline_metadata.delete(key, value):
                self._delete_inline_metadata(key, value)
                changed_value = True

        if changed_value:
            return True
        return False

    def has_changes(self) -> bool:
        """Check if the note has been updated.

        Returns:
            bool: Whether the note has been updated.
        """
        if self.frontmatter.has_changes():
            return True

        if self.inline_tags.has_changes():
            return True

        if self.inline_metadata.has_changes():
            return True

        if self.file_content != self.original_file_content:
            return True

        return False

    def insert(
        self,
        new_string: str,
        location: InsertLocation,
        allow_multiple: bool = False,
    ) -> None:
        """Insert a string at the top of a note.

        Args:
            new_string (str): String to insert at the top of the note.
            allow_multiple (bool): Whether to allow inserting the string if it already exists in the note.
            location (InsertLocation): Location to insert the string.
        """
        if not allow_multiple and len(re.findall(re.escape(new_string), self.file_content)) > 0:
            return

        match location:
            case InsertLocation.BOTTOM:
                self.file_content += f"\n{new_string}"
            case InsertLocation.TOP:
                try:
                    top = PATTERNS.frontmatter_block.search(self.file_content).group("frontmatter")
                except AttributeError:
                    top = ""

                if top == "":
                    self.file_content = f"{new_string}\n{self.file_content}"
                else:
                    new_string = f"{top}\n{new_string}"
                    top = re.escape(top)
                    self.sub(top, new_string, is_regex=True)
            case InsertLocation.AFTER_TITLE:
                try:
                    top = PATTERNS.top_with_header.search(self.file_content).group("top")
                except AttributeError:
                    top = ""

                if top == "":
                    self.file_content = f"{new_string}\n{self.file_content}"
                else:
                    new_string = f"{top}\n{new_string}"
                    top = re.escape(top)
                    self.sub(top, new_string, is_regex=True)
            case _:
                raise ValueError(f"Invalid location: {location}")
        pass

    def print_note(self) -> None:
        """Print the note to the console."""
        print(self.file_content)

    def print_diff(self) -> None:
        """Print a diff of the note's original state and it's new state."""
        a = self.original_file_content.splitlines()
        b = self.file_content.splitlines()

        diff = difflib.Differ()
        result = list(diff.compare(a, b))
        table = Table(title=f"\nDiff of {self.note_path.name}", show_header=False, min_width=50)

        for line in result:
            if line.startswith("+"):
                table.add_row(line, style="green")
            elif line.startswith("-"):
                table.add_row(line, style="red")

        Console().print(table)

    def rename_inline_tag(self, tag_1: str, tag_2: str) -> bool:
        """Rename an inline tag from the note ONLY if it's not in the metadata as well.

        Args:
            tag_1 (str): Tag to rename.
            tag_2 (str): New tag name.

        Returns:
            bool: Whether the tag was renamed.
        """
        if tag_1 in self.inline_tags.list:
            self.sub(
                rf"#{tag_1}([ \|,;:\*\(\)\[\]\\\.\n#&])",
                rf"#{tag_2}\1",
                is_regex=True,
            )
            self.inline_tags.rename(tag_1, tag_2)
            return True
        return False

    def rename_metadata(self, key: str, value_1: str, value_2: str = None) -> bool:
        """Rename a key or key-value pair in the note's metadata.

        If no value is provided, will rename an entire key.

        Args:
            key (str): Key to rename.
            value_1 (str): Value to rename or new name of key if no value_2 is provided.
            value_2 (str, optional): New value.

        Returns:
            bool: Whether the note was updated.
        """
        changed_value: bool = False
        if value_2 is None:
            if self.frontmatter.rename(key, value_1):
                self.update_frontmatter()
                changed_value = True
            if self.inline_metadata.rename(key, value_1):
                self._rename_inline_metadata(key, value_1)
                changed_value = True
        else:
            if self.frontmatter.rename(key, value_1, value_2):
                self.update_frontmatter()
                changed_value = True
            if self.inline_metadata.rename(key, value_1, value_2):
                self._rename_inline_metadata(key, value_1, value_2)
                changed_value = True

        if changed_value:
            return True

        return False

    def sub(self, pattern: str, replacement: str, is_regex: bool = False) -> None:
        """Substitutes text within the note.

        Args:
            pattern (str): The pattern to replace (plain text or regular expression).
            replacement (str): What to replace the pattern with.
            is_regex (bool): Whether the pattern is a regex pattern or plain text.
        """
        if not is_regex:
            pattern = re.escape(pattern)

        self.file_content = re.sub(pattern, replacement, self.file_content, re.MULTILINE)

    def transpose_metadata(
        self,
        begin: MetadataType,
        end: MetadataType,
        key: str = None,
        value: str | list[str] = None,
        location: InsertLocation = InsertLocation.BOTTOM,
    ) -> bool:
        """Transpose metadata from one type to another.

        Args:
            begin (MetadataType): The type of metadata to transpose from.
            end (MetadataType): The type of metadata to transpose to.
            key (str, optional): The key to transpose. Defaults to None.
            value (str | list[str], optional): The value to transpose. Defaults to None.

        Returns:
            bool: Whether the note was updated.
        """
        if (begin == MetadataType.FRONTMATTER or begin == MetadataType.INLINE) and (
            end == MetadataType.FRONTMATTER or end == MetadataType.INLINE
        ):
            if begin == MetadataType.FRONTMATTER:
                begin_dict = self.frontmatter.dict
            else:
                begin_dict = self.inline_metadata.dict

            if begin_dict == {}:
                return False

            if key is None:  # Transpose all metadata when no key is provided
                for _key, _value in begin_dict.items():
                    self.add_metadata(key=_key, value=_value, area=end, location=location)
                    self.delete_metadata(key=_key, area=begin)
                return True

            has_changes = False
            temp_dict = copy.deepcopy(begin_dict)
            for k, v in begin_dict.items():
                if key == k:
                    if value is None:
                        self.add_metadata(key=k, value=v, area=end, location=location)
                        self.delete_metadata(key=k, area=begin)
                        return True

                    if value == v:
                        self.add_metadata(key=k, value=v, area=end, location=location)
                        self.delete_metadata(key=k, area=begin)
                        return True

                    if isinstance(value, str):
                        if value in v:
                            self.add_metadata(key=k, value=value, area=end, location=location)
                            self.delete_metadata(key=k, value=value, area=begin)
                            return True
                        else:
                            return False

                    if isinstance(value, list):
                        for value_item in value:
                            if value_item in v:
                                self.add_metadata(
                                    key=k, value=value_item, area=end, location=location
                                )
                                self.delete_metadata(key=k, value=value_item, area=begin)
                                temp_dict[k].remove(value_item)
                                has_changes = True

                        if temp_dict[k] == []:
                            self.delete_metadata(key=k, area=begin)

                    if has_changes:
                        return True
                    else:
                        return False

        if begin == MetadataType.TAGS:
            # TODO: Implement transposing to and from tags
            pass

        return False

    def update_frontmatter(self, sort_keys: bool = False) -> None:
        """Replace the frontmatter in the note with the current frontmatter object."""
        try:
            current_frontmatter = PATTERNS.frontmatter_block.search(self.file_content).group(
                "frontmatter"
            )
        except AttributeError:
            current_frontmatter = None

        if current_frontmatter is None and self.frontmatter.dict == {}:
            return

        new_frontmatter = self.frontmatter.to_yaml(sort_keys=sort_keys)
        if self.frontmatter.dict == {}:
            new_frontmatter = ""
        else:
            new_frontmatter = f"---\n{new_frontmatter}---\n"

        if current_frontmatter is None:
            self.file_content = new_frontmatter + self.file_content
            return

        current_frontmatter = f"{re.escape(current_frontmatter)}\n?"
        self.sub(current_frontmatter, new_frontmatter, is_regex=True)

    def write(self, path: Path = None) -> None:
        """Write the note's content to disk.

        Args:
            path (Path): Path to write the note to. Defaults to the note's path.

        Raises:
            typer.Exit: If the note's path is not found.
        """
        p = self.note_path if path is None else path
        if self.dry_run:
            log.trace(f"DRY RUN: Writing note {p} to disk")
            return

        try:
            with open(p, "w") as f:
                log.trace(f"Writing note {p} to disk")
                f.write(self.file_content)
        except FileNotFoundError as e:
            alerts.error(f"Note {p} not found. Exiting")
            raise typer.Exit(code=1) from e
