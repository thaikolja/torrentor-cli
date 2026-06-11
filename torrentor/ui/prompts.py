"""InquirerPy interactive prompts: menus, text inputs, confirmations, and settings editors."""

from InquirerPy import inquirer
from InquirerPy.separator import Separator

from torrentor.ui.theme import INQUIRER_STYLE


# The top-level menu when you run `torrentor` without arguments
def main_menu() -> str:
    """Show the main navigation menu and return the selected action ('add', 'settings', 'quit')."""
    return inquirer.select(
        message="What would you like to do?",
        choices=[
            {"name": "  Add Torrent", "value": "add"},
            Separator(),
            {"name": "  Settings", "value": "settings"},
            {"name": "  Quit", "value": "quit"},
        ],
        style=INQUIRER_STYLE,
        pointer="❯",
        qmark="",
        amark="",
        instruction="(↑/↓ to move, Enter to select)",
    ).execute()


# Ask whether they want to add via magnet or .torrent file
def add_torrent_menu() -> str:
    """Prompt the user to choose between magnet link, .torrent file, or go back."""
    return inquirer.select(
        message="How would you like to add a torrent?",
        choices=[
            {"name": "  Magnet Link", "value": "magnet"},
            {"name": "  Torrent File (.torrent)", "value": "file"},
            Separator(),
            {"name": "  Back", "value": "back"},
        ],
        style=INQUIRER_STYLE,
        pointer="❯",
        qmark="",
        amark="",
    ).execute()


# Text input for a magnet URI with basic validation
def magnet_input() -> str:
    """Ask the user to paste a magnet link, validated to start with 'magnet:'."""
    return inquirer.text(
        message="Paste magnet link:",
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: v.startswith("magnet:") or "Must be a valid magnet link",
        invalid_message="Must start with magnet:",
    ).execute()


# File browser / path input for .torrent files
def file_input() -> str:
    """Ask the user to pick a .torrent file, validated to end with '.torrent'."""
    return inquirer.filepath(
        message="Path to .torrent file:",
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: v.endswith(".torrent") or "Must be a .torrent file",
        invalid_message="Must be a .torrent file",
    ).execute()


# Yes / No confirmation before starting a download
def confirm_download() -> bool:
    """Ask the user to confirm they want to start the download."""
    return inquirer.confirm(
        message="Start download?",
        default=True,
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
    ).execute()


# Settings menu — choose which config key to edit
def settings_menu() -> str:
    """Let the user pick which setting to change, or go back."""
    return inquirer.select(
        message="Which setting to change?",
        choices=[
            {"name": "  Output Directory", "value": "output_dir"},
            {"name": "  Download Speed Limit", "value": "download_limit"},
            {"name": "  Upload Speed Limit", "value": "upload_limit"},
            {"name": "  Port", "value": "port"},
            {"name": "  Encryption", "value": "encryption"},
            Separator(),
            {"name": "  Back", "value": "back"},
        ],
        style=INQUIRER_STYLE,
        pointer="❯",
        qmark="",
        amark="",
    ).execute()


# Simple text input for the output directory path
def directory_input(current: str) -> str:
    """Prompt for a directory path, pre-filled with the current value."""
    return inquirer.text(
        message="Output directory:",
        default=current,
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
    ).execute()


# Number input for speed limits — leave empty for "unlimited"
def speed_limit_input(label: str, current: int | None) -> int | None:
    """Ask for a speed limit in kB/s. Empty input means unlimited (returns None)."""
    default = str(current) if current is not None else ""
    value = inquirer.text(
        message=f"{label} (kB/s, empty for unlimited):",
        default=default,
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: v == "" or v.isdigit() or "Must be a number or empty",
        invalid_message="Enter a number or leave empty for unlimited",
    ).execute()
    return int(value) if value.strip() else None


# Number input for port number with range validation
def port_input(current: int) -> int:
    """Ask for a port number (1-65535), pre-filled with the current value."""
    value = inquirer.text(
        message="Port:",
        default=str(current),
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: (v.isdigit() and 1 <= int(v) <= 65535) or "Must be 1-65535",
        invalid_message="Enter a valid port (1-65535)",
    ).execute()
    return int(value)


# Dropdown to pick encryption mode
def encryption_select(current: str) -> str:
    """Let the user pick between required, preferred, or tolerated encryption."""
    choices = ["required", "preferred", "tolerated"]
    default = current if current in choices else "preferred"
    return inquirer.select(
        message="Encryption mode:",
        choices=choices,
        default=default,
        style=INQUIRER_STYLE,
        pointer="❯",
        qmark="",
        amark="",
    ).execute()
