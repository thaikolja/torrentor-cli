[![PyPI Version](https://img.shields.io/pypi/v/torrentor?style=rounded)](https://pypi.org/project/torrentor/) [![Release](https://img.shields.io/github/v/release/thaikolja/torrentor-cli?style=rounded)](https://github.com/thaikolja/torrentor-cli/releases) [![Python Versions](https://img.shields.io/pypi/pyversions/torrentor?style=rounded&logo=python&logoColor=white)](https://pypi.org/project/torrentor/) [![License](https://img.shields.io/github/license/thaikolja/torrentor-cli?style=rounded)](https://github.com/thaikolja/torrentor-cli/blob/main/LICENSE) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=rounded)](https://github.com/astral-sh/ruff)

# torrentor

Download [torrent](https://en.wikipedia.org/wiki/BitTorrent) files from your terminal: no complicated setup, works on **macOS**, **Linux**, and **Windows**.

```
╺┳╸┏━┓┏━┓┏━┓┏━╸┏┓╻╺┳╸┏━┓┏━┓
 ┃ ┃ ┃┣┳┛┣┳┛┣╸ ┃┗┫ ┃ ┃ ┃┣┳┛
 ╹ ┗━┛╹┗╸╹┗╸┗━╸╹ ╹ ╹ ┗━┛╹┗╸
```

## What It Does

1. You give it a [magnet link](https://en.wikipedia.org/wiki/Magnet_URI_scheme), a [`.torrent` file](https://en.wikipedia.org/wiki/Torrent_file), or a URL to one
2. It downloads the file using [`transmission-cli`](https://transmissionbt.com/) in the background
3. When the download is done, it automatically stops [seeding](https://en.wikipedia.org/wiki/Seeding_(computing)) (sharing)
4. It packs everything into a `.zip` file with a clean, [URL-friendly filename](https://en.wikipedia.org/wiki/Clean_URL#Slug)
5. The `.zip` is saved to your chosen folder, and the temp files are cleaned up

## What You Need

- **Python 3.10 or newer**: [download here](https://www.python.org/downloads/) if you don't have it
- **transmission-cli**: this is the download engine that runs in the background

### Installing Transmission-CLI

<details>
<summary><strong>macOS</strong></summary>

Using [Homebrew](https://brew.sh/) (recommended):

```bash
# Install transmission-cli on macOS using Homebrew
brew install transmission-cli
```

Using [MacPorts](https://www.macports.org/):

```bash
# Install transmission on macOS using MacPorts
sudo port install transmission
```

</details>

<details>
<summary><strong>Linux</strong></summary>

```bash
# Debian / Ubuntu
sudo apt install transmission-cli

# Fedora / RHEL
sudo dnf install transmission-cli

# Arch Linux
sudo pacman -S transmission-cli
```

</details>

<details>
<summary><strong>Windows</strong></summary>

Using [Chocolatey](https://chocolatey.org/):

```powershell
# Install transmission-cli on Windows using Chocolatey
choco install transmission-cli
```

Using [Scoop](https://scoop.sh/):

```powershell
# Install transmission on Windows using Scoop
scoop install transmission
```

Or use [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) (Windows Subsystem for Linux) and follow the Linux instructions above.

</details>

## Installing Torrentor

### With Pipx (Recommended)

[pipx](https://pipx.pypa.io/) installs torrentor in its own isolated environment so it doesn't interfere with anything else on your system.

First, install pipx if you don't have it:

```bash
# macOS
brew install pipx

# Linux (Debian / Ubuntu)
sudo apt install pipx

# Windows (Scoop)
scoop install pipx

# Or with pip (works everywhere)
pip install --user pipx
```

Then install torrentor:

```bash
# Install torrentor via pipx
pipx install torrentor
```

### With Pip

```bash
# Install directly from the repository
pip install git+https://github.com/thaikolja/torrentor-cli.git
```

### From Source

```bash
# Clone the repository
git clone https://github.com/thaikolja/torrentor-cli.git

# Enter the project folder
cd torrentor-cli

# Create a virtual environment (keeps things isolated)
python -m venv .venv

# Activate it (on Windows use: .venv\Scripts\activate)
source .venv/bin/activate

# Install torrentor
pip install -e .
```

After installing, the `torrentor` command is available in your terminal.

## How to Use It

There are two ways: **interactive mode** (guided step-by-step) or **direct mode** (one command).

### Interactive Mode (Easiest)

Just type:

```bash
# Start the interactive menu
torrentor
```

You'll see a menu where you can pick what to do: download a torrent, change your settings, or quit. Everything is guided.

### Direct Mode (One Command)

Pass a [magnet link](https://en.wikipedia.org/wiki/Magnet_URI_scheme), a `.torrent` file path, or a URL:

```bash
# Download from a magnet link
torrentor "magnet:?xt=urn:btih:..."

# Download from a .torrent file on your computer
torrentor ./my-file.torrent

# Download from a URL to a .torrent file
torrentor "https://example.com/file.torrent"

# Download with a custom save location and speed limit
torrentor "magnet:?xt=urn:btih:..." --save-to ~/Movies --max-download 5000
```

### All Available Flags

Everything below is visible when you run `torrentor -h`. No need to dig into subcommands.

**Options** (the important ones):

| Flag               | Short | Type       | What it does                                                  |
| ------------------ | ----- | ---------- | ------------------------------------------------------------- |
| `--save-to`        | `-o`  | PATH       | Where to save the file (Default: ~/Downloads)                 |
| `--no-limit`       | `-n`  | TRUE/FALSE | Download at full speed (Default: false)                       |
| `--flush-cache`    | `-f`  |            | Delete all cached/incomplete downloads                       |

**Optional** (extra control):

| Flag              | Short | Type   | What it does                                                  |
| ----------------- | ----- | ------ | ------------------------------------------------------------- |
| `--max-download`  | `-l`  | NUMBER | Limit download speed, in kB/s (Default: no limit)             |
| `--max-upload`    | `-u`  | NUMBER | Limit upload speed, in kB/s (Default: no limit)               |
| `--timeout`       | `-t`  | NUMBER | Stop after this many seconds (Default: none)                  |

**Advanced** (for power users):

| Flag              | Short | Type       | What it does                                                                              |
| ----------------- | ----- | ---------- | ----------------------------------------------------------------------------------------- |
| `--seed`          | `-s`  | TRUE/FALSE | Keep [sharing](https://en.wikipedia.org/wiki/Seeding_(computing)) after download (Default: false) |
| `--in-order`      | `-q`  | TRUE/FALSE | Download from start to finish instead of jumping around (Default: false)                  |
| `--check`         | `-y`  | TRUE/FALSE | Check the file for errors after downloading (Default: false)                              |
| `--port`          | `-p`  | NUMBER     | Network port for peers (Default: 51413)                                                    |
| `--encryption`    | `-e`  | MODE       | Connection privacy: required, preferred, or tolerated (Default: preferred)                |
| `--blocklist`     | `-b`  | TRUE/FALSE | Block known bad peers (Default: false)                                                     |

### Managing Your Settings

Your settings are remembered between sessions. You can view and change them:

```bash
# See your current settings
torrentor config

# Change where files are saved
torrentor config set output_dir ~/Movies

# Limit download speed to 5 MB/s
torrentor config set download_limit 5000

# Remove a speed limit
torrentor config set download_limit none

# Reset everything to defaults
torrentor config reset

# Find where the settings file is stored on your computer
torrentor config path
```

Your settings are saved to a file on your computer:

- **macOS / Linux**: `~/.config/torrentor/config.json`
- **Windows**: `%APPDATA%\torrentor\config.json`

## What Happens When You Download

Here's what torrentor does behind the scenes:

```
You paste a magnet link, file path, or URL
        │
        ▼
transmission-cli downloads the file in the background
        │  (you see a live progress bar with speed and estimated time)
        ▼
Download complete: sharing stops automatically
        │
        ▼
The file is packed into a .zip
        │  (the filename is cleaned up: "My Movie! (2024)" -> "my-movie-2024.zip")
        ▼
The .zip is moved to your chosen folder
        │
        ▼
Temporary files are deleted
```

If the download seems slow, torrentor will let you know after about a minute and suggest things to try.

If something goes wrong (or you press `Ctrl+C`), you can **retry from where you left off**: your progress is saved.

## Full Command Reference

```bash
# Start interactive mode
torrentor

# Download a torrent directly
torrentor "magnet:?xt=urn:btih:..."

# Download with options
torrentor ./file.torrent --save-to ~/Movies --max-download 5000

# Delete cached/incomplete downloads
torrentor --flush-cache

# View your settings
torrentor config

# Change a setting
torrentor config set <key> <value>

# Reset all settings
torrentor config reset

# Show where the settings file is stored
torrentor config path

# Show version
torrentor -V

# Show help (includes all available flags)
torrentor -h
```

## For Developers

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, code style, and testing.

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run the linter
ruff check .

# Check formatting
ruff format --check .

# Run type checking
mypy torrentor

# Run tests
pytest

# Run tests with coverage report
pytest --cov=torrentor
```

## Author

**Kolja Nolte** — [kolja.nolte@gmail.com](mailto:kolja.nolte@gmail.com)

## License

[MIT](LICENSE): free to use, modify, and distribute.
