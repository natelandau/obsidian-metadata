"""Shared utilities."""

from obsidian_frontmatter._utils import alerts
from obsidian_frontmatter._utils.alerts import LoggerManager
from obsidian_frontmatter._utils.config import Configuration, ask_for_vault
from obsidian_frontmatter._utils.utilities import docstring_parameter
from obsidian_frontmatter._utils.vault import Vault

__all__ = [
    "alerts",
    "ask_for_vault",
    "LoggerManager",
    "Configuration",
    "docstring_parameter",
    "Vault",
]
