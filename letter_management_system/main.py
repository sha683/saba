import sys
from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow
from .database.database import initialize_database
from .ui.settings_dialog import SettingsDialog # Import for static methods

def main():
    # Initialize the database first
    initialize_database()

    app = QApplication(sys.argv)

    # Apply initial settings (Font and Theme)
    # It's better if MainWindow handles its own settings application after it's created,
    # but global font and stylesheet can be set here.
    # For a more encapsulated approach, MainWindow could have an apply_settings method
    # called after its __init__ and also after settings dialog is saved.

    # Apply global font
    initial_font = SettingsDialog.get_font()
    app.setFont(initial_font)

    # Apply theme stylesheet
    stylesheet = SettingsDialog.get_theme_stylesheet()
    if stylesheet: # Apply only if not empty (dark theme)
        app.setStyleSheet(stylesheet)

    print(f"Applied initial font: {initial_font.family()} {initial_font.pointSize()}pt")
    if stylesheet:
        print("Applied dark theme stylesheet on startup.")
    else:
        print("Using default light theme on startup.")

    window = MainWindow() # MainWindow will now also apply its specific settings if needed
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
