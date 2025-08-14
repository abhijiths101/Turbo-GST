import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

def load_stylesheet():
    """Loads the application's stylesheet."""
    try:
        with open("resources/styles/dark_theme.qss", "r") as f:
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