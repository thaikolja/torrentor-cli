"""Rich UI panels: info, error, success, dependency warnings, torrent details, and settings."""

import platform

from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from torrentor.ui.theme import ACCENT, CYAN, DIM, ERROR, MAGENTA, SUCCESS, WARNING, console


# Generic info panel — cyan border, bold title
def info_panel(title: str, message: str) -> None:
    """Show an informational cyan-bordered panel."""
    panel = Panel(
        Align.left(Text(message, style="default")),
        title=f"[bold {CYAN}]{title}[/]",
        border_style=CYAN,
        padding=(1, 2),
    )
    console.print(panel)


# Error panel — red border, bold title
def error_panel(message: str) -> None:
    """Show a red-bordered error panel."""
    panel = Panel(
        Align.left(Text(message, style=ERROR)),
        title=f"[bold {ERROR}]Error[/]",
        border_style=ERROR,
        padding=(1, 2),
    )
    console.print(panel)


# Dependency-missing panel — shows install commands for macOS, Linux, AND Windows
def dependency_error() -> None:
    """Show a detailed panel when transmission-cli is not found, with per-OS install commands."""
    content = Text()
    content.append("  transmission-cli", style=f"bold {CYAN}")
    content.append(" was not found on your system.\n", style="default")
    content.append("  Torrentor needs it to download files.\n\n", style="default")

    content.append("  How to install:\n\n", style=f"bold {ACCENT}")

    # Detect the OS and show the right commands
    system = platform.system().lower()
    instructions = []
    if system == "darwin":
        instructions = [
            ("macOS (Homebrew)", "brew install transmission-cli"),
            ("macOS (MacPorts)", "sudo port install transmission"),
        ]
    elif system == "win32" or system == "windows":
        instructions = [
            ("Windows (Chocolatey)", "choco install transmission-cli"),
            ("Windows (Scoop)", "scoop install transmission"),
            ("Windows (WSL)", "sudo apt install transmission-cli"),
        ]
    else:
        instructions = [
            ("Debian / Ubuntu", "sudo apt install transmission-cli"),
            ("Fedora / RHEL", "sudo dnf install transmission-cli"),
            ("Arch Linux", "sudo pacman -S transmission-cli"),
        ]

    for label, cmd in instructions:
        content.append(f"    {label}\n", style=DIM)
        content.append(f"    $ {cmd}\n\n", style=f"bold {SUCCESS}")

    # Always show all OS options as fallback
    if system == "darwin":
        content.append(f"  [{DIM}]Linux: sudo apt install transmission-cli[/]\n", style=DIM)
    elif system != "linux":
        content.append(f"  [{DIM}]macOS: brew install transmission-cli[/]\n", style=DIM)
        content.append(f"  [{DIM}]Linux: sudo apt install transmission-cli[/]\n", style=DIM)

    content.append("\n  Or download from:\n", style=f"bold {ACCENT}")
    content.append("  https://transmissionbt.com/download\n", style=f"underline {CYAN}")

    panel = Panel(
        content,
        title=f"[bold {ERROR}]Missing Dependency[/]",
        border_style=ERROR,
        padding=(1, 1),
    )
    console.print(panel)


# Slow download notification — yellow border, tips to improve speed
def slow_download_warning() -> None:
    """Show a non-blocking warning with tips when the download is unusually slow."""
    content = Text()
    content.append(
        "  Your download seems unusually slow. A few things to try:\n\n", style="default"
    )
    content.append("  • Check your internet connection\n", style="default")
    content.append(
        "  • Try a torrent with more seeders (more people sharing = faster)\n", style="default"
    )
    content.append("  • Make sure your firewall isn't blocking the connection\n", style="default")
    content.append("  • Try a different network or a VPN\n", style="default")

    panel = Panel(
        content,
        title=f"[bold {WARNING}]Slow Download[/]",
        border_style=WARNING,
        padding=(1, 1),
    )
    console.print(panel)


# Success panel — green border, bold title
def success_panel(message: str) -> None:
    """Show a green-bordered success panel."""
    panel = Panel(
        Align.left(Text(message, style=SUCCESS)),
        title=f"[bold {SUCCESS}]Done[/]",
        border_style=SUCCESS,
        padding=(1, 2),
    )
    console.print(panel)


# Download-complete panel — shows the zip file path and its size
def download_complete_panel(zip_path: str, zip_size: str) -> None:
    """Show a completion panel with the final zip file path and total size."""
    content = Text()
    content.append("  Your download is ready!\n\n", style="default")
    content.append("  File   ", style=f"bold {ACCENT}")
    content.append(f"{zip_path}\n", style="default")
    content.append("  Size   ", style=f"bold {ACCENT}")
    content.append(f"{zip_size}\n", style="default")

    panel = Panel(
        content,
        title=f"[bold {SUCCESS}]Download Complete[/]",
        border_style=SUCCESS,
        padding=(1, 1),
    )
    console.print(panel)


# Torrent details panel — name, type (magnet/file), source URI, output path + zip filename
def torrent_details_panel(
    name: str,
    source_type: str,
    source: str,
    output_dir: str | None = None,
    zip_filename: str | None = None,
) -> None:
    """Show a magenta-bordered panel with torrent metadata and expected output path."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style=f"bold {ACCENT}")
    table.add_column(style="default")
    table.add_row("Name", name)
    table.add_row("Type", source_type.capitalize())
    table.add_row("Source", source if len(source) <= 60 else source[:57] + "...")
    # Show the full expected output path including the .zip filename
    if output_dir and zip_filename:
        table.add_row("Saves to", f"{output_dir}/{zip_filename}")
    elif output_dir:
        table.add_row("Saves to", output_dir)

    panel = Panel(
        table,
        title=f"[bold {MAGENTA}]Torrent Details[/]",
        border_style=MAGENTA,
        padding=(1, 1),
    )
    console.print(panel)


# Settings panel — shows all current config values in a key-value table
def settings_panel(config: dict) -> None:
    """Display the current configuration in a cyan-bordered table inside a panel."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style=f"bold {ACCENT}")
    table.add_column(style="default")

    # Human-readable labels for each config key
    labels = {
        "output_dir": "Save files to",
        "download_limit": "Max download speed",
        "upload_limit": "Max upload speed",
        "port": "Network port",
        "encryption": "Connection privacy",
        "seed": "Keep sharing after download",
        "timeout": "Time limit",
        "in_order": "Download in order",
        "check": "Check file for errors",
        "blocklist": "Block bad peers",
    }

    for key, label in labels.items():
        val = config.get(key)
        # Format the value nicely depending on the key type
        if key in ("download_limit", "upload_limit"):
            display = f"{val} kB/s" if val is not None else f"[{DIM}]no limit[/]"
        elif key == "timeout":
            display = f"{val}s" if val is not None else f"[{DIM}]none[/]"
        elif isinstance(val, bool):
            display = f"[{SUCCESS}]yes[/]" if val else f"[{DIM}]no[/]"
        elif val is None:
            display = f"[{DIM}]off[/]"
        else:
            display = str(val)
        table.add_row(label, display)

    panel = Panel(
        table,
        title=f"[bold {CYAN}]Settings[/]",
        border_style=CYAN,
        padding=(1, 1),
    )
    console.print(panel)
