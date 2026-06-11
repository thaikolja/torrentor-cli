from dataclasses import dataclass


@dataclass
class TorrentInfo:
    name: str
    source: str
    source_type: str
    size: str = "Unknown"
    progress: float = 0.0
    download_speed: str = "0 B/s"
    upload_speed: str = "0 B/s"
    peers: int = 0
    eta: str = "—"
    status: str = "queued"
