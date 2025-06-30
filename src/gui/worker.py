# src/gui/worker.py
from PyQt5.QtCore import QObject, pyqtSignal


class DownloaderWorker(QObject):
    """
    Runs the download task in a separate thread.
    """

    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(dict)

    def __init__(self, download_function, url, options):
        super().__init__()
        self.download_function = download_function
        self.url = url
        self.options = options

    def run(self):
        """Execute the download."""
        try:
            # Preserve existing progress hooks and add our own
            existing_hooks = self.options.get("progress_hooks", [])
            if self.progress.emit not in existing_hooks:
                existing_hooks.append(self.progress.emit)
            self.options["progress_hooks"] = existing_hooks
            self.download_function(self.url, **self.options)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
