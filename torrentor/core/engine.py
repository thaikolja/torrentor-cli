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

TRANSMISSION_BIN = "transmission-cli"
TRANSMISSION_URL = "https://transmissionbt.com/download"

PROGRESS_RE = re.compile(
    r"Progress:\s*([\d.]+)%.*?"
    r"dl from \d+ of (\d+) peers \(([\d.]+ [A-Za-z/]+)\).*?"
    r"ul to \d+ \(([\d.]+ [A-Za-z/]+)\)",
    re.IGNORECASE,
)

PROGRESS_SIMPLE_RE = re.compile(
    r"Progress:\s*([\d.]+)%",
    re.IGNORECASE,
)


def is_transmission_installed() -> bool:
    return shutil.which(TRANSMISSION_BIN) is not None


def parse_progress(line: str) -> dict | None:
    match = PROGRESS_RE.search(line)
    if match:
        return {
            "progress": float(match.group(1)),
            "peers": int(match.group(2)),
            "down_speed": match.group(3),
            "up_speed": match.group(4),
        }
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
    def __init__(self, config: TorrentorConfig | None = None):
        self.config = config or TorrentorConfig()
        self._process: subprocess.Popen | None = None  # type: ignore[type-arg]
        self._temp_dir: Path | None = None

    @property
    def temp_dir(self) -> Path | None:
        return self._temp_dir

    def build_command(self, source: str, download_dir: str, finish_script: str) -> list[str]:
        cmd = [TRANSMISSION_BIN]
        cmd.extend(["-w", download_dir])
        cmd.extend(["-f", finish_script])

        if self.config.download_limit is not None:
            cmd.extend(["-d", str(self.config.download_limit)])
        else:
            cmd.append("-D")

        if self.config.upload_limit is not None:
            cmd.extend(["-u", str(self.config.upload_limit)])
        else:
            cmd.append("-U")

        encryption_map = {
            "required": "-er",
            "preferred": "-ep",
            "tolerated": "-et",
        }
        if self.config.encryption in encryption_map:
            cmd.append(encryption_map[self.config.encryption])

        cmd.extend(["-p", str(self.config.port)])
        cmd.append(source)
        return cmd

    def download(
        self,
        source: str,
        on_progress: Callable[[dict], None] | None = None,
    ) -> Path:
        self._temp_dir = Path(tempfile.mkdtemp(prefix="torrentor-"))
        download_dir = self._temp_dir / "data"
        download_dir.mkdir()

        marker = self._temp_dir / ".done"
        finish_script = self._temp_dir / "finish.sh"
        finish_script.write_text(f"#!/bin/sh\ntouch '{marker}'\n")
        finish_script.chmod(finish_script.stat().st_mode | stat.S_IEXEC)

        cmd = self.build_command(source, str(download_dir), str(finish_script))

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        done_event = threading.Event()

        def _watch_marker() -> None:
            while not done_event.is_set():
                if marker.exists():
                    done_event.set()
                    return
                done_event.wait(0.5)

        watcher = threading.Thread(target=_watch_marker, daemon=True)
        watcher.start()

        try:
            assert self._process.stdout is not None
            for line in self._process.stdout:
                line = line.strip()
                if not line:
                    continue
                if on_progress:
                    info = parse_progress(line)
                    if info:
                        on_progress(info)
                if done_event.is_set():
                    break
        except KeyboardInterrupt:
            self.abort()
            raise

        done_event.wait(timeout=5)
        self._stop_process()

        return download_dir

    def _stop_process(self) -> None:
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

    def abort(self) -> None:
        self._stop_process()
        if self._temp_dir and self._temp_dir.exists():
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            self._temp_dir = None
