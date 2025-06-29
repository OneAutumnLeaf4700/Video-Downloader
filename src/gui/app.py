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
    try:
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Warning: Stylesheet file not found at {style_path}")
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
    return app.exec_()


if __name__ == "__main__":
    run_app()
