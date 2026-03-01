# uDownloader

<p align="center">
  <img src="https://raw.githubusercontent.com/bolablg/uDownloader/2ce88885eacb82a4cb6681f1414978fec47759c5/img/logo.png" alt="uDownloader Logo" width="120"/>
</p>

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Version 0.1.7](https://img.shields.io/badge/version-0.1.7-green)](./docs/CHANGELOG.md)
[![License MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![GitHub CI/CD](https://github.com/bolablg/uDownloader/workflows/Tests/badge.svg)](https://github.com/bolablg/uDownloader/actions)

A fast, powerful Python application to download YouTube videos or audio. Supports single videos or entire playlists with both CLI and **Desktop GUI**. Uses `yt-dlp` for efficiency and modern format handling.

**Available as a pip-installable package!** Install with `pip install udownloader`

## Features

### Core Features
- Download video or audio from YouTube, Instagram, TikTok, Twitter, and more
- Process single content or playlists
- Command-line interface with quality and format options
- Configuration file support with sensible defaults
- Detailed progress reporting during downloads
- Automatic retry logic for failed downloads
- Platform-specific organization (YouTube, Instagram, Twitter, TikTok, etc.)

### Desktop Application
- **Modern PyQt6 GUI** for intuitive downloading
- **Async/Concurrent Downloads** - download multiple videos simultaneously
- **Download History Tracking** - view all past downloads with statistics
- **Live Progress Monitoring** - track active downloads in real-time
- **Queue Management** - manage multiple downloads at once
- **Video Format Selection** - choose output container (mp4, mkv, webm) per download
- **X/Twitter Support** - browser cookie injection for auth-gated content
- **Settings Panel** - configure quality, format, output, retries, concurrent limits, and cookies

## Installation

### Option 1: Install via pip (Recommended)

```bash
# From PyPI
pip install udownloader

# Or install from source (development mode)
git clone https://github.com/bolablg/uDownloader.git
cd uDownloader
pip install -e .
```

### Option 2: Manual installation from source

```bash
git clone https://github.com/bolablg/uDownloader.git
cd uDownloader
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

After installation, you'll have two commands available:
- `udownloader` - CLI version
- `udownloader-desktop` - Desktop GUI version


## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.8+ | Core application |
| **Video Downloading** | yt-dlp 2024.8.2+ | Format detection & download |
| **Desktop GUI** | PyQt6 6.6.0+ | Modern graphical interface |
| **Async Processing** | asyncio + ThreadPoolExecutor | Concurrent downloads |
| **Configuration** | JSON | User settings persistence |
| **History Tracking** | JSON | Download records database |
| **Testing** | pytest + pytest-cov | Unit testing & coverage |
| **Code Quality** | black + flake8 | Formatting & linting |
| **Packaging** | setuptools + wheel | PyPI distribution |
| **CI/CD** | GitHub Actions | Automated testing & publishing |

**Key Dependencies:**
- `yt-dlp` - Video downloading engine
- `PyQt6` - Desktop application framework
- `pytest` - Testing framework (dev only)
- `black` - Code formatter (dev only)
- `flake8` - Code linter (dev only)

## Quick Start

### CLI Mode

```bash
# Initialize config file (creates ~/.uDownloader/config.json)
udownloader --init-config

# Download best quality video
udownloader --url https://youtube.com/watch?v=VIDEO_ID

# Download as MP3 audio only
udownloader --url https://youtube.com/watch?v=VIDEO_ID --audio

# Download specific quality (best, 1080p, 720p, 480p, 360p)
udownloader --url https://youtube.com/watch?v=VIDEO_ID --quality 720p

# Download in a specific container format (mp4, mkv, webm, original)
udownloader --url https://youtube.com/watch?v=VIDEO_ID --video-format mkv

# Download from X/Twitter using browser cookies for authentication
udownloader --url https://x.com/user/status/POST_ID --cookies-browser chrome

# Download entire playlist to custom location
udownloader --url https://youtube.com/playlist?list=PLAYLIST_ID --output ~/Downloads --retries 5

# Verbose logging for debugging
udownloader --url https://youtube.com/watch?v=VIDEO_ID --verbose
```

### Desktop Application

```bash
# Launch desktop app (from installed package)
udownloader-desktop

# Or if running from source directory
python launcher_desktop.py
```

**Features in Desktop App:**

- **Download Tab**: Paste URLs and start downloads with quality and format selection
- **Queue Tab**: Monitor active downloads in real-time
- **History Tab**: View all previous downloads with details
- **Statistics Tab**: See download stats by platform and overall success rate
- **Settings**: Configure output directory, quality, video format, concurrent limits, retry attempts, and browser cookies for X/Twitter

### Screenshots

![uDownloader GUI](https://raw.githubusercontent.com/bolablg/uDownloader/2ce88885eacb82a4cb6681f1414978fec47759c5/img/uDownloader%20-%20GUI.png)

![uDownloader Settings](https://raw.githubusercontent.com/bolablg/uDownloader/2ce88885eacb82a4cb6681f1414978fec47759c5/img/uDownloader%20-%20GUI%20Settings.png)

## Configuration

The configuration file is automatically created at `~/.uDownloader/config.json` when you run `--init-config`.

### Default Settings:
```json
{
    "output_dir": "uDownload",
    "audio_only": false,
    "video_quality": "best",
    "audio_quality": "192",
    "format_preference": "mp4",
    "max_concurrent_downloads": 1,
    "timeout": 300,
    "retries": 3,
    "verbose": false
}
```

You can edit this file directly to change defaults, or override with command-line arguments (CLI) or settings dialog (Desktop app).

## Command-line Options

```
--url URL, -u URL              YouTube video or playlist URL (required for downloads)
--output OUTPUT, -o OUTPUT     Directory to save downloads (default: config or 'uDownload')
--audio, -a                    Download audio only (mp3)
--quality {best,1080p,720p,480p,360p}  Video quality preference
--config CONFIG, -c CONFIG     Path to custom config file
--init-config                  Create default config file and exit
--retries RETRIES, -r RETRIES  Number of retries on failure (default: 3)
--verbose, -v                  Show detailed logging
--help, -h                     Show help message
```

## Architecture

### Modules
- **`cli.py`** - Command-line interface
- **`downloader.py`** - Single download handler
- **`async_downloader.py`** - Async/concurrent download manager
- **`desktop.py`** - PyQt6 desktop GUI application
- **`history.py`** - Download history tracking and statistics
- **`config.py`** - Configuration management

### Key Features in Code
- **`AsyncDownloader`** class handles concurrent downloads using ThreadPoolExecutor
- **`DownloadHistory`** class manages download records in JSON format
- **`uDownloaderApp`** is the main desktop application with multi-tab interface
- **`DownloadWorker`** runs downloads in separate thread to keep UI responsive

## Documentation

Comprehensive documentation is available in the [docs](docs/) folder:

- **[Installation Guide](docs/INSTALLATION.md)** - Platform-specific installation instructions
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Commands, workflows, and FAQ
- **[Contributing Guide](docs/CONTRIBUTING.md)** - Development setup and contribution guidelines
- **[CI/CD Setup](docs/CICD_SETUP.md)** - GitHub Actions and testing infrastructure
- **[Changelog](docs/CHANGELOG.md)** - Version history and planned features
- **[Security Policy](docs/SECURITY.md)** - Vulnerability reporting and security practices

## License

uDownloader is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ with CodeX 5.3 for video downloaders everywhere**
