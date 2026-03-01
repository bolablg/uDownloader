import os
import logging
from typing import Dict, Any, Callable
from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)


def detect_platform(url: str) -> str:
    """Detect the platform from the given URL.

    Returns:
        Platform name: 'YouTube', 'Twitter', 'Instagram', etc.
    """
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


def download(
    url: str,
    output_dir: str = "uDownload",
    audio_only: bool = False,
    config: Dict[str, Any] = None,
    progress_callback: Callable = None,
    retries: int = 3,
) -> Dict[str, Any]:
    """Download video/audio from YouTube, Instagram, Twitter, etc.

    Args:
        url: The video or playlist URL.
        output_dir: Directory where files will be saved (defaults to 'uDownload').
        audio_only: If True, extract audio only (mp3)
        config: Configuration dictionary with quality/format preferences
        progress_callback: Function to call with progress updates
        retries: Number of retries on failure

    Returns:
        Dictionary with download statistics
    """
    if config is None:
        config = {}

    # Detect platform and create platform-specific subfolder
    platform = detect_platform(url)
    platform_dir = os.path.join(output_dir, platform)
    os.makedirs(platform_dir, exist_ok=True)

    ydl_opts = {
        "outtmpl": os.path.join(platform_dir, "%(title)s.%(ext)s"),
        "quiet": False,
        "noplaylist": False,  # allow playlist
        "progress_hooks": [_progress_hook] if progress_callback is None else [progress_callback],
        "no_warnings": False,
    }

    cookies_browser = config.get("cookies_browser", "")
    if cookies_browser:
        ydl_opts["cookiesfrombrowser"] = (cookies_browser,)

    if audio_only:
        audio_quality = config.get("audio_quality", "192")
        # convert video to mp3
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
                }
            except Exception as e:
                last_error = e
                attempt += 1
                if attempt < retries:
                    logger.warning(
                        f"Download failed (attempt {attempt}/{retries}): {e}. Retrying..."
                    )
                else:
                    logger.error(f"Download failed after {retries} attempts: {e}")

    raise last_error


def _progress_hook(d):
    """Default progress hook for yt-dlp."""
    status = d.get("status")
    if status == "downloading":
        percent = d.get("_percent_str", "N/A")
        speed = d.get("_speed_str", "N/A")
        eta = d.get("_eta_str", "N/A")
        logger.info(f"Progress: {percent} at {speed}, ETA: {eta}")
    elif status == "finished":
        logger.info("Download finished, now post-processing...")
