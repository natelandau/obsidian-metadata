# type: ignore
"""Test the questions class."""


from obsidian_metadata._utils import Questions


def test_vault_validation():
    """Test vault validation."""
    assert Questions._validate_vault("tests/") is True
    assert "Path is not a directory" in Questions._validate_vault("pyproject.toml")
    assert "Path does not exist" in Questions._validate_vault("tests/vault2")
