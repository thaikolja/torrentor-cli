# Contributing to Torrentor

Thanks for your interest in contributing! Here's how to get started.

## Setup

```bash
git clone https://github.com/thaikolja/torrentor-cli.git
cd torrentor-cli
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Development Workflow

1. Create a branch from `main`
2. Make your changes
3. Run the quality checks (all four must pass):

```bash
ruff check .                # lint
ruff format --check .       # format check
mypy torrentor              # type check
pytest                      # tests
```

4. Fix any issues: `ruff check --fix . && ruff format .`
5. Submit a pull request

## Code Style

- Formatted with **ruff** (line length 100)
- Type hints on all function signatures (`disallow_untyped_defs`)
- `X | None` instead of `Optional[X]` (enforced by ruff UP045)
- **RUF001 is intentionally ignored** — the codebase uses Unicode characters for the terminal UI
- **mypy overrides** exist for `torrentor.ui.prompts` and `torrentor.ui.progress` because InquirerPy and Rich have incomplete type stubs

## Testing

Tests live in `tests/` and use **pytest**. Run with coverage:

```bash
pytest --cov=torrentor --cov-report=term-missing
```

When adding a feature, add tests for the happy path, edge cases, and error conditions.

## Project Structure

```
torrentor/
  cli.py          # Typer app, commands, interactive mode
  ui/             # Rich panels, prompts, progress, theme, effects
  core/           # Engine, config, post-processing, validators
  models/         # Data models
tests/            # pytest test suite
```

## Cross-Platform Notes

- Config path uses `%APPDATA%` on Windows, `~/.config` on Unix
- Process termination uses `process.terminate()` (works on all OSes)
- Terminal effects use Rich's `Live` display (no raw ANSI escapes)
- Test and verify on macOS, Linux, and Windows when possible
