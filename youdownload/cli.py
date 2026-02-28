import argparse
import logging
import sys
import json

from .downloader import download
from .config import load_config, save_config, create_default_config, CONFIG_FILE


def main():
    parser = argparse.ArgumentParser(
        description="uDownloader: download YouTube video or audio, including playlists."
    )
    parser.add_argument("--url", "-u", required=False, help="YouTube video or playlist URL")
    parser.add_argument(
        "--output", "-o", default=None, help="Directory to save downloads (default from config or 'uDownload')"
    )
    parser.add_argument(
        "--audio", "-a", action="store_true", help="Download audio only (mp3)"
    )
    parser.add_argument(
        "--quality", "-q",
        choices=["best", "1080p", "720p", "480p", "360p"],
        default=None,
        help="Video quality preference"
    )
    parser.add_argument(
        "--config", "-c",
        default=None,
        help=f"Path to config file (default: {CONFIG_FILE})"
    )
    parser.add_argument(
        "--init-config",
        action="store_true",
        help="Create default config file and exit"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show verbose logging"
    )
    parser.add_argument(
        "--retries", "-r",
        type=int,
        default=3,
        help="Number of retries on download failure (default: 3)"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # Handle config initialization
    if args.init_config:
        create_default_config()
        return

    # Require URL for download
    if not args.url:
        parser.error("--url is required for downloads")

    # Load configuration
    config = load_config(args.config)
    
    # CLI args override config file
    if args.output:
        config["output_dir"] = args.output
    if args.quality:
        config["video_quality"] = args.quality
    if args.audio:
        config["audio_only"] = True
    config["verbose"] = args.verbose

    try:
        result = download(
            args.url,
            output_dir=config["output_dir"],
            audio_only=config.get("audio_only", False),
            config=config,
            retries=args.retries,
        )
        logging.info(f"✓ Successfully downloaded: {result['title']}")
    except Exception as e:
        logging.error(f"✗ Download failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
