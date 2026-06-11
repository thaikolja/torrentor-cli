import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "torrentor"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class TorrentorConfig:
    output_dir: str = field(default_factory=lambda: str(Path.home() / "Downloads"))
    download_limit: int | None = None
    upload_limit: int | None = None
    port: int = 51413
    encryption: str = "preferred"

    def to_dict(self) -> dict:
        return asdict(self)


def load_config() -> TorrentorConfig:
    if not CONFIG_FILE.exists():
        config = TorrentorConfig()
        save_config(config)
        return config

    try:
        data = json.loads(CONFIG_FILE.read_text())
        return TorrentorConfig(
            **{k: v for k, v in data.items() if k in TorrentorConfig.__dataclass_fields__}
        )
    except (json.JSONDecodeError, TypeError):
        config = TorrentorConfig()
        save_config(config)
        return config


def save_config(config: TorrentorConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config.to_dict(), indent=2) + "\n")
