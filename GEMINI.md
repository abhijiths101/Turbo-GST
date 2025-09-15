# Project Overview

This project is a desktop application named "Turbo GST" designed to convert GSTR-1 and GSTR-2 JSON files into user-friendly Excel spreadsheets. It provides a graphical user interface for selecting files and configuring the conversion process.

**Key Technologies:**

*   **Backend:** Python
*   **GUI:** PySide6 (Qt for Python)
*   **Data Processing:** pandas
*   **Styling:** qt-material, QSS (Qt Style Sheets)

**Architecture:**

The application follows a standard structure for a Python desktop application:

*   `main.py`: The main entry point that initializes and runs the application.
*   `app/main_window.py`: Defines the main application window, UI layout, and user interactions.
*   `app/core/`: Contains the core business logic for processing GSTR data.
    *   `gstr1_converter.py`: Handles the conversion of GSTR-1 JSON files.
    *   `gstr2_converter.py`: Handles the conversion of GSTR-2 JSON files.
*   `resources/`: Stores static assets like icons, stylesheets, and configuration files.

# Building and Running

**1. Install Dependencies:**

It is recommended to use a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install -r requirements.txt
```

**2. Run the Application:**

```bash
python main.py
```

# Development Conventions

*   **UI:** The user interface is built with PySide6. UI elements and layouts are defined in `app/main_window.py`.
*   **Styling:** The application is styled using QSS (Qt Style Sheets). The main stylesheet is located at `resources/styles/dark_theme.qss`. The `qt-material` library is also used for theming.
*   **Data Processing:** The core data processing logic is handled by the `gstr1_converter.py` and `gstr2_converter.py` modules. These modules use the pandas library to create and manipulate DataFrames, which are then written to Excel files.
*   **Configuration:** The structure of the GSTR JSON data and the processing rules are defined in JSON configuration files located in the `resources/configs/` directory. This allows for easy modification of the processing logic without changing the Python code.
