"""Persistent config stored as JSON. Location is OS-aware: ~/.config on Unix, %APPDATA% on Windows."""

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Pick the right config home for each OS
if sys.platform == "win32":
    _config_home = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
else:
    _config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

# Where we keep the config file
CONFIG_DIR = _config_home / "torrentor"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class TorrentorConfig:
    """All user-configurable settings with sensible defaults."""

    # Where the final .zip lands
    output_dir: str = field(default_factory=lambda: str(Path.home() / "Downloads"))
    # Speed limits in kB/s — None means no limit
    download_limit: int | None = None
    upload_limit: int | None = None
    # Peer port and encryption preference
    port: int = 51413
    encryption: str = "preferred"
    # Whether to keep sharing the file after download completes
    seed: bool = False
    # Download timeout in seconds — None means no timeout
    timeout: int | None = None
    # Download from beginning to end instead of jumping around
    in_order: bool = False
    # Double-check the file for errors after downloading
    check: bool = False
    # Block known bad peers from connecting
    blocklist: bool = False

    # Turn the dataclass into a plain dict for JSON serialization
    def to_dict(self) -> dict:
        """Serialize the config to a JSON-friendly dict."""
        return asdict(self)


# Read the config from disk, falling back to defaults if something's wrong
def load_config() -> TorrentorConfig:
    """Load config from the config file. Creates it with defaults if missing or broken."""
    # No file yet? Write defaults and return those
    if not CONFIG_FILE.exists():
        config = TorrentorConfig()
        save_config(config)
        return config

    # Try to parse the JSON. If it's corrupted or has wrong types, fall back to defaults.
    try:
        data = json.loads(CONFIG_FILE.read_text())
        # Only keep keys that belong to the dataclass — ignore any junk
        return TorrentorConfig(
            **{k: v for k, v in data.items() if k in TorrentorConfig.__dataclass_fields__}
        )
    except (json.JSONDecodeError, TypeError):
        # Corrupted file — overwrite with defaults
        config = TorrentorConfig()
        save_config(config)
        return config


# Write the config to disk as pretty-printed JSON
def save_config(config: TorrentorConfig) -> None:
    """Persist the given config to the config file."""
    # Ensure the directory exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config.to_dict(), indent=2) + "\n")
