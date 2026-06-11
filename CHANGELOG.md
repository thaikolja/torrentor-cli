# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.0.0

**Released:** June 12, 2026

This is the first version of *Torrentor CLI*.

### Added

- Interactive CLI mode with menu-driven navigation
- Direct CLI mode via `torrentor add <magnet|file>`
- Magnet link and `.torrent` file support
- Automatic seeding stop after download completes
- Post-download processing: zip with light compression + slugified filenames
- Persistent configuration at `~/.config/torrentor/config.json`
- `torrentor config` subcommand to view, set, reset, and locate config
- Configurable output directory, speed limits, port, and encryption
- CLI flag overrides for per-invocation settings
- `transmission-cli` dependency check with styled install instructions
- `torrentor demo` command showcasing all UI elements
- Beautiful Rich-powered UI: banner, panels, progress bars, status cards
- InquirerPy interactive prompts for guided workflows
