import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

HISTORY_DIR = Path.home() / ".uDownloader"
HISTORY_FILE = HISTORY_DIR / "history.json"


class DownloadHistory:
    """Tracks download history."""
    
    def __init__(self, history_file: Optional[Path] = None):
        """
        Initialize download history.
        
        Args:
            history_file: Path to history file (uses default if not provided)
        """
        self.history_file = history_file or HISTORY_FILE
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure history file exists."""
        if not self.history_file.exists():
            self._save_history([])
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load history from file."""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []
    
    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        """Save history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
    
    def add_download(self, download_info: Dict[str, Any]) -> None:
        """
        Add a download record to history.
        
        Args:
            download_info: Dictionary with download details
        """
        history = self._load_history()
        
        # Add metadata
        record = {
            **download_info,
            "added_at": datetime.now().isoformat(),
        }
        
        history.append(record)
        self._save_history(history)
        logger.info(f"Added to history: {download_info.get('title', 'Unknown')}")
    
    def get_history(
        self,
        platform: Optional[str] = None,
        limit: Optional[int] = None,
        success_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get download history with optional filtering.
        
        Args:
            platform: Filter by platform (YouTube, Instagram, etc.)
            limit: Limit number of results
            success_only: Only return successful downloads
            
        Returns:
            List of download records
        """
        history = self._load_history()
        
        # Filter
        if platform:
            history = [h for h in history if h.get("platform") == platform]
        
        if success_only:
            history = [h for h in history if h.get("success", False)]
        
        # Reverse to show newest first
        history = list(reversed(history))
        
        # Limit
        if limit:
            history = history[:limit]
        
        return history
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get download statistics.
        
        Returns:
            Dictionary with statistics
        """
        history = self._load_history()
        
        total = len(history)
        successful = sum(1 for h in history if h.get("success", False))
        failed = total - successful
        
        platforms = {}
        for h in history:
            platform = h.get("platform", "Unknown")
            platforms[platform] = platforms.get(platform, 0) + 1
        
        return {
            "total_downloads": total,
            "successful": successful,
            "failed": failed,
            "by_platform": platforms,
        }
    
    def clear_history(self) -> None:
        """Clear all download history."""
        self._save_history([])
        logger.info("Download history cleared")
    
    def remove_entry(self, index: int) -> bool:
        """
        Remove a history entry by index.
        
        Args:
            index: Index of entry to remove
            
        Returns:
            True if successful, False otherwise
        """
        history = self._load_history()
        if 0 <= index < len(history):
            history.pop(index)
            self._save_history(history)
            return True
        return False
    
    def export_history(self, export_path: Path) -> None:
        """
        Export history to external file.
        
        Args:
            export_path: Path to save exported history
        """
        history = self._load_history()
        try:
            with open(export_path, 'w') as f:
                json.dump(history, f, indent=2)
            logger.info(f"Exported history to {export_path}")
        except Exception as e:
            logger.error(f"Failed to export history: {e}")
            raise
