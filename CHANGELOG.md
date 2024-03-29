## v0.12.1 (2023-09-02)

### Fix

- **notes**: preserve file encoding when writing to filesystem (#59)

## v0.12.0 (2023-05-17)

### Feat

- greatly improve capturing all formats of inline metadata (#41)
- greatly improve capturing metadata all formats of inline metadata

### Fix

- allow markdown inline code in metadata values
- only ask for valid metadata types when adding new metadata
- convert charsets to utf-8 when necessary (#32)
- improve TOML error handing and docs for Windows paths (#31)

## v0.11.1 (2023-03-29)

### Fix

- add custom exceptions (#29)

## v0.11.0 (2023-03-24)

### Feat

- add `--import-csv` option to cli

## v0.10.0 (2023-03-21)

### Feat

- add `--export-template` cli option

### Fix

- `--export-template` correctly exports all notes
- `--export-csv` exports csv not json
- **csv-import**: fail if `type` does not validate

### Refactor

- pave the way for non-regex key/value deletions
- remove unused code
- cleanup rename and delete from dict functions

## v0.9.0 (2023-03-20)

### Feat

- bulk update metadata from a CSV file

### Fix

- find more instances of inline metadata
- ensure frontmatter values are unique within a key
- improve validation of bulk imports
- improve logging to screen

## v0.8.0 (2023-03-12)

### Feat

- move inline metadata to specific location in note (#27)

### Fix

- add `back` option to transpose menus

## v0.7.0 (2023-03-11)

### Feat

- transpose metadata between frontmatter and inline
- select insert location for new inline metadata

### Fix

- exit after committing changes
- fix typo and sort order of options

## v0.6.1 (2023-03-03)

### Fix

- improve error handling when frontmatter malformed

### Refactor

- use single console instance

## v0.6.0 (2023-02-06)

### Feat

- transpose metadata (#18)

### Fix

- **ui**: add separator to top of select lists
- allow adding inline tags with same key different values (#17)
- remove unnecessary question when viewing diffs

## v0.5.0 (2023-02-04)

### Feat

-   add new tags (#16)
-   add new inline metadata (#15)
-   **configuration**: `insert_location` specifies where content is added within notes

### Fix

-   find more emojis

## v0.4.0 (2023-02-02)

### Feat

-   export metadata (#14)

    -   export metadata to CSV
    -   export metadata to JSON
    -   export CSV or JSON from command line

-   limit scope of notes with one or more filters (#13)

### Fix

-   do not count in-page links as tags
-   improve terminal colors of questions

## v0.3.0 (2023-01-30)

### Feat

-   **application**: add new metadata to frontmatter (#9)

### Fix

-   **application**: improve ux (#10)

## v0.2.0 (2023-01-25)

### Feat

-   **configuration**: support multiple vaults in the configuration file (#6)

### Refactor

-   **application**: refactor questions to separate class (#7)

## v0.1.1 (2023-01-23)

### Fix

-   **notes**: diff now prints values in the form `[value]`
-   **application**: exit after committing changes

## v0.1.0 (2023-01-22)

### Feat

-   initial application release
