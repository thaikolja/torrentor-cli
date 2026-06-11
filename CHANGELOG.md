# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-06-12

### Added

- Interactive mode with guided menus (just run `torrentor`)
- Direct mode via `torrentor add <magnet|file>` with flags
- Magnet link and `.torrent` file support
- Automatic stop after download completes (no seeding by default)
- Post-download packaging: zip with light compression + clean filenames
- Persistent settings at `~/.config/torrentor/config.json` (macOS/Linux) or `%APPDATA%\torrentor\config.json` (Windows)
- `torrentor config` command to view, change, reset, and locate settings
- Cancel/retry with cache support — resume interrupted downloads
- Confetti celebration on download completion
- Spinning progress indicator with live speed, upload, and peer count
- `transmission-cli` dependency check with OS-specific install instructions
- Cross-platform support: macOS, Linux, and Windows
- Main flags: `--save-to`, `--max-download`, `--max-upload`, `--no-limit`, `--timeout`
- Advanced flags: `--seed`, `--in-order`, `--check`, `--port`, `--encryption`, `--blocklist`
- Every `--flag` has a short `-x` equivalent; `-h` works everywhere
