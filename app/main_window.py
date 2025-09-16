import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QStatusBar, QFrame, QGridLayout, QCheckBox, QFileDialog
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
from qt_material import apply_stylesheet, get_theme

from app.core.gstr1_converter import convert_gstr1_json_to_excel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Turbo GST")
        self.resize(1024, 768)
        self.is_sidebar_collapsed = False
        
        self.gstr1_source_paths = None
        self.gstr1_dest_path = None
        
        # Define all checkbox options with default values (all True)
        self.checkbox_options = {
            "B2B": True,
            "B2C": True,
            "CDNR": True,
            "Export": True
        }
        
        # Initialize dictionary to store checkboxes
        self.gstr1_checkboxes = {}

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Sidebar ---
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        # --- Main Content ---
        self.main_content = self._create_main_content()
        main_layout.addWidget(self.main_content, 1)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Status: Ready")
        self.version_label = QLabel("Version 1.0.0")
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.version_label)

        # Set initial page
        self._update_active_button(self.home_button)

    def _create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        self.sidebar_layout = QVBoxLayout(sidebar)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_layout.setSpacing(5)

        # --- Header with Title and Toggle Button ---
        header_layout = QHBoxLayout()
        self.title_label = QLabel("TURBO GST")
        self.title_label.setObjectName("titleLabel")
        
        self.toggle_button = QPushButton()
        self.toggle_button.setIcon(QIcon(os.path.join('resources', 'icons', 'left_arrow.svg')))
        self.toggle_button.setFixedSize(28, 28)
        self.toggle_button.setIconSize(QSize(28, 28))
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_button)
        self.sidebar_layout.addLayout(header_layout)

        # --- Menu Buttons ---
        self.home_button = QPushButton("Home")
        self.gstr1_button = QPushButton("GSTR-1")
        self.gstr2_button = QPushButton("GSTR-2")
        self.settings_button = QPushButton("Settings")
        self.about_button = QPushButton("About")
        
        self.menu_buttons = {
            self.home_button: {"icon": "home", "text": "Home"},
            self.gstr1_button: {"icon": "description", "text": "GSTR-1"},
            self.gstr2_button: {"icon": "receipt_long", "text": "GSTR-2"},
            self.settings_button: {"icon": "settings", "text": "Settings"},
            self.about_button: {"icon": "info", "text": "About"}
        }
        
        for btn, data in self.menu_buttons.items():
            btn.setIcon(QIcon(os.path.join('resources', 'icons', f'{data["icon"]}.svg')))
            btn.setText(f" {data['text']}")
            btn.setIconSize(QSize(24, 24))

        self.sidebar_layout.addWidget(self.home_button)
        self.sidebar_layout.addWidget(self.gstr1_button)
        self.sidebar_layout.addWidget(self.gstr2_button)
        
        self.sidebar_layout.addStretch()

        self.sidebar_layout.addWidget(self.settings_button)
        self.sidebar_layout.addWidget(self.about_button)

        return sidebar

    def _create_main_content(self):
        main_content = QWidget()
        main_content.setObjectName("mainContent")
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(20, 20, 20, 20)

        self.stacked_widget = QStackedWidget()
        main_content_layout.addWidget(self.stacked_widget)

        self.home_page = self._create_home_page()
        self.gstr1_page = self._create_gstr1_page()
        self.gstr2_page = self._create_placeholder_page("GSTR-2")
        self.settings_page = self._create_placeholder_page("Settings")
        self.about_page = self._create_placeholder_page("About")

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.gstr1_page)
        self.stacked_widget.addWidget(self.gstr2_page)
        self.stacked_widget.addWidget(self.settings_page)
        self.stacked_widget.addWidget(self.about_page)

        self.home_button.clicked.connect(lambda: self._change_page(0, self.home_button))
        self.gstr1_button.clicked.connect(lambda: self._change_page(1, self.gstr1_button))
        self.gstr2_button.clicked.connect(lambda: self._change_page(2, self.gstr2_button))
        self.settings_button.clicked.connect(lambda: self._change_page(3, self.settings_button))
        self.about_button.clicked.connect(lambda: self._change_page(4, self.about_button))

        return main_content

    def _create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        header = QLabel("Welcome to Turbo GST")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("contentCard")
        card_layout = QVBoxLayout(card)
        
        instructions_title = QLabel("Instructions")
        instructions_title.setObjectName("cardTitleLabel")
        card_layout.addWidget(instructions_title)

        desc1 = QLabel("To get started, select either GSTR-1 or GSTR-2 from the sidebar menu. Then use the 'File' or 'Folder' buttons to select your JSON data.")
        desc1.setObjectName("descriptionLabel")
        desc1.setWordWrap(True)
        card_layout.addWidget(desc1)

        desc2 = QLabel("The application will automatically detect the GST type based on your selected files. Configure your options in the scrollable area below, then click 'Convert' to generate your output.")
        desc2.setObjectName("descriptionLabel")
        desc2.setWordWrap(True)
        card_layout.addWidget(desc2)

        layout.addWidget(card)
        return page

    def _create_gstr1_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        header = QLabel("GSTR-1 Conversion")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("contentCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)

        file_select_layout = QHBoxLayout()
        file_button = QPushButton("Select File(s)")
        file_button.setIcon(QIcon(os.path.join('resources', 'icons', 'file.svg')))
        file_button.setIconSize(QSize(24, 24))
        file_button.setObjectName("fileSelectButton")
        file_button.clicked.connect(self._select_gstr1_source_files)
        
        folder_button = QPushButton("Select Folder")
        folder_button.setIcon(QIcon(os.path.join('resources', 'icons', 'folder.svg')))
        folder_button.setIconSize(QSize(24, 24))
        folder_button.setObjectName("folderSelectButton")
        folder_button.clicked.connect(self._select_gstr1_source_folder)
        
        file_select_layout.addWidget(file_button)
        file_select_layout.addWidget(folder_button)
        file_select_layout.addStretch()
        card_layout.addLayout(file_select_layout)

        self.gstr1_source_path_button = QPushButton("Select source path...")
        self.gstr1_source_path_button.setIcon(QIcon(os.path.join('resources', 'icons', 'source.svg')))
        self.gstr1_source_path_button.setIconSize(QSize(24, 24))
        self.gstr1_source_path_button.setObjectName("pathDisplayButton")
        card_layout.addWidget(self.gstr1_source_path_button)

        self.gstr1_dest_path_button = QPushButton("Select destination path...")
        self.gstr1_dest_path_button.setIcon(QIcon(os.path.join('resources', 'icons', 'destination.svg')))
        self.gstr1_dest_path_button.setIconSize(QSize(24, 24))
        self.gstr1_dest_path_button.setObjectName("pathDisplayButton")
        self.gstr1_dest_path_button.clicked.connect(self._select_gstr1_dest_folder)
        card_layout.addWidget(self.gstr1_dest_path_button)

        options_container = QFrame()
        options_container.setObjectName("optionsContainer")
        options_layout = QVBoxLayout(options_container)
        options_layout.setContentsMargins(0,0,0,0)
        options_layout.setSpacing(0)

        self.options_header = QPushButton()
        self.options_header.setObjectName("optionsHeaderButton")
        self.options_header.setCheckable(True)
        self.options_header.setChecked(True)
        
        self.options_body = QWidget()
        self.options_body.setObjectName("optionsBody")
        options_grid = QGridLayout(self.options_body)
        
        for i, (key, default_value) in enumerate(self.checkbox_options.items()):
            row, col = i // 2, (i % 2) * 2
            checkbox = QCheckBox(key)
            checkbox.setChecked(default_value)
            self.gstr1_checkboxes[key] = checkbox
            options_grid.addWidget(checkbox, row, col)

        options_layout.addWidget(self.options_header)
        options_layout.addWidget(self.options_body)
        card_layout.addWidget(options_container)
        
        self.options_header.toggled.connect(self.on_options_toggled)
        self.on_options_toggled(True)

        convert_button = QPushButton("Convert")
        convert_button.setIcon(QIcon(os.path.join('resources', 'icons', 'convert.svg')))
        convert_button.setIconSize(QSize(24, 24))
        convert_button.setObjectName("convertButton")
        convert_button.clicked.connect(self.on_gstr1_convert_clicked)
        card_layout.addWidget(convert_button)

        layout.addWidget(card)
        return page

    def _create_placeholder_page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(f"{title} page is under construction.")
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName("sectionHeader")
        layout.addWidget(label)
        return page

    def _change_page(self, index, button):
        self.stacked_widget.setCurrentIndex(index)
        self._update_active_button(button)

    def _update_active_button(self, active_button):
        for button in self.menu_buttons:
            button.setProperty("active", False)
        active_button.setProperty("active", True)
        
        for button in self.menu_buttons:
            button.style().unpolish(button)
            button.style().polish(button)

    def on_options_toggled(self, checked):
        self.options_body.setVisible(checked)
        if checked:
            self.options_header.setText("Options")
            self.options_header.setIcon(QIcon(os.path.join('resources', 'icons', 'arrow_down.svg')))
        else:
            self.options_header.setText("Options")
            self.options_header.setIcon(QIcon(os.path.join('resources', 'icons', 'arrow_up.svg')))

    def toggle_sidebar(self):
        self.is_sidebar_collapsed = not self.is_sidebar_collapsed
        
        start_width = self.sidebar.width()
        end_width = 70 if self.is_sidebar_collapsed else 250

        self.title_label.setVisible(not self.is_sidebar_collapsed)
        
        for btn, data in self.menu_buttons.items():
            if self.is_sidebar_collapsed:
                btn.setText("")
            else:
                btn.setText(f" {data['text']}")
        
        if self.is_sidebar_collapsed:
            self.toggle_button.setIcon(QIcon(os.path.join('resources', 'icons', 'right_arrow.svg')))
        else:
            self.toggle_button.setIcon(QIcon(os.path.join('resources', 'icons', 'left_arrow.svg')))

        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(end_width)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.start()
    
    def get_checkbox_states(self):
        return {key: checkbox.isChecked() for key, checkbox in self.gstr1_checkboxes.items()}
    
    def _select_gstr1_source_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select GSTR-1 JSON Files", "", "JSON Files (*.json)")
        if files:
            self.gstr1_source_paths = files
            self.gstr1_source_path_button.setText(f"{len(files)} file(s) selected")
            self.status_label.setText(f"Status: Loaded {len(files)} source file(s).")

    def _select_gstr1_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder Containing GSTR-1 JSON Files")
        if folder:
            self.gstr1_source_paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.json')]
            self.gstr1_source_path_button.setText(folder)
            self.status_label.setText(f"Status: Loaded {len(self.gstr1_source_paths)} file(s) from folder.")

    def _select_gstr1_dest_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.gstr1_dest_path = folder
            self.gstr1_dest_path_button.setText(folder)
            self.status_label.setText("Status: Destination folder selected.")

    def on_gstr1_convert_clicked(self):
        if not self.gstr1_source_paths:
            self.status_label.setText("Status: Error - Please select source file(s) or a folder.")
            return
        if not self.gstr1_dest_path:
            self.status_label.setText("Status: Error - Please select a destination folder.")
            return

        checkbox_states = self.get_checkbox_states()
        self.status_label.setText(f"Status: Starting conversion with options: {checkbox_states}")
        
        total_files = len(self.gstr1_source_paths)
        success_count = 0
        
        for i, json_path in enumerate(self.gstr1_source_paths):
            base_name = os.path.basename(json_path)
            excel_name = os.path.splitext(base_name)[0] + '.xlsx'
            excel_path = os.path.join(self.gstr1_dest_path, excel_name)
            
            self.status_label.setText(f"Status: Converting {i+1}/{total_files}: {base_name}...")
            QApplication.processEvents()

            success, message = convert_gstr1_json_to_excel(json_path, excel_path)
            
            if success:
                success_count += 1
            else:
                print(f"Failed to convert {json_path}: {message}")

        self.status_label.setText(f"Status: Conversion complete. {success_count}/{total_files} file(s) converted successfully.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_blue.xml')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())