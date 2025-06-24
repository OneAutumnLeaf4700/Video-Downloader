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
            # Add the progress hook to the options
            self.options['progress_hooks'] = [self.progress.emit]
            self.download_function(self.url, **self.options)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e)) 