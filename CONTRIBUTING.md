# Contributing to Torrentor

Thanks for your interest in contributing! Here's how to get started.

## Setup

```bash
git clone https://github.com/your-username/torrentor-cli.git
cd torrentor-cli
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Development Workflow

1. Create a branch from `main`
2. Make your changes
3. Run the quality checks:

```bash
ruff check .                # lint
ruff format --check .       # format check
mypy torrentor              # type check
pytest                      # tests
```

4. Fix any issues, then submit a pull request

## Code Style

- Formatted with **ruff** (line length 100)
- Type hints on all function signatures
- No comments unless absolutely necessary for non-obvious logic
- Follow existing patterns in the codebase

## Testing

Tests live in `tests/` and use **pytest**. Run with coverage:

```bash
pytest --cov=torrentor --cov-report=term-missing
```

When adding a new feature, add corresponding tests covering:
- Happy path
- Edge cases
- Error conditions

## Project Structure

```
torrentor/
  cli.py          # Typer app, commands, interactive mode
  ui/             # Rich panels, prompts, progress, theme
  core/           # Engine, config, post-processing, validators
  models/         # Data models
tests/            # pytest test suite
```

## Commit Messages

Use clear, imperative-mood messages:

```
Add magnet link validation
Fix zip compression for single files
Update config schema with output_dir
```
