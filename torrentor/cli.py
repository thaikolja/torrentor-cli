"""Typer CLI app — commands: add, config (set/reset/path), and an interactive mode."""

from pathlib import Path
from urllib.parse import unquote_plus

import typer
from rich.progress import TaskID

from torrentor import __version__
from torrentor.core.config import CONFIG_FILE, TorrentorConfig, load_config, save_config
from torrentor.core.engine import TransmissionEngine, is_transmission_installed
from torrentor.core.postprocess import (
    cleanup,
    format_size,
    predict_zip_filename,
    zip_and_move,
)
from torrentor.core.validators import validate_source
from torrentor.ui.banner import show_banner
from torrentor.ui.effects import celebrate
from torrentor.ui.panels import (
    dependency_error,
    download_complete_panel,
    error_panel,
    info_panel,
    settings_panel,
    success_panel,
    torrent_details_panel,
)
from torrentor.ui.progress import create_download_progress, show_controls_hint
from torrentor.ui.prompts import (
    add_torrent_menu,
    directory_input,
    encryption_select,
    file_input,
    magnet_input,
    main_menu,
    port_input,
    post_download_menu,
    settings_menu,
    speed_limit_input,
)
from torrentor.ui.theme import CYAN, DIM, console

# Main Typer app and its nested config sub-app
app = typer.Typer(
    name="torrentor",
    help="Download torrents from the command line — easy, fast, cross-platform.",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

config_app = typer.Typer(
    help="View and change your torrentor settings.",
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)
app.add_typer(config_app, name="config")


# When the user passes --version / -V, print the version and bail
def _version_callback(value: bool) -> None:
    """Print the current version and exit."""
    if value:
        console.print(f"[bold {CYAN}]torrentor[/] [dim]v{__version__}[/]")
        raise typer.Exit()


# Guard that checks transmission-cli is on PATH before doing anything real
def _require_transmission() -> None:
    """Exit with a styled error if transmission-cli is not installed."""
    if not is_transmission_installed():
        console.print()
        dependency_error()
        console.print()
        raise typer.Exit(1)


# Extract a human-readable name from a magnet link or file path
def _extract_name(source: str) -> str:
    """Pull the torrent name from a magnet's dn= parameter or the filename."""
    if "&dn=" in source:
        raw = source.split("&dn=")[-1].split("&")[0]
        return unquote_plus(raw)
    return source.rsplit("/", maxsplit=1)[-1]


# The core download-and-postprocess pipeline
# Returns (success, engine) — engine is kept alive on failure so caller can manage the cache
def _run_download(
    source: str,
    config: TorrentorConfig,
    resume_dir: Path | None = None,
) -> tuple[bool, TransmissionEngine | None]:
    """Download, zip, celebrate. Returns (True, None) on success, (False, engine) on failure."""
    name = _extract_name(source)
    source_type = validate_source(source)

    # Bail early if the source is neither a magnet link nor a .torrent file
    if source_type is None:
        error_panel("That doesn't look like a magnet link or a .torrent file.")
        return False, None

    # Predict what the .zip will be called so we can show it up front
    zip_name = predict_zip_filename(name)

    console.print()
    torrent_details_panel(name, source_type, source, config.output_dir, zip_name)
    console.print()

    # Set up the engine and a progress bar
    engine = TransmissionEngine(config)
    progress = create_download_progress()

    # Show the spinner immediately with a "Connecting..." label
    task_label = name if len(name) <= 30 else name[:27] + "..."
    task_id: TaskID | None = None

    # This callback gets called by the engine on every progress update
    def on_progress(info: dict) -> None:
        nonlocal task_id
        pct = info.get("progress", 0.0)
        fields = {
            "down": info.get("down_speed", "—"),
            "up": info.get("up_speed", "—"),
            "peers": info.get("peers", 0),
        }
        if task_id is None:
            # First progress update — replace the connecting task with real data
            task_id = progress.add_task(task_label, total=100, completed=pct, **fields)
        else:
            progress.update(task_id, completed=pct, **fields)

    # Show controls hint and start the download with spinner visible from the start
    show_controls_hint()
    try:
        with progress:
            # Add an initial "connecting" task so the spinner shows right away
            connecting_id = progress.add_task(
                "Connecting...", total=None, down="—", up="—", peers=0
            )

            # Remove the connecting task on first real update
            first_update = True

            def _on_progress_wrapper(info: dict) -> None:
                nonlocal first_update
                if first_update:
                    progress.remove_task(connecting_id)
                    first_update = False
                on_progress(info)

            download_dir = engine.download(
                source, on_progress=_on_progress_wrapper, resume_dir=resume_dir
            )
    except KeyboardInterrupt:
        # Stop the process but keep the cache for potential resume
        console.print()
        info_panel("Paused", "Download paused. Your progress is saved.")
        return False, engine
    except Exception as exc:
        console.print()
        error_panel(f"Something went wrong: {exc}")
        return False, engine

    console.print()

    # Post-process: zip it up, celebrate, show the result, clean up the temp dir
    try:
        zip_path = zip_and_move(download_dir, Path(config.output_dir))
        zip_size = format_size(zip_path.stat().st_size)
        # Confetti burst before the completion panel
        celebrate()
        download_complete_panel(str(zip_path), zip_size)
    except Exception as exc:
        error_panel(f"Couldn't package the file: {exc}")
        return False, engine
    finally:
        if engine.temp_dir:
            cleanup(engine.temp_dir)

    console.print()
    return True, None


# ── Default callback: when no subcommand is given, launch interactive mode ──
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


# ── Interactive loop ──
def _interactive_mode() -> None:
    """Clear screen, show banner, and loop through the main menu until the user quits."""
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


# Interactive "download a torrent" flow with cancel/retry + cache support
def _interactive_add() -> None:
    """Walk the user through choosing source type, entering the source, and downloading with retry."""
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

    # Download with retry loop — cache is preserved between attempts
    config = load_config()
    resume_dir: Path | None = None

    while True:
        success, engine = _run_download(source, config, resume_dir=resume_dir)
        if success:
            break

        # Download interrupted or failed — show the cancel/retry menu
        console.print()
        try:
            action = post_download_menu()
        except (KeyboardInterrupt, EOFError):
            # Emergency exit — clean up everything
            if engine:
                engine.abort()
            return

        if action == "retry_cache":
            # Reuse the existing temp dir so transmission can resume partial data
            resume_dir = engine.temp_dir if engine else None
        elif action == "retry":
            # Start fresh — nuke the old cache first
            if engine:
                engine.abort()
            resume_dir = None
        elif action == "cancel_keep":
            # Keep the cache on disk for later
            return
        else:
            # "cancel" — delete cache and go back
            if engine:
                engine.abort()
            return


# Interactive settings editor — loop until the user picks "back"
def _interactive_settings() -> None:
    """Show current settings, let the user pick one to change, save on each change."""
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
                config.download_limit = speed_limit_input("Download speed", config.download_limit)
            elif choice == "upload_limit":
                config.upload_limit = speed_limit_input("Upload speed", config.upload_limit)
            elif choice == "port":
                config.port = port_input(config.port)
            elif choice == "encryption":
                config.encryption = encryption_select(config.encryption)

            save_config(config)
            console.print()
            success_panel("Settings saved.")
        except (KeyboardInterrupt, EOFError):
            continue


# Farewell message
def _quit() -> None:
    """Print goodbye and exit."""
    console.print()
    console.print(f"[{DIM}]Goodbye![/]")
    raise typer.Exit()


# ── CLI command: add ──
@app.command()
def add(
    source: str = typer.Argument(..., help="Magnet link or path to a .torrent file."),
    # ── Main options ──
    save_to: str | None = typer.Option(
        None,
        "--save-to",
        "-o",
        help="Where to save the downloaded file.",
    ),
    max_download: int | None = typer.Option(
        None,
        "--max-download",
        "-l",
        help="Limit how fast the file downloads (kB/s).",
    ),
    max_upload: int | None = typer.Option(
        None,
        "--max-upload",
        "-u",
        help="Limit how fast you share with others (kB/s).",
    ),
    no_limit: bool = typer.Option(
        False,
        "--no-limit",
        "-n",
        help="Download and upload at full speed.",
    ),
    timeout: int | None = typer.Option(
        None,
        "--timeout",
        "-t",
        help="Stop if the download takes longer than this (seconds).",
    ),
    # ── Advanced options ──
    seed: bool | None = typer.Option(
        None,
        "--seed",
        "-s",
        help="Keep sharing the file after it finishes downloading.",
        rich_help_panel="Advanced",
    ),
    in_order: bool | None = typer.Option(
        None,
        "--in-order",
        "-q",
        help="Download from beginning to end instead of jumping around.",
        rich_help_panel="Advanced",
    ),
    check_file: bool | None = typer.Option(
        None,
        "--check",
        "-y",
        help="Double-check the downloaded file for errors.",
        rich_help_panel="Advanced",
    ),
    port: int | None = typer.Option(
        None,
        "--port",
        "-p",
        help="Network port for connecting to other peers.",
        rich_help_panel="Advanced",
    ),
    encryption: str | None = typer.Option(
        None,
        "--encryption",
        "-e",
        help="Connection privacy: required, preferred, or tolerated.",
        rich_help_panel="Advanced",
    ),
    blocklist: bool | None = typer.Option(
        None,
        "--blocklist",
        "-b",
        help="Block known bad peers from connecting.",
        rich_help_panel="Advanced",
    ),
) -> None:
    """Download a torrent from a magnet link or .torrent file."""
    _require_transmission()
    show_banner()

    # Load saved settings, then override with any flags the user passed
    config = load_config()

    if save_to:
        config.output_dir = save_to
    if max_download is not None:
        config.download_limit = max_download
    if max_upload is not None:
        config.upload_limit = max_upload
    if no_limit:
        config.download_limit = None
        config.upload_limit = None
    if timeout is not None:
        config.timeout = timeout
    if seed is not None:
        config.seed = seed
    if in_order is not None:
        config.in_order = in_order
    if check_file is not None:
        config.check = check_file
    if port is not None:
        config.port = port
    if encryption:
        config.encryption = encryption
    if blocklist is not None:
        config.blocklist = blocklist

    # Run the download — in CLI mode, always clean up cache on failure and exit
    success, engine = _run_download(source, config)
    if not success:
        if engine:
            engine.abort()
        raise typer.Exit(1)


# ── Config subcommands ──


# `torrentor config` — show current settings
@config_app.callback(invoke_without_command=True)
def config_main(ctx: typer.Context) -> None:
    """Show your current settings."""
    if ctx.invoked_subcommand is None:
        config = load_config()
        console.print()
        settings_panel(config.to_dict())
        console.print(f"\n  [{DIM}]Settings file: {CONFIG_FILE}[/]\n")


# `torrentor config set <key> <value>`
@config_app.command("set")
def config_set(
    key: str = typer.Argument(
        ...,
        help="Setting name (e.g. output_dir, download_limit, seed, in_order, ...).",
    ),
    value: str = typer.Argument(
        ..., help="New value. Use 'none' to clear, 'true'/'false' for on/off settings."
    ),
) -> None:
    """Change a setting."""
    config = load_config()

    valid_keys = set(TorrentorConfig.__dataclass_fields__)
    if key not in valid_keys:
        error_panel(f"Unknown setting '{key}'. Available: {', '.join(sorted(valid_keys))}")
        raise typer.Exit(1)

    # Boolean settings
    bool_keys = {"seed", "in_order", "check", "blocklist"}
    # Optional number settings (None = off)
    optional_int_keys = {"download_limit", "upload_limit", "timeout"}

    if key in bool_keys:
        setattr(config, key, value.lower() in ("true", "yes", "1", "on"))
    elif key in optional_int_keys:
        setattr(config, key, None if value.lower() in ("none", "off", "") else int(value))
    elif key == "output_dir":
        config.output_dir = value
    elif key == "port":
        config.port = int(value)
    elif key == "encryption":
        if value not in ("required", "preferred", "tolerated"):
            error_panel("Must be: required, preferred, or tolerated.")
            raise typer.Exit(1)
        config.encryption = value

    save_config(config)
    console.print()
    success_panel(f"{key} is now {getattr(config, key)!r}")
    console.print()


# `torrentor config reset`
@config_app.command()
def reset() -> None:
    """Reset all settings to defaults."""
    save_config(TorrentorConfig())
    console.print()
    success_panel("All settings have been reset to defaults.")
    console.print()


# `torrentor config path`
@config_app.command()
def path() -> None:
    """Show where your settings file is stored."""
    console.print(str(CONFIG_FILE))
