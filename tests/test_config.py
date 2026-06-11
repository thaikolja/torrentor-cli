"""Tests for config persistence: dataclass defaults, load/save roundtrip, corrupted data handling."""

import json
from pathlib import Path
from unittest.mock import patch

from torrentor.core.config import TorrentorConfig, load_config, save_config


class TestTorrentorConfig:
    """Verify the TorrentorConfig dataclass defaults and serialization."""

    def test_defaults(self) -> None:
        config = TorrentorConfig()
        assert config.output_dir == str(Path.home() / "Downloads")
        assert config.download_limit is None
        assert config.upload_limit is None
        assert config.port == 51413
        assert config.encryption == "preferred"

    def test_to_dict(self) -> None:
        config = TorrentorConfig(output_dir="/tmp/test", port=9999)
        d = config.to_dict()
        assert d["output_dir"] == "/tmp/test"
        assert d["port"] == 9999
        assert d["download_limit"] is None

    def test_custom_values(self) -> None:
        config = TorrentorConfig(
            output_dir="/custom",
            download_limit=1000,
            upload_limit=500,
            port=12345,
            encryption="required",
        )
        assert config.download_limit == 1000
        assert config.encryption == "required"


class TestLoadSaveConfig:
    """Verify reading and writing the config file, including edge cases."""

    def test_save_and_load(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.json"
        config_dir = tmp_path

        with (
            patch("torrentor.core.config.CONFIG_FILE", config_file),
            patch("torrentor.core.config.CONFIG_DIR", config_dir),
        ):
            original = TorrentorConfig(output_dir="/test/dir", port=9999)
            save_config(original)

            loaded = load_config()
            assert loaded.output_dir == "/test/dir"
            assert loaded.port == 9999

    def test_load_creates_default_on_missing(self, tmp_path: Path) -> None:
        config_file = tmp_path / "nonexistent" / "config.json"
        config_dir = tmp_path / "nonexistent"

        with (
            patch("torrentor.core.config.CONFIG_FILE", config_file),
            patch("torrentor.core.config.CONFIG_DIR", config_dir),
        ):
            config = load_config()
            assert config.port == 51413
            assert config_file.exists()

    def test_load_handles_corrupted_json(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.json"
        config_file.write_text("{invalid json!!")

        with (
            patch("torrentor.core.config.CONFIG_FILE", config_file),
            patch("torrentor.core.config.CONFIG_DIR", tmp_path),
        ):
            config = load_config()
            assert config.port == 51413

    def test_load_ignores_unknown_keys(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "output_dir": "/custom",
                    "unknown_key": "value",
                    "port": 8888,
                }
            )
        )

        with (
            patch("torrentor.core.config.CONFIG_FILE", config_file),
            patch("torrentor.core.config.CONFIG_DIR", tmp_path),
        ):
            config = load_config()
            assert config.output_dir == "/custom"
            assert config.port == 8888
