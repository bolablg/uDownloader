import os
import logging
import asyncio
from typing import Dict, Any, Callable, List, Optional
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL
from datetime import datetime

logger = logging.getLogger(__name__)


class AsyncDownloader:
    """Handles async/concurrent downloads with progress tracking."""

    def __init__(self, max_concurrent: int = 1):
        """
        Initialize async downloader.

        Args:
            max_concurrent: Maximum number of concurrent downloads
        """
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.active_downloads: Dict[str, bool] = {}

    def detect_platform(self, url: str) -> str:
        """Detect the platform from the given URL."""
        url_lower = url.lower()

        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "YouTube"
        elif "twitter.com" in url_lower or "x.com" in url_lower:
            return "Twitter"
        elif "facebook.com" in url_lower or "fb.com" in url_lower or "fb.me" in url_lower:
            return "Facebook"
        elif "instagram.com" in url_lower:
            return "Instagram"
        elif "tiktok.com" in url_lower:
            return "TikTok"
        elif "vimeo.com" in url_lower:
            return "Vimeo"
        else:
            return "Other"

    def _download_sync(
        self,
        url: str,
        output_dir: str,
        audio_only: bool,
        config: Dict[str, Any],
        progress_callback: Optional[Callable],
        retries: int,
        download_id: str,
    ) -> Dict[str, Any]:
        """Synchronous download function to run in thread pool."""

        platform = self.detect_platform(url)
        platform_dir = os.path.join(output_dir, platform)
        os.makedirs(platform_dir, exist_ok=True)

        ydl_opts = {
            "outtmpl": os.path.join(platform_dir, "%(title)s.%(ext)s"),
            "quiet": False,
            "noplaylist": False,
            "progress_hooks": [progress_callback] if progress_callback else [],
            "no_warnings": False,
        }

        cookies_browser = config.get("cookies_browser", "")
        if cookies_browser:
            ydl_opts["cookiesfrombrowser"] = (cookies_browser,)

        if audio_only:
            audio_quality = config.get("audio_quality", "192")
            ydl_opts.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": audio_quality,
                        }
                    ],
                }
            )
        else:
            video_quality = config.get("video_quality", "best")
            video_format = str(config.get("format_preference", "mp4")).lower()
            if video_format not in {"mp4", "mkv", "webm", "original"}:
                video_format = "mp4"
            format_pref = {
                "best": "bestvideo+bestaudio/best",
                "1080p": "bestvideo[height<=1080]+bestaudio/best",
                "720p": "bestvideo[height<=720]+bestaudio/best",
                "480p": "bestvideo[height<=480]+bestaudio/best",
                "360p": "bestvideo[height<=360]+bestaudio/best",
            }
            ydl_opts.update(
                {
                    "format": format_pref.get(video_quality, "bestvideo+bestaudio/best"),
                }
            )
            if video_format != "original":
                ydl_opts["merge_output_format"] = video_format
                ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegVideoConvertor",
                        "preferedformat": video_format,
                    }
                ]

        attempt = 0
        last_error = None

        while attempt < retries:
            if not self.active_downloads.get(download_id, True):
                return {
                    "success": False,
                    "platform": platform,
                    "url": url,
                    "error": "Download cancelled",
                    "title": "Unknown",
                }

            with YoutubeDL(ydl_opts) as ydl:
                try:
                    logger.info(f"Starting download (attempt {attempt + 1}/{retries}): {url}")
                    info = ydl.extract_info(url, download=True)
                    logger.info(f"Download succeeded: {info.get('title', 'Unknown')}")

                    return {
                        "success": True,
                        "platform": platform,
                        "title": info.get("title", "Unknown"),
                        "url": url,
                        "timestamp": datetime.now().isoformat(),
                        "output_dir": platform_dir,
                    }
                except Exception as e:
                    last_error = e
                    attempt += 1
                    if attempt < retries:
                        logger.warning(f"Download failed (attempt {attempt}/{retries}): {e}")

        return {
            "success": False,
            "platform": platform,
            "url": url,
            "error": str(last_error),
            "title": "Unknown",
        }

    async def download_async(
        self,
        url: str,
        output_dir: str = "uDownload",
        audio_only: bool = False,
        config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None,
        retries: int = 3,
        download_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Asynchronously download video/audio.

        Args:
            url: The video or playlist URL
            output_dir: Directory where files will be saved
            audio_only: If True, extract audio only (mp3)
            config: Configuration dictionary with quality/format preferences
            progress_callback: Function to call with progress updates
            retries: Number of retries on failure
            download_id: Unique ID for tracking this download

        Returns:
            Dictionary with download result
        """
        if config is None:
            config = {}

        if download_id:
            self.active_downloads[download_id] = True

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self.executor,
                self._download_sync,
                url,
                output_dir,
                audio_only,
                config,
                progress_callback,
                retries,
                download_id or url,
            )
            return result
        finally:
            if download_id:
                self.active_downloads.pop(download_id, None)

    async def download_multiple_async(
        self,
        urls: List[str],
        output_dir: str = "uDownload",
        audio_only: bool = False,
        config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None,
        retries: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Download multiple videos concurrently.

        Args:
            urls: List of URLs to download
            output_dir: Directory where files will be saved
            audio_only: If True, extract audio only
            config: Configuration dictionary
            progress_callback: Function to call with progress updates
            retries: Number of retries on failure

        Returns:
            List of download results
        """
        tasks = [
            self.download_async(
                url,
                output_dir,
                audio_only,
                config,
                progress_callback,
                retries,
                download_id=f"download_{i}",
            )
            for i, url in enumerate(urls)
        ]

        return await asyncio.gather(*tasks)

    def cancel_download(self, download_id: str) -> None:
        """Cancel a download."""
        if download_id in self.active_downloads:
            self.active_downloads[download_id] = False
            logger.info(f"Cancelled download: {download_id}")
