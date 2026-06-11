from pathlib import Path


def is_magnet_link(source: str) -> bool:
    return source.strip().startswith("magnet:?")


def is_torrent_file(source: str) -> bool:
    path = Path(source)
    return path.exists() and path.suffix == ".torrent"


def validate_source(source: str) -> str | None:
    if is_magnet_link(source):
        return "magnet"
    if is_torrent_file(source):
        return "file"
    return None
