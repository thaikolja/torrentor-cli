from pathlib import Path

from torrentor.core.validators import is_magnet_link, is_torrent_file, validate_source


class TestIsMagnetLink:
    def test_valid_magnet(self) -> None:
        assert is_magnet_link("magnet:?xt=urn:btih:abc123") is True

    def test_valid_magnet_with_whitespace(self) -> None:
        assert is_magnet_link("  magnet:?xt=urn:btih:abc123  ") is True

    def test_invalid_magnet(self) -> None:
        assert is_magnet_link("https://example.com") is False

    def test_empty_string(self) -> None:
        assert is_magnet_link("") is False

    def test_partial_magnet(self) -> None:
        assert is_magnet_link("magnet:") is False


class TestIsTorrentFile:
    def test_existing_torrent_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.torrent"
        f.write_bytes(b"data")
        assert is_torrent_file(str(f)) is True

    def test_nonexistent_torrent_file(self) -> None:
        assert is_torrent_file("/nonexistent/file.torrent") is False

    def test_wrong_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_bytes(b"data")
        assert is_torrent_file(str(f)) is False


class TestValidateSource:
    def test_magnet_source(self) -> None:
        assert validate_source("magnet:?xt=urn:btih:abc") == "magnet"

    def test_torrent_file_source(self, tmp_path: Path) -> None:
        f = tmp_path / "test.torrent"
        f.write_bytes(b"data")
        assert validate_source(str(f)) == "file"

    def test_invalid_source(self) -> None:
        assert validate_source("https://example.com") is None

    def test_empty_source(self) -> None:
        assert validate_source("") is None
