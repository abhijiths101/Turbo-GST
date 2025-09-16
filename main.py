import sys
import os
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_stylesheet():
    """Loads the application's stylesheet."""
    try:
        with open(resource_path("resources/styles/dark_theme.qss"), "r") as f:
            return f.read()
    except FileNotFoundError:
        print("Warning: Stylesheet 'dark_theme.qss' not found. Using default style.")
        return ""

if __name__ == "__main__":
    print(sys.executable)
    app = QApplication(sys.argv)
    
    # Apply the stylesheet
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
