# Changelog

All notable changes to uDownloader will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - Unreleased

### Added

- **X/Twitter support** — browser cookie injection (`cookiesfrombrowser`) for auth-gated content;
  selectable via `--cookies-browser` CLI flag or the Settings dialog in the GUI
- **GUI logo** — window and dock icon sourced from `img/logo.png` (transparent PNG)
- **Video format selector in Download tab** — choose mp4 / mkv / webm / original directly
  from the main download form without opening Settings

### Fixed

- **Real-time log display** — progress lines were only appearing after the download finished
  because the `worker_thread.started` lambda was dispatched to the main thread via Qt's
  `AutoConnection`, blocking the Qt event loop inside `asyncio.run_until_complete`.
  Fixed by using `Qt.ConnectionType.DirectConnection` so the download runs in the worker
  thread and the main thread stays free to process paint and signal events.
- **GUI font warning** — replaced `QFont("Courier")` (missing alias) with `QFont("Courier New")`
  to eliminate the 88 ms font-alias lookup warning on macOS.
- **Window icon path** — used `os.path.abspath` to normalise the `../img/logo.png` path so
  `QIcon` receives a fully-resolved absolute path on all platforms.

### Changed

- Logo PNG background made transparent (circle retained, white rectangular background removed).
- README updated with logo, GUI screenshots, new CLI examples, and feature list.

---

## [0.1.3] - 2026-02-28

### Changed

- Documentation updates: Sources, CI/CD status badge, contact info.
- Minor commit-history cleanup (unused blank lines removed from launcher and core modules).

---

## [0.1.2] - 2026-02-27

### Fixed

- Pinned `black` and `ruff` versions across all CI workflows to prevent version-skew failures.
- Applied consistent `black` formatting to all Python source files.
- Added `.gitattributes` for cross-platform line-ending normalisation.

---

## [0.1.1] - 2026-02-26

### Changed

- Upgraded CI Python version to 3.12; replaced `flake8` with `ruff` for linting.
- Lint and format checks now run only on Python 3.12 to avoid version-specific differences.
- Enhanced dev → staging CI workflow with linting and formatting gates.

---

## [0.1.0] - 2026-02-25

### Added

- **Async downloader module** — concurrent downloads with `ThreadPoolExecutor`
  - `AsyncDownloader` class supporting parallel downloads
  - Download cancellation support
  - Configurable concurrent limits (1–10 simultaneous)
- **Download history tracking** — complete download record management
  - `DownloadHistory` class with JSON persistence
  - Filtering by platform and success status
  - Statistics dashboard (total, success rate, platform breakdown)
  - History export functionality
- **PyQt6 Desktop GUI** — modern, multi-tab desktop application
  - Download tab with URL input and quality selection
  - Queue tab for monitoring active downloads
  - History tab with filtering and details
  - Statistics tab with comprehensive metrics
  - Settings dialog for full configuration
  - Threaded downloads for a responsive UI
- **CLI support** — command-line interface
  - Quality selection (`best`, `1080p`, `720p`, `480p`, `360p`)
  - Audio-only mode (MP3 extraction)
  - Configurable retry logic
  - Verbose logging
  - Config file support (`~/.uDownloader/config.json`)
- **Configuration management** — default config at `~/.uDownloader/config.json`
  with sensible defaults and CLI override support
- **pip installation support** — two entry points: `udownloader` (CLI) and
  `udownloader-desktop` (GUI); MIT License; full documentation

### Features

- Support for YouTube, Instagram, TikTok, Twitter/X, Vimeo, Facebook
- Video quality and audio quality (bitrate) selection
- Custom output directories with platform-specific sub-folders
- Progress reporting during downloads
- Error handling with automatic retries

---

## Future Releases

### [0.3.0] — Planned

- [ ] Batch download features
- [ ] Download scheduling
- [ ] Proxy support
- [ ] Database backend for history (SQLite)
- [ ] Search/filter improvements for history
- [ ] Download speed limiting
- [ ] Subtitle extraction
- [ ] Playlist metadata preservation

### [0.4.0] — Planned

- [ ] Web dashboard
- [ ] REST API
- [ ] Automated testing suite
- [ ] Performance optimisations
- [ ] Plugin system support
