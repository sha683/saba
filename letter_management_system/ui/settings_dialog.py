from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox,
                             QPushButton, QHBoxLayout, QFontComboBox, QSpinBox, QGroupBox)
from PyQt6.QtCore import QSettings, Qt, QVariant
from PyQt6.QtGui import QFont

# Define settings keys
SETTINGS_FONT_FAMILY = "font/family"
SETTINGS_FONT_SIZE = "font/size"
SETTINGS_THEME = "theme/name" # "light", "dark"
SETTINGS_DEFAULT_SENDER = "defaults/sender"
SETTINGS_DEFAULT_SUBJECT = "defaults/subject"


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تنظیمات برنامه")
        self.setMinimumWidth(450)

        self.settings = QSettings("MyCompany", "LetterManagementSystem") # Company, AppName

        layout = QVBoxLayout(self)

        # --- Font Settings ---
        font_group = QGroupBox("تنظیمات فونت")
        font_layout = QFormLayout(font_group)

        self.font_combo_box = QFontComboBox()
        self.font_size_spin_box = QSpinBox()
        self.font_size_spin_box.setRange(8, 30)
        self.font_size_spin_box.setSuffix(" pt")

        font_layout.addRow("فونت اصلی برنامه:", self.font_combo_box)
        font_layout.addRow("اندازه فونت:", self.font_size_spin_box)
        layout.addWidget(font_group)

        # --- Theme Settings ---
        theme_group = QGroupBox("تنظیمات پوسته (تم)")
        theme_layout = QFormLayout(theme_group)
        self.theme_combo_box = QComboBox()
        self.theme_combo_box.addItems(["روشن (پیش‌فرض)", "تیره"])
        theme_layout.addRow("انتخاب پوسته:", self.theme_combo_box)
        layout.addWidget(theme_group)

        # --- Default Values Settings ---
        defaults_group = QGroupBox("مقادیر پیش‌فرض برای نامه جدید")
        defaults_layout = QFormLayout(defaults_group)
        self.default_sender_edit = QLineEdit()
        self.default_subject_edit = QLineEdit()
        defaults_layout.addRow("فرستنده پیش‌فرض:", self.default_sender_edit)
        defaults_layout.addRow("موضوع پیش‌فرض:", self.default_subject_edit)
        layout.addWidget(defaults_group)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("ذخیره و اعمال")
        self.cancel_button = QPushButton("انصراف")

        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.load_settings()

    def load_settings(self):
        # Font
        current_font_family = self.settings.value(SETTINGS_FONT_FAMILY, QFont().family())
        current_font_size = int(self.settings.value(SETTINGS_FONT_SIZE, QFont().pointSize()))
        if current_font_size <= 0: current_font_size = 10 # Default if invalid

        self.font_combo_box.setCurrentFont(QFont(current_font_family))
        self.font_size_spin_box.setValue(current_font_size)

        # Theme
        theme_name = self.settings.value(SETTINGS_THEME, "روشن (پیش‌فرض)")
        if theme_name == "تیره":
            self.theme_combo_box.setCurrentIndex(1)
        else:
            self.theme_combo_box.setCurrentIndex(0)

        # Defaults
        default_sender = self.settings.value(SETTINGS_DEFAULT_SENDER, "دفتر اسناد رسمی شماره ۲۹۴ کوهپایه")
        default_subject = self.settings.value(SETTINGS_DEFAULT_SUBJECT, "")
        self.default_sender_edit.setText(default_sender)
        self.default_subject_edit.setText(default_subject)
        print("Settings loaded into dialog.")

    def save_settings(self):
        # Font
        new_font = self.font_combo_box.currentFont()
        self.settings.setValue(SETTINGS_FONT_FAMILY, new_font.family())
        self.settings.setValue(SETTINGS_FONT_SIZE, self.font_size_spin_box.value())

        # Theme
        theme_name = self.theme_combo_box.currentText()
        self.settings.setValue(SETTINGS_THEME, theme_name)

        # Defaults
        self.settings.setValue(SETTINGS_DEFAULT_SENDER, self.default_sender_edit.text())
        self.settings.setValue(SETTINGS_DEFAULT_SUBJECT, self.default_subject_edit.text())

        self.settings.sync() # Ensure changes are written
        print(f"Settings saved: Font Family={new_font.family()}, Size={self.font_size_spin_box.value()}, Theme={theme_name}")

        self.accept() # Close the dialog

    @staticmethod
    def get_font():
        """Returns the saved QFont for the application."""
        settings = QSettings("MyCompany", "LetterManagementSystem")
        family = settings.value(SETTINGS_FONT_FAMILY, QFont().family())
        size = int(settings.value(SETTINGS_FONT_SIZE, QFont().pointSize()))
        if size <= 0: size = 10 # Default reasonable size
        return QFont(family, size)

    @staticmethod
    def get_theme_stylesheet():
        """Returns the stylesheet for the selected theme."""
        settings = QSettings("MyCompany", "LetterManagementSystem")
        theme_name = settings.value(SETTINGS_THEME, "روشن (پیش‌فرض)")

        if theme_name == "تیره":
            return """
                QWidget {
                    background-color: #333;
                    color: #EEE;
                    selection-background-color: #555;
                    selection-color: #FFF;
                }
                QPushButton {
                    background-color: #555;
                    color: #EEE;
                    border: 1px solid #666;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #666;
                }
                QPushButton:pressed {
                    background-color: #444;
                }
                QLineEdit, QTextEdit, QSpinBox, QComboBox, QDateEdit {
                    background-color: #444;
                    color: #EEE;
                    border: 1px solid #555;
                }
                QTableView {
                    background-color: #444;
                    color: #EEE;
                    gridline-color: #555;
                    selection-background-color: #666; /* Darker selection for table */
                }
                QHeaderView::section {
                    background-color: #555;
                    color: #EEE;
                    border: 1px solid #666;
                }
                QGroupBox {
                    color: #EEE;
                    border: 1px solid #555;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 3px;
                }
                QLabel { color: #EEE; }
                QMessageBox { background-color: #333; color: #EEE; }
                QMessageBox QLabel { color: #EEE; }
                QMessageBox QPushButton { background-color: #555; color: #EEE; }
            """
        else: # Light theme (default or explicitly "روشن")
            # Return empty or a default light stylesheet if needed
            # For default Qt look, empty string is fine.
            return ""

    @staticmethod
    def get_default_sender():
        settings = QSettings("MyCompany", "LetterManagementSystem")
        return settings.value(SETTINGS_DEFAULT_SENDER, "دفتر اسناد رسمی شماره ۲۹۴ کوهپایه")

    @staticmethod
    def get_default_subject():
        settings = QSettings("MyCompany", "LetterManagementSystem")
        return settings.value(SETTINGS_DEFAULT_SUBJECT, "")


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)

    # Test static methods
    print("Current app font:", SettingsDialog.get_font())
    print("Current theme stylesheet:\n", SettingsDialog.get_theme_stylesheet())
    print("Default Sender:", SettingsDialog.get_default_sender())

    dialog = SettingsDialog()
    if dialog.exec():
        print("Settings dialog accepted.")
        # After saving, test getters again
        print("New app font:", SettingsDialog.get_font())
        print("New theme stylesheet:\n", SettingsDialog.get_theme_stylesheet())
        print("New Default Sender:", SettingsDialog.get_default_sender())
    else:
        print("Settings dialog cancelled.")
    sys.exit(app.exec())
