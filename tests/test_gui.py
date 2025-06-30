# tests/test_gui.py
import sys
import os
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app
    app.quit()


@pytest.fixture
def main_window(qapp):
    """Create MainWindow instance for testing"""
    window = MainWindow()
    return window


class TestMainWindow:
    """Test class for MainWindow GUI components"""

    def test_window_initialization(self, main_window):
        """Test that the main window initializes correctly"""
        assert main_window.windowTitle() == "Video Downloader"
        assert main_window.minimumSize().width() == 600
        assert main_window.minimumSize().height() == 400

    def test_url_input_placeholder(self, main_window):
        """Test that URL input has correct placeholder text"""
        assert main_window.url_input.placeholderText() == "Enter video or playlist URL"

    def test_format_combo_items(self, main_window):
        """Test that format combo box has correct items"""
        expected_items = ["MP4", "MP3"]
        actual_items = [
            main_window.format_combo.itemText(i)
            for i in range(main_window.format_combo.count())
        ]
        assert actual_items == expected_items

    def test_resolution_combo_items(self, main_window):
        """Test that resolution combo box has correct items"""
        expected_items = ["1080p", "720p", "480p", "360p"]
        actual_items = [
            main_window.resolution_combo.itemText(i)
            for i in range(main_window.resolution_combo.count())
        ]
        assert actual_items == expected_items

    def test_format_change_effects(self, main_window):
        """Test that changing format affects resolution combo visibility"""
        # Show the window for proper layout
        main_window.show()

        # Test MP4 format (resolution should be enabled)
        main_window.format_combo.setCurrentText("MP4")
        main_window.on_format_changed("MP4")
        assert main_window.resolution_combo.isEnabled()
        assert main_window.resolution_combo.isVisible()

        # Test MP3 format (resolution should be disabled)
        main_window.format_combo.setCurrentText("MP3")
        main_window.on_format_changed("MP3")
        assert not main_window.resolution_combo.isEnabled()
        assert not main_window.resolution_combo.isVisible()

        main_window.hide()

    def test_empty_url_validation(self, main_window):
        """Test that empty URL shows error dialog"""
        with patch.object(main_window, "show_error_dialog") as mock_error:
            main_window.url_input.setText("")
            main_window.start_download()
            mock_error.assert_called_once_with("Please enter a video or playlist URL.")

    def test_invalid_directory_validation(self, main_window):
        """Test that invalid directory shows error dialog"""
        with patch.object(main_window, "show_error_dialog") as mock_error:
            main_window.url_input.setText("https://example.com/video")
            main_window.output_path_input.setText("/nonexistent/directory")
            main_window.start_download()
            mock_error.assert_called_once()
            assert "does not exist" in mock_error.call_args[0][0]

    @patch("os.path.isdir", return_value=True)
    @patch("gui.main_window.QThread")
    @patch("gui.main_window.DownloaderWorker")
    def test_successful_download_start(
        self, mock_worker, mock_thread, mock_isdir, main_window
    ):
        """Test that valid inputs start download process"""
        main_window.url_input.setText("https://example.com/video")
        main_window.output_path_input.setText("/valid/directory")

        main_window.start_download()

        # Verify UI state changes
        assert not main_window.download_button.isEnabled()
        assert main_window.status_label.text() == "Download in progress..."
        assert main_window.progress_bar.value() == 0

    def test_progress_update(self, main_window):
        """Test progress bar updates correctly"""
        # Test downloading status
        progress_data = {
            "status": "downloading",
            "downloaded_bytes": 500,
            "total_bytes": 1000,
        }
        main_window.update_progress(progress_data)
        assert main_window.progress_bar.value() == 50

        # Test finished status
        finished_data = {"status": "finished"}
        main_window.update_progress(finished_data)
        assert main_window.progress_bar.value() == 100

    def test_download_finished_callback(self, main_window):
        """Test download finished callback resets UI state"""
        # Mock thread to avoid actual thread operations
        main_window.thread = Mock()

        main_window.on_download_finished()

        assert main_window.download_button.isEnabled()
        assert "successfully" in main_window.status_label.text()
        assert main_window.progress_bar.value() == 100

    def test_download_error_callback(self, main_window):
        """Test download error callback handles errors properly"""
        # Mock thread to avoid actual thread operations
        main_window.thread = Mock()

        with patch.object(main_window, "show_error_dialog") as mock_error:
            main_window.on_download_error("Test error message")

            mock_error.assert_called_once_with("Test error message")
            assert main_window.download_button.isEnabled()
            assert "failed" in main_window.status_label.text()

    def test_browse_directory_dialog(self, main_window):
        """Test browse directory dialog functionality"""
        with patch(
            "gui.main_window.QFileDialog.getExistingDirectory",
            return_value="/selected/path",
        ):
            main_window.browse_output_directory()
            assert main_window.output_path_input.text() == "/selected/path"

        # Test when dialog is cancelled
        with patch("gui.main_window.QFileDialog.getExistingDirectory", return_value=""):
            original_path = main_window.output_path_input.text()
            main_window.browse_output_directory()
            assert main_window.output_path_input.text() == original_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
