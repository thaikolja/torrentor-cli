"""Rich UI panels: info, error, success, dependency warnings, torrent details, settings, and active-downloads cards."""

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


# Dependency-missing panel — platform-specific install instructions + download link
def dependency_error() -> None:
    """Show a detailed panel when transmission-cli is not found, with per-OS install commands."""
    content = Text()
    content.append("  transmission-cli", style=f"bold {CYAN}")
    content.append(" was not found on your system.\n", style="default")
    content.append("  Torrentor requires it to download torrents.\n\n", style="default")

    content.append("  Install it:\n\n", style=f"bold {ACCENT}")

    # Detect the OS and show the right command
    system = platform.system().lower()
    instructions = []
    if system == "darwin":
        instructions = [
            ("macOS (Homebrew)", "brew install transmission-cli"),
            ("macOS (MacPorts)", "sudo port install transmission"),
        ]
    elif system == "linux":
        instructions = [
            ("Debian / Ubuntu", "sudo apt install transmission-cli"),
            ("Fedora / RHEL", "sudo dnf install transmission-cli"),
            ("Arch Linux", "sudo pacman -S transmission-cli"),
        ]
    else:
        instructions = [
            ("Debian / Ubuntu", "sudo apt install transmission-cli"),
            ("macOS (Homebrew)", "brew install transmission-cli"),
        ]

    for label, cmd in instructions:
        content.append(f"    {label}\n", style=DIM)
        content.append(f"    $ {cmd}\n\n", style=f"bold {SUCCESS}")

    content.append("  Or download from:\n", style=f"bold {ACCENT}")
    content.append("  https://transmissionbt.com/download\n", style=f"underline {CYAN}")

    panel = Panel(
        content,
        title=f"[bold {ERROR}]Missing Dependency[/]",
        border_style=ERROR,
        padding=(1, 1),
    )
    console.print(panel)


# Success panel — green border, bold title
def success_panel(message: str) -> None:
    """Show a green-bordered success panel."""
    panel = Panel(
        Align.left(Text(message, style=SUCCESS)),
        title=f"[bold {SUCCESS}]Success[/]",
        border_style=SUCCESS,
        padding=(1, 2),
    )
    console.print(panel)


# Download-complete panel — shows the zip file path and its size
def download_complete_panel(zip_path: str, zip_size: str) -> None:
    """Show a completion panel with the final zip file path and total size."""
    content = Text()
    content.append("  Download complete and packaged!\n\n", style="default")
    content.append("  File   ", style=f"bold {ACCENT}")
    content.append(f"{zip_path}\n", style="default")
    content.append("  Size   ", style=f"bold {ACCENT}")
    content.append(f"{zip_size}\n", style="default")

    panel = Panel(
        content,
        title=f"[bold {SUCCESS}]Complete[/]",
        border_style=SUCCESS,
        padding=(1, 1),
    )
    console.print(panel)


# Torrent details panel — name, type (magnet/file), source URI, and optional output dir
def torrent_details_panel(
    name: str, source_type: str, source: str, output_dir: str | None = None
) -> None:
    """Show a magenta-bordered panel with torrent metadata."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style=f"bold {ACCENT}")
    table.add_column(style="default")
    table.add_row("Name", name)
    table.add_row("Type", source_type.capitalize())
    table.add_row("Source", source if len(source) <= 60 else source[:57] + "...")
    if output_dir:
        table.add_row("Output", output_dir)

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

    labels = {
        "output_dir": "Output Directory",
        "download_limit": "Download Limit",
        "upload_limit": "Upload Limit",
        "port": "Port",
        "encryption": "Encryption",
    }

    for key, label in labels.items():
        val = config.get(key)
        display = str(val) if val is not None else f"[{DIM}]unlimited[/]"
        if key in ("download_limit", "upload_limit") and val is not None:
            display = f"{val} kB/s"
        table.add_row(label, display)

    panel = Panel(
        table,
        title=f"[bold {CYAN}]Settings[/]",
        border_style=CYAN,
        padding=(1, 1),
    )
    console.print(panel)


# Active-downloads status cards — each torrent is rendered as a mini card with progress and metadata
def status_table(torrents: list[dict]) -> None:
    """Render a list of torrents as styled status cards inside a Panel."""
    status_colors = {
        "downloading": SUCCESS,
        "seeding": MAGENTA,
        "paused": WARNING,
        "queued": DIM,
    }

    status_icons = {
        "downloading": "▼",
        "seeding": "▲",
        "paused": "⏸",
        "queued": "◦",
    }

    content = Text()
    for i, t in enumerate(torrents):
        # Separator between torrents
        if i > 0:
            content.append(f"\n  {'─' * 52}\n\n", style=DIM)

        name = t.get("name", "Unknown")
        status = t.get("status", "downloading")
        color = status_colors.get(status, DIM)
        icon = status_icons.get(status, "·")

        # First line: icon + name + status label
        content.append(f"  {icon} ", style=color)
        content.append(name, style="bold")
        content.append(f"  {status.upper()}\n", style=color)

        # Second line: progress bar + percentage
        pct = t.get("progress", 0)
        bar_width = 30
        filled = int(bar_width * pct / 100)
        content.append("    ")
        content.append("━" * filled, style=SUCCESS)
        content.append("━" * (bar_width - filled), style=DIM)
        content.append(f"  {pct:>3}%\n", style="bold")

        # Third line: download/upload speeds, peers, ETA
        details = []
        down = t.get("down_speed", "—")
        up = t.get("up_speed", "—")
        peers = t.get("peers", 0)
        eta = t.get("eta", "—")

        if down != "—":
            details.append(("↓ ", DIM, down, SUCCESS))
        if up != "—":
            details.append(("↑ ", DIM, up, MAGENTA))
        if peers:
            details.append(("", "", f"{peers} peers", ACCENT))
        if eta != "—":
            details.append(("ETA ", DIM, eta, WARNING))

        content.append("    ")
        for j, (prefix, prefix_style, val, val_style) in enumerate(details):
            if j > 0:
                content.append("  ·  ", style=DIM)
            if prefix:
                content.append(prefix, style=prefix_style)
            content.append(val, style=val_style)
        content.append("\n")

    panel = Panel(
        content,
        title=f"[bold {MAGENTA}]Active Downloads[/]",
        border_style=CYAN,
        padding=(1, 1),
    )
    console.print()
    console.print(panel)
    console.print()
