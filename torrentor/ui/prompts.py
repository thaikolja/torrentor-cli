from InquirerPy import inquirer
from InquirerPy.separator import Separator

from torrentor.ui.theme import INQUIRER_STYLE


def main_menu() -> str:
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


def add_torrent_menu() -> str:
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


def magnet_input() -> str:
    return inquirer.text(
        message="Paste magnet link:",
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: v.startswith("magnet:") or "Must be a valid magnet link",
        invalid_message="Must start with magnet:",
    ).execute()


def file_input() -> str:
    return inquirer.filepath(
        message="Path to .torrent file:",
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: v.endswith(".torrent") or "Must be a .torrent file",
        invalid_message="Must be a .torrent file",
    ).execute()


def confirm_download() -> bool:
    return inquirer.confirm(
        message="Start download?",
        default=True,
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
    ).execute()


def settings_menu() -> str:
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


def directory_input(current: str) -> str:
    return inquirer.text(
        message="Output directory:",
        default=current,
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
    ).execute()


def speed_limit_input(label: str, current: int | None) -> int | None:
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


def port_input(current: int) -> int:
    value = inquirer.text(
        message="Port:",
        default=str(current),
        style=INQUIRER_STYLE,
        qmark="",
        amark="",
        validate=lambda v: v.isdigit() and 1 <= int(v) <= 65535 or "Must be 1-65535",
        invalid_message="Enter a valid port (1-65535)",
    ).execute()
    return int(value)


def encryption_select(current: str) -> str:
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
