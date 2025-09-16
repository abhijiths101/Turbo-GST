# Function Call Graph

This document outlines the function call hierarchy of the Turbo-GST application.

## High-Level Overview

The application starts in `main.py`, which initializes a `QApplication` and the `MainWindow`. The `MainWindow` is the central hub of the UI, from which all other parts of the application are accessed. The core data processing logic is located in the `app/core` directory, with different modules for GSTR-1 and GSTR-2 conversion. These converters use common processing functions from `app/core/common_processors.py`.

## Call Graph

```
main.py
|
|-- main()
    |-- QApplication()
    |-- load_stylesheet()
    |-- MainWindow()
        |-- __init__()
        |   |-- _create_sidebar()
        |   |-- _create_main_content()
        |   |   |-- _create_home_page()
        |   |   |-- _create_gstr1_page()
        |   |   |   |-- on_options_toggled()
        |   |   |   |-- on_gstr1_convert_clicked()
        |   |   |-- _create_placeholder_page()
        |   |   |-- _change_page()
        |   |       |-- _update_active_button()
        |   |-- toggle_sidebar()
        |
        |-- GSTR-1 Conversion (Triggered by user interaction in GSTR-1 page)
        |   |-- on_gstr1_convert_clicked() (in app/main_window.py)
        |       |-- convert_gstr1_json_to_excel() (in app/core/gstr1_converter.py)
        |           |-- load_json_from_path()
        |           |-- split_nested_and_non_nested_keys()
        |           |-- json_normalize_with_meta()
        |           |-- safe_reorder()
        |           |-- convert_column_to_date()
        |
        |-- GSTR-2 Conversion (Triggered by user interaction)
            |-- convert_gstr2_to_excel() (in app/core/gstr2_converter.py)
                |-- (Details for GSTR-2 would follow a similar pattern)

```
