# tests/test_worker.py
import sys
import os
import pytest
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from PyQt5.QtCore import QObject
from gui.worker import DownloaderWorker


class TestDownloaderWorker:
    """Test class for DownloaderWorker thread functionality"""

    def test_worker_initialization(self):
        """Test that worker initializes correctly"""
        mock_download_func = Mock()
        url = "https://example.com/video"
        options = {"format": "mp4"}

        worker = DownloaderWorker(mock_download_func, url, options)

        assert worker.download_function == mock_download_func
        assert worker.url == url
        assert worker.options == options
        assert isinstance(worker, QObject)

    def test_successful_download_run(self):
        """Test worker run method with successful download"""
        mock_download_func = Mock()
        url = "https://example.com/video"
        options = {"format": "mp4"}

        worker = DownloaderWorker(mock_download_func, url, options)

        # Mock signals
        worker.finished = Mock()
        worker.error = Mock()
        worker.progress = Mock()

        worker.run()

        # Verify download function was called once
        mock_download_func.assert_called_once()

        # Verify it was called with the URL and progress hooks
        call_args = mock_download_func.call_args
        assert call_args[0][0] == url
        assert worker.progress.emit in call_args[1]["progress_hooks"]
        assert call_args[1]["format"] == "mp4"

        # Verify finished signal was emitted
        worker.finished.emit.assert_called_once()

        # Verify error signal was not emitted
        worker.error.emit.assert_not_called()

    def test_download_error_handling(self):
        """Test worker error handling when download fails"""
        mock_download_func = Mock(side_effect=Exception("Download failed"))
        url = "https://example.com/video"
        options = {"format": "mp4"}

        worker = DownloaderWorker(mock_download_func, url, options)

        # Mock signals
        worker.finished = Mock()
        worker.error = Mock()
        worker.progress = Mock()

        worker.run()

        # Verify error signal was emitted with correct message
        worker.error.emit.assert_called_once_with("Download failed")

        # Verify finished signal was not emitted
        worker.finished.emit.assert_not_called()

    def test_progress_hooks_added(self):
        """Test that progress hooks are correctly added to options"""
        mock_download_func = Mock()
        url = "https://example.com/video"
        options = {"format": "mp4"}

        worker = DownloaderWorker(mock_download_func, url, options)
        worker.progress = Mock()

        worker.run()

        # Verify progress_hooks were added to options
        call_args = mock_download_func.call_args
        assert call_args[0][0] == url
        assert worker.progress.emit in call_args[1]["progress_hooks"]
        assert call_args[1]["format"] == "mp4"

    def test_existing_progress_hooks_preserved(self):
        """Test that existing progress hooks in options are preserved"""
        existing_hook = Mock()
        mock_download_func = Mock()
        url = "https://example.com/video"
        options = {"format": "mp4", "progress_hooks": [existing_hook]}

        worker = DownloaderWorker(mock_download_func, url, options)
        worker.progress = Mock()

        worker.run()

        # Verify both existing and new progress hooks are present
        call_args = mock_download_func.call_args[1]
        assert existing_hook in call_args["progress_hooks"]
        assert worker.progress.emit in call_args["progress_hooks"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
