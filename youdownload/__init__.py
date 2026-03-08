"""
uDownloader: Fast async YouTube/Instagram/TikTok downloader with desktop GUI and CLI.

A powerful Python application to download videos and audio from multiple platforms
with both command-line and desktop GUI interfaces.

Features:
    - Async/concurrent downloads
    - Download history tracking
    - PyQt6 desktop GUI
    - CLI interface
    - Configuration management
    - Cross-platform support
"""

from importlib.metadata import version as _pkg_version, PackageNotFoundError
from pathlib import Path as _Path

try:
    __version__ = _pkg_version("uDownloader")
except PackageNotFoundError:
    # Fallback: read from VERSION file at project root (for dev / editable installs)
    _version_file = _Path(__file__).resolve().parent.parent / "VERSION"
    if _version_file.exists():
        __version__ = _version_file.read_text().strip()
    else:
        __version__ = "0.0.0"
__author__ = "Bolaji BALOGOUN"
__license__ = "MIT"

from youdownload.config import load_config, save_config  # noqa: F401
from youdownload.async_downloader import AsyncDownloader  # noqa: F401
from youdownload.history import DownloadHistory  # noqa: F401

__all__ = [
    "AsyncDownloader",
    "DownloadHistory",
    "load_config",
    "save_config",
]
