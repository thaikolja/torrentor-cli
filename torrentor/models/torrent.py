"""Dataclass that represents a single torrent during and after download."""

from dataclasses import dataclass


@dataclass
class TorrentInfo:
    """Holds all the runtime info about a torrent: name, speeds, peers, status, etc."""

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
