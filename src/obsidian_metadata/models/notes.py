"""Representation of a not in the vault."""


import copy
import difflib
import re
from pathlib import Path

import rich.repr
import typer
from rich.table import Table

from obsidian_metadata._utils import alerts, inline_metadata_from_string
from obsidian_metadata._utils.alerts import logger as log
from obsidian_metadata._utils.console import console
from obsidian_metadata.models import (
    Frontmatter,
    InlineMetadata,
    InlineTags,
    InsertLocation,
    MetadataType,
    Patterns,
)
from obsidian_metadata.models.exceptions import (
    FrontmatterError,
    InlineMetadataError,
    InlineTagError,
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
        tags (list): List of inline tags in the note.
        inline_metadata (dict): Dictionary of inline metadata in the note.
        original_file_content (str): Original contents of the note file (frontmatter and content)
    """

    def __init__(self, note_path: Path, dry_run: bool = False) -> None:
        log.trace(f"Creating Note object for {note_path}")
        self.note_path: Path = Path(note_path)
        self.dry_run: bool = dry_run

        try:
            with self.note_path.open():
                self.file_content: str = self.note_path.read_text()
                self.original_file_content: str = self.file_content
        except FileNotFoundError as e:
            alerts.error(f"Note {self.note_path} not found. Exiting")
            raise typer.Exit(code=1) from e

        try:
            self.frontmatter: Frontmatter = Frontmatter(self.file_content)
            self.inline_metadata: InlineMetadata = InlineMetadata(self.file_content)
            self.tags: InlineTags = InlineTags(self.file_content)
        except FrontmatterError as e:
            alerts.error(f"Invalid frontmatter: {self.note_path}\n{e}")
            raise typer.Exit(code=1) from e
        except InlineMetadataError as e:
            alerts.error(f"Error parsing inline metadata: {self.note_path}.\n{e}")
            raise typer.Exit(code=1) from e
        except InlineTagError as e:
            alerts.error(f"Error parsing inline tags: {self.note_path}\n{e}")
            raise typer.Exit(code=1) from e

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover
        """Define rich representation of Vault."""
        yield "note_path", self.note_path
        yield "dry_run", self.dry_run
        yield "frontmatter", self.frontmatter
        yield "tags", self.tags
        yield "inline_metadata", self.inline_metadata

    def add_metadata(  # noqa: C901
        self,
        area: MetadataType,
        key: str = None,
        value: str | list[str] = None,
        location: InsertLocation = None,
    ) -> bool:
        """Add metadata to the note if it does not already exist. This method adds specified metadata to the appropriate MetadataType object AND writes the new metadata to the note's file.

        Args:
            area (MetadataType): Area to add metadata to.
            key (str, optional): Key to add
            location (InsertLocation, optional): Location to add inline metadata and tags.
            value (str, optional): Value to add.

        Returns:
            bool: Whether the metadata was added.
        """
        match area:
            case MetadataType.FRONTMATTER if self.frontmatter.add(key, value):
                self.write_frontmatter()
                return True

            case MetadataType.INLINE:
                if value is None and self.inline_metadata.add(key):
                    line = f"{key}::"
                    self.write_string(new_string=line, location=location)
                    return True

                new_values = []
                if isinstance(value, list):
                    new_values = [_v for _v in value if self.inline_metadata.add(key, _v)]
                elif self.inline_metadata.add(key, value):
                    new_values = [value]

                if new_values:
                    for value in new_values:
                        self.write_string(new_string=f"{key}:: {value}", location=location)
                    return True

            case MetadataType.TAGS:
                new_values = []
                if isinstance(value, list):
                    new_values = [_v for _v in value if self.tags.add(_v)]
                elif self.tags.add(value):
                    new_values = [value]

                if new_values:
                    for value in new_values:
                        _v = value
                        if _v.startswith("#"):
                            _v = _v[1:]
                        self.write_string(new_string=f"#{_v}", location=location)
                    return True

            case _:
                return False

        return False

    def commit(self, path: Path = None) -> None:
        """Write the note's new content to disk. This is a destructive action.

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
            with p.open(mode="w") as f:
                log.trace(f"Writing note {p} to disk")
                f.write(self.file_content)
        except FileNotFoundError as e:
            alerts.error(f"Note {p} not found. Exiting")
            raise typer.Exit(code=1) from e

    def contains_tag(self, tag: str, is_regex: bool = False) -> bool:
        """Check if a note contains the specified inline tag.

        Args:
            tag (str): Tag to check for.
            is_regex (bool, optional): Whether to use regex to match the tag.

        Returns:
            bool: Whether the note has inline tags.
        """
        return self.tags.contains(tag, is_regex=is_regex)

    def contains_metadata(self, key: str, value: str = None, is_regex: bool = False) -> bool:
        """Check if a note has a key or a key-value pair in its Frontmatter or InlineMetadata.

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

    def delete_all_metadata(self) -> None:
        """Delete all metadata from the note. Removes all frontmatter and inline metadata and tags from the body of the note and from the associated metadata objects."""
        for key in self.inline_metadata.dict:
            self.delete_metadata(key=key, area=MetadataType.INLINE)

        for tag in self.tags.list:
            self.delete_tag(tag=tag)

        self.frontmatter.delete_all()
        self.write_frontmatter()

    def delete_tag(self, tag: str) -> bool:
        """Delete an inline tag from the `tags` attribute AND removes the tag from the text of the note if it exists.

        Args:
            tag (str): Tag to delete.

        Returns:
            bool: Whether the tag was deleted.
        """
        new_list = self.tags.list.copy()

        for _t in new_list:
            if re.search(tag, _t):
                _t = re.escape(_t)
                self.sub(rf"#{_t}([ \|,;:\*\(\)\[\]\\\.\n#&])", r"\1", is_regex=True)
                self.tags.delete(tag)

        if new_list != self.tags.list:
            return True

        return False

    def delete_metadata(
        self,
        key: str,
        value: str = None,
        area: MetadataType = MetadataType.ALL,
        is_regex: bool = False,
    ) -> bool:
        """Delete a key or key-value pair from the note's Metadata object and the content of the note.  Regex is supported.

        If no value is provided, will delete an entire specified key.

        Args:
            area (MetadataType, optional): Area to delete metadata from. Defaults to MetadataType.ALL.
            is_regex (bool, optional): Whether to use regex to match the key/value.
            key (str): Key to delete.
            value (str, optional): Value to delete.

        Returns:
            bool: Whether the key or key-value pair was deleted.
        """
        changed_value: bool = False

        if (
            area == MetadataType.FRONTMATTER or area == MetadataType.ALL
        ) and self.frontmatter.delete(key=key, value_to_delete=value, is_regex=is_regex):
            self.write_frontmatter()
            changed_value = True

        if (
            area == MetadataType.INLINE or area == MetadataType.ALL
        ) and self.inline_metadata.contains(key, value):
            self.write_delete_inline_metadata(key=key, value=value, is_regex=is_regex)
            self.inline_metadata.delete(key=key, value_to_delete=value, is_regex=is_regex)
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

        if self.tags.has_changes():
            return True

        if self.inline_metadata.has_changes():
            return True

        if self.file_content != self.original_file_content:
            return True

        return False

    def print_diff(self) -> None:
        """Print a diff of the note's content. Compares original state to it's new state."""
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

        console.print(table)

    def print_note(self) -> None:
        """Print the note to the console."""
        console.print(self.file_content)

    def rename_tag(self, tag_1: str, tag_2: str) -> bool:
        """Rename an inline tag. Updates the Metadata object and the text of the note.

        Args:
            tag_1 (str): Tag to rename.
            tag_2 (str): New tag name.

        Returns:
            bool: Whether the tag was renamed.
        """
        if tag_1 in self.tags.list:
            self.sub(
                rf"#{tag_1}([ \|,;:\*\(\)\[\]\\\.\n#&])",
                rf"#{tag_2}\1",
                is_regex=True,
            )
            self.tags.rename(tag_1, tag_2)
            return True
        return False

    def rename_metadata(self, key: str, value_1: str, value_2: str = None) -> bool:
        """Rename a key or key-value pair in the note's InlineMetadata and Frontmatter objects and the content of the note.

        If no value is provided, will rename the entire specified key.

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
                self.write_frontmatter()
                changed_value = True
            if self.inline_metadata.rename(key, value_1):
                self.write_inline_metadata_change(key, value_1)
                changed_value = True
        else:
            if self.frontmatter.rename(key, value_1, value_2):
                self.write_frontmatter()
                changed_value = True
            if self.inline_metadata.rename(key, value_1, value_2):
                self.write_inline_metadata_change(key, value_1, value_2)
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

    def transpose_metadata(  # noqa: C901, PLR0912, PLR0911
        self,
        begin: MetadataType,
        end: MetadataType,
        key: str = None,
        value: str | list[str] = None,
        location: InsertLocation = InsertLocation.BOTTOM,
    ) -> bool:
        """Move metadata from one metadata object to another. i.e. Frontmatter to InlineMetadata or vice versa.

        If no key is specified, will transpose all metadata. If a key is specified, but no value, the entire key will be transposed. if a specific value is specified, just that value will be transposed.

        Args:
            begin (MetadataType): The type of metadata to transpose from.
            end (MetadataType): The type of metadata to transpose to.
            key (str, optional): The key to transpose. Defaults to None.
            location (InsertLocation, optional): Where to insert the metadata. Defaults to InsertLocation.BOTTOM.
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

                    return bool(has_changes)

        if begin == MetadataType.TAGS:
            # TODO: Implement transposing to and from tags
            pass

        return False

    def write_delete_inline_metadata(
        self, key: str = None, value: str = None, is_regex: bool = False
    ) -> bool:
        """For a given inline metadata key and/or key-value pair, delete it from the text of the note. If no key is provided, will delete all inline metadata from the text of the note.

        IMPORTANT: This method makes no changes to the InlineMetadata object.

        Args:
            is_regex (bool, optional): Whether the key is a regex pattern or plain text. Defaults to False.
            key (str, optional): Key to delete.
            value (str, optional): Value to delete.

        Returns:
            bool: Whether the note was updated.
        """
        if self.inline_metadata.dict != {}:
            if key is None:
                for _k, _v in self.inline_metadata.dict.items():
                    for _value in _v:
                        _k = re.escape(_k)
                        _value = re.escape(_value)
                        self.sub(rf"\[?{_k}:: ?\[?\[?{_value}\]?\]?", "", is_regex=True)
                return True

            for _k, _v in self.inline_metadata.dict.items():
                if (is_regex and re.search(key, _k)) or (not is_regex and key == _k):
                    for _value in _v:
                        if value is None:
                            _k = re.escape(_k)
                            _value = re.escape(_value)
                            self.sub(rf"\[?{_k}:: \[?\[?{_value}\]?\]?", "", is_regex=True)
                        elif (is_regex and re.search(value, _value)) or (
                            not is_regex and value == _value
                        ):
                            _k = re.escape(_k)
                            _value = re.escape(_value)
                            self.sub(rf"\[?({_k}::) ?\[?\[?{_value}\]?\]?", r"\1", is_regex=True)
                    return True
        return False

    def write_frontmatter(self, sort_keys: bool = False) -> bool:
        """Replace the frontmatter in the note with the current Frontmatter object.  If the Frontmatter object is empty, will delete the frontmatter from the note.

        Returns:
            bool: Whether the note was updated.
        """
        try:
            current_frontmatter = PATTERNS.frontmatter_block.search(self.file_content).group(
                "frontmatter"
            )
        except AttributeError:
            current_frontmatter = None

        if current_frontmatter is None and self.frontmatter.dict == {}:
            return False

        new_frontmatter = self.frontmatter.to_yaml(sort_keys=sort_keys)
        new_frontmatter = "" if self.frontmatter.dict == {} else f"---\n{new_frontmatter}---\n"

        if current_frontmatter is None:
            self.file_content = new_frontmatter + self.file_content
            return True

        current_frontmatter = f"{re.escape(current_frontmatter)}\n?"
        self.sub(current_frontmatter, new_frontmatter, is_regex=True)
        return True

    def write_all_inline_metadata(
        self,
        location: InsertLocation,
    ) -> bool:
        """Write all metadata found in the InlineMetadata object to the note at a specified insert location.

        Args:
            location (InsertLocation): Where to insert the metadata.

        Returns:
            bool: Whether the note was updated.
        """
        if self.inline_metadata.dict != {}:
            string = ""
            for k, v in sorted(self.inline_metadata.dict.items()):
                for value in v:
                    string += f"{k}:: {value}\n"

            if self.write_string(new_string=string, location=location, allow_multiple=True):
                return True

        return False

    def write_inline_metadata_change(self, key: str, value_1: str, value_2: str = None) -> None:
        """Write changes to a specific inline metadata key or value.

        Args:
            key (str): Key to rename.
            value_1 (str): Value to replace OR new key name (if value_2 is None).
            value_2 (str, optional): New value.

        """
        found_inline_metadata = inline_metadata_from_string(self.file_content)

        for _k, _v in found_inline_metadata:
            if re.search(key, _k):
                if value_2 is None:
                    if re.search(rf"{key}[^\\w\\d_-]+", _k):
                        key_text = re.split(r"[^\\w\\d_-]+$", _k)[0]
                        key_markdown = re.split(r"^[\\w\\d_-]+", _k)[1]
                        self.sub(
                            rf"{key_text}{key_markdown}::",
                            rf"{value_1}{key_markdown}::",
                        )
                    else:
                        self.sub(f"{_k}::", f"{value_1}::")
                elif re.search(key, _k) and re.search(value_1, _v):
                    _k = re.escape(_k)
                    _v = re.escape(_v)
                    self.sub(f"{_k}:: ?{_v}", f"{_k}:: {value_2}", is_regex=True)

    def write_string(
        self,
        new_string: str,
        location: InsertLocation,
        allow_multiple: bool = False,
    ) -> bool:
        """Insert a string into the note at a requested location.

        Args:
            new_string (str): String to insert at the top of the note.
            allow_multiple (bool): Whether to allow inserting the string if it already exists in the note.
            location (InsertLocation): Location to insert the string.

        Returns:
            bool: Whether the note was updated.
        """
        if not allow_multiple and len(re.findall(re.escape(new_string), self.file_content)) > 0:
            return False

        match location:
            case InsertLocation.BOTTOM:
                self.file_content += f"\n{new_string}"
                return True
            case InsertLocation.TOP:
                try:
                    top = PATTERNS.frontmatter_block.search(self.file_content).group("frontmatter")
                except AttributeError:
                    top = ""

                if not top:
                    self.file_content = f"{new_string}\n{self.file_content}"
                    return True

                new_string = f"{top}\n{new_string}"
                top = re.escape(top)
                self.sub(top, new_string, is_regex=True)
                return True
            case InsertLocation.AFTER_TITLE:
                try:
                    top = PATTERNS.top_with_header.search(self.file_content).group("top")
                except AttributeError:
                    top = ""

                if not top:
                    self.file_content = f"{new_string}\n{self.file_content}"
                    return True

                new_string = f"{top}\n{new_string}"
                top = re.escape(top)
                self.sub(top, new_string, is_regex=True)
                return True
            case _:  # pragma: no cover
                raise ValueError(f"Invalid location: {location}")
