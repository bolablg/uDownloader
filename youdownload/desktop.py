import sys
import os
import asyncio
import logging
import re
import time
import threading
from html import escape
from datetime import datetime
from typing import Dict, Any, Callable, Optional

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLineEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QSpinBox,
    QMessageBox,
    QDialogButtonBox,
    QTextEdit,
)
from PyQt6.QtCore import pyqtSignal, QObject, QThread, Qt
from PyQt6.QtGui import QFont, QIcon

from youdownload.config import load_config, save_config
from youdownload.history import DownloadHistory
from youdownload.async_downloader import AsyncDownloader

logger = logging.getLogger(__name__)
ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


class DownloadWorker(QObject):
    """Worker for async downloads in separate thread."""

    progress = pyqtSignal(str, dict)  # download_id, progress_data
    finished = pyqtSignal(str, dict)  # download_id, result

    def __init__(
        self,
        async_downloader: AsyncDownloader,
        config: Dict[str, Any],
        progress_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        super().__init__()
        self.async_downloader = async_downloader
        self.config = config
        self.progress_callback = progress_callback
        self.loop = asyncio.new_event_loop()

    def run_download(self, url: str, download_id: str, audio_only: bool):
        """Run a download."""
        asyncio.set_event_loop(self.loop)
        try:
            def progress_hook(progress_data: Dict[str, Any]):
                if self.progress_callback:
                    self.progress_callback(download_id, progress_data)
                else:
                    self.progress.emit(download_id, progress_data)

            result = self.loop.run_until_complete(
                self.async_downloader.download_async(
                    url=url,
                    output_dir=self.config.get("output_dir", "uDownload"),
                    audio_only=audio_only,
                    config=self.config,
                    download_id=download_id,
                    retries=self.config.get("retries", 3),
                    progress_callback=progress_hook,
                )
            )
            self.finished.emit(download_id, result)
        except Exception as e:
            self.finished.emit(
                download_id,
                {
                    "success": False,
                    "error": str(e),
                    "url": url,
                },
            )


class SettingsDialog(QDialog):
    """Settings dialog for configuration."""

    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Output directory
        layout.addWidget(QLabel("Output Directory:"))
        self.output_input = QLineEdit(self.config.get("output_dir", "uDownload"))
        layout.addWidget(self.output_input)

        # Video quality
        layout.addWidget(QLabel("Video Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "1080p", "720p", "480p", "360p"])
        self.quality_combo.setCurrentText(self.config.get("video_quality", "best"))
        layout.addWidget(self.quality_combo)

        # Video output format
        layout.addWidget(QLabel("Video Output Format:"))
        self.video_format_combo = QComboBox()
        self.video_format_combo.addItems(["mp4", "mkv", "webm", "original"])
        self.video_format_combo.setCurrentText(self.config.get("format_preference", "mp4"))
        layout.addWidget(self.video_format_combo)

        # Audio quality
        layout.addWidget(QLabel("Audio Quality (kbps):"))
        self.audio_quality_spin = QSpinBox()
        self.audio_quality_spin.setRange(64, 320)
        self.audio_quality_spin.setValue(int(self.config.get("audio_quality", "192")))
        layout.addWidget(self.audio_quality_spin)

        # Concurrent downloads
        layout.addWidget(QLabel("Max Concurrent Downloads:"))
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 10)
        self.concurrent_spin.setValue(self.config.get("max_concurrent_downloads", 1))
        layout.addWidget(self.concurrent_spin)

        # Retries
        layout.addWidget(QLabel("Retries on Failure:"))
        self.retries_spin = QSpinBox()
        self.retries_spin.setRange(1, 10)
        self.retries_spin.setValue(self.config.get("retries", 3))
        layout.addWidget(self.retries_spin)

        # Cookies browser (for auth-gated platforms like X/Twitter)
        layout.addWidget(QLabel("Cookies Browser (for X/Twitter auth):"))
        self.cookies_browser_combo = QComboBox()
        self.cookies_browser_combo.addItems(["none", "chrome", "firefox", "safari", "edge", "brave", "chromium"])
        self.cookies_browser_combo.setCurrentText(self.config.get("cookies_browser", "") or "none")
        layout.addWidget(self.cookies_browser_combo)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_config(self) -> Dict[str, Any]:
        """Get updated configuration."""
        return {
            **self.config,
            "output_dir": self.output_input.text(),
            "video_quality": self.quality_combo.currentText(),
            "format_preference": self.video_format_combo.currentText(),
            "audio_quality": str(self.audio_quality_spin.value()),
            "max_concurrent_downloads": self.concurrent_spin.value(),
            "retries": self.retries_spin.value(),
            "cookies_browser": "" if self.cookies_browser_combo.currentText() == "none" else self.cookies_browser_combo.currentText(),
        }


class uDownloaderApp(QMainWindow):
    """Main application window."""

    progress_update = pyqtSignal(str, dict)

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.history = DownloadHistory()
        self.async_downloader = AsyncDownloader(
            max_concurrent=self.config.get("max_concurrent_downloads", 1)
        )
        self.downloads: Dict[str, Dict] = {}  # Track active downloads
        self.worker_threads: Dict[str, QThread] = {}
        self.workers: Dict[str, DownloadWorker] = {}
        self.progress_state: Dict[str, Dict[str, Any]] = {}
        self.completed_downloads = set()
        self.emit_state: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.emit_state_lock = threading.Lock()
        self.init_ui()
        self.setup_logging()
        self.progress_update.connect(self.on_download_progress, Qt.ConnectionType.QueuedConnection)

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle("uDownloader - Desktop")
        self.setGeometry(100, 100, 1000, 700)

        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img", "logo.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        layout = QVBoxLayout()

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_download_tab(), "Download")
        tabs.addTab(self.create_queue_tab(), "Queue")
        tabs.addTab(self.create_history_tab(), "History")
        tabs.addTab(self.create_stats_tab(), "Statistics")

        layout.addWidget(tabs)

        # Bottom status bar
        bottom_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        bottom_layout.addWidget(self.status_label)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.open_settings)
        bottom_layout.addWidget(settings_btn)

        layout.addLayout(bottom_layout)

        central.setLayout(layout)

    def create_download_tab(self) -> QWidget:
        """Create download tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # URL input
        layout.addWidget(QLabel("YouTube/Instagram/TikTok URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste URL here...")
        layout.addWidget(self.url_input)

        # Options
        options_layout = QHBoxLayout()

        self.audio_only_check = QCheckBox("Audio Only (MP3)")
        options_layout.addWidget(self.audio_only_check)

        layout.addWidget(QLabel("Video Quality:"))
        self.quality_select = QComboBox()
        self.quality_select.addItems(["best", "1080p", "720p", "480p", "360p"])
        self.quality_select.setCurrentText(self.config.get("video_quality", "best"))
        options_layout.addWidget(self.quality_select)

        layout.addWidget(QLabel("Video Format:"))
        self.format_select = QComboBox()
        self.format_select.addItems(["mp4", "mkv", "webm", "original"])
        self.format_select.setCurrentText(self.config.get("format_preference", "mp4"))
        options_layout.addWidget(self.format_select)

        layout.addLayout(options_layout)

        # Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;"
        )
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        # Live download log under button
        layout.addWidget(QLabel("Download Log:"))
        self.download_log = QTextEdit()
        self.download_log.setReadOnly(True)
        self.download_log.setStyleSheet(
            "QTextEdit { background: #0f172a; color: #e2e8f0; border: 1px solid #334155; }"
        )
        self.download_log.setPlaceholderText(
            "Progress updates will appear here (percent, speed, ETA, status)..."
        )
        self.download_log.setMinimumHeight(180)
        layout.addWidget(self.download_log)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_queue_tab(self) -> QWidget:
        """Create queue/progress tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Active Downloads:"))

        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(5)
        self.queue_table.setHorizontalHeaderLabels(
            ["Title", "Platform", "Progress", "Status", "Action"]
        )
        self.queue_table.setColumnWidth(0, 250)
        self.queue_table.setColumnWidth(1, 100)
        self.queue_table.setColumnWidth(2, 200)
        self.queue_table.setColumnWidth(3, 100)
        self.queue_table.setColumnWidth(4, 80)
        layout.addWidget(self.queue_table)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_history_tab(self) -> QWidget:
        """Create history tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Controls
        controls_layout = QHBoxLayout()

        self.refresh_history_btn = QPushButton("Refresh")
        self.refresh_history_btn.clicked.connect(self.refresh_history)
        controls_layout.addWidget(self.refresh_history_btn)

        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.clicked.connect(self.clear_history)
        controls_layout.addWidget(self.clear_history_btn)

        layout.addLayout(controls_layout)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(
            ["Title", "Platform", "Status", "Date", "View"]
        )
        self.history_table.setColumnWidth(0, 300)
        self.history_table.setColumnWidth(1, 100)
        self.history_table.setColumnWidth(2, 80)
        self.history_table.setColumnWidth(3, 150)
        self.history_table.setColumnWidth(4, 80)
        layout.addWidget(self.history_table)

        self.refresh_history()
        widget.setLayout(layout)
        return widget

    def create_stats_tab(self) -> QWidget:
        """Create statistics tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        self.stats_label = QLabel()
        self.stats_label.setFont(QFont("Courier New", 10))
        layout.addWidget(self.stats_label)

        self.refresh_stats_btn = QPushButton("Refresh Stats")
        self.refresh_stats_btn.clicked.connect(self.refresh_stats)
        layout.addWidget(self.refresh_stats_btn)

        layout.addStretch()
        self.refresh_stats()
        widget.setLayout(layout)
        return widget

    def start_download(self):
        """Start a download."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return

        audio_only = self.audio_only_check.isChecked()
        # Apply current tab selections to config for this download.
        self.config["video_quality"] = self.quality_select.currentText()
        self.config["format_preference"] = self.format_select.currentText()
        download_id = f"download_{len(self.downloads)}_{datetime.now().timestamp()}"

        # Add to queue
        self.downloads[download_id] = {
            "url": url,
            "status": "starting",
            "title": "Loading...",
        }

        # Start download in thread
        worker_thread = QThread()
        worker = DownloadWorker(
            self.async_downloader, self.config, progress_callback=self.enqueue_progress
        )
        worker.moveToThread(worker_thread)
        worker.finished.connect(self.on_download_finished)
        worker_thread.started.connect(
            lambda: worker.run_download(url, download_id, audio_only),
            Qt.ConnectionType.DirectConnection,
        )
        self.worker_threads[download_id] = worker_thread
        self.workers[download_id] = worker
        worker_thread.start()

        self.log_message(f"Queued [{self.short_download_id(download_id)}] {url}")
        self.url_input.clear()
        self.status_label.setText(f"Downloading... ({len(self.downloads)} active)")

    def on_download_progress(self, download_id: str, progress_data: Dict[str, Any]):
        """Handle progress updates from yt-dlp."""
        status = progress_data.get("status", "")
        file_name = self.format_filename(progress_data.get("filename", "file"))
        download_label = self.short_download_id(download_id)

        if status == "downloading":
            percent = self.clean_ansi(progress_data.get("_percent_str", "").strip() or "N/A")
            speed = self.clean_ansi(progress_data.get("_speed_str", "").strip() or "N/A")
            eta = self.clean_ansi(progress_data.get("_eta_str", "").strip() or "N/A")

            # Keep UI log concise.
            progress_value = self.extract_percent_value(percent)
            state = self.progress_state.setdefault(download_id, {})
            file_state = state.setdefault(file_name, {"last_percent": None})
            last_percent = file_state.get("last_percent")

            should_log = False
            if progress_value is None:
                should_log = last_percent is None
            elif last_percent is None:
                should_log = True
            elif progress_value == 100.0 or progress_value - last_percent >= 5.0:
                should_log = True

            if not should_log:
                return

            file_state["last_percent"] = progress_value
            message = (
                f"[{download_label}] {file_name} | {percent} | {speed} | ETA {eta}"
            )
        elif status == "finished":
            message = f"[{download_label}] Post-processing: {file_name}"
        else:
            message = f"[{download_label}] Status: {status or 'unknown'}"

        self.log_message(message)

    def on_download_finished(self, download_id: str, result: Dict[str, Any]):
        """Handle download completion."""
        self.downloads[download_id] = result

        # Add to history
        self.history.add_download(result)

        # Update status
        download_label = self.short_download_id(download_id)
        if result.get("success"):
            self.status_label.setText(f"✓ Downloaded: {result.get('title', 'Unknown')}")
            title = result.get("title", "Unknown")
            self.log_message(f"[{download_label}] Completed: {title}")
        else:
            self.status_label.setText(f"✗ Failed: {result.get('error', 'Unknown error')}")
            self.log_message(f"[{download_label}] Failed: {result.get('error', 'Unknown error')}")

        self.completed_downloads.add(download_id)
        self.progress_state.pop(download_id, None)
        with self.emit_state_lock:
            self.emit_state.pop(download_id, None)
        self.refresh_history()
        self.refresh_stats()

        # Cleanup thread resources for this download cycle
        worker_thread = self.worker_threads.pop(download_id, None)
        self.workers.pop(download_id, None)
        if worker_thread:
            worker_thread.quit()
            worker_thread.wait()

    def log_message(self, message: str):
        """Append a timestamped, colorized message to the download log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = "#cbd5e1"  # default
        if "Completed:" in message:
            color = "#22c55e"
        elif "Failed:" in message:
            color = "#ef4444"
        elif "Queued" in message:
            color = "#f59e0b"
        elif "Post-processing:" in message:
            color = "#a78bfa"
        elif "ETA" in message and "%" in message:
            color = "#38bdf8"
        elif "Status:" in message:
            color = "#94a3b8"

        safe_time = escape(f"[{timestamp}]")
        safe_msg = escape(message)
        html_line = (
            f"<span style='color:#64748b; font-family: Menlo, monospace;'>{safe_time}</span> "
            f"<span style='color:{color}; font-family: Menlo, monospace;'>{safe_msg}</span>"
        )
        self.download_log.append(html_line)

    def enqueue_progress(self, download_id: str, progress_data: Dict[str, Any]):
        """Forward throttled progress to the UI thread via queued Qt signal."""
        status = progress_data.get("status", "")
        if status == "downloading":
            file_name = self.format_filename(progress_data.get("filename", "file"))
            percent_text = self.clean_ansi(progress_data.get("_percent_str", "").strip() or "")
            percent_value = self.extract_percent_value(percent_text)
            now = time.monotonic()

            with self.emit_state_lock:
                download_state = self.emit_state.setdefault(download_id, {})
                file_state = download_state.setdefault(
                    file_name, {"last_percent": None, "last_emit": 0.0}
                )
                last_percent = file_state.get("last_percent")
                last_emit = file_state.get("last_emit", 0.0)

                should_emit = False
                if percent_value is None:
                    should_emit = now - last_emit >= 0.8
                elif last_percent is None:
                    should_emit = True
                elif percent_value == 100.0 or percent_value - last_percent >= 5.0:
                    should_emit = True
                elif now - last_emit >= 1.2:
                    should_emit = True

                if not should_emit:
                    return

                file_state["last_percent"] = percent_value
                file_state["last_emit"] = now

        self.progress_update.emit(download_id, progress_data)

    def short_download_id(self, download_id: str) -> str:
        """Create a compact download label for log readability."""
        return download_id.replace("download_", "d#")

    def format_filename(self, filename: str) -> str:
        """Return basename to avoid noisy absolute paths in logs."""
        return os.path.basename(filename) if filename else "file"

    def clean_ansi(self, text: str) -> str:
        """Strip ANSI color codes from yt-dlp progress strings."""
        return ANSI_ESCAPE_RE.sub("", text).strip()

    def extract_percent_value(self, percent_text: str):
        """Parse numeric percentage from yt-dlp text; return None if unavailable."""
        match = re.search(r"(\d+(?:\.\d+)?)\s*%", percent_text)
        if not match:
            return None
        try:
            return float(match.group(1))
        except ValueError:
            return None

    def refresh_history(self):
        """Refresh history table."""
        history = self.history.get_history(limit=50)

        self.history_table.setRowCount(len(history))
        for i, record in enumerate(history):
            self.history_table.setItem(i, 0, QTableWidgetItem(record.get("title", "Unknown")))
            self.history_table.setItem(i, 1, QTableWidgetItem(record.get("platform", "Unknown")))

            status = "✓" if record.get("success") else "✗"
            self.history_table.setItem(i, 2, QTableWidgetItem(status))

            date_str = record.get("added_at", "")[:10]
            self.history_table.setItem(i, 3, QTableWidgetItem(date_str))

            view_btn = QPushButton("View")
            view_btn.clicked.connect(lambda checked, r=record: self.view_download_info(r))
            self.history_table.setCellWidget(i, 4, view_btn)

    def refresh_stats(self):
        """Refresh statistics."""
        stats = self.history.get_stats()

        stats_text = f"""
Download Statistics:

Total Downloads:    {stats['total_downloads']}
Successful:         {stats['successful']}
Failed:             {stats['failed']}

By Platform:
"""
        for platform, count in stats["by_platform"].items():
            stats_text += f"  {platform}: {count}\n"

        self.stats_label.setText(stats_text)

    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.config = dialog.get_config()
            save_config(self.config)
            self.async_downloader.max_concurrent = self.config.get("max_concurrent_downloads", 1)
            self.quality_select.setCurrentText(self.config.get("video_quality", "best"))
            self.format_select.setCurrentText(self.config.get("format_preference", "mp4"))
            self.status_label.setText("Settings saved")

    def clear_history(self):
        """Clear download history."""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all download history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.history.clear_history()
            self.refresh_history()
            self.refresh_stats()

    def view_download_info(self, record: Dict[str, Any]):
        """View detailed download information."""
        info = f"""
Title: {record.get('title', 'Unknown')}
Platform: {record.get('platform', 'Unknown')}
URL: {record.get('url', 'N/A')}
Status: {'Success' if record.get('success') else 'Failed'}
Date: {record.get('added_at', 'N/A')[:10]}

{f"Error: {record.get('error', '')}" if not record.get('success') else ""}
"""
        QMessageBox.information(self, "Download Info", info)

    def setup_logging(self):
        """Setup logging."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img", "logo.png"))
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))
    window = uDownloaderApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
