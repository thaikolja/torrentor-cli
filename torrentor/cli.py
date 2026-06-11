"""Typer CLI app: torrentor <source> downloads directly, torrentor launches interactive mode."""

import time
from pathlib import Path
from urllib.parse import unquote_plus

import typer
from rich.progress import TaskID
from typer.main import TyperGroup

from torrentor import __author__, __version__
from torrentor.core.config import CONFIG_FILE, TorrentorConfig, load_config, save_config
from torrentor.core.engine import (
    TransmissionEngine,
    format_speed,
    is_transmission_installed,
    parse_speed_kbps,
)
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
    slow_download_warning,
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
    timeout_input,
    toggle_input,
)
from torrentor.ui.theme import CYAN, DIM, console

# How long to wait before checking if the download is slow (in seconds)
_SLOW_CHECK_DELAY = 90
# Speed below this (in kB/s) is considered slow
_SLOW_THRESHOLD_KBPS = 10.0


# Custom group that treats unknown first args as a torrent source, not a subcommand
class _SourceGroup(TyperGroup):
    """When the first positional arg isn't a known command, pass it through as ctx.args."""

    def invoke(self, ctx: typer.Context) -> object:  # type: ignore[override]
        """Check if the first arg is a known command; if not, invoke the callback directly."""
        args = [*ctx._protected_args, *ctx.args]
        cmd_name = args[0] if args else None
        if cmd_name and cmd_name in (self.commands or {}):
            return super().invoke(ctx)
        if cmd_name:
            ctx.args = list(args)
            ctx._protected_args = []
        return TyperGroup.__mro__[1].invoke(self, ctx)  # type: ignore[attr-defined]


# Main Typer app and its nested config sub-app
app = typer.Typer(
    name="torrentor",
    cls=_SourceGroup,
    help=(
        "Download torrents from the command line: easy, fast, cross-platform.\n\n"
        "Pass a magnet link or .torrent file (path or URL) to start downloading:\n"
        '  torrentor "magnet:?xt=urn:btih:..."\n\n'
        "Run without arguments for interactive mode."
    ),
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "allow_extra_args": True,
        "allow_interspersed_args": False,
    },
)

config_app = typer.Typer(
    help="View and change your torrentor settings.",
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)
app.add_typer(config_app, name="config")


# ── Helpers ──


# When the user passes --version / -V, print the version and bail
def _version_callback(value: bool) -> None:
    """Print the current version and exit."""
    if value:
        console.print(f"[bold {CYAN}]torrentor[/] [dim]v{__version__}[/]")
        console.print(f"[dim]by {__author__}[/]")
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


# Check if an engine's cache actually contains downloaded data
def _has_cache_data(engine: TransmissionEngine | None) -> bool:
    """Return True if the engine has a temp dir with actual files in it."""
    if engine is None or engine.temp_dir is None:
        return False
    data_dir = engine.temp_dir / "data"
    if not data_dir.exists():
        return False
    return any(not f.name.startswith(".") for f in data_dir.iterdir())


# Valid boolean string values the user can pass to TRUE/FALSE flags
_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


# Parse a "true"/"false" string flag into a Python bool, with validation
def _parse_bool(value: str, flag_name: str = "") -> bool:
    """Turn a CLI string like 'true'/'false' into a bool. Exits with an error for invalid input."""
    lower = value.lower()
    if lower in _BOOL_TRUE:
        return True
    if lower in _BOOL_FALSE:
        return False
    hint = f" for {flag_name}" if flag_name else ""
    error_panel(f"'{value}' is not a valid value{hint}. Use true or false.")
    raise typer.Exit(1)


# Apply CLI flag overrides to a config object
def _apply_flags(
    config: TorrentorConfig,
    *,
    save_to: str | None,
    max_download: int | None,
    max_upload: int | None,
    no_limit: str | None,
    timeout: int | None,
    seed: str | None,
    in_order: str | None,
    check_file: str | None,
    port: int | None,
    encryption: str | None,
    blocklist: str | None,
) -> None:
    """Merge CLI flags into a config, skipping anything the user didn't pass."""
    if save_to:
        config.output_dir = save_to
    if max_download is not None:
        config.download_limit = max_download
    if max_upload is not None:
        config.upload_limit = max_upload
    if no_limit is not None and _parse_bool(no_limit, "--no-limit"):
        config.download_limit = None
        config.upload_limit = None
    if timeout is not None:
        config.timeout = timeout
    if seed is not None:
        config.seed = _parse_bool(seed, "--seed")
    if in_order is not None:
        config.in_order = _parse_bool(in_order, "--in-order")
    if check_file is not None:
        config.check = _parse_bool(check_file, "--check")
    if port is not None:
        config.port = port
    if encryption:
        config.encryption = encryption
    if blocklist is not None:
        config.blocklist = _parse_bool(blocklist, "--blocklist")


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
        error_panel(
            "That doesn't look like a valid magnet link or .torrent file — please try again"
        )
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

    # Track elapsed time and whether we've already shown the slow-download warning
    download_start = time.monotonic()
    slow_warned = False

    # This callback gets called by the engine on every progress update
    def on_progress(info: dict) -> None:
        nonlocal task_id, slow_warned
        pct = info.get("progress", 0.0)

        # Parse raw speed strings and re-format with auto-scaling units
        down_kbps = parse_speed_kbps(info.get("down_speed", "—"))
        up_kbps = parse_speed_kbps(info.get("up_speed", "—"))
        fields = {
            "down": format_speed(down_kbps),
            "up": format_speed(up_kbps),
            "peers": info.get("peers", 0),
        }

        if task_id is None:
            # First progress update — replace the connecting task with real data
            task_id = progress.add_task(task_label, total=100, completed=pct, **fields)
        else:
            progress.update(task_id, completed=pct, **fields)

        # After 90 seconds, check if the download is unusually slow
        elapsed = time.monotonic() - download_start
        if (
            not slow_warned
            and elapsed > _SLOW_CHECK_DELAY
            and (down_kbps < _SLOW_THRESHOLD_KBPS or pct < 1.0)
        ):
            slow_download_warning()
            slow_warned = True

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


# ── Main callback: handles both direct download and interactive mode ──
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    # ── Options (vital) ──
    save_to: str | None = typer.Option(
        None,
        "--save-to",
        "-o",
        metavar="PATH",
        help="Where to save the downloaded file (Default: ~/Downloads)",
    ),
    no_limit: str | None = typer.Option(
        None,
        "--no-limit",
        "-n",
        metavar="TRUE/FALSE",
        help="Download and upload at full speed (Default: false)",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit",
        callback=_version_callback,
        is_eager=True,
    ),
    # ── Optional ──
    max_download: int | None = typer.Option(
        None,
        "--max-download",
        "-l",
        metavar="NUMBER",
        help="Limit how fast the file downloads, in kB/s (Default: no limit)",
        rich_help_panel="Optional",
    ),
    max_upload: int | None = typer.Option(
        None,
        "--max-upload",
        "-u",
        metavar="NUMBER",
        help="Limit how fast you share with others, in kB/s (Default: no limit)",
        rich_help_panel="Optional",
    ),
    timeout: int | None = typer.Option(
        None,
        "--timeout",
        "-t",
        metavar="NUMBER",
        help="Stop if the download takes longer than this, in seconds (Default: none)",
        rich_help_panel="Optional",
    ),
    # ── Advanced ──
    seed: str | None = typer.Option(
        None,
        "--seed",
        "-s",
        metavar="TRUE/FALSE",
        help="Keep sharing the file after it finishes downloading (Default: false)",
        rich_help_panel="Advanced",
    ),
    in_order: str | None = typer.Option(
        None,
        "--in-order",
        "-q",
        metavar="TRUE/FALSE",
        help="Download from beginning to end instead of jumping around (Default: false)",
        rich_help_panel="Advanced",
    ),
    check_file: str | None = typer.Option(
        None,
        "--check",
        "-y",
        metavar="TRUE/FALSE",
        help="Double-check the downloaded file for errors (Default: false)",
        rich_help_panel="Advanced",
    ),
    port: int | None = typer.Option(
        None,
        "--port",
        "-p",
        metavar="NUMBER",
        help="Network port for connecting to other peers (Default: 51413)",
        rich_help_panel="Advanced",
    ),
    encryption: str | None = typer.Option(
        None,
        "--encryption",
        "-e",
        metavar="MODE",
        help="Connection privacy: required, preferred, or tolerated (Default: preferred)",
        rich_help_panel="Advanced",
    ),
    blocklist: str | None = typer.Option(
        None,
        "--blocklist",
        "-b",
        metavar="TRUE/FALSE",
        help="Block known bad peers from connecting (Default: false)",
        rich_help_panel="Advanced",
    ),
) -> None:
    # If a subcommand was invoked (like "config"), let it handle things
    if ctx.invoked_subcommand is not None:
        return

    # Pick up the source from any extra positional args (magnet link or .torrent path)
    source = ctx.args[0] if ctx.args else None

    # Source provided → download directly
    if source:
        _require_transmission()
        show_banner()
        config = load_config()
        _apply_flags(
            config,
            save_to=save_to,
            max_download=max_download,
            max_upload=max_upload,
            no_limit=no_limit,
            timeout=timeout,
            seed=seed,
            in_order=in_order,
            check_file=check_file,
            port=port,
            encryption=encryption,
            blocklist=blocklist,
        )
        success, engine = _run_download(source, config)
        if not success:
            if engine:
                engine.abort()
            raise typer.Exit(1)
        return

    # No source → launch interactive mode
    _interactive_mode()


# ── Hidden alias: `torrentor add <source>` still works for backward compatibility ──
@app.command(hidden=True)
def add(
    source: str = typer.Argument(..., help="Magnet link, .torrent file path, or URL."),
    save_to: str | None = typer.Option(None, "--save-to", "-o", metavar="PATH"),
    max_download: int | None = typer.Option(None, "--max-download", "-l", metavar="NUMBER"),
    max_upload: int | None = typer.Option(None, "--max-upload", "-u", metavar="NUMBER"),
    no_limit: str | None = typer.Option(None, "--no-limit", "-n", metavar="TRUE/FALSE"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", metavar="NUMBER"),
    seed: str | None = typer.Option(None, "--seed", "-s", metavar="TRUE/FALSE"),
    in_order: str | None = typer.Option(None, "--in-order", "-q", metavar="TRUE/FALSE"),
    check_file: str | None = typer.Option(None, "--check", "-y", metavar="TRUE/FALSE"),
    port: int | None = typer.Option(None, "--port", "-p", metavar="NUMBER"),
    encryption: str | None = typer.Option(None, "--encryption", "-e", metavar="MODE"),
    blocklist: str | None = typer.Option(None, "--blocklist", "-b", metavar="TRUE/FALSE"),
) -> None:
    """Download a torrent (same as: torrentor <source>)."""
    _require_transmission()
    show_banner()
    config = load_config()
    _apply_flags(
        config,
        save_to=save_to,
        max_download=max_download,
        max_upload=max_upload,
        no_limit=no_limit,
        timeout=timeout,
        seed=seed,
        in_order=in_order,
        check_file=check_file,
        port=port,
        encryption=encryption,
        blocklist=blocklist,
    )
    success, engine = _run_download(source, config)
    if not success:
        if engine:
            engine.abort()
        raise typer.Exit(1)


# ── Interactive mode ──
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

        # Validation failed (no engine created) — ask for a new source instead of retrying the same one
        if engine is None:
            resume_dir = None
            console.print()
            try:
                if method == "magnet":
                    new_source = magnet_input()
                elif method == "file":
                    new_source = file_input()
                else:
                    return
            except (KeyboardInterrupt, EOFError):
                return
            if not new_source:
                return
            source = new_source
            continue

        # Download actually started but failed — cache options only shown when data exists
        has_cache = _has_cache_data(engine)
        console.print()
        try:
            action = post_download_menu(has_cache=has_cache)
        except (KeyboardInterrupt, EOFError):
            if engine:
                engine.abort()
            return

        if action == "retry_cache":
            resume_dir = engine.temp_dir if engine else None
        elif action == "retry":
            if engine:
                engine.abort()
            resume_dir = None
        elif action == "cancel_keep":
            return
        else:
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
            elif choice == "timeout":
                config.timeout = timeout_input(config.timeout)
            elif choice == "port":
                config.port = port_input(config.port)
            elif choice == "encryption":
                config.encryption = encryption_select(config.encryption)
            elif choice == "seed":
                config.seed = toggle_input("Keep sharing after download", config.seed)
            elif choice == "in_order":
                config.in_order = toggle_input("Download in order", config.in_order)
            elif choice == "check":
                config.check = toggle_input("Check file for errors", config.check)
            elif choice == "blocklist":
                config.blocklist = toggle_input("Block bad peers", config.blocklist)

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
