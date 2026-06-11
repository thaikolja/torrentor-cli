# Torrentor CLI

[![PyPI Version](https://img.shields.io/pypi/v/torrentor?style=rounded)](https://pypi.org/project/torrentor/) [![Python Versions](https://img.shields.io/pypi/pyversions/torrentor?style=rounded&logo=python&logoColor=white)](https://pypi.org/project/torrentor/) [![License](https://img.shields.io/github/license/thaikolja/torrentor-cli?style=rounded)](https://github.com/thaikolja/torrentor-cli/blob/main/LICENSE) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=rounded)](https://github.com/astral-sh/ruff)

A beautiful CLI torrent client powered by `transmission-cli`.
Download torrents, auto-stop seeding, and get a neatly zipped + slugified output file – all from your terminal.

```
╺┳╸┏━┓┏━┓┏━┓┏━╸┏┓╻╺┳╸┏━┓┏━┓
 ┃ ┃ ┃┣┳┛┣┳┛┣╸ ┃┗┫ ┃ ┃ ┃┣┳┛
 ╹ ┗━┛╹┗╸╹┗╸┗━╸╹ ╹ ╹ ┗━┛╹┗╸
```

## Features

- **Two modes** — interactive (guided menus) or direct (flags & args)
- **Magnet links & .torrent files** — both supported
- **Auto-stop seeding** — process terminates once download completes
- **Post-processing** — downloaded files are zipped (light compression) with slugified filenames
- **Persistent config** — output directory, speed limits, port, encryption — all remembered
- **Beautiful UI** — Rich panels, progress bars, InquirerPy interactive prompts

## Requirements

- Python 3.10+
- [`transmission-cli`](https://transmissionbt.com/download)

```bash
# macOS
brew install transmission-cli

# Debian / Ubuntu
sudo apt install transmission-cli

# Arch Linux
sudo pacman -S transmission-cli
```

## Installation

```bash
git clone https://github.com/your-username/torrentor-cli.git
cd torrentor-cli
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

### Interactive Mode

```bash
torrentor
```

Launches a guided menu to add torrents, view settings, and more.

### Direct Mode

```bash
# Add via magnet link
torrentor add "magnet:?xt=urn:btih:..."

# Add via .torrent file
torrentor add ./ubuntu.torrent

# With options
torrentor add "magnet:..." -o ~/Movies -l 5000

# Remove speed limits for this download
torrentor add "magnet:..." --no-limit
```

### Configuration

```bash
# View current config
torrentor config

# Change output directory
torrentor config set output_dir ~/Movies

# Set download speed limit (kB/s)
torrentor config set download_limit 5000

# Remove a limit
torrentor config set upload_limit none

# Reset everything to defaults
torrentor config reset

# Find your config file
torrentor config path
```

Config is stored at `~/.config/torrentor/config.json`.

### UI Demo

```bash
torrentor demo
```

Showcases all UI elements with mock data — great for seeing the interface without downloading anything.

## How It Works

1. You provide a magnet link or `.torrent` file
2. `transmission-cli` downloads the torrent to a temp directory
3. Once complete, seeding stops automatically
4. Downloaded files are zipped with light compression
5. The zip filename is slugified (`"My Movie! (2024)"` → `my-movie-2024.zip`)
6. The `.zip` is moved to your configured output directory
7. Temp files are cleaned up

## Development

```bash
pip install -e ".[dev]"

ruff check .            # lint
ruff format --check .   # format check
mypy torrentor          # type check
pytest                  # tests
pytest --cov=torrentor  # tests with coverage
```

## License

[MIT](LICENSE)
