"""Tests for the transmission engine: progress parsing, command building, and install check."""

from unittest.mock import patch

from torrentor.core.config import TorrentorConfig
from torrentor.core.engine import (
    TransmissionEngine,
    is_transmission_installed,
    parse_progress,
)


class TestIsTransmissionInstalled:
    """Verify is_transmission_installed() by mocking shutil.which."""

    def test_installed(self) -> None:
        with patch("torrentor.core.engine.shutil.which", return_value="/usr/bin/transmission-cli"):
            assert is_transmission_installed() is True

    def test_not_installed(self) -> None:
        with patch("torrentor.core.engine.shutil.which", return_value=None):
            assert is_transmission_installed() is False


class TestParseProgress:
    """Verify that parse_progress() extracts data from real-looking transmission-cli output lines."""

    def test_full_progress_line(self) -> None:
        line = "Progress: 45.2%, dl from 3 of 8 peers (1.2 MB/s), ul to 2 (200 kB/s) [T R]"
        result = parse_progress(line)
        assert result is not None
        assert result["progress"] == 45.2
        assert result["peers"] == 8
        assert result["down_speed"] == "1.2 MB/s"
        assert result["up_speed"] == "200 kB/s"

    def test_simple_progress_line(self) -> None:
        line = "Progress: 100.0%"
        result = parse_progress(line)
        assert result is not None
        assert result["progress"] == 100.0

    def test_no_progress(self) -> None:
        line = "Connecting to peers..."
        result = parse_progress(line)
        assert result is None

    def test_zero_progress(self) -> None:
        line = "Progress: 0.0%, dl from 0 of 1 peers (0 kB/s), ul to 0 (0 kB/s)"
        result = parse_progress(line)
        assert result is not None
        assert result["progress"] == 0.0


class TestBuildCommand:
    """Verify that build_command() constructs the right CLI arguments for different configs."""

    def test_default_config(self) -> None:
        engine = TransmissionEngine(TorrentorConfig())
        cmd = engine.build_command("magnet:?xt=abc", "/tmp/dl", "/tmp/finish.sh")

        assert cmd[0] == "transmission-cli"
        assert "-w" in cmd
        assert "/tmp/dl" in cmd
        assert "-f" in cmd
        assert "/tmp/finish.sh" in cmd
        assert "-D" in cmd
        assert "-U" in cmd
        assert cmd[-1] == "magnet:?xt=abc"

    def test_with_limits(self) -> None:
        config = TorrentorConfig(download_limit=1000, upload_limit=500)
        engine = TransmissionEngine(config)
        cmd = engine.build_command("source", "/tmp/dl", "/tmp/f.sh")

        assert "-d" in cmd
        idx = cmd.index("-d")
        assert cmd[idx + 1] == "1000"

        assert "-u" in cmd
        idx = cmd.index("-u")
        assert cmd[idx + 1] == "500"

        assert "-D" not in cmd
        assert "-U" not in cmd

    def test_encryption_required(self) -> None:
        config = TorrentorConfig(encryption="required")
        engine = TransmissionEngine(config)
        cmd = engine.build_command("source", "/tmp/dl", "/tmp/f.sh")
        assert "-er" in cmd

    def test_custom_port(self) -> None:
        config = TorrentorConfig(port=9999)
        engine = TransmissionEngine(config)
        cmd = engine.build_command("source", "/tmp/dl", "/tmp/f.sh")
        assert "-p" in cmd
        idx = cmd.index("-p")
        assert cmd[idx + 1] == "9999"
