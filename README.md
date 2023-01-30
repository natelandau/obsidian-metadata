[![Python Code Checker](https://github.com/natelandau/obsidian-metadata/actions/workflows/python-code-checker.yml/badge.svg)](https://github.com/natelandau/obsidian-metadata/actions/workflows/python-code-checker.yml) [![codecov](https://codecov.io/gh/natelandau/obsidian-metadata/branch/main/graph/badge.svg?token=3F2R43SSX4)](https://codecov.io/gh/natelandau/obsidian-metadata)
# obsidian-metadata
A script to make batch updates to metadata in an Obsidian vault. No changes are
 made to the Vault until they are explicitly committed.

[![asciicast](https://asciinema.org/a/555789.svg)](https://asciinema.org/a/555789)

## Important Disclaimer
**It is strongly recommended that you back up your vault prior to committing changes.** This script makes changes directly to the markdown files in your vault. Once the changes are committed, there is no ability to recreate the original information unless you have a backup.  Follow the instructions in the script to create a backup of your vault if needed.  The author of this script is not responsible for any data loss that may occur. Use at your own risk.


## Install
Requires Python v3.10 or above.

```bash
pip install obsidian-metadata
```

## Usage
Run `obsidian-metadata` from the command line to invoke the script.  Add `--help` to view additional options.

Obsidian-metadata provides a menu of sub-commands.

**Vault Actions**
- Backup:        Create a backup of the vault.
- Delete Backup: Delete a backup of the vault.

**Inspect Metadata**
- View all metadata in the vault

**Filter Notes in Scope**:
Limit the scope of notes to be processed with a regex.
- Apply regex:          Set a regex to limit scope
- List notes in scope:  List notes that will be processed.

**Add Metadata**
- Add metadata to the frontmatter
- Add to inline metadata (Not yet implemented)
- Add to inline tag (Not yet implemented)

**Rename Metadata**
- Rename a key
- Rename a value
- rename an inline tag

**Delete Metadata**
- Delete a key and associated values
- Delete a value from a key
- Delete an inline tag

**Review Changes**
- View a diff of the changes that will be made

**Commit Changes**
- Commit changes to the vault

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
