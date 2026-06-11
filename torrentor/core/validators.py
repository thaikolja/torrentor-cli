"""Helpers that figure out whether the user passed a magnet link or a .torrent file path."""

from pathlib import Path


# Check if a string looks like a magnet URI
def is_magnet_link(source: str) -> bool:
    """Return True if the string starts with 'magnet:?'."""
    return source.strip().startswith("magnet:?")


# Check if a path exists and ends with .torrent
def is_torrent_file(source: str) -> bool:
    """Return True if the string is a path to an existing .torrent file."""
    path = Path(source)
    return path.exists() and path.suffix == ".torrent"


# Returns "magnet", "file", or None depending on what the source looks like
def validate_source(source: str) -> str | None:
    """Classify a source string — returns 'magnet', 'file', or None if invalid."""
    if is_magnet_link(source):
        return "magnet"
    if is_torrent_file(source):
        return "file"
    return None
