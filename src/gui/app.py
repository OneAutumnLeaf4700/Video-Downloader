# src/gui/app.py
import sys
from PyQt5.QtWidgets import QApplication
from .main_window import MainWindow

def run_app():
    """Initialize and run the GUI application"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    run_app() 