# src/gui/app.py
import logging
import os
import shutil
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

# Support running both as a package (python -m) and as a top-level script (PyInstaller)
try:  # Relative import when package context is available
    from .main_window import MainWindow
except Exception:  # Fallbacks for script/frozen contexts
    try:
        from gui.main_window import MainWindow  # type: ignore
    except Exception:
        import importlib
        MainWindow = importlib.import_module("main_window").MainWindow  # type: ignore

logger = logging.getLogger(__name__)


def _configure_logging():
    """Initialise root logging once, gated by the VIDEO_DOWNLOADER_DEBUG env var."""
    level = logging.DEBUG if os.environ.get("VIDEO_DOWNLOADER_DEBUG") else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _check_ffmpeg_or_warn(parent=None):
    """Show a non-fatal warning dialog if ffmpeg isn't on PATH.

    yt-dlp depends on ffmpeg for merging and audio extraction; without it,
    most downloads fail mid-flight with cryptic errors. Surfacing the missing
    binary up front lets the user fix the install before they queue work.
    Returns True if ffmpeg is available.
    """
    if shutil.which("ffmpeg"):
        return True
    logger.warning("ffmpeg not found on PATH — downloads will fail mid-flight")
    QMessageBox.warning(
        parent,
        "FFmpeg not found",
        "FFmpeg is required for video/audio conversion but was not found on "
        "your system PATH.\n\nDownload it from https://ffmpeg.org/download.html "
        "and ensure the ffmpeg binary is on PATH, then restart this app.",
    )
    return False


def run_app():
    """Initialize and run the GUI application"""
    _configure_logging()
    app = QApplication(sys.argv)
    _check_ffmpeg_or_warn()

    # Load and apply the stylesheet (handle PyInstaller one-file via _MEIPASS)
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        style_path = os.path.join(base_path, "gui", "style.qss")
    else:
        style_path = os.path.join(os.path.dirname(__file__), "style.qss")
    try:
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        logger.warning("Stylesheet file not found at %s", style_path)
        # Use a basic dark theme as fallback
        fallback_style = (
            "QMainWindow { background-color: #2c3e50; }"
            "QWidget { color: #ecf0f1; font-family: 'Segoe UI', Arial, sans-serif; }"
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "border-radius: 4px; padding: 8px; }"
            "QPushButton:hover { background-color: #2980b9; }"
            "QLineEdit, QComboBox { background-color: #34495e; border: 1px solid "
            "#2c3e50; border-radius: 4px; padding: 4px; }"
        )
        app.setStyleSheet(fallback_style)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    run_app()
