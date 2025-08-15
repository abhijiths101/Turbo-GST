# import sys
import os
from PySide6.QtWidgets import (
    # QApplication, 
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QStatusBar, QFrame, QGridLayout, QCheckBox,
    QRadioButton, QButtonGroup, QGroupBox
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QSettings
from PySide6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Turbo GST")
        self.resize(1024, 768)
        self.is_sidebar_collapsed = False
        
        # Initialize settings
        self.settings = QSettings("TurboGST", "App")
        self.current_theme = self.settings.value("theme", "dark")
        
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

        # Apply initial theme
        self.apply_theme(self.current_theme)
        
        # Set initial page
        self._update_active_button(self.home_button)

    def get_icon_path(self, icon_name):
        """Get the icon path based on current theme"""
        if self.current_theme == "light":
            # Check if light version exists
            light_icon_path = os.path.join('resources', 'icons', f'{icon_name}_light.svg')
            if os.path.exists(light_icon_path):
                return light_icon_path
        
        # Default to dark theme icon
        return os.path.join('resources', 'icons', f'{icon_name}.svg')

    def apply_theme(self, theme):
        """Apply the selected theme to the application"""
        try:
            if theme == "dark":
                with open("resources/styles/dark_theme.qss", "r") as f:
                    stylesheet = f.read()
            else:  # light theme
                with open("resources/styles/light_theme.qss", "r") as f:
                    stylesheet = f.read()
            
            self.setStyleSheet(stylesheet)
            self.settings.setValue("theme", theme)
            self.current_theme = theme
            self.status_label.setText(f"Status: Theme changed to {theme}")
            
            # Update all icons
            self.update_all_icons()
        except FileNotFoundError as e:
            print(f"Warning: Stylesheet not found. {e}")

    def update_all_icons(self):
        """Update all icons in the application based on current theme"""
        # Update sidebar toggle button
        self.toggle_button.setIcon(QIcon(self.get_icon_path("left_arrow" if not self.is_sidebar_collapsed else "right_arrow")))
        
        # Update menu buttons
        for btn, data in self.menu_buttons.items():
            btn.setIcon(QIcon(self.get_icon_path(data["icon"])))
        
        # Update GSTR-1 page icons
        if hasattr(self, 'gstr1_page'):
            # Find and update file and folder buttons
            for child in self.gstr1_page.findChildren(QPushButton):
                if child.objectName() == "fileSelectButton":
                    child.setIcon(QIcon(self.get_icon_path("file")))
                elif child.objectName() == "folderSelectButton":
                    child.setIcon(QIcon(self.get_icon_path("folder")))
                elif child.objectName() == "pathDisplayButton":
                    # Check if it's source or destination path button
                    if "source" in child.text().lower():
                        child.setIcon(QIcon(self.get_icon_path("source")))
                    elif "destination" in child.text().lower():
                        child.setIcon(QIcon(self.get_icon_path("destination")))
                elif child.objectName() == "convertButton":
                    child.setIcon(QIcon(self.get_icon_path("convert")))
                elif child.objectName() == "optionsHeaderButton":
                    if self.options_body.isVisible():
                        child.setIcon(QIcon(self.get_icon_path("arrow_down")))
                    else:
                        child.setIcon(QIcon(self.get_icon_path("arrow_up")))

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
        self.toggle_button.setIcon(QIcon(self.get_icon_path("left_arrow")))
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
            btn.setIcon(QIcon(self.get_icon_path(data["icon"])))
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
        self.settings_page = self._create_settings_page()
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

    def _create_settings_page(self):
        """Create the settings page with theme selection"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        header = QLabel("Application Settings")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("contentCard")
        card_layout = QVBoxLayout(card)
        
        # Theme Selection Group
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout()
        
        self.dark_theme_radio = QRadioButton("Dark Theme")
        self.light_theme_radio = QRadioButton("Light Theme")
        
        theme_layout.addWidget(self.dark_theme_radio)
        theme_layout.addWidget(self.light_theme_radio)
        theme_group.setLayout(theme_layout)
        
        # Set initial selection based on saved theme
        if self.current_theme == "dark":
            self.dark_theme_radio.setChecked(True)
        else:
            self.light_theme_radio.setChecked(True)
        
        # Create button group for exclusive selection
        self.theme_button_group = QButtonGroup()
        self.theme_button_group.addButton(self.dark_theme_radio)
        self.theme_button_group.addButton(self.light_theme_radio)
        
        # Connect radio buttons to theme change
        self.dark_theme_radio.clicked.connect(lambda: self.apply_theme("dark"))
        self.light_theme_radio.clicked.connect(lambda: self.apply_theme("light"))
        
        card_layout.addWidget(theme_group)
        
        # Additional settings section
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout()
        
        # Add any additional settings here
        # For example:
        # auto_save_checkbox = QCheckBox("Enable auto-save")
        # general_layout.addWidget(auto_save_checkbox)
        
        general_group.setLayout(general_layout)
        card_layout.addWidget(general_group)
        
        card_layout.addStretch()
        layout.addWidget(card)
        return page

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
        file_button.setIcon(QIcon(self.get_icon_path("file")))
        file_button.setIconSize(QSize(24, 24))
        file_button.setObjectName("fileSelectButton")
        folder_button = QPushButton("Select Folder")
        folder_button.setIcon(QIcon(self.get_icon_path("folder")))
        folder_button.setIconSize(QSize(24, 24))
        folder_button.setObjectName("folderSelectButton")
        file_select_layout.addWidget(file_button)
        file_select_layout.addWidget(folder_button)
        file_select_layout.addStretch()
        card_layout.addLayout(file_select_layout)

        source_path_button = QPushButton("Select source path...")
        source_path_button.setIcon(QIcon(self.get_icon_path("source")))
        source_path_button.setIconSize(QSize(24, 24))
        source_path_button.setObjectName("pathDisplayButton")
        card_layout.addWidget(source_path_button)

        dest_path_button = QPushButton("Select destination path...")
        dest_path_button.setIcon(QIcon(self.get_icon_path("destination")))
        dest_path_button.setIconSize(QSize(24, 24))
        dest_path_button.setObjectName("pathDisplayButton")
        card_layout.addWidget(dest_path_button)

        options_container = QFrame()
        options_container.setObjectName("optionsContainer")
        options_layout = QVBoxLayout(options_container)
        options_layout.setContentsMargins(0,0,0,0)
        options_layout.setSpacing(0)

        self.options_header = QPushButton()
        self.options_header.setIcon(QIcon(self.get_icon_path("arrow_down")))
        self.options_header.setObjectName("optionsHeaderButton")
        self.options_header.setCheckable(True)
        self.options_header.setChecked(True)
        
        self.options_body = QWidget()
        self.options_body.setObjectName("optionsBody")
        options_grid = QGridLayout(self.options_body)
        options_grid.addWidget(QCheckBox("B2B"), 0, 0)
        options_grid.addWidget(QCheckBox("B2C"), 0, 2)
        options_grid.addWidget(QCheckBox("CDNR"), 1, 0)
        options_grid.addWidget(QCheckBox("Export"), 1, 1)

        options_layout.addWidget(self.options_header)
        options_layout.addWidget(self.options_body)
        card_layout.addWidget(options_container)
        
        self.options_header.toggled.connect(self.on_options_toggled)
        self.on_options_toggled(True) # Set initial state

        convert_button = QPushButton("Convert")
        convert_button.setIcon(QIcon(self.get_icon_path("convert")))
        convert_button.setIconSize(QSize(24, 24))
        convert_button.setObjectName("convertButton")
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
            self.options_header.setIcon(QIcon(self.get_icon_path("arrow_down")))
        else:
            self.options_header.setText("Options")
            self.options_header.setIcon(QIcon(self.get_icon_path("arrow_up")))

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
        
        # Update toggle button icon
        if self.is_sidebar_collapsed:
            self.toggle_button.setIcon(QIcon(self.get_icon_path("right_arrow")))
        else:
            self.toggle_button.setIcon(QIcon(self.get_icon_path("left_arrow")))

        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(end_width)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.start()