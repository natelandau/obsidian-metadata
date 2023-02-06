[![PyPI version](https://badge.fury.io/py/obsidian-metadata.svg)](https://badge.fury.io/py/obsidian-metadata) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/obsidian-metadata) [![Python Code Checker](https://github.com/natelandau/obsidian-metadata/actions/workflows/automated-tests.yml/badge.svg)](https://github.com/natelandau/obsidian-metadata/actions/workflows/automated-tests.yml) [![codecov](https://codecov.io/gh/natelandau/obsidian-metadata/branch/main/graph/badge.svg?token=3F2R43SSX4)](https://codecov.io/gh/natelandau/obsidian-metadata)

# obsidian-metadata

A script to make batch updates to metadata in an Obsidian vault. No changes are
made to the Vault until they are explicitly committed.

[![asciicast](https://asciinema.org/a/555789.svg)](https://asciinema.org/a/555789)

## Important Disclaimer

**It is strongly recommended that you back up your vault prior to committing changes.** This script makes changes directly to the markdown files in your vault. Once the changes are committed, there is no ability to recreate the original information unless you have a backup. Follow the instructions in the script to create a backup of your vault if needed. The author of this script is not responsible for any data loss that may occur. Use at your own risk.

## Install

Requires Python v3.10 or above.

```bash
pip install obsidian-metadata
```

## Usage

### CLI Commands

-   `--config-file`: Specify a custom configuration file location
-   `--dry-run`: Make no destructive changes
-   `--export-csv`: Specify a path and create a CSV export of all metadata
-   `--export-json`: Specify a path and create a JSON export of all metadata
-   `--help`: Shows interactive help and exits
-   `--log-file`: Specify a log file location
-   `--log-to-file`: Will log to a file
-   `--vault-path`: Specify a path to an Obsidian Vault
-   `--verbose`: Set verbosity level (0=WARN, 1=INFO, 2=DEBUG, 3=TRACE)
-   `--version`: Prints the version number and exits

### Running the script

Once installed, run `obsidian-metadata` in your terminal to enter an interactive menu of sub-commands.

**Vault Actions**

-   Backup: Create a backup of the vault.
-   Delete Backup: Delete a backup of the vault.

**Inspect Metadata**

-   **View all metadata in the vault**
-   View all **frontmatter**
-   View all **inline metadata**
-   View all **inline tags**
-   **Export all metadata to CSV or JSON file**

**Filter Notes in Scope**: Limit the scope of notes to be processed with one or more filters.

-   **Path filter (regex)**: Limit scope based on the path or filename
-   **Metadata filter**: Limit scope based on a key or key/value pair
-   **Tag filter**: Limit scope based on an in-text tag
-   **List and clear filters**: List all current filters and clear one or all
-   **List notes in scope**: List notes that will be processed.

**Add Metadata**: Add new metadata to your vault.

-   **Add new metadata to the frontmatter**
-   **Add new inline metadata** - Set `insert_location` in the config to control where the new metadata is inserted. (Default: Bottom)
-   **Add new inline tag** - Set `insert_location` in the config to control where the new tag is inserted. (Default: Bottom)

**Rename Metadata**: Rename either a key and all associated values, a specific value within a key. or an in-text tag.

-   **Rename a key**
-   **Rename a value**
-   **Rename an inline tag**

**Delete Metadata**: Delete either a key and all associated values, or a specific value.

-   **Delete a key and associated values**
-   **Delete a value from a key**
-   **Delete an inline tag**

**Transpose Metadata**: Move metadata from inline to frontmatter or the reverse.

-   **Transpose all metadata** - Moves all frontmatter to inline metadata, or the reverse
-   **Transpose key** - Transposes a specific key and all it's values
-   **Transpose value**- Transpose a specific key:value pair

**Review Changes**: Prior to committing changes, review all changes that will be made.

-   **View a diff of the changes** that will be made

**Commit Changes**: Write the changes to disk. This step is not undoable.

-   **Commit changes to the vault**

### Configuration

`obsidian-metadata` requires a configuration file at `~/.obsidian_metadata.toml`. On first run, this file will be created. You can specify a new location for the configuration file with the `--config-file` option.

To add additional vaults, copy the default section and add the appropriate information. The script will prompt you to select a vault if multiple exist in the configuration file

Below is an example with two vaults.

```toml
["Vault One"] # Name of the vault.

    # Path to your obsidian vault
    path = "/path/to/vault"

    # Folders within the vault to ignore when indexing metadata
    exclude_paths = [".git", ".obsidian"]

    # Location to add metadata. One of:
    #    TOP:            Directly after frontmatter.
    #    AFTER_TITLE:    After a header following frontmatter.
    #    BOTTOM:         The bottom of the note
    insert_location = "BOTTOM"

["Vault Two"]
    path = "/path/to/second_vault"
    exclude_paths = [".git", ".obsidian", "daily_notes"]
    insert_location = "AFTER_TITLE"
```

To bypass the configuration file and specify a vault to use at runtime use the `--vault-path` option.

# Contributing

## Setup: Once per project

There are two ways to contribute to this project.

### 1. Containerized development

1. Clone this repository. `git clone https://github.com/natelandau/obsidian-metadata`
2. Open the repository in Visual Studio Code
3. Start the [Dev Container](https://code.visualstudio.com/docs/remote/containers). Run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Remote-Containers: Reopen in Container_.
4. Run `poetry env info -p` to find the PATH to the Python interpreter if needed by VSCode.

### 2. Local development

1. Install Python 3.10 and [Poetry](https://python-poetry.org)
2. Clone this repository. `git clone https://github.com/natelandau/obsidian-metadata`
3. Install the Poetry environment with `poetry install`.
4. Activate your Poetry environment with `poetry shell`.
5. Install the pre-commit hooks with `pre-commit install --install-hooks`.

## Developing

-   This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard to automate [Semantic Versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/) with [Commitizen](https://github.com/commitizen-tools/commitizen).
    -   When you're ready to commit changes run `cz c`
-   Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project. Common commands:
    -   `poe lint` runs all linters
    -   `poe test` runs all tests with Pytest
-   Run `poetry add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `poetry.lock`.
-   Run `poetry remove {package}` from within the development environment to uninstall a run time dependency and remove it from `pyproject.toml` and `poetry.lock`.
-   Run `poetry update` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`.
