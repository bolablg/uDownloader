"""Tests for youdownload package."""

import pytest
from youdownload import __version__
from youdownload.config import load_config, DEFAULT_CONFIG
from youdownload.history import DownloadHistory
from youdownload.async_downloader import AsyncDownloader
from pathlib import Path
import tempfile


class TestVersion:
    """Test package version."""

    def test_version_exists(self):
        """Test that version is defined."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_version_format(self):
        """Test version follows semantic versioning."""
        parts = __version__.split(".")
        assert len(parts) >= 2


class TestConfig:
    """Test configuration management."""

    def test_default_config_structure(self):
        """Test default config has required keys."""
        required_keys = [
            "output_dir",
            "audio_only",
            "video_quality",
            "audio_quality",
            "max_concurrent_downloads",
            "retries",
        ]
        for key in required_keys:
            assert key in DEFAULT_CONFIG

    def test_load_config_with_no_file(self):
        """Test loading config returns defaults when no file exists."""
        # Use temp file that doesn't exist
        config = load_config("/tmp/nonexistent_config_12345.json")
        assert config["output_dir"] == "uDownload"
        assert config["video_quality"] == "best"


class TestHistory:
    """Test download history tracking."""

    def test_history_initialization(self):
        """Test history object initializes correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            history_file = Path(f.name)

        try:
            history = DownloadHistory(history_file)
            assert history.history_file == history_file
            assert history_file.exists()
        finally:
            if history_file.exists():
                history_file.unlink()

    def test_add_and_get_history(self):
        """Test adding and retrieving history."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            history_file = Path(f.name)

        try:
            history = DownloadHistory(history_file)

            record = {
                "title": "Test Video",
                "platform": "YouTube",
                "url": "https://youtube.com/watch?v=test",
                "success": True,
            }

            history.add_download(record)
            records = history.get_history()

            assert len(records) > 0
            assert records[0]["title"] == "Test Video"
        finally:
            if history_file.exists():
                history_file.unlink()

    def test_get_stats(self):
        """Test statistics calculation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            history_file = Path(f.name)

        try:
            history = DownloadHistory(history_file)

            # Add test records
            history.add_download(
                {
                    "title": "Video 1",
                    "platform": "YouTube",
                    "url": "https://example.com",
                    "success": True,
                }
            )
            history.add_download(
                {
                    "title": "Video 2",
                    "platform": "Instagram",
                    "url": "https://example.com",
                    "success": False,
                }
            )

            stats = history.get_stats()
            assert stats["total_downloads"] == 2
            assert stats["successful"] == 1
            assert stats["failed"] == 1
        finally:
            if history_file.exists():
                history_file.unlink()


class TestAsyncDownloader:
    """Test async downloader."""

    def test_initialization(self):
        """Test AsyncDownloader initializes correctly."""
        downloader = AsyncDownloader(max_concurrent=2)
        assert downloader.max_concurrent == 2
        assert downloader.executor is not None

    def test_platform_detection(self):
        """Test platform detection."""
        downloader = AsyncDownloader()

        assert downloader.detect_platform("https://youtube.com/watch?v=test") == "YouTube"
        assert downloader.detect_platform("https://youtu.be/test") == "YouTube"
        assert downloader.detect_platform("https://instagram.com/p/test") == "Instagram"
        assert downloader.detect_platform("https://tiktok.com/@user/video/123") == "TikTok"
        assert downloader.detect_platform("https://twitter.com/user/status/123") == "Twitter"
        assert downloader.detect_platform("https://x.com/user/status/123") == "Twitter"
        assert downloader.detect_platform("https://vimeo.com/123") == "Vimeo"
        assert downloader.detect_platform("https://facebook.com/video/123") == "Facebook"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
