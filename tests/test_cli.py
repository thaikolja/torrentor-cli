"""Smoke tests for the CLI: help output, version flag, config subcommands, and source validation."""

from typer.testing import CliRunner

from torrentor import __version__
from torrentor.cli import app

runner = CliRunner()


class TestVersion:
    """Check that --version and -V print the version string."""

    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_version_short_flag(self) -> None:
        result = runner.invoke(app, ["-V"])
        assert result.exit_code == 0
        assert "torrentor" in result.output


class TestHelp:
    """Check that -h shows all flag sections and commands."""

    def test_main_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "config" in result.output
        assert "--save-to" in result.output

    def test_main_help_short(self) -> None:
        result = runner.invoke(app, ["-h"])
        assert result.exit_code == 0
        assert "config" in result.output

    def test_main_help_shows_all_sections(self) -> None:
        result = runner.invoke(app, ["-h"])
        assert result.exit_code == 0
        assert "Options" in result.output
        assert "Optional" in result.output
        assert "Advanced" in result.output

    def test_main_help_shows_all_flags(self) -> None:
        result = runner.invoke(app, ["-h"])
        assert result.exit_code == 0
        assert "--save-to" in result.output
        assert "--max-download" in result.output
        assert "--max-upload" in result.output
        assert "--no-limit" in result.output
        assert "--timeout" in result.output
        assert "--seed" in result.output
        assert "--in-order" in result.output
        assert "--check" in result.output
        assert "--port" in result.output
        assert "--encryption" in result.output
        assert "--blocklist" in result.output

    def test_integer_shown_as_number(self) -> None:
        result = runner.invoke(app, ["-h"])
        assert "NUMBER" in result.output
        assert "INTEGER" not in result.output

    def test_config_help(self) -> None:
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "set" in result.output
        assert "reset" in result.output
        assert "path" in result.output


class TestConfigCommands:
    """Check that the config subcommands work as expected."""

    def test_config_path(self) -> None:
        result = runner.invoke(app, ["config", "path"])
        assert result.exit_code == 0
        assert "config.json" in result.output

    def test_config_show(self) -> None:
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Save files to" in result.output

    def test_config_set_invalid_key(self) -> None:
        result = runner.invoke(app, ["config", "set", "nonexistent", "value"])
        assert result.exit_code == 1

    def test_config_reset(self) -> None:
        result = runner.invoke(app, ["config", "reset"])
        assert result.exit_code == 0


class TestAddValidation:
    """Check that invalid sources are rejected."""

    def test_add_invalid_source_via_hidden_alias(self) -> None:
        result = runner.invoke(app, ["add", "not-a-valid-source"])
        assert result.exit_code == 1
