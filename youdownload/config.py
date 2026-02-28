import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".uDownloader"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "output_dir": "uDownload",
    "audio_only": False,
    "video_quality": "best",  # 'best', '1080p', '720p', '480p', '360p'
    "audio_quality": "192",  # in kbps
    "format_preference": "mp4",  # 'mp4', 'mkv', 'webm'
    "max_concurrent_downloads": 1,
    "timeout": 300,
    "retries": 3,
    "verbose": False,
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or return defaults.

    Args:
        config_path: Optional path to custom config file.

    Returns:
        Configuration dictionary.
    """
    config = DEFAULT_CONFIG.copy()

    # Try provided path first
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
                config.update(user_config)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")

    # Try default location
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                config.update(user_config)
                logger.info(f"Loaded config from {CONFIG_FILE}")
                return config
        except Exception as e:
            logger.warning(f"Failed to load config from {CONFIG_FILE}: {e}")

    logger.info("Using default configuration")
    return config


def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """Save configuration to file.

    Args:
        config: Configuration dictionary.
        config_path: Optional path to save. Uses default location if not provided.
    """
    target_path = Path(config_path) if config_path else CONFIG_FILE
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(target_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved config to {target_path}")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        raise


def create_default_config() -> None:
    """Create default config file if it doesn't exist."""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        print(f"Created default config at {CONFIG_FILE}")
