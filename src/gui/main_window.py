# src/gui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QLineEdit, QComboBox, QCheckBox, 
                           QPushButton, QProgressBar)
from PyQt5.QtCore import Qt

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

    def on_format_changed(self, format_text):
        """Enable/disable resolution combo box based on format selection"""
        is_video = format_text.lower() == "mp4"
        self.resolution_combo.setEnabled(is_video)
        self.resolution_combo.setVisible(is_video)
        self.resolution_combo.parent().findChild(QLabel, "").setVisible(is_video)

    def start_download(self):
        """Initiate the download process"""
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("Please enter a URL")
            return

        # Get selected options
        format_option = self.format_combo.currentText().lower()
        resolution = self.resolution_combo.currentText().replace("p", "") if format_option == "mp4" else None
        is_playlist = self.playlist_check.isChecked()

        # TODO: Implement actual download logic
        self.status_label.setText(f"Starting download: {format_option} {'playlist' if is_playlist else 'video'}")
        self.progress_bar.setValue(0) 