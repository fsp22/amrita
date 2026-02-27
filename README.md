# Amrita - App Key Bindings and Shortcut Searcher

A TUI (Text User Interface) application to search and display application key bindings and shortcuts with fuzzy matching.

## Features

- Searchable shortcut list with fuzzy matching
- Scrollable content pane (mouse or keyboard arrows)
- Configurable via YAML files
- Automatic app name detection with fuzzy matching

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python amrita.py <app_name>
```

If no app name is provided, Amrita will list available config files.

## Configuration

Create YAML files in the `config/` directory with the following format:

```yaml
section1:
  - name: Open new file
    key: ctrl+b
  - name: Create new file
    key: ctrl+n
section2:
  - name: Open new window
    key: ctrl+v
  - name: Create new window
    key: ctrl+1
```

File names should follow the pattern `{APPNAME}.yml` (e.g., `vscode.yml`, `sublime.yml`).

## Controls

- **Up/Down arrows**: Scroll through shortcuts
- **Type in search box**: Filter shortcuts using fuzzy matching
- **Mouse wheel**: Scroll content pane
- **ESC**: Reset search field
- **TAB**: Switch focus between search and content
- **Ctrl+D**: Quit the application

## Dependencies

- Python 3.7+
- Textual (TUI framework)
- PyYAML (YAML parsing)
- rapidfuzz (fuzzy string matching)

## License

See license file
