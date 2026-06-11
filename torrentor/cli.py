import time
from pathlib import Path
from urllib.parse import unquote_plus

import typer
from rich.text import Text

from torrentor import __version__
from torrentor.core.config import CONFIG_FILE, TorrentorConfig, load_config, save_config
from torrentor.core.engine import TransmissionEngine, is_transmission_installed
from torrentor.core.postprocess import cleanup, format_size, zip_and_move
from torrentor.core.validators import validate_source
from torrentor.ui.banner import show_banner
from torrentor.ui.panels import (
    dependency_error,
    download_complete_panel,
    error_panel,
    info_panel,
    settings_panel,
    status_table,
    success_panel,
    torrent_details_panel,
)
from torrentor.ui.progress import create_download_progress, show_mock_progress
from torrentor.ui.prompts import (
    add_torrent_menu,
    confirm_download,
    directory_input,
    encryption_select,
    file_input,
    magnet_input,
    main_menu,
    port_input,
    settings_menu,
    speed_limit_input,
)
from torrentor.ui.theme import ACCENT, CYAN, DIM, MAGENTA, console

app = typer.Typer(
    name="torrentor",
    help="A beautiful CLI torrent client powered by transmission-cli.",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
)

config_app = typer.Typer(
    help="View and manage torrentor configuration.",
    no_args_is_help=False,
)
app.add_typer(config_app, name="config")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold {CYAN}]torrentor[/] [dim]v{__version__}[/]")
        raise typer.Exit()


def _require_transmission() -> None:
    if not is_transmission_installed():
        console.print()
        dependency_error()
        console.print()
        raise typer.Exit(1)


def _extract_name(source: str) -> str:
    if "&dn=" in source:
        raw = source.split("&dn=")[-1].split("&")[0]
        return unquote_plus(raw)
    return source.rsplit("/", maxsplit=1)[-1]


def _run_download(source: str, config: TorrentorConfig) -> None:
    name = _extract_name(source)
    source_type = validate_source(source)

    if source_type is None:
        error_panel("Invalid source. Provide a magnet link or path to a .torrent file.")
        raise typer.Exit(1)

    console.print()
    torrent_details_panel(name, source_type, source, config.output_dir)
    console.print()

    engine = TransmissionEngine(config)
    progress = create_download_progress()
    task_id = None

    def on_progress(info: dict) -> None:
        nonlocal task_id
        pct = info.get("progress", 0.0)
        if task_id is None:
            task_id = progress.add_task(
                name if len(name) <= 30 else name[:27] + "...",
                total=100,
                completed=pct,
                down=info.get("down_speed", "—"),
                up=info.get("up_speed", "—"),
                peers=info.get("peers", 0),
            )
        else:
            progress.update(
                task_id,
                completed=pct,
                down=info.get("down_speed", "—"),
                up=info.get("up_speed", "—"),
                peers=info.get("peers", 0),
            )

    try:
        with progress:
            download_dir = engine.download(source, on_progress=on_progress)
    except KeyboardInterrupt:
        console.print()
        info_panel("Interrupted", "Download cancelled. Temp files cleaned up.")
        raise typer.Exit(1) from None
    except Exception as exc:
        engine.abort()
        console.print()
        error_panel(f"Download failed: {exc}")
        raise typer.Exit(1) from None

    console.print()

    try:
        zip_path = zip_and_move(download_dir, Path(config.output_dir))
        zip_size = format_size(zip_path.stat().st_size)
        download_complete_panel(str(zip_path), zip_size)
    except Exception as exc:
        error_panel(f"Post-processing failed: {exc}")
    finally:
        if engine.temp_dir:
            cleanup(engine.temp_dir)

    console.print()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    if ctx.invoked_subcommand is None:
        _interactive_mode()


def _interactive_mode() -> None:
    _require_transmission()
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

    config = load_config()
    name = _extract_name(source)
    console.print()
    torrent_details_panel(name, method, source, config.output_dir)
    console.print()

    try:
        if not confirm_download():
            info_panel("Cancelled", "Download was not started.")
            console.print()
            return
    except (KeyboardInterrupt, EOFError):
        return

    _run_download(source, config)


def _interactive_settings() -> None:
    config = load_config()

    while True:
        console.print()
        settings_panel(config.to_dict())
        console.print()

        try:
            choice = settings_menu()
        except (KeyboardInterrupt, EOFError):
            return

        if choice == "back":
            return

        try:
            if choice == "output_dir":
                config.output_dir = directory_input(config.output_dir)
            elif choice == "download_limit":
                config.download_limit = speed_limit_input("Download limit", config.download_limit)
            elif choice == "upload_limit":
                config.upload_limit = speed_limit_input("Upload limit", config.upload_limit)
            elif choice == "port":
                config.port = port_input(config.port)
            elif choice == "encryption":
                config.encryption = encryption_select(config.encryption)

            save_config(config)
            console.print()
            success_panel("Settings saved.")
        except (KeyboardInterrupt, EOFError):
            continue


def _quit() -> None:
    console.print()
    console.print(f"[{DIM}]Goodbye![/]")
    raise typer.Exit()


@app.command()
def add(
    source: str = typer.Argument(..., help="Magnet link or path to .torrent file."),
    output_dir: str | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory for the final .zip file.",
    ),
    download_limit: int | None = typer.Option(
        None,
        "--download-limit",
        "-l",
        help="Max download speed in kB/s.",
    ),
    upload_limit: int | None = typer.Option(
        None,
        "--upload-limit",
        "-u",
        help="Max upload speed in kB/s.",
    ),
    no_limit: bool = typer.Option(
        False,
        "--no-limit",
        help="Remove all speed limits.",
    ),
    encryption: str | None = typer.Option(
        None,
        "--encryption",
        "-e",
        help="Encryption mode: required, preferred, tolerated.",
    ),
) -> None:
    """Add a torrent for download via magnet link or .torrent file."""
    _require_transmission()
    show_banner()

    config = load_config()

    if output_dir:
        config.output_dir = output_dir
    if download_limit is not None:
        config.download_limit = download_limit
    if upload_limit is not None:
        config.upload_limit = upload_limit
    if no_limit:
        config.download_limit = None
        config.upload_limit = None
    if encryption:
        config.encryption = encryption

    _run_download(source, config)


@config_app.callback(invoke_without_command=True)
def config_main(ctx: typer.Context) -> None:
    """Show current configuration."""
    if ctx.invoked_subcommand is None:
        config = load_config()
        console.print()
        settings_panel(config.to_dict())
        console.print(f"\n  [{DIM}]Config file: {CONFIG_FILE}[/]\n")


@config_app.command("set")
def config_set(
    key: str = typer.Argument(
        ..., help="Config key (output_dir, download_limit, upload_limit, port, encryption)."
    ),
    value: str = typer.Argument(..., help="New value (use 'none' for unlimited)."),
) -> None:
    """Set a configuration value."""
    config = load_config()

    valid_keys = set(TorrentorConfig.__dataclass_fields__)
    if key not in valid_keys:
        error_panel(f"Unknown key '{key}'. Valid keys: {', '.join(sorted(valid_keys))}")
        raise typer.Exit(1)

    if key == "output_dir":
        config.output_dir = value
    elif key in ("download_limit", "upload_limit"):
        setattr(config, key, None if value.lower() in ("none", "unlimited", "") else int(value))
    elif key == "port":
        config.port = int(value)
    elif key == "encryption":
        if value not in ("required", "preferred", "tolerated"):
            error_panel("Encryption must be: required, preferred, or tolerated.")
            raise typer.Exit(1)
        config.encryption = value

    save_config(config)
    console.print()
    success_panel(f"{key} set to {getattr(config, key)!r}")
    console.print()


@config_app.command()
def reset() -> None:
    """Reset configuration to defaults."""
    save_config(TorrentorConfig())
    console.print()
    success_panel("Configuration reset to defaults.")
    console.print()


@config_app.command()
def path() -> None:
    """Print the config file path."""
    console.print(str(CONFIG_FILE))


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
        "~/Downloads",
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
        (f"[bold {CYAN}]❯[/]", "[bold]  Add Torrent[/]"),
        ("  ", f"[{DIM}]  ─────────────────────[/]"),
        ("  ", f"[{DIM}]  Settings[/]"),
        ("  ", f"[{DIM}]  Quit[/]"),
    ]

    lines = Text()
    for pointer, label in choices:
        lines.append_text(Text.from_markup(f"  {pointer} {label}\n"))

    from rich.panel import Panel

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
            "name": "Ubuntu 24.04 LTS",
            "progress": 87,
            "down_speed": "2.4 MB/s",
            "up_speed": "312 KB/s",
            "peers": 12,
            "eta": "0:02:14",
            "status": "downloading",
        },
        {
            "name": "Arch Linux 2024.06",
            "progress": 100,
            "down_speed": "—",
            "up_speed": "1.2 MB/s",
            "peers": 4,
            "eta": "—",
            "status": "seeding",
        },
        {
            "name": "Debian 12.5 netinst",
            "progress": 23,
            "down_speed": "3.1 MB/s",
            "up_speed": "89 KB/s",
            "peers": 21,
            "eta": "0:08:47",
            "status": "downloading",
        },
        {
            "name": "Fedora Workstation 40",
            "progress": 0,
            "down_speed": "—",
            "up_speed": "—",
            "peers": 0,
            "eta": "—",
            "status": "queued",
        },
    ]
    status_table(mock_torrents)
