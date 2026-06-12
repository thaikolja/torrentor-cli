# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-06-12

### Added

- Interactive mode with guided menus (just run `torrentor`)
- Direct mode: `torrentor <magnet link or .torrent file>` with flags
- Magnet link and `.torrent` file support
- Automatic stop after download completes (no seeding by default)
- Post-download packaging: zip with light compression + clean filenames
- Persistent settings at `~/.config/torrentor/config.json` (macOS/Linux) or `%APPDATA%\torrentor\config.json` (Windows)
- `torrentor config` subcommand to view, change, reset, and locate settings
- Cancel/retry with cache support: resume interrupted downloads
- Confetti celebration effect on download completion
- Spinning progress indicator with live speed (auto-scaling B/s → kB/s → MB/s), upload, and peer count
- Slow-download notification after 90 seconds if speed is below 10 kB/s
- `transmission-cli` dependency check with OS-specific install instructions (macOS, Linux, Windows)
- Cross-platform support: macOS, Linux, and Windows
- All flags visible in `torrentor -h` across three sections: Options, Optional, Advanced
- Every `--flag` has a short `-x` equivalent; `-h` works everywhere
- Every flag shows its input type: PATH, NUMBER, TRUE/FALSE, or MODE
- `torrentor add` kept as a hidden alias for backward compatibility
- Input validation on all CLI flags — invalid boolean values show a clear error
- Interactive settings menu exposes all config fields (seed, timeout, in-order, check, blocklist)
- Cache-aware retry menu — "continue from cache" and "keep cache" options only appear when data exists
- CLI flags are per-run only and never save to the config file
- Every flag shows its type (PATH, NUMBER, TRUE/FALSE, MODE) and default value in `--help`
- Bold spaced title in the banner for stronger branding
- Production-ready packaging: PyPI metadata, project URLs, keywords, py.typed marker, MANIFEST.in
- Development extras include build and twine for PyPI publishing
