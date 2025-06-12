from PyQt6.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, QMessageBox,
                             QWidget, QTableView, QHBoxLayout, QAbstractItemView)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

import shutil # For file operations (backup/restore)
from PyQt6.QtWidgets import QFileDialog, QApplication # For save/open dialogs and app instance

# Corrected relative imports assuming main_window.py is in the 'ui' subdirectory
from ..models.letter_model import LetterTableModel
from .letter_form_dialog import LetterFormDialog
from .search_dialog import SearchDialog
from .settings_dialog import SettingsDialog # Import SettingsDialog
from ..database import database # For add_letter etc, and DATABASE_PATH


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نرم افزار مدیریت نامه ها")
        self.setGeometry(100, 100, 1200, 700)  # Increased size slightly more for better table view

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)

        title_label = QLabel("لیست نامه ها")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Table View for letters
        self.letter_table_view = QTableView()
        self.letter_model = LetterTableModel()
        self.letter_table_view.setModel(self.letter_model)

        self.letter_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.letter_table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.letter_table_view.horizontalHeader().setStretchLastSection(True)
        self.letter_table_view.resizeColumnsToContents()
        self.letter_table_view.setAlternatingRowColors(True) # Improvement for readability
        # self.letter_table_view.setSortingEnabled(True) # TODO: Implement sorting in model if needed
        layout.addWidget(self.letter_table_view)

        # Buttons Layout
        button_layout = QHBoxLayout()

        self.add_letter_button = QPushButton("افزودن نامه جدید")
        self.add_letter_button.setFont(QFont("Arial", 12))
        self.add_letter_button.clicked.connect(self.open_add_letter_dialog)

        self.edit_letter_button = QPushButton("ویرایش نامه")
        self.edit_letter_button.setFont(QFont("Arial", 12))
        self.edit_letter_button.clicked.connect(self.open_edit_letter_dialog)
        self.edit_letter_button.setEnabled(False)

        self.delete_letter_button = QPushButton("حذف نامه")
        self.delete_letter_button.setFont(QFont("Arial", 12))
        self.delete_letter_button.clicked.connect(self.delete_letter)
        self.delete_letter_button.setEnabled(False)

        # Search and Clear Search Buttons
        self.search_button = QPushButton("جستجوی پیشرفته")
        self.search_button.setFont(QFont("Arial", 12))
        self.search_button.clicked.connect(self.open_search_dialog)

        self.clear_search_button = QPushButton("نمایش همه / پاک کردن جستجو")
        self.clear_search_button.setFont(QFont("Arial", 12))
        self.clear_search_button.clicked.connect(self.clear_letter_search)

        # Print Button
        self.print_letter_button = QPushButton("چاپ نامه انتخاب شده")
        self.print_letter_button.setFont(QFont("Arial", 12))
        self.print_letter_button.clicked.connect(self.print_selected_letter)
        self.print_letter_button.setEnabled(False) # Enabled when a row is selected

        button_layout.addWidget(self.add_letter_button)
        button_layout.addWidget(self.edit_letter_button)
        button_layout.addWidget(self.delete_letter_button)
        button_layout.addWidget(self.print_letter_button)
        button_layout.addSpacing(30)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.clear_search_button)
        button_layout.addStretch() # Pushes functional buttons to left

        # Backup and Restore Buttons (typically on the right or in a menu)
        self.backup_button = QPushButton("تهیه نسخه پشتیبان")
        self.backup_button.setFont(QFont("Arial", 10)) # Slightly smaller font
        self.backup_button.clicked.connect(self.backup_database_ui)

        self.restore_button = QPushButton("بازیابی اطلاعات")
        self.restore_button.setFont(QFont("Arial", 10))
        self.restore_button.clicked.connect(self.restore_database_ui)

        # Add backup/restore buttons to the main button layout or a new one
        # For simplicity, adding to the same layout, they will appear on the far right due to addStretch earlier
        button_layout.addWidget(self.backup_button)
        button_layout.addWidget(self.restore_button)

        # Settings button (could also be in a menu bar)
        self.settings_button = QPushButton("تنظیمات")
        self.settings_button.setFont(QFont("Arial", 10))
        self.settings_button.clicked.connect(self.open_settings_dialog)
        # Add it to the layout, perhaps at the very end or in a new QHBoxLayout for system buttons
        button_layout.addStretch(2) # Add more stretch to separate from backup/restore
        button_layout.addWidget(self.settings_button)


        layout.addLayout(button_layout)

        # Initial application of settings specific to MainWindow if any, beyond global
        # For example, if some widgets don't inherit app font automatically.
        # self.apply_window_specific_settings() # Placeholder for such logic

        # Connect selection change to enable/disable buttons
        self.letter_table_view.selectionModel().selectionChanged.connect(self.on_table_selection_changed)

    def on_table_selection_changed(self, selected, deselected):
        """Enables or disables edit/delete/print buttons based on table selection."""
        is_row_selected = bool(self.letter_table_view.selectionModel().selectedRows())
        self.edit_letter_button.setEnabled(is_row_selected)
        self.delete_letter_button.setEnabled(is_row_selected)
        self.print_letter_button.setEnabled(is_row_selected) # Manage print button state

    def open_add_letter_dialog(self):
        dialog = LetterFormDialog(self) # parent is self (MainWindow)
        if dialog.exec(): # This means user clicked "Save" (accepted the dialog)
            letter_data = dialog.get_data()
            new_id, indicator_number = database.add_letter(letter_data)
            if new_id is not None and indicator_number is not None:
                self.letter_model.refresh_data() # Refresh table
                # Update dialog with generated IDs (optional, as dialog is usually closed)
                # dialog.set_generated_ids(new_id, indicator_number)
                # Instead, show a success message or simply rely on table refresh
                QMessageBox.information(self, "موفقیت", f"نامه با شماره ردیف {new_id} و شماره دفتر {indicator_number} با موفقیت افزوده شد.")
                print(f"Letter added successfully with ID: {new_id}, Indicator: {indicator_number}")
            else:
                QMessageBox.warning(self, "خطا", "خطایی در افزودن نامه رخ داد. لطفاً اطلاعات ورودی یا لاگ برنامه را بررسی کنید.")
                print("Failed to add letter to database.")
        else:
            print("Add letter dialog cancelled.")

    def open_edit_letter_dialog(self):
        selected_rows = self.letter_table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک نامه را برای ویرایش انتخاب کنید.")
            return

        # Assuming single selection, get data from the first selected row's model
        # The LetterTableModel stores data as a list of dicts.
        # We need the original data dict to populate the form.
        row_index = selected_rows[0].row()
        letter_to_edit = self.letter_model.get_letter_data_by_row(row_index) # Ensure this method exists in model

        if not letter_to_edit:
            QMessageBox.critical(self, "خطا", "اطلاعات نامه انتخاب شده یافت نشد.")
            return

        dialog = LetterFormDialog(self, letter_data=letter_to_edit)
        if dialog.exec():
            updated_data = dialog.get_data()
            letter_id = letter_to_edit['id'] # Get the ID from the original data

            success = database.update_letter(letter_id, updated_data)
            if success:
                self.letter_model.refresh_data()
                QMessageBox.information(self, "موفقیت", f"نامه با شماره ردیف {letter_id} با موفقیت ویرایش شد.")
                print(f"Letter ID {letter_id} updated successfully.")
            else:
                QMessageBox.warning(self, "خطا", f"خطایی در ویرایش نامه با شماره ردیف {letter_id} رخ داد.")
                print(f"Failed to update letter ID {letter_id}.")
            # No need for self.letter_model.refresh_data() here if already done above or if error

    def delete_letter(self):
        selected_rows = self.letter_table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک نامه را برای حذف انتخاب کنید.")
            return

        row_index = selected_rows[0].row()
        letter_to_delete = self.letter_model.get_letter_data_by_row(row_index)
        if not letter_to_delete:
            QMessageBox.critical(self, "خطا", "اطلاعات نامه انتخاب شده یافت نشد.")
            return

        letter_id = letter_to_delete['id']
        indicator_number = letter_to_delete['indicator_number']

        reply = QMessageBox.question(self, "تایید حذف",
                                     f"آیا از حذف نامه با شماره دفتر {indicator_number} (ردیف {letter_id}) اطمینان دارید؟",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            success = database.delete_letter_from_db(letter_id) # Use the renamed function
            if success:
                self.letter_model.refresh_data()
                QMessageBox.information(self, "موفقیت", f"نامه با شماره ردیف {letter_id} (شماره دفتر {indicator_number}) با موفقیت حذف شد.")
                print(f"Letter ID {letter_id} deleted successfully.")
                # After deletion, buttons should be disabled if no selection or table is empty
                self.on_table_selection_changed(None, None)
            else:
                QMessageBox.warning(self, "خطا", f"خطایی در حذف نامه با شماره ردیف {letter_id} رخ داد.")
                print(f"Failed to delete letter ID {letter_id}.")
            # No need for self.letter_model.refresh_data() here if already done or error occurred

    def open_search_dialog(self):
        dialog = SearchDialog(self)
        if dialog.exec():
            criteria = dialog.get_search_criteria()
            print("Search criteria from dialog:", criteria)
            found_count = self.letter_model.apply_search(criteria)
            if found_count > 0:
                QMessageBox.information(self, "نتایج جستجو", f"تعداد {found_count} نامه مطابق با معیارهای شما یافت شد.")
            else:
                QMessageBox.information(self, "نتایج جستجو", "هیچ نامه‌ای مطابق با معیارهای شما یافت نشد.\nجدول اکنون خالی است. برای نمایش مجدد همه نامه‌ها، روی 'نمایش همه' کلیک کنید.")
        else:
            print("Search dialog cancelled.")

    def clear_letter_search(self):
        self.letter_model.clear_search()
        QMessageBox.information(self, "پاک کردن جستجو", "نمایش تمامی نامه‌ها فعال شد.")
        # Ensure button states are updated if the table was previously empty due to search
        self.on_table_selection_changed(None,None)

    def print_selected_letter(self):
        selected_rows = self.letter_table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "عدم انتخاب نامه", "لطفاً ابتدا یک نامه را برای چاپ انتخاب کنید.")
            return

        row_index = selected_rows[0].row()
        letter_data = self.letter_model.get_letter_data_by_row(row_index)

        if not letter_data:
            QMessageBox.critical(self, "خطا", "اطلاعات نامه انتخاب شده یافت نشد.")
            return

        # Basic HTML formatting for the letter
        # TODO: Improve this format to be more "standard" as per requirements
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>چاپ نامه - {letter_data.get('subject', '')}</title>
            <style>
                body {{ font-family: 'Tahoma', 'Arial', sans-serif; direction: rtl; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
                th {{ background-color: #f2f2f2; }}
                h1 {{ text-align: center; }}
            </style>
        </head>
        <body>
            <h1>مشخصات نامه</h1>
            <table>
                <tr><th>شماره دفتر اندیکاتور:</th><td>{letter_data.get('indicator_number', '')}</td></tr>
                <tr><th>شماره ردیف (ID):</th><td>{letter_data.get('id', '')}</td></tr>
                <tr><th>نوع نامه:</th><td>{'وارده' if letter_data.get('type') == 'incoming' else 'صادره'}</td></tr>
                <tr><th>تاریخ:</th><td>{letter_data.get('date', '')}</td></tr>
                <tr><th>موضوع:</th><td>{letter_data.get('subject', '')}</td></tr>
                <tr><th>فرستنده:</th><td>{letter_data.get('sender', '')}</td></tr>
                <tr><th>گیرنده:</th><td>{letter_data.get('recipient', '')}</td></tr>
                <tr><th>توضیحات:</th><td style="white-space: pre-wrap;">{letter_data.get('description', '')}</td></tr>
                <tr><th>فایل ضمیمه:</th><td>{letter_data.get('file_path', 'ندارد')}</td></tr>
            </table>
        </body>
        </html>
        """

        from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt6.QtGui import QTextDocument

        doc = QTextDocument()
        doc.setHtml(html_content)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            doc.print_(printer)
            QMessageBox.information(self, "چاپ نامه", "نامه برای چاپ ارسال شد (اگر پرینتر متصل باشد).")
        else:
            QMessageBox.information(self, "چاپ نامه", "عملیات چاپ لغو شد.")


    def resizeEvent(self, event):
        super().resizeEvent(event)
        # For layout-based widgets, Qt handles most of it.
        # self.letter_table_view.resizeColumnsToContents() # Optional: resize on window resize

    def backup_database_ui(self):
        db_path = database.DATABASE_PATH
        if not db_path or not shutil.os.path.exists(db_path):
            QMessageBox.critical(self, "خطا در پشتیبان‌گیری", f"فایل پایگاه داده در مسیر {db_path} یافت نشد.")
            return

        # Propose a filename like: letters_backup_YYYY-MM-DD_HH-MM-SS.db
        current_time = QDate.currentDate().toString("yyyy-MM-dd") + "_" + \
                       shutil.datetime.datetime.now().strftime("%H-%M-%S")
        proposed_filename = f"letters_backup_{current_time}.db"

        # Use QFileDialog to get the destination path from the user
        backup_file_path, _ = QFileDialog.getSaveFileName(
            self,
            "انتخاب مسیر برای ذخیره نسخه پشتیبان",
            proposed_filename, # Default filename
            "فایل‌های پایگاه داده (*.db);;تمامی فایل‌ها (*)"
        )

        if not backup_file_path:
            QMessageBox.information(self, "لغو عملیات", "عملیات پشتیبان‌گیری لغو شد.")
            return

        try:
            shutil.copy2(db_path, backup_file_path)
            QMessageBox.information(self, "پشتیبان‌گیری موفق", f"نسخه پشتیبان با موفقیت در مسیر زیر ذخیره شد:\n{backup_file_path}")
            print(f"Database backed up successfully to {backup_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "خطا در پشتیبان‌گیری", f"خطایی هنگام تهیه نسخه پشتیبان رخ داد: {e}")
            print(f"Error during database backup: {e}")

    def restore_database_ui(self):
        db_path = database.DATABASE_PATH

        reply = QMessageBox.warning(
            self,
            "تایید بازیابی اطلاعات",
            f"<b>هشدار جدی:</b> این عملیات تمامی اطلاعات فعلی برنامه را با اطلاعات فایل پشتیبان جایگزین خواهد کرد. "
            f"این عمل غیرقابل بازگشت است.<br><br>"
            f"آیا از ادامه عملیات بازیابی اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Default to No
        )

        if reply == QMessageBox.StandardButton.No:
            QMessageBox.information(self, "لغو عملیات", "عملیات بازیابی اطلاعات لغو شد.")
            return

        backup_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب فایل پشتیبان برای بازیابی",
            "", # Default directory
            "فایل‌های پایگاه داده (*.db *.sqlite *.sqlitebak);;تمامی فایل‌ها (*)"
        )

        if not backup_file_path:
            QMessageBox.information(self, "لغو عملیات", "هیچ فایلی برای بازیابی انتخاب نشد. عملیات لغو شد.")
            return

        if not shutil.os.path.exists(backup_file_path):
            QMessageBox.critical(self, "خطا در بازیابی", f"فایل پشتیبان انتخاب شده در مسیر زیر یافت نشد:\n{backup_file_path}")
            return

        try:
            # Step 1: Clear the model to release any views on the data (optional but good practice)
            # This helps if the model or view holds direct references that might interfere with file replacement.
            # self.letter_model.beginResetModel()
            # self.letter_model._data = []
            # self.letter_model.endResetModel()
            # The above is not strictly necessary with current model if load_data() handles reset well.

            # Step 2: Perform the file copy (overwrite)
            shutil.copy2(backup_file_path, db_path)
            print(f"Database file {db_path} overwritten with {backup_file_path}")

            # Step 3: Force the model to reload data from the newly restored database
            self.letter_model.load_data() # This method should handle beginResetModel/endResetModel

            # Step 4: Update UI elements that might depend on the data
            self.on_table_selection_changed(None, None) # Update button states

            QMessageBox.information(self, "بازیابی موفق", "اطلاعات با موفقیت از فایل پشتیبان بازیابی شد.\nبرنامه اکنون از داده‌های جدید استفاده می‌کند.")
            print(f"Database restored successfully from {backup_file_path}")

        except Exception as e:
            QMessageBox.critical(self, "خطا در بازیابی", f"خطایی هنگام بازیابی اطلاعات رخ داد: {e}")
            print(f"Error during database restore: {e}")
            # It might be prudent to try and reload the original data if restore fails mid-way,
            # but simple file copy failure usually means the original file is untouched or already overwritten.
            # For now, just inform the user. A more robust solution might involve temp files.
            self.letter_model.load_data() # Try to reload whatever state the DB is in

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        if dialog.exec(): # Dialog calls accept() on successful save
            print("Settings dialog accepted. Applying changes...")
            self.apply_application_settings()
            QMessageBox.information(self, "اعمال تنظیمات", "تنظیمات جدید با موفقیت اعمال شد. برخی تغییرات ممکن است نیاز به راه‌اندازی مجدد برنامه داشته باشند (مانند فونت برخی بخش‌ها).")
        else:
            print("Settings dialog cancelled.")

    def apply_application_settings(self):
        """Applies font and theme settings to the entire application."""
        app = QApplication.instance()
        if not app:
            print("No QApplication instance found to apply settings.")
            return

        # Apply global font
        app_font = SettingsDialog.get_font()
        app.setFont(app_font)

        # Apply theme stylesheet
        stylesheet = SettingsDialog.get_theme_stylesheet()
        app.setStyleSheet(stylesheet) # Applies to all windows of the app

        # Optionally, update specific widgets in MainWindow if they don't fully re-render
        # For example, if QFont changes aren't picked up by existing widgets,
        # or if the main window itself needs a specific update call.
        # self.update() # This schedules a repaint, might not be enough for font changes everywhere
        # self.letter_table_view.setFont(app_font) # Example: force font on table
        # And for all buttons:
        # for button in self.findChildren(QPushButton):
        #     button.setFont(app_font) # This is a bit heavy-handed, usually stylesheet or app.setFont is enough

        print(f"Applied settings: Font={app_font.family()} {app_font.pointSize()}pt. Theme={'Dark' if stylesheet else 'Light'}")

        # After applying settings, it's good to refresh the view components if needed
        # For example, if font changes affect column sizes in QTableView
        self.letter_table_view.resizeColumnsToContents()
        # Potentially re-populate dialogs if they are open or if their default values depend on settings
        # that aren't live-updated.
