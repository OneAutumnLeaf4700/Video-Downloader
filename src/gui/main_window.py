# src/gui/main_window.py
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QLineEdit, QComboBox, QCheckBox, 
                           QPushButton, QProgressBar, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QThread
from .worker import DownloaderWorker
from src.video_downloader.downloader import download_video

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Downloader")
        self.setMinimumSize(600, 400)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # URL Input
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter video or playlist URL")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Output Directory Selection
        output_layout = QHBoxLayout()
        output_label = QLabel("Save to:")
        self.output_path_input = QLineEdit()
        self.output_path_input.setText(os.path.join(os.getcwd(), "downloaded_content"))
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_output_directory)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path_input)
        output_layout.addWidget(browse_button)
        layout.addLayout(output_layout)

        # Format and Resolution Selection
        format_res_layout = QHBoxLayout()
        
        # Format Selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "MP3"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_res_layout.addLayout(format_layout)
        
        # Resolution Selection
        resolution_layout = QHBoxLayout()
        resolution_label = QLabel("Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1080p", "720p", "480p", "360p"])
        resolution_layout.addWidget(resolution_label)
        resolution_layout.addWidget(self.resolution_combo)
        format_res_layout.addLayout(resolution_layout)
        
        # Add some stretch to keep the dropdowns from expanding too much
        format_res_layout.addStretch()
        layout.addLayout(format_res_layout)

        # Playlist Checkbox
        self.playlist_check = QCheckBox("Download as playlist")
        layout.addWidget(self.playlist_check)

        # Download Button
        self.download_button = QPushButton("Download")
        self.download_button.setFixedHeight(40)
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        # Progress Bar
        progress_layout = QVBoxLayout()
        progress_label = QLabel("Progress:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)

        # Status Label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Add stretch to push everything to the top
        layout.addStretch()

        self.thread = None
        self.worker = None

    def show_error_dialog(self, message):
        """Displays a critical error message in a dialog box."""
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Critical)
        dialog.setText("An Error Occurred")
        dialog.setInformativeText(message)
        dialog.setWindowTitle("Error")
        dialog.exec_()

    def browse_output_directory(self):
        """Open a dialog to select the output directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.output_path_input.setText(directory)

    def on_format_changed(self, format_text):
        """Enable/disable resolution combo box based on format selection"""
        is_video = format_text.lower() == "mp4"
        self.resolution_combo.setEnabled(is_video)
        self.resolution_combo.setVisible(is_video)
        # Find the QLabel associated with the resolution combo box and show/hide it.
        # This is a bit of a workaround to find the label in the layout.
        res_label = self.resolution_combo.parent().findChild(QLabel)
        if res_label:
            res_label.setVisible(is_video)

    def start_download(self):
        """Initiate the download process in a background thread."""
        url = self.url_input.text().strip()
        if not url:
            self.show_error_dialog("Please enter a video or playlist URL.")
            return

        output_dir = self.output_path_input.text().strip()
        if not os.path.isdir(output_dir):
            self.show_error_dialog(f"The selected output directory does not exist:\n{output_dir}")
            return

        # Prepare download options
        options = {
            'output_path': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'file_format': self.format_combo.currentText().lower(),
            'resolution': self.resolution_combo.currentText().replace('p', '') if self.resolution_combo.isEnabled() else None,
            'is_playlist': self.playlist_check.isChecked(),
        }
        
        # Setup and start the background worker
        self.thread = QThread()
        self.worker = DownloaderWorker(download_video, url, options)
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_download_error)
        self.worker.progress.connect(self.update_progress)
        
        self.thread.start()

        # Update UI
        self.download_button.setEnabled(False)
        self.status_label.setText("Download in progress...")
        self.progress_bar.setValue(0)

    def on_download_finished(self):
        """Called when the download is successfully completed."""
        self.status_label.setText("Download finished successfully!")
        self.progress_bar.setValue(100)
        self.download_button.setEnabled(True)
        self.thread.quit()
        self.thread.wait()

    def on_download_error(self, error_message):
        """Called when an error occurs during download."""
        self.show_error_dialog(error_message)
        self.status_label.setText("Download failed. Please try again.")
        self.download_button.setEnabled(True)
        self.thread.quit()
        self.thread.wait()

    def update_progress(self, data):
        """Update the progress bar based on yt-dlp's output."""
        if data['status'] == 'downloading':
            total_bytes = data.get('total_bytes') or data.get('total_bytes_estimate', 0)
            if total_bytes > 0:
                percentage = (data['downloaded_bytes'] / total_bytes) * 100
                self.progress_bar.setValue(int(percentage))
        elif data['status'] == 'finished':
             self.progress_bar.setValue(100) 