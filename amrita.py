import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any
from rapidfuzz import fuzz, process
from textual.app import App, ComposeResult
from textual.widgets import Input, Static
from textual.containers import Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.binding import Binding

class PairRow(Horizontal):
    def __init__(self, left: str, right: str = ""):
        super().__init__()
        self.left_value = left
        self.right_value = right

    def compose(self) -> ComposeResult:
        yield Static(self.left_value, classes="left")
        if self.right_value:
            yield Static(self.right_value, classes="right")

class ShortcutApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    #search-bar {
        height: 3;
        dock: top;
        padding: 0 1;
    }

    #content {
        height: 1fr;
        overflow-y: auto;
    }

    ScrollableContainer {
        border: solid gray;
    }

    PairRow {
        height: auto;
        width: 100%;
        layout: horizontal;
        border-bottom: dashed #444;
    }

    .left {
        width: 80%;
        padding-left: 1;
    }

    .right {
        width: 20%;
        text-align: right;
        color: yellow;
        padding-right: 1;
    }

    .heading {
        width: 100%;
        background: #333;
        color: white;
        padding-left: 1;
        height: 1;
    }
    """

    search_query = reactive("")
    BINDINGS = [
        Binding("up", "scroll_up", "Scroll Up", show=True),
        Binding("down", "scroll_down", "Scroll Down", show=True),
        Binding("escape", "reset_search", "Reset Search", show=True),
        Binding("ctrl+d", "quit_app", "Quit", show=True),
    ]

    def __init__(self, shortcuts: Dict[str, List[Dict[str, str]]]):
        super().__init__()
        self.shortcuts = shortcuts

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search-bar")
        with ScrollableContainer(id="content", can_focus=True):
            for section, items in self.shortcuts.items():
                yield Static(section, classes="heading")
                for item in items:
                    yield PairRow(item["name"], item["key"])

    def on_mount(self) -> None:
        self.query_one("#search-bar", Input).focus()

    def on_input_changed(self, event: Input.Changed):
        query = event.value.lower()
        self.search_query = query
        
        for row in self.query(PairRow):
            # Show all if search field is empty
            if not query:
                row.display = True
                continue
                
            # Use fuzzy matching for better search results
            score_name = fuzz.partial_ratio(query, row.left_value.lower())
            score_key = fuzz.partial_ratio(query, row.right_value.lower())
            visible = score_name > 70 or score_key > 70
            row.display = visible

    def action_scroll_up(self) -> None:
        self.query_one("#content", ScrollableContainer).scroll_up()

    def action_scroll_down(self) -> None:
        self.query_one("#content", ScrollableContainer).scroll_down()

    def action_reset_search(self) -> None:
        search_input = self.query_one("#search-bar", Input)
        search_input.value = ""
        search_input.focus()

    def action_quit_app(self) -> None:
        self.exit()

    def on_key(self, event):
        if event.key == "up":
            self.action_scroll_up()
        elif event.key == "down":
            self.action_scroll_down()
        elif event.key == "escape":
            self.action_reset_search()
        elif event.key == "ctrl+d":
            self.action_quit_app()

def load_config_file(app_name: str) -> Dict[str, Any]:
    """Load YAML config file for the specified app name."""
    config_dir = Path("config")
    
    if not config_dir.exists():
        print(f"Error: Config directory '{config_dir}' does not exist.")
        sys.exit(1)
    
    # Find all YAML files in config directory
    yaml_files = list(config_dir.glob("*.yml")) + list(config_dir.glob("*.yaml"))
    
    if not yaml_files:
        print(f"Error: No YAML config files found in '{config_dir}'.")
        sys.exit(1)
    
    # Use fuzzy matching to find the best matching file
    file_names = [f.stem for f in yaml_files]
    best_match, score, _ = process.extractOne(app_name, file_names, scorer=fuzz.token_set_ratio)
    
    if score < 60:
        print(f"Available config files:")
        for f in file_names:
            print(f"  - {f}")
        print(f"\nNo close match found for '{app_name}'. Please specify a valid app name.")
        sys.exit(1)
    
    config_file = config_dir / f"{best_match}.yml"
    if not config_file.exists():
        config_file = config_dir / f"{best_match}.yaml"
    
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config file '{config_file}': {e}")
        sys.exit(1)

def parse_shortcuts(config: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """Parse shortcuts from config file."""
    shortcuts = {}
    
    for section, items in config.items():
        shortcuts[section] = []
        for item in items:
            if isinstance(item, dict):
                shortcuts[section].append({
                    "name": item.get("name", ""),
                    "key": item.get("key", "")
                })
    
    return shortcuts

def main():
    if len(sys.argv) < 2:
        print("Usage: python amrita.py <app_name>")
        print("\nAvailable config files:")
        config_dir = Path("config")
        if config_dir.exists():
            for f in sorted(config_dir.glob("*.yml")):
                print(f"  - {f.stem}")
            for f in sorted(config_dir.glob("*.yaml")):
                print(f"  - {f.stem}")
        sys.exit(1)
    
    app_name = sys.argv[1]
    config = load_config_file(app_name)
    shortcuts = parse_shortcuts(config)
    
    app = ShortcutApp(shortcuts)
    app.run()

if __name__ == "__main__":
    main()
