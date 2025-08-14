import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

def load_stylesheet(theme="dark"):
    """Loads the application's stylesheet based on the selected theme."""
    try:
        if theme == "dark":
            with open("resources/styles/dark_theme.qss", "r") as f:
                return f.read()
        else:  # light theme
            with open("resources/styles/light_theme.qss", "r") as f:
                return f.read()
    except FileNotFoundError as e:
        print(f"Warning: Stylesheet not found. {e}")
        return ""

if __name__ == "__main__":
    print(sys.executable)
    app = QApplication(sys.argv)
    
    # Set application name and organization for settings
    app.setApplicationName("TurboGST")
    app.setOrganizationName("TurboGST")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())