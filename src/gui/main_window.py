# src/gui/main_window.py
import os
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QProgressBar,
    QFileDialog,
    QMessageBox,
    QApplication,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QGroupBox,
    QTextEdit,
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QIcon
from .worker import DownloaderWorker
from ..video_downloader.downloader import download_video
from ..video_downloader.queue_manager import DownloadQueueManager, DownloadStatus


class _UiBridge(QObject):
    task_started = pyqtSignal(object)
    task_progress = pyqtSignal(object)
    task_completed = pyqtSignal(object)
    task_failed = pyqtSignal(object)
    queue_empty = pyqtSignal()


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
        self.output_path_input.setReadOnly(True)
        browse_button = QPushButton("Browse")
        browse_button.setIcon(QIcon.fromTheme("document-open"))
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
        
        # Store reference to resolution label for later use
        self.resolution_label = resolution_label

        # Add some stretch to keep the dropdowns from expanding too much
        format_res_layout.addStretch()
        layout.addLayout(format_res_layout)

        # Playlist Checkbox
        self.playlist_check = QCheckBox("Download as playlist")
        layout.addWidget(self.playlist_check)

        # Download Button
        self.download_button = QPushButton("Download")
        self.download_button.setFixedHeight(40)
        self.download_button.setIcon(QIcon.fromTheme("arrow-down"))
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

        # Download Queue Display
        queue_layout = QVBoxLayout()
        queue_label = QLabel("Download Queue:")
        self.queue_list = QListWidget()
        self.queue_list.setMaximumHeight(100)
        queue_layout.addWidget(queue_label)
        queue_layout.addWidget(self.queue_list)
        layout.addLayout(queue_layout)

        # Status Label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Add stretch to push everything to the top
        layout.addStretch()

        # Initialize download queue manager
        self.queue_manager = DownloadQueueManager(download_video, max_workers=3)
        # Bridge signals to ensure thread-safe GUI updates
        self._bridge = _UiBridge()
        self._bridge.task_started.connect(self.on_task_started)
        self._bridge.task_progress.connect(self.on_task_progress)
        self._bridge.task_completed.connect(self.on_task_completed)
        self._bridge.task_failed.connect(self.on_task_failed)
        self._bridge.queue_empty.connect(self.on_queue_empty)
        self.setup_queue_callbacks()
        
        # Download tracking
        self.active_downloads = {}  # task_id -> task info

    def setup_queue_callbacks(self):
        """Setup callbacks for the download queue manager."""
        self.queue_manager.on_task_started = lambda task: self._bridge.task_started.emit(task)
        self.queue_manager.on_task_progress = lambda task: self._bridge.task_progress.emit(task)
        self.queue_manager.on_task_completed = lambda task: self._bridge.task_completed.emit(task)
        self.queue_manager.on_task_failed = lambda task: self._bridge.task_failed.emit(task)
        self.queue_manager.on_queue_empty = lambda: self._bridge.queue_empty.emit()

    def show_error_dialog(self, message):
        """Displays a critical error message in a dialog box."""
        QMessageBox.critical(self, "An Error Occurred", message)

    def browse_output_directory(self):
        """Open a dialog to select the output directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.output_path_input.setText(directory)

    def on_format_changed(self, format_text):
        """Enable/disable resolution combo box based on format selection"""
        print(f"DEBUG: Format changed to: {format_text}")
        is_video = format_text.lower() == "mp4"
        print(f"DEBUG: Is video format: {is_video}")
        
        self.resolution_combo.setEnabled(is_video)
        self.resolution_combo.setVisible(is_video)
        self.resolution_label.setVisible(is_video)
        print(f"DEBUG: Resolution label visible: {is_video}")

    def start_download(self):
        """Add download to the multi-threaded queue."""
        print("DEBUG: start_download() called")
        
        url = self.url_input.text().strip()
        print(f"DEBUG: URL = '{url}'")
        
        if not url:
            print("DEBUG: No URL provided, showing error dialog")
            self.show_error_dialog("Please enter a video or playlist URL.")
            return

        output_dir = self.output_path_input.text().strip()
        print(f"DEBUG: Output directory = '{output_dir}'")
        
        if not os.path.isdir(output_dir):
            print(f"DEBUG: Output directory doesn't exist, creating: {output_dir}")
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                print(f"DEBUG: Failed to create output directory: {e}")
                self.show_error_dialog(
                    f"Failed to create output directory:\n{output_dir}\n\n{e}"
                )
                return

        # Prepare download options
        options = {
            "output_path": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "file_format": self.format_combo.currentText().lower(),
            "resolution": (
                self.resolution_combo.currentText().replace("p", "")
                if self.resolution_combo.isEnabled()
                else None
            ),
            "is_playlist": self.playlist_check.isChecked(),
        }
        print(f"DEBUG: Download options = {options}")

        try:
            # Add to queue
            print("DEBUG: Adding download to queue manager...")
            task_id = self.queue_manager.add_download(url, options)
            print(f"DEBUG: Task ID = {task_id}")
            
            self.active_downloads[task_id] = {
                "url": url,
                "options": options,
                "started": False
            }

            # Update UI
            print("DEBUG: Updating UI...")
            self.download_button.setEnabled(False)
            self.status_label.setText("Download added to queue...")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.update_queue_display()
            print("DEBUG: start_download() completed successfully")
            
        except Exception as e:
            print(f"DEBUG: Exception in start_download(): {e}")
            import traceback
            traceback.print_exc()
            self.show_error_dialog(f"Failed to start download: {e}")
            self.download_button.setEnabled(True)
            QApplication.restoreOverrideCursor()

    def on_task_started(self, task):
        """Called when a download task starts."""
        if task.id in self.active_downloads:
            self.active_downloads[task.id]["started"] = True
            self.status_label.setText(f"Downloading: {task.url[:50]}...")
            self.update_queue_display()

    def on_task_progress(self, task):
        """Called when a download task progress updates."""
        if task.id in self.active_downloads:
            self.progress_bar.setValue(int(task.progress))

    def on_task_completed(self, task):
        """Called when a download task completes successfully."""
        if task.id in self.active_downloads:
            del self.active_downloads[task.id]
            self.status_label.setText("Download completed successfully!")
            self.progress_bar.setValue(100)
            self.download_button.setEnabled(True)
            QApplication.restoreOverrideCursor()
            self.update_queue_display()

    def on_task_failed(self, task):
        """Called when a download task fails."""
        if task.id in self.active_downloads:
            del self.active_downloads[task.id]
            self.show_error_dialog(f"Download failed: {task.error_message}")
            self.status_label.setText("Download failed. Please try again.")
            self.download_button.setEnabled(True)
            QApplication.restoreOverrideCursor()
            self.update_queue_display()

    def on_queue_empty(self):
        """Called when the download queue is empty."""
        self.status_label.setText("All downloads completed!")
        self.progress_bar.setValue(100)
        self.download_button.setEnabled(True)
        QApplication.restoreOverrideCursor()
        self.update_queue_display()

    def update_queue_display(self):
        """Update the download queue display."""
        self.queue_list.clear()
        
        # Get all tasks from queue manager
        all_tasks = self.queue_manager.get_all_tasks()
        queue_info = self.queue_manager.get_queue_info()
        
        # Add active downloads
        for task_id, task in all_tasks.items():
            if task.status == DownloadStatus.DOWNLOADING:
                item_text = f"🔄 Downloading: {task.url[:40]}... ({task.progress:.1f}%)"
            elif task.status == DownloadStatus.PENDING:
                item_text = f"⏳ Queued: {task.url[:40]}..."
            elif task.status == DownloadStatus.COMPLETED:
                item_text = f"✅ Completed: {task.url[:40]}..."
            elif task.status == DownloadStatus.FAILED:
                item_text = f"❌ Failed: {task.url[:40]}..."
            else:
                item_text = f"📋 {task.url[:40]}..."
            
            item = QListWidgetItem(item_text)
            self.queue_list.addItem(item)
        
        # Update status with queue info
        if queue_info["total"] > 0:
            status_text = f"Queue: {queue_info['downloading']} downloading, {queue_info['pending']} pending"
            if queue_info["failed"] > 0:
                status_text += f", {queue_info['failed']} failed"
            self.status_label.setText(status_text)
