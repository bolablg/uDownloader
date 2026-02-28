# Changelog

All notable changes to uDownloader will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-28

### Added
- **Async downloader module** - Concurrent downloads with ThreadPoolExecutor
  - `AsyncDownloader` class supporting parallel downloads
  - Download cancellation support
  - Configurable concurrent limits (1-10 simultaneous)
  
- **Download history tracking** - Complete download record management
  - `DownloadHistory` class with JSON persistence
  - Filtering by platform, success status
  - Statistics dashboard (total, success rate, platform breakdown)
  - History export functionality
  
- **PyQt6 Desktop GUI** - Modern, multi-tab desktop application
  - Download tab with URL input and quality selection
  - Queue tab for monitoring active downloads
  - History tab with filtering and details
  - Statistics tab with comprehensive metrics
  - Settings dialog for configuration
  - Threaded downloads for responsive UI
  
- **CLI support** - Command-line interface
  - Quality selection (best, 1080p, 720p, 480p, 360p)
  - Audio-only mode (MP3 extraction)
  - Configurable retry logic
  - Verbose logging
  - Config file support
  
- **Configuration management**
  - Default config file at `~/.uDownloader/config.json`
  - Sensible defaults for all options
  - CLI override support
  
- **Pip installation support**
  - Semantic versioning and proper package structure
  - Two entry points: `udownloader` (CLI) and `udownloader-desktop` (GUI)
  - MIT License
  - Complete documentation
  
### Features
- Support for multiple platforms (YouTube, Instagram, TikTok, Twitter, Vimeo, Facebook)
- Video quality selection
- Audio quality configuration (bitrate)
- Custom output directories
- Progress reporting during downloads
- Platform-specific folder organization
- Error handling with automatic retries

### Documentation
- Comprehensive README.md
- Detailed INSTALLATION.md with platform-specific guides
- Inline code documentation
- CLI help messages

## Future Releases

### [0.2.0] - Planned
- [ ] Batch download features
- [ ] Download scheduling
- [ ] Proxy support
- [ ] More download platforms
- [ ] Database backend for history (SQLite)
- [ ] Search/filter improvements for history
- [ ] Download speed limiting
- [ ] Subtitle extraction
- [ ] Playlist metadata preservation

### [0.3.0] - Planned
- [ ] Web dashboard
- [ ] REST API
- [ ] Automated testing suite
- [ ] Performance optimizations
- [ ] Plugin system support
