# type: ignore
"""Test the questions class."""

from pathlib import Path

from obsidian_metadata._config import Config
from obsidian_metadata.models.questions import Questions
from obsidian_metadata.models.vault import Vault

VAULT_PATH = Path("tests/fixtures/test_vault")
CONFIG = Config(config_path="tests/fixtures/test_vault_config.toml", vault_path=VAULT_PATH)
VAULT_CONFIG = CONFIG.vaults[0]
VAULT = Vault(config=VAULT_CONFIG)


def test_validate_valid_dir() -> None:
    """Test vault validation."""
    questions = Questions(vault=VAULT)
    assert questions._validate_valid_dir("tests/") is True
    assert "Path is not a directory" in questions._validate_valid_dir("pyproject.toml")
    assert "Path does not exist" in questions._validate_valid_dir("tests/vault2")


def test_validate_valid_regex() -> None:
    """Test regex validation."""
    questions = Questions(vault=VAULT)
    assert questions._validate_valid_vault_regex(r".*\.md") is True
    assert "Invalid regex" in questions._validate_valid_vault_regex("[")
    assert "Regex does not match paths" in questions._validate_valid_vault_regex(r"\d\d\d\w\d")


def test_validate_key_exists() -> None:
    """Test key validation."""
    questions = Questions(vault=VAULT)
    assert "'test' does not exist" in questions._validate_key_exists("test")
    assert "Key cannot be empty" in questions._validate_key_exists("")
    assert questions._validate_key_exists("frontmatter_Key1") is True


def test_validate_new_key() -> None:
    """Test new key validation."""
    questions = Questions(vault=VAULT)
    assert "Key cannot contain spaces or special characters" in questions._validate_new_key(
        "new key"
    )
    assert "Key cannot contain spaces or special characters" in questions._validate_new_key(
        "new_key!"
    )
    assert "New key cannot be empty" in questions._validate_new_key("")
    assert questions._validate_new_key("new_key") is True


def test_validate_new_tag() -> None:
    """Test new tag validation."""
    questions = Questions(vault=VAULT)
    assert "New tag cannot be empty" in questions._validate_new_tag("")
    assert "Tag cannot contain spaces or special characters" in questions._validate_new_tag(
        "new tag"
    )
    assert questions._validate_new_tag("new_tag") is True


def test_validate_number() -> None:
    """Test number validation."""
    questions = Questions(vault=VAULT)
    assert "Must be an integer" in questions._validate_number("test")
    assert "Must be an integer" in questions._validate_number("1.1")
    assert questions._validate_number("1") is True


def test_validate_existing_tag() -> None:
    """Test existing tag validation."""
    questions = Questions(vault=VAULT)
    assert "Tag cannot be empty" in questions._validate_existing_tag("")
    assert "'test' does not exist" in questions._validate_existing_tag("test")
    assert questions._validate_existing_tag("shared_tag") is True


def test_validate_key_exists_regex() -> None:
    """Test key exists regex validation."""
    questions = Questions(vault=VAULT)
    assert "'test' does not exist" in questions._validate_key_exists_regex("test")
    assert "Key cannot be empty" in questions._validate_key_exists_regex("")
    assert "Invalid regex" in questions._validate_key_exists_regex("[")
    assert questions._validate_key_exists_regex(r"\w+_Key\d") is True


def test_validate_value() -> None:
    """Test value validation."""
    questions = Questions(vault=VAULT)

    assert questions._validate_value("test") is True
    questions2 = Questions(vault=VAULT, key="frontmatter_Key1")
    assert questions2._validate_value("test") == "frontmatter_Key1:test does not exist"
    assert questions2._validate_value("author name") is True


def test_validate_value_exists_regex() -> None:
    """Test value exists regex validation."""
    questions2 = Questions(vault=VAULT, key="frontmatter_Key1")
    assert "Invalid regex" in questions2._validate_value_exists_regex("[")
    assert "Regex cannot be empty" in questions2._validate_value_exists_regex("")
    assert (
        questions2._validate_value_exists_regex(r"\d\d\d\w\d")
        == r"No values in frontmatter_Key1 match regex: \d\d\d\w\d"
    )
    assert questions2._validate_value_exists_regex(r"^author \w+") is True


def test_validate_new_value() -> None:
    """Test new value validation."""
    questions = Questions(vault=VAULT, key="frontmatter_Key1")
    assert questions._validate_new_value("not_exists") is True
    assert "Value cannot be empty" in questions._validate_new_value("")
    assert (
        questions._validate_new_value("author name")
        == "frontmatter_Key1:author name already exists"
    )
