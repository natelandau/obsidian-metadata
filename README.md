[![Python Code Checker](https://github.com/natelandau/obsidian-metadata/actions/workflows/python-code-checker.yml/badge.svg)](https://github.com/natelandau/obsidian-metadata/actions/workflows/python-code-checker.yml) [![codecov](https://codecov.io/gh/natelandau/obsidian-metadata/branch/main/graph/badge.svg?token=3F2R43SSX4)](https://codecov.io/gh/natelandau/obsidian-metadata)
# obsidian-metadata
A script to make batch updates to metadata in an Obsidian vault.  Provides the following capabilities:

- `in-text tag`: delete every occurrence
- `in-text tags`: Rename tag (`#tag1` -> `#tag2`)
- `frontmatter`: Delete a key matching a regex pattern and all associated values
- `frontmatter`: Rename a key
- `frontmatter`: Delete a value matching a regex pattern from a specified key
- `frontmatter`: Rename a value from a specified key
- `inline metadata`: Delete a key matching a regex pattern and all associated values
- `inline metadata`: Rename a key
- `inline metadata`: Delete a value matching a regex pattern from a specified key
- `inline metadata`: Rename a value from a specified key
- `vault`: Create a backup of the Obsidian vault


## Install
`obsidian-metadata` requires Python v3.10 or above.

```bash
pip install obsidian-metadata
```


## Important Disclaimer
**It is strongly recommended that you back up your vault prior to committing changes.** This script makes changes directly to the markdown files in your vault. Once the changes are committed, there is no ability to recreate the original information unless you have a backup.  Follow the instructions in the script to create a backup of your vault if needed.  The author of this script is not responsible for any data loss that may occur. Use at your own risk.

## Usage
The script provides a menu of available actions. Make as many changes as you require and review them as you go.  No changes are made to the Vault until they are explicitly committed.

[![asciicast](https://asciinema.org/a/553464.svg)](https://asciinema.org/a/553464)


### Configuration
`obsidian-metadata` requires a configuration file at `~/.obsidian_metadata.toml`.  On first run, this file will be created.  You can specify a new location for the configuration file with the `--config-file` option.

To add additional vaults, copy the default section and add the appropriate information. The script will prompt you to select a vault if multiple exist in the configuration file

Below is an example with two vaults.

```toml
["Vault One"] # Name of the vault.

    # Path to your obsidian vault
    path = "/path/to/vault"

    # Folders within the vault to ignore when indexing metadata
    exclude_paths = [".git", ".obsidian"]

["Vault Two"]
    path = "/path/to/second_vault"
    exclude_paths = [".git", ".obsidian"]
```

To bypass the configuration file and specify a vault to use at runtime use the `--vault-path` option.


# Contributing

## Setup: Once per project

There are two ways to contribute to this project.

### 1. Containerized development (Recommended)

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
