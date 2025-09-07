# src/gui/app.py
import sys
import os
from PyQt6.QtWidgets import QApplication

# Support running both as a package (python -m) and as a top-level script (PyInstaller)
try:  # Relative import when package context is available
    from .main_window import MainWindow
except Exception:  # Fallbacks for script/frozen contexts
    try:
        from gui.main_window import MainWindow  # type: ignore
    except Exception:
        import importlib
        MainWindow = importlib.import_module("main_window").MainWindow  # type: ignore


def run_app():
    """Initialize and run the GUI application"""
    app = QApplication(sys.argv)

    # Load and apply the stylesheet (handle PyInstaller one-file via _MEIPASS)
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        style_path = os.path.join(base_path, "gui", "style.qss")
    else:
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
    return app.exec()


if __name__ == "__main__":
    run_app()
