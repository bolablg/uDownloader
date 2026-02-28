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

__version__ = "0.1.0"
__author__ = "Developer"
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
