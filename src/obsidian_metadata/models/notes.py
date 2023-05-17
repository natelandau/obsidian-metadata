"""Representation of a not in the vault."""


import copy
import difflib
import re
from pathlib import Path

import rich.repr
import typer
from charset_normalizer import from_path
from rich.table import Table
from ruamel.yaml import YAML

from obsidian_metadata._utils import alerts
from obsidian_metadata._utils.alerts import logger as log
from obsidian_metadata._utils.console import console_no_markup
from obsidian_metadata.models import (
    InlineField,
    InsertLocation,
    MetadataType,
    Wrapping,
    dict_to_yaml,
)
from obsidian_metadata.models.exceptions import (
    FrontmatterError,
    InlineMetadataError,
    InlineTagError,
)
from obsidian_metadata.models.parsers import Parser

P = Parser()


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
            result = from_path(self.note_path).best()
            self.encoding: str = result.encoding
            self.file_content: str = str(result)
            self.original_file_content: str = str(result)
        except FileNotFoundError as e:
            alerts.error(f"Note {self.note_path} not found. Exiting")
            raise typer.Exit(code=1) from e
        except UnicodeDecodeError as e:
            alerts.error(
                f"Error decoding note {self.note_path}.\nDetected encoding: {self.encoding}\nExiting"
            )
            raise typer.Exit(code=1) from e

        try:
            self.metadata = self._grab_all_metadata(self.file_content)
            self.original_metadata = copy.deepcopy(self.metadata)
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
        yield "dry_run", self.dry_run
        yield "encoding", self.encoding
        yield "note_path", self.note_path

    def _grab_all_metadata(self, text: str) -> list[InlineField]:  # noqa: C901
        """Grab all metadata from the note and create list of InlineField objects."""
        all_metadata = []  # List of all metadata to be returned

        # First parse the frontmatter
        frontmatter_block = P.return_frontmatter(text, data_only=True)
        if frontmatter_block:
            yaml = YAML(typ="safe")
            yaml.allow_unicode = False
            try:
                frontmatter: dict = yaml.load(frontmatter_block)
            except Exception as e:  # noqa: BLE001
                raise FrontmatterError(e) from e

            for key, value in frontmatter.items():
                if isinstance(value, dict):
                    raise FrontmatterError(
                        f"Nested frontmatter is not supported.\nKey: {key}\n Value: {value}"
                    )
                if isinstance(value, list):
                    for item in value:
                        all_metadata.append(
                            InlineField(
                                meta_type=MetadataType.FRONTMATTER,
                                key=key,
                                value=str(item),
                            )
                        )
                else:
                    all_metadata.append(
                        InlineField(
                            meta_type=MetadataType.FRONTMATTER,
                            key=key,
                            value=str(value),
                        )
                    )

        # strip frontmatter and code blocks from the text and parse inline metadata
        text = P.strip_frontmatter(P.strip_code_blocks(text))
        for _line in text.splitlines():
            inline_metadata = P.return_inline_metadata(_line)
            if inline_metadata:
                # for item in inline_metadata:
                for key, value, wrapper in inline_metadata:
                    all_metadata.append(
                        InlineField(
                            meta_type=MetadataType.INLINE,
                            key=key,
                            value=value,
                            wrapping=wrapper,
                        )
                    )

        # Then strip all inline code and parse tags
        text = P.strip_inline_code(text)
        for _line in text.splitlines():
            tags = [
                InlineField(meta_type=MetadataType.TAGS, key=None, value=tag.lstrip("#"))
                for tag in P.return_tags(_line)
            ]
            all_metadata.extend(tags)

        return list(set(all_metadata))

    def _delete_inline_metadata(self, source: InlineField) -> bool:
        """Delete a specified inline metadata field from the note.

        Args:
            source (InlineField): InlineField object to delete.

        Returns:
            bool: True if successful, False if not.
        """
        if source.meta_type != MetadataType.INLINE:
            log.error("Must provide inline metadata to _sub_inline_metadata")
            raise typer.Exit(code=1)

        remove_string = f"{re.escape(source.key)}::{re.escape(source.value)}"
        if source.wrapping == Wrapping.NONE:
            return self.sub(
                rf"( *> *){remove_string}\s+|{remove_string}(\s+|$)",
                "",
                is_regex=True,
            )

        if source.wrapping == Wrapping.PARENS:
            return self.sub(
                rf" ?\({remove_string}\)",
                "",
                is_regex=True,
            )

        if source.wrapping == Wrapping.BRACKETS:
            return self.sub(
                rf" ?\[{remove_string}\]",
                "",
                is_regex=True,
            )

        return False

    def _edit_inline_metadata(
        self, source: InlineField, new_key: str, new_value: str = None
    ) -> InlineField:
        """Edit an inline metadata field. Takes an InlineField object and a new key and/or value and edits the inline metadata in the object and note accordingly.

        Args:
            source (InlineField): InlineField object to edit.
            new_key (str, optional): New key to use.
            new_value (str, optional): New value to use.

        Returns:
            InlineField: New InlineField object.
        """
        if source.meta_type != MetadataType.INLINE:
            log.error("Must provide inline metadata to _sub_inline_metadata")
            raise typer.Exit(code=1)

        new_inline_field = InlineField(
            meta_type=MetadataType.INLINE,
            key=f"{source.key_open}{new_key}{source.key_close}",
            value=new_value if new_value else source.value,
            wrapping=source.wrapping,
            is_changed=True,
        )

        if source.wrapping == Wrapping.NONE:
            self.sub(
                f"{source.key}::{source.value}",
                f"{new_inline_field.key}:: {new_inline_field.value.lstrip()}",
            )

        if source.wrapping == Wrapping.PARENS:
            self.sub(
                pattern=f"({source.key}::{source.value})",
                replacement=f"({new_inline_field.key}:: {new_inline_field.value.lstrip()})",
            )
        if source.wrapping == Wrapping.BRACKETS:
            self.sub(
                pattern=f"[{source.key}::{source.value}]",
                replacement=f"[{new_inline_field.key}:: {new_inline_field.value.lstrip()}]",
            )

        self.metadata.remove(source)
        self.metadata.append(new_inline_field)
        return new_inline_field

    def _find_matching_fields(
        self, meta_type: MetadataType, key: str = None, value: str = None, is_regex: bool = False
    ) -> list[InlineField]:
        """Create a list of InlineField objects matching the specified key and/or value.

        - When key and value are None, all fields of the specified type are returned.
        - When value is None, all fields of the specified type with the specified key are returned.
        - When key is None, all fields of the specified type with the specified value are returned.


        Args:
            meta_type (MetadataType): Type of metadata to search for.
            key (str, optional): Key to match.
            value (str, optional): Value to match.
            is_regex (bool, optional): Whether to treat the key and value as regex.

        Returns:
            list[InlineField]: List of matching InlineField objects.

        # TODO: Add support for fields where value is a [[link]]
        """
        if meta_type == MetadataType.TAGS and value:
            value = value.lstrip("#")

        if not is_regex:
            key = f"^{re.escape(key)}$" if key else None
            value = f"^{re.escape(value)}$" if value else None

        matching_inline_fields = []
        if key is None and value is None:
            matching_inline_fields.extend([x for x in self.metadata if x.meta_type == meta_type])
        elif value is None:
            matching_inline_fields.extend(
                [
                    x
                    for x in self.metadata
                    if x.meta_type == meta_type and re.search(key, x.clean_key)
                ]
            )
        elif key is None:
            matching_inline_fields.extend(
                [
                    x
                    for x in self.metadata
                    if x.meta_type == meta_type and re.search(value, x.normalized_value)
                ]
            )
        else:
            matching_inline_fields.extend(
                [
                    x
                    for x in self.metadata
                    if x.meta_type == meta_type
                    and re.search(key, x.clean_key)
                    and re.search(value, x.normalized_value)
                ]
            )

        return matching_inline_fields

    def _update_inline_metadata(
        self, source: InlineField, new_key: str = None, new_value: str = None
    ) -> bool:
        """Update an inline metadata field. Takes an InlineField object and a new key and/or value and updates the inline metadata in the object and note accordingly.

        Args:
            source (InlineField): InlineField object to update.
            new_key (str, optional): New key to use.
            new_value (str, optional): New value to use.

        Returns:
            bool: True if successful, False if not.

        # TODO: Add support for fields where value is a [[link]]
        """
        if source.meta_type != MetadataType.INLINE:
            log.error("Must provide inline metadata to _sub_inline_metadata")
            raise typer.Exit(code=1)

        if new_key is None and new_value is None:
            log.error("Must provide new key or value to _sub_inline_metadata")
            raise typer.Exit(code=1)

        original_key = re.escape(source.key)
        original_value = re.escape(source.value)

        source.key = f"{source.key_open}{new_key}{source.key_close}" if new_key else source.key
        source.clean_key = (
            f"{source.key_open}{new_key}{source.key_close}" if new_key else source.clean_key
        )
        source.normalized_key = (
            new_key.replace(" ", "-").lower() if new_key else source.normalized_key
        )
        source.value = f" {new_value.lstrip()}" if new_value else source.value
        source.normalized_value = new_value if new_value else source.normalized_value
        source.is_changed = True

        match source.wrapping:
            case Wrapping.NONE:
                return self.sub(
                    f"{original_key}:: ?{original_value}",
                    f"{source.key}::{source.value}",
                    is_regex=True,
                )
            case Wrapping.PARENS:
                return self.sub(
                    rf"\({original_key}:: ?{original_value}\)",
                    f"({source.key}::{source.value})",
                    is_regex=True,
                )
            case Wrapping.BRACKETS:
                return self.sub(
                    rf"\[{original_key}::{original_value}\]",
                    f"[{source.key}::{source.value}]",
                    is_regex=True,
                )

    def add_metadata(
        self,
        meta_type: MetadataType,
        added_key: str = None,
        added_value: str = None,
        location: InsertLocation = None,
    ) -> bool:
        """Add metadata to the note if it does not already exist. This method adds specified metadata to the appropriate MetadataType object AND writes the new metadata to the note's file.

        Args:
            added_key (str, optional): Key to add
            added_value (str, optional): Value to add.
            location (InsertLocation, optional): Location to add inline metadata and tags.
            meta_type (MetadataType): Area to add metadata to.

        Returns:
            bool: Whether the metadata was added.
        """
        match meta_type:
            case MetadataType.FRONTMATTER | MetadataType.INLINE:
                if added_key is None or re.match(r"^\s*$", added_key):
                    log.error("A valid key must be specified.")
                    raise typer.Exit(code=1)
                if self.contains_metadata(meta_type, added_key, added_value):
                    return False

                new_meta = InlineField(
                    meta_type=meta_type, key=added_key, value=added_value, is_changed=True
                )

                match meta_type:
                    case MetadataType.FRONTMATTER:
                        self.metadata.append(new_meta)
                        self.write_frontmatter()
                        return True
                    case MetadataType.INLINE:
                        self.metadata.append(new_meta)
                        self.write_string(
                            f"{added_key}:: {added_value}", location
                        ) if added_value else self.write_string(f"{added_key}::", location)
                        return True

            case MetadataType.TAGS:
                if added_value is None or re.match(r"^\s*$", added_value):
                    log.error("A tag must be specified to add.")
                    raise typer.Exit(code=1)

                new_tags = P.return_tags(f"#{added_value.lstrip('#')}")

                if len(new_tags) == 0:
                    log.error("A valid tag must be specified.")
                    raise typer.Exit(code=1)

                tag_added = False
                for tag in new_tags:
                    if self.contains_metadata(meta_type, None, tag.lstrip("#")):
                        continue

                    new_tag = InlineField(
                        meta_type=MetadataType.TAGS,
                        key=None,
                        value=tag.lstrip("#"),
                        is_changed=True,
                    )

                    tag_added = True
                    self.metadata.append(new_tag)
                    self.write_string(f"#{new_tag.value}", location)

                return tag_added

            case _:
                log.error(
                    f"Invalid metadata type '{meta_type}' was provided to note.add_metadata()."
                )
                raise typer.Exit(code=1)

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
            log.trace(f"Writing note {p} to disk")
            p.write_text(self.file_content)
        except FileNotFoundError as e:
            alerts.error(f"Note {p} not found. Exiting")
            raise typer.Exit(code=1) from e

    def contains_metadata(  # noqa: PLR0911
        self,
        meta_type: MetadataType,
        search_key: str,
        search_value: str = None,
        is_regex: bool = False,
    ) -> bool:
        """Check if a note contains the specified metadata.

        Args:
            meta_type (MetadataType): Metadata type to check for.
            search_key (str): Key to check for.
            search_value (str, optional): Value to check for.
            is_regex (bool, optional): Whether to use regex to match the key/value.

        Returns:
            bool: Whether the note contains the metadata.
        """
        if meta_type == MetadataType.ALL:
            return self.contains_metadata(
                MetadataType.META, search_key, search_value, is_regex
            ) or self.contains_metadata(MetadataType.TAGS, search_key, search_value, is_regex)

        if meta_type == MetadataType.META:
            return self.contains_metadata(
                MetadataType.FRONTMATTER, search_key, search_value, is_regex
            ) or self.contains_metadata(MetadataType.INLINE, search_key, search_value, is_regex)

        if meta_type == MetadataType.FRONTMATTER or meta_type == MetadataType.INLINE:
            if search_key is None or re.match(r"^\s*$", search_key):
                return False

            search_key = re.escape(search_key) if not is_regex else search_key

            if search_value is None:
                return any(
                    re.search(search_key, item.clean_key)
                    for item in self.metadata
                    if item.meta_type == meta_type
                )

            search_value = re.escape(search_value) if not is_regex else search_value

            return any(
                re.search(search_value, str(item.normalized_value))
                for item in self.metadata
                if item.meta_type == meta_type and re.search(search_key, str(item.clean_key))
            )

        if meta_type == MetadataType.TAGS:
            if search_key is not None or search_value is None or re.match(r"^\s*$", search_value):
                return False

            search_value = search_value.lstrip("#")
            search_value = re.escape(search_value) if not is_regex else search_value

            return any(
                re.search(search_value, str(item.normalized_value))
                for item in self.metadata
                if item.meta_type == meta_type
            )

        return False

    def delete_metadata(  # noqa: PLR0912, C901
        self, meta_type: MetadataType, key: str = None, value: str = None, is_regex: bool = False
    ) -> bool:
        """Delete specified metadata from the note. Removes the metadata from the note and the metadata list. When a key is provided without a value, all values associated with that key are deleted.

        Args:
            meta_type (MetadataType): Metadata type to delete.
            key (str, optional): Key to delete.
            value (str, optional): Value to delete.
            is_regex (bool, optional): Whether to use regex to match the key/value.

        Returns:
            bool: Whether metadata was deleted.
        """
        removed_frontmatter = False
        meta_to_delete = []
        if meta_type == MetadataType.META:
            if key is None or re.match(r"^\s*$", key):
                log.error("A valid key must be specified.")
                raise typer.Exit(code=1)

            meta_to_delete.extend(
                self._find_matching_fields(MetadataType.FRONTMATTER, key, value, is_regex)
            )
            meta_to_delete.extend(
                self._find_matching_fields(MetadataType.INLINE, key, value, is_regex)
            )

        elif meta_type == MetadataType.ALL:
            if key is not None and not re.match(r"^\s*$", key):
                meta_to_delete.extend(
                    self._find_matching_fields(MetadataType.FRONTMATTER, key, value, is_regex)
                )
                meta_to_delete.extend(
                    self._find_matching_fields(MetadataType.INLINE, key, value, is_regex)
                )

            if key is None and value is not None and not re.match(r"^\s*$", value):
                meta_to_delete.extend(
                    self._find_matching_fields(MetadataType.TAGS, key, value, is_regex)
                )

        elif meta_type == MetadataType.FRONTMATTER or meta_type == MetadataType.INLINE:
            if key is None or re.match(r"^\s*$", key):
                log.error("A valid key must be specified.")
                raise typer.Exit(code=1)

            meta_to_delete.extend(self._find_matching_fields(meta_type, key, value, is_regex))

        elif meta_type == MetadataType.TAGS:
            if key is not None or (value is None or re.match(r"^\s*$", value)):
                log.error("A valid tag must be specified.")
                raise typer.Exit(code=1)

            meta_to_delete.extend(self._find_matching_fields(meta_type, key, value, is_regex))

        if len(meta_to_delete) == 0:
            return False

        for field in meta_to_delete:
            match field.meta_type:
                case MetadataType.FRONTMATTER:
                    removed_frontmatter = True
                    self.metadata.remove(field)

                case MetadataType.INLINE:
                    if self._delete_inline_metadata(field):
                        self.metadata.remove(field)
                    else:
                        log.warning(
                            f"Failed to delete {field.clean_key} from {self.note_path.name}"
                        )

                case MetadataType.TAGS:
                    if self.sub(
                        f"#{re.escape(field.value)}([{P.chars_not_in_tags}])", "\1", is_regex=True
                    ):
                        self.metadata.remove(field)
                    else:
                        log.warning(f"Failed to delete #{field.value} from {self.note_path.name}")
                        return False

        if removed_frontmatter:
            self.write_frontmatter()

        return True

    def delete_all_metadata(self) -> bool:
        """Delete all metadata from the note. Removes all frontmatter and inline metadata and tags from the body of the note and from the associated InlineField objects.

        Returns:
            bool: Whether metadata was deleted.
        """
        deleted_frontmatter = False
        meta_to_delete = copy.deepcopy(self.metadata)

        for field in meta_to_delete:
            if field.meta_type == MetadataType.FRONTMATTER:
                deleted_frontmatter = True
                self.metadata.remove(field)
            else:
                self.delete_metadata(
                    field.meta_type, field.clean_key, field.normalized_value, is_regex=False
                )

        if deleted_frontmatter:
            self.write_frontmatter()

        if len(self.metadata) > 0:
            return False

        return True

    def has_changes(self) -> bool:
        """Check if the note has been updated.

        Returns:
            bool: Whether the note has been updated.
        """
        if (
            self.original_metadata != self.metadata
            or self.original_file_content != self.file_content
        ):
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

        console_no_markup.print(table)

    def print_note(self) -> None:
        """Print the note to the console."""
        console_no_markup.print(self.file_content)

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
        # TODO: Add support for TAGS
        fields_to_rename = []
        if value_2 is None:
            fields_to_rename.extend(
                self._find_matching_fields(meta_type=MetadataType.INLINE, key=key)
            )
            fields_to_rename.extend(
                self._find_matching_fields(meta_type=MetadataType.FRONTMATTER, key=key)
            )
        else:
            fields_to_rename.extend(
                self._find_matching_fields(meta_type=MetadataType.INLINE, key=key, value=value_1)
            )
            fields_to_rename.extend(
                self._find_matching_fields(
                    meta_type=MetadataType.FRONTMATTER, key=key, value=value_1
                )
            )

        if len(fields_to_rename) == 0:
            return False

        frontmatter_is_changed = False
        for field in fields_to_rename:
            if field.meta_type == MetadataType.FRONTMATTER:
                frontmatter_is_changed = True
                field.is_changed = True
                if value_2 is None:
                    field.clean_key = value_1
                    field.key = value_1
                    field.normalized_key = value_1.replace(" ", "-").lower()
                else:
                    field.value = value_2
                    field.normalized_value = value_2.strip()

            if field.meta_type == MetadataType.INLINE:
                field.is_changed = True
                if value_2 is None:
                    self._update_inline_metadata(field, new_key=value_1)
                else:
                    self._update_inline_metadata(field, new_value=value_2)

        if frontmatter_is_changed:
            self.write_frontmatter()

        return True

    def rename_tag(self, old_tag: str, new_tag: str) -> bool:
        """Rename a tag in the note's body and tags.

        Args:
            old_tag (str): Tag to rename.
            new_tag (str): New tag name.

        Returns:
            bool: Whether the note was updated.
        """
        old_tag = old_tag.lstrip("#").strip()
        new_tag = new_tag.lstrip("#").strip()
        fields_to_rename = [
            x for x in self.metadata if x.meta_type == MetadataType.TAGS and x.value == old_tag
        ]

        if len(fields_to_rename) == 0:
            return False

        for field in fields_to_rename:
            field.is_changed = True
            self.sub(rf"#{re.escape(field.value)}", f"#{new_tag}", is_regex=True)
            field.value = new_tag
            field.normalized_value = new_tag

        return True

    def sub(self, pattern: str, replacement: str, is_regex: bool = False) -> bool:
        """Substitutes text within the note.

        Args:
            pattern (str): The pattern to replace (plain text or regular expression).
            replacement (str): What to replace the pattern with.
            is_regex (bool): Whether the pattern is a regex pattern or plain text.

        Returns:
            bool: Whether text was substituted.
        """
        if not is_regex:
            pattern = re.escape(pattern)

        self.file_content, num_subs = re.subn(pattern, replacement, self.file_content, re.MULTILINE)

        return num_subs > 0

    def transpose_metadata(
        self,
        begin: MetadataType,
        end: MetadataType,
        key: str = None,
        value: str = None,
        location: InsertLocation = InsertLocation.BOTTOM,
    ) -> bool:
        """Move metadata from one metadata object to another. i.e. Frontmatter to InlineMetadata or vice versa.

        If the beginning and end type of the metadata are the same, will move the metadata within the same type to the specified location.

        If no key is specified, will transpose all metadata. If a key is specified, but no value, the key and all associated values will be transposed. If a specific value is specified, just that value will be transposed.

        Args:
            begin (MetadataType): The type of metadata to transpose from.
            end (MetadataType): The type of metadata to transpose to.
            key (str, optional): The key to transpose. Defaults to None.
            location (InsertLocation, optional): Where to insert the metadata. Defaults to InsertLocation.BOTTOM.
            value (str, optional): The value to transpose. Defaults to None.

        Returns:
            bool: Whether the note was updated.
        """
        if begin == MetadataType.FRONTMATTER and end == MetadataType.FRONTMATTER:
            return False

        if begin == MetadataType.TAGS or end == MetadataType.TAGS:
            # TODO: Implement transposing to and from tags
            return False

        if key is None:  # When no key is provided, transpose all metadata
            meta_to_transpose = [x for x in self.metadata if x.meta_type == begin]
        else:
            meta_to_transpose = self._find_matching_fields(begin, key, value)

        if len(meta_to_transpose) == 0:
            return False

        for field in sorted(
            meta_to_transpose,
            reverse=location != InsertLocation.BOTTOM,
            key=lambda x: (x.clean_key, x.normalized_value),
        ):
            self.delete_metadata(begin, field.clean_key, field.normalized_value)
            self.add_metadata(
                end,
                field.clean_key,
                field.normalized_value if field.normalized_value != "-" else "",
                location,
            )

        return True

    def write_frontmatter(self, sort_keys: bool = False) -> bool:
        """Replace the frontmatter in the note with the current metadata. If not frontmatter exists the entire block will be removed from the note.

        Args:
            sort_keys (bool, optional): Whether to sort the keys in the frontmatter alphabetically.

        Returns:
            bool: Whether frontmatter was written to the note.
        """
        # First we find the current frontmatter block in the note.
        try:
            current_frontmatter = P.return_frontmatter(self.file_content, data_only=False)
        except AttributeError:
            current_frontmatter = None

        frontmatter_objects_as_dict: dict[str, list[str]] = {}
        for k, v in [
            (x.key, x.value) for x in self.metadata if x.meta_type == MetadataType.FRONTMATTER
        ]:
            frontmatter_objects_as_dict.setdefault(k, []).append(v)

        # Make no changes when there are no changes to make:
        if current_frontmatter is None and len(frontmatter_objects_as_dict) == 0:
            return False

        # TODO: Make no changes if frontmatter in content is the same as all frontmatter metadata objects

        # Update frontmatter in the note
        new_frontmatter = dict_to_yaml(frontmatter_objects_as_dict, sort_keys=sort_keys)

        new_frontmatter = "" if not new_frontmatter else f"---\n{new_frontmatter}---\n"

        if current_frontmatter is None:
            self.file_content = new_frontmatter + self.file_content
            return True

        current_frontmatter = f"{re.escape(current_frontmatter)}\n?"
        self.sub(current_frontmatter, new_frontmatter, is_regex=True)
        return True

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
                frontmatter = P.return_frontmatter(self.file_content)

                if frontmatter is None:
                    self.file_content = f"{new_string}\n{self.file_content}"
                    return True

                new_string = f"{frontmatter}\n{new_string}"
                ecaped_frontmatter = re.escape(frontmatter)
                self.sub(ecaped_frontmatter, new_string, is_regex=True)
                return True

            case InsertLocation.AFTER_TITLE:
                top = P.return_top_with_header(self.file_content)

                if top is None:
                    self.file_content = f"{new_string}\n{self.file_content}"
                    return True

                new_string = f"{top.strip()}\n{new_string}\n"
                top = re.escape(top)
                self.sub(top, new_string, is_regex=True)
                return True
            case _:  # pragma: no cover
                raise ValueError(f"Invalid location: {location}")
