import time
from typing import Optional

import typer
from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from torrentor import __version__
from torrentor.ui.theme import console, CYAN, MAGENTA, DIM, SUCCESS, ACCENT
from torrentor.ui.banner import show_banner
from torrentor.ui.panels import (
    info_panel,
    success_panel,
    error_panel,
    torrent_details_panel,
    settings_panel,
    status_table,
)
from torrentor.ui.progress import show_mock_progress
from torrentor.ui.prompts import (
    main_menu,
    add_torrent_menu,
    magnet_input,
    file_input,
    confirm_download,
)
from torrentor.core.config import DEFAULT_CONFIG
from torrentor.core.validators import validate_source

app = typer.Typer(
    name="torrentor",
    help="A beautiful CLI torrent client powered by transmission-cli.",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold {CYAN}]torrentor[/] [dim]v{__version__}[/]")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    if ctx.invoked_subcommand is None:
        _interactive_mode()


def _interactive_mode() -> None:
    console.clear()
    show_banner()
    console.print()

    while True:
        try:
            choice = main_menu()
        except (KeyboardInterrupt, EOFError):
            _quit()

        if choice == "add":
            _interactive_add()
        elif choice == "status":
            _interactive_status()
        elif choice == "settings":
            _interactive_settings()
        elif choice == "quit":
            _quit()


def _interactive_add() -> None:
    console.print()
    try:
        method = add_torrent_menu()
    except (KeyboardInterrupt, EOFError):
        return

    if method == "back":
        return

    source = None
    try:
        if method == "magnet":
            source = magnet_input()
        elif method == "file":
            source = file_input()
    except (KeyboardInterrupt, EOFError):
        return

    if not source:
        return

    console.print()
    name = source.split("&dn=")[-1].split("&")[0] if "&dn=" in source else source.split("/")[-1]
    torrent_details_panel(name, method, source)
    console.print()

    try:
        if confirm_download():
            success_panel("Torrent queued for download!")
        else:
            info_panel("Cancelled", "Download was not started.")
    except (KeyboardInterrupt, EOFError):
        return

    console.print()


def _interactive_status() -> None:
    console.print()
    info_panel("Active Downloads", "No active downloads yet. Add a torrent to get started!")
    console.print()


def _interactive_settings() -> None:
    console.print()
    settings_panel(DEFAULT_CONFIG.to_dict())
    console.print()


def _quit() -> None:
    console.print()
    console.print(f"[{DIM}]Goodbye![/]")
    raise typer.Exit()


@app.command()
def add(
    source: str = typer.Argument(..., help="Magnet link or path to .torrent file."),
    download_dir: Optional[str] = typer.Option(
        None, "--download-dir", "-d",
        help="Directory to save downloaded files.",
    ),
    download_limit: Optional[int] = typer.Option(
        None, "--download-limit", "-l",
        help="Max download speed in kB/s.",
    ),
    upload_limit: Optional[int] = typer.Option(
        None, "--upload-limit", "-u",
        help="Max upload speed in kB/s.",
    ),
    no_limit: bool = typer.Option(
        False, "--no-limit",
        help="Remove all speed limits.",
    ),
    encryption: str = typer.Option(
        "preferred", "--encryption", "-e",
        help="Encryption mode: required, preferred, tolerated.",
    ),
) -> None:
    """Add a torrent for download via magnet link or .torrent file."""
    show_banner()
    console.print()

    source_type = validate_source(source)
    if source_type is None:
        error_panel("Invalid source. Provide a magnet link or path to a .torrent file.")
        raise typer.Exit(1)

    name = source.split("&dn=")[-1].split("&")[0] if "&dn=" in source else source.split("/")[-1]
    torrent_details_panel(name, source_type, source)
    console.print()
    success_panel("Torrent queued for download!")


@app.command()
def demo() -> None:
    """Showcase all UI elements with mock data."""
    console.clear()

    console.print(f"\n[{DIM}]{'─' * 50}[/]")
    console.print(f"[bold {MAGENTA}]  TORRENTOR UI DEMO[/]")
    console.print(f"[{DIM}]{'─' * 50}[/]\n")
    time.sleep(0.8)

    console.print(f"[{ACCENT}]1/5[/] [bold]Banner[/]\n")
    show_banner()
    time.sleep(1.5)

    console.print(f"\n[{ACCENT}]2/5[/] [bold]Interactive Menu[/]\n")
    _demo_menu()
    time.sleep(1.2)

    console.print(f"\n[{ACCENT}]3/5[/] [bold]Torrent Details Panel[/]\n")
    torrent_details_panel(
        "Ubuntu 24.04.1 LTS (Desktop, 64-bit)",
        "magnet",
        "magnet:?xt=urn:btih:a1b2c3d4e5...&dn=Ubuntu+24.04.1+LTS",
    )
    time.sleep(1.2)

    console.print(f"\n[{ACCENT}]4/5[/] [bold]Download Progress[/]\n")
    show_mock_progress(duration=4.0)
    time.sleep(0.8)

    console.print(f"\n[{ACCENT}]5/5[/] [bold]Status Table[/]\n")
    _demo_status_table()
    time.sleep(0.5)

    console.print(f"\n[{DIM}]{'─' * 50}[/]")
    success_panel("Demo complete! Run 'torrentor' to start the interactive mode.")
    console.print()


def _demo_menu() -> None:
    choices = [
        (f"[bold {CYAN}]❯[/]", f"[bold]  Add Torrent[/]"),
        ("  ", f"[{DIM}]  Active Downloads[/]"),
        ("  ", f"[{DIM}]  ─────────────────────[/]"),
        ("  ", f"[{DIM}]  Settings[/]"),
        ("  ", f"[{DIM}]  Quit[/]"),
    ]

    lines = Text()
    for pointer, label in choices:
        lines.append_text(Text.from_markup(f"  {pointer} {label}\n"))

    panel = Panel(
        lines,
        title=f"[bold {CYAN}]What would you like to do?[/]",
        subtitle=f"[{DIM}](↑/↓ to move, Enter to select)[/]",
        border_style=CYAN,
        padding=(1, 2),
    )
    console.print(panel)


def _demo_status_table() -> None:
    mock_torrents = [
        {
            "name":       "Ubuntu 24.04 LTS",
            "progress":   87,
            "down_speed": "2.4 MB/s",
            "up_speed":   "312 KB/s",
            "peers":      12,
            "eta":        "0:02:14",
            "status":     "downloading",
        },
        {
            "name":       "Arch Linux 2024.06",
            "progress":   100,
            "down_speed": "—",
            "up_speed":   "1.2 MB/s",
            "peers":      4,
            "eta":        "—",
            "status":     "seeding",
        },
        {
            "name":       "Debian 12.5 netinst",
            "progress":   23,
            "down_speed": "3.1 MB/s",
            "up_speed":   "89 KB/s",
            "peers":      21,
            "eta":        "0:08:47",
            "status":     "downloading",
        },
        {
            "name":       "Fedora Workstation 40",
            "progress":   0,
            "down_speed": "—",
            "up_speed":   "—",
            "peers":      0,
            "eta":        "—",
            "status":     "queued",
        },
    ]
    status_table(mock_torrents)
