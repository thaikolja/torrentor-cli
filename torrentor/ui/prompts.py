"""InquirerPy interactive prompts: menus, text inputs, and settings editors. Written in plain English."""

from InquirerPy import inquirer
from InquirerPy.separator import Separator

from torrentor.ui.theme import INQUIRER_STYLE


# The top-level menu when you run `torrentor` without arguments
def main_menu() -> str:
    """Show the main menu and return the selected action."""
    return inquirer.select(
        message="What would you like to do?",
        choices=[
            {"name": "  Download a torrent", "value": "add"},
            Separator(),
            {"name": "  Settings", "value": "settings"},
            {"name": "  Quit", "value": "quit"},
        ],
        style=INQUIRER_STYLE,
        pointer="❯",
        qmark="",
        amark="",
        instruction="(use arrow keys, then press Enter)",
    ).execute()


# Ask how the user wants to provide the torrent
def add_torrent_menu() -> str:
    """Ask whether to use a magnet link or a .torrent file."""
    return inquirer.select(
        message="How do you want to add it?",
        choices=[
            {"name": "  Paste a magnet link", "value": "magnet"},
            {"name": "  Torrent file (path or URL)", "value": "file"},
            Separator(),
            {"name": "  Go back", "value": "back"},
        ],
        style=INQUIRER_STYLE,
        pointer="❯",
        qmark="",
        amark="",
    ).execute()


# Text input for a magnet URI with basic validation
def magnet_input() -> str:
    """Ask the user to paste a magnet link."""
    return inquirer.text(
        message="Paste your magnet link here:",
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: v.startswith("magnet:") or "That doesn't look like a magnet link",
        invalid_message="A magnet link starts with magnet:",
    ).execute()


# File or URL input for .torrent files
def file_input() -> str:
    """Ask the user to provide a path or URL to a .torrent file."""
    return inquirer.text(
        message="Path or URL to .torrent file:",
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: (
            v.endswith(".torrent")
            or "That doesn't look like a .torrent file (must end with .torrent)"
        ),
        invalid_message="Must be a path or URL ending in .torrent",
    ).execute()


# Shown after a download is interrupted or fails — cache options only appear when data exists
def post_download_menu(has_cache: bool = False) -> str:
    """Ask the user what to do next. Cache-related options only show when cached data exists."""
    choices = []
    if has_cache:
        choices.append({"name": "  Retry (continue from cache)", "value": "retry_cache"})
    choices.append({"name": "  Retry", "value": "retry"})
    choices.append(Separator())
    if has_cache:
        choices.append({"name": "  Cancel (keep cache)", "value": "cancel_keep"})
    choices.append({"name": "  Cancel", "value": "cancel"})

    return inquirer.select(
        message="What would you like to do?",
        choices=choices,
        style=INQUIRER_STYLE,
        pointer="❯",
        qmark="",
        amark="",
    ).execute()


# Settings menu — choose which setting to change (includes ALL config fields)
def settings_menu() -> str:
    """Let the user pick which setting to change, or go back."""
    return inquirer.select(
        message="Which setting do you want to change?",
        choices=[
            {"name": "  Where to save files", "value": "output_dir"},
            {"name": "  Download speed limit", "value": "download_limit"},
            {"name": "  Upload speed limit", "value": "upload_limit"},
            {"name": "  Time limit", "value": "timeout"},
            Separator(),
            {"name": "  Network port", "value": "port"},
            {"name": "  Connection privacy", "value": "encryption"},
            {"name": "  Keep sharing after download", "value": "seed"},
            {"name": "  Download in order", "value": "in_order"},
            {"name": "  Check file for errors", "value": "check"},
            {"name": "  Block bad peers", "value": "blocklist"},
            Separator(),
            {"name": "  Go back", "value": "back"},
        ],
        style=INQUIRER_STYLE,
        pointer="❯",
        qmark="",
        amark="",
    ).execute()


# Simple text input for the output directory path
def directory_input(current: str) -> str:
    """Ask where to save downloaded files."""
    return inquirer.text(
        message="Save files to:",
        default=current,
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
    ).execute()


# Number input for speed limits — leave empty for "no limit"
def speed_limit_input(label: str, current: int | None) -> int | None:
    """Ask for a speed limit. Leave empty for no limit."""
    default = str(current) if current is not None else ""
    value = inquirer.text(
        message=f"{label} (kB/s, leave empty for no limit):",
        default=default,
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: v == "" or v.isdigit() or "Please enter a number or leave it empty",
        invalid_message="Enter a number or leave empty for no limit",
    ).execute()
    return int(value) if value.strip() else None


# Number input for timeout — leave empty for "no time limit"
def timeout_input(current: int | None) -> int | None:
    """Ask for a download time limit in seconds. Leave empty for no limit."""
    default = str(current) if current is not None else ""
    value = inquirer.text(
        message="Time limit in seconds (leave empty for no limit):",
        default=default,
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: v == "" or v.isdigit() or "Please enter a number or leave it empty",
        invalid_message="Enter a number of seconds or leave empty",
    ).execute()
    return int(value) if value.strip() else None


# Number input for port number with range validation
def port_input(current: int) -> int:
    """Ask for a network port number."""
    value = inquirer.text(
        message="Network port (1-65535):",
        default=str(current),
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: (v.isdigit() and 1 <= int(v) <= 65535) or "Must be between 1 and 65535",
        invalid_message="Enter a number between 1 and 65535",
    ).execute()
    return int(value)


# Dropdown to pick encryption mode
def encryption_select(current: str) -> str:
    """Let the user pick the connection privacy level."""
    choices = ["required", "preferred", "tolerated"]
    default = current if current in choices else "preferred"
    return inquirer.select(
        message="Connection privacy:",
        choices=choices,
        default=default,
        style=INQUIRER_STYLE,
        pointer="❯",
        qmark="",
        amark="",
    ).execute()


# Yes/No toggle for boolean settings
def toggle_input(label: str, current: bool) -> bool:
    """Let the user toggle a setting on or off."""
    return inquirer.select(
        message=f"{label}:",
        choices=[
            {"name": "  Yes", "value": True},
            {"name": "  No", "value": False},
        ],
        default=bool(current),
        style=INQUIRER_STYLE,
        pointer="❯",
        qmark="",
        amark="",
    ).execute()
