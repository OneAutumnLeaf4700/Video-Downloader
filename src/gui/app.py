# src/gui/app.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from .main_window import MainWindow

def run_app():
    """Initialize and run the GUI application"""
    app = QApplication(sys.argv)

    # Load and apply the stylesheet
    style_path = os.path.join(os.path.dirname(__file__), "style.qss")
    with open(style_path, "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    run_app() 