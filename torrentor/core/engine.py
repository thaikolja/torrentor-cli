"""Runs transmission-cli as a subprocess, monitors progress, and stops seeding when done."""

import re
import shutil
import signal
import stat
import subprocess
import tempfile
import threading
from collections.abc import Callable
from pathlib import Path

from torrentor.core.config import TorrentorConfig

# Binary we shell out to
TRANSMISSION_BIN = "transmission-cli"
TRANSMISSION_URL = "https://transmissionbt.com/download"

# Regexes to parse progress lines like: "Progress: 45.2%, dl from 3 of 8 peers (1.2 MB/s), ul to 2 (200 kB/s)"
PROGRESS_RE = re.compile(
    r"Progress:\s*([\d.]+)%.*?"
    r"dl from \d+ of (\d+) peers \(([\d.]+ [A-Za-z/]+)\).*?"
    r"ul to \d+ \(([\d.]+ [A-Za-z/]+)\)",
    re.IGNORECASE,
)

# Fallback regex when we only get the percentage
PROGRESS_SIMPLE_RE = re.compile(
    r"Progress:\s*([\d.]+)%",
    re.IGNORECASE,
)


# Check whether transmission-cli is available on the PATH
def is_transmission_installed() -> bool:
    """Return True if transmission-cli can be found on $PATH."""
    return shutil.which(TRANSMISSION_BIN) is not None


# Extract download progress info from a single line of transmission-cli stdout
def parse_progress(line: str) -> dict | None:
    """Parse a transmission-cli output line and return progress/peers/speeds, or None if irrelevant."""
    # Try the full regex first (peers + speeds)
    match = PROGRESS_RE.search(line)
    if match:
        return {
            "progress": float(match.group(1)),
            "peers": int(match.group(2)),
            "down_speed": match.group(3),
            "up_speed": match.group(4),
        }
    # Fall back to just the percentage
    simple = PROGRESS_SIMPLE_RE.search(line)
    if simple:
        return {
            "progress": float(simple.group(1)),
            "peers": 0,
            "down_speed": "—",
            "up_speed": "—",
        }
    return None


class TransmissionEngine:
    """Manages a transmission-cli subprocess: start, monitor progress, stop on completion."""

    def __init__(self, config: TorrentorConfig | None = None):
        self.config = config or TorrentorConfig()
        self._process: subprocess.Popen | None = None  # type: ignore[type-arg]
        self._temp_dir: Path | None = None

    @property
    def temp_dir(self) -> Path | None:
        """The temp directory where files are downloaded — useful for cleanup later."""
        return self._temp_dir

    # Build the list of CLI args for transmission-cli
    def build_command(self, source: str, download_dir: str, finish_script: str) -> list[str]:
        """Assemble the transmission-cli command with all relevant flags."""
        # Always start with the binary name
        cmd = [TRANSMISSION_BIN]
        # Where to save and what script to run on completion
        cmd.extend(["-w", download_dir])
        cmd.extend(["-f", finish_script])

        # Speed limits — use -D/-U flags to disable when no limit is set
        if self.config.download_limit is not None:
            cmd.extend(["-d", str(self.config.download_limit)])
        else:
            cmd.append("-D")

        if self.config.upload_limit is not None:
            cmd.extend(["-u", str(self.config.upload_limit)])
        else:
            cmd.append("-U")

        # Encryption preference maps to three possible flags
        encryption_map = {
            "required": "-er",
            "preferred": "-ep",
            "tolerated": "-et",
        }
        if self.config.encryption in encryption_map:
            cmd.append(encryption_map[self.config.encryption])

        # Port and the actual torrent source always go last
        cmd.extend(["-p", str(self.config.port)])
        cmd.append(source)
        return cmd

    # The main download loop: spawn transmission-cli, watch progress, return when done
    def download(
        self,
        source: str,
        on_progress: Callable[[dict], None] | None = None,
    ) -> Path:
        """Download a torrent, calling on_progress with speed/peer updates, then return the data path."""
        # Set up a temp directory for the raw download
        self._temp_dir = Path(tempfile.mkdtemp(prefix="torrentor-"))
        download_dir = self._temp_dir / "data"
        download_dir.mkdir()

        # Create a finish script that touches a marker file — transmission-cli runs this when done
        marker = self._temp_dir / ".done"
        finish_script = self._temp_dir / "finish.sh"
        finish_script.write_text(f"#!/bin/sh\ntouch '{marker}'\n")
        finish_script.chmod(finish_script.stat().st_mode | stat.S_IEXEC)

        cmd = self.build_command(source, str(download_dir), str(finish_script))

        # Fire up transmission-cli and pipe its stdout so we can read progress
        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # A background thread watches for the marker file
        done_event = threading.Event()

        def _watch_marker() -> None:
            while not done_event.is_set():
                if marker.exists():
                    done_event.set()
                    return
                done_event.wait(0.5)

        watcher = threading.Thread(target=_watch_marker, daemon=True)
        watcher.start()

        # Read stdout line by line, parse progress, and check if we're done
        try:
            assert self._process.stdout is not None
            for line in self._process.stdout:
                line = line.strip()
                if not line:
                    continue
                # Feed each line to the progress callback if one was provided
                if on_progress:
                    info = parse_progress(line)
                    if info:
                        on_progress(info)
                # Marker appeared? Stop reading output
                if done_event.is_set():
                    break
        except KeyboardInterrupt:
            # User hit Ctrl+C — clean up everything
            self.abort()
            raise

        # Wait for the marker and kill the process
        done_event.wait(timeout=5)
        self._stop_process()

        return download_dir

    # Send SIGTERM to the subprocess, kill if it doesn't respond
    def _stop_process(self) -> None:
        """Gracefully stop the transmission-cli process (SIGTERM, then SIGKILL if stubborn)."""
        if self._process is None:
            return
        try:
            self._process.send_signal(signal.SIGTERM)
            self._process.wait(timeout=10)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                self._process.kill()
                self._process.wait(timeout=5)
            except (ProcessLookupError, OSError):
                pass
        self._process = None

    # Emergency cleanup: kill the process and remove the temp directory
    def abort(self) -> None:
        """Terminate the subprocess and delete the temp download directory."""
        self._stop_process()
        if self._temp_dir and self._temp_dir.exists():
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            self._temp_dir = None
