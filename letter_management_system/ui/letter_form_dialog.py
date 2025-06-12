from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
                             QDateEdit, QTextEdit, QComboBox, QPushButton, QHBoxLayout)
from PyQt6.QtCore import QDate, Qt

class LetterFormDialog(QDialog):
    def __init__(self, parent=None, letter_data=None):
        super().__init__(parent)

        if letter_data:
            self.setWindowTitle("ویرایش نامه")
        else:
            self.setWindowTitle("افزودن نامه جدید")

        self.setMinimumWidth(500)
        self.setLayout(QVBoxLayout())

        form_layout = QFormLayout()

        # Letter Type (Incoming/Outgoing)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["وارده", "صادره"]) # "incoming", "outgoing"
        form_layout.addRow("نوع نامه:", self.type_combo)

        # Indicator Number (Read-only for now, or auto-generated)
        self.indicator_number_label = QLabel("...") # Will be set or is read-only
        self.indicator_number_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form_layout.addRow("شماره دفتر اندیکاتور:", self.indicator_number_label)

        # Row Number (ID - usually handled by DB, shown for info)
        self.row_number_label = QLabel("...") # Will be set for existing letters
        self.row_number_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form_layout.addRow("شماره ردیف:", self.row_number_label)

        # Date (Shamsi later, for now Gregorian)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("تاریخ:", self.date_edit)

        # Subject
        self.subject_edit = QLineEdit()
        form_layout.addRow("موضوع:", self.subject_edit)

        # Sender
        self.sender_edit = QLineEdit()
        # Default for new letters, will be loaded from settings
        self.sender_edit = QLineEdit()
        form_layout.addRow("فرستنده:", self.sender_edit)

        # Recipient
        self.recipient_edit = QLineEdit()
        form_layout.addRow("گیرنده:", self.recipient_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setFixedHeight(100) # Set a reasonable initial height
        form_layout.addRow("توضیحات:", self.description_edit)

        # File Path (Basic for now)
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("مسیر فایل ضمیمه (اختیاری)")
        # TODO: Add browse button later
        form_layout.addRow("فایل ضمیمه:", self.file_path_edit)

        self.layout().addLayout(form_layout)

        # Buttons (Save, Cancel)
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("ذخیره")
        self.cancel_button = QPushButton("انصراف")

        self.save_button.clicked.connect(self.accept) # Built-in accept
        self.cancel_button.clicked.connect(self.reject) # Built-in reject

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        self.layout().addLayout(button_layout)

        if letter_data:
            self.populate_data(letter_data)
        else: # For new letter, set defaults from settings and clear labels
            # Import here to avoid circular dependency if SettingsDialog imports this module for any reason
            from .settings_dialog import SettingsDialog
            self.sender_edit.setText(SettingsDialog.get_default_sender())
            self.subject_edit.setText(SettingsDialog.get_default_subject())
            self.indicator_number_label.setText("(پس از ذخیره مشخص می‌شود)")
            self.row_number_label.setText("(پس از ذخیره مشخص می‌شود)")

    def populate_data(self, data):
        """Populates the form with existing letter data for editing."""
        self.type_combo.setCurrentText("وارده" if data.get('type') == 'incoming' else "صادره")
        self.indicator_number_label.setText(str(data.get('indicator_number', '...'))) # Assuming 'indicator_number' key exists
        self.row_number_label.setText(str(data.get('id', '...')))

        date_str = data.get('date')
        if date_str:
            # Assuming date is stored as YYYY-MM-DD or compatible with QDate.fromString
            # For now, this is Gregorian. Shamsi conversion will be needed.
            self.date_edit.setDate(QDate.fromString(date_str, Qt.DateFormat.ISODate))
        else:
            self.date_edit.setDate(QDate.currentDate())

        self.subject_edit.setText(data.get('subject', ''))
        self.sender_edit.setText(data.get('sender', ''))
        self.recipient_edit.setText(data.get('recipient', ''))
        self.description_edit.setPlainText(data.get('description', ''))
        self.file_path_edit.setText(data.get('file_path', ''))

        # If 'type' is incoming, the default sender might not apply
        if data.get('type') == 'incoming':
             if not data.get('sender') and not self.sender_edit.text(): # If sender was empty for an incoming letter and not already set
                self.sender_edit.setText("")
        elif data.get('type') == 'outgoing' and not self.sender_edit.text(): # Ensure default for outgoing if empty
            self.sender_edit.setText("دفتر اسناد رسمی شماره ۲۹۴ کوهپایه")


    def set_generated_ids(self, new_id, indicator_number):
        """Sets the ID and indicator number labels after successful save."""
        self.row_number_label.setText(str(new_id))
        self.indicator_number_label.setText(str(indicator_number))
        # Disable save button as it's already saved, or change its text/purpose
        self.save_button.setEnabled(False)
        self.save_button.setText("ذخیره شد")

    def get_data(self):
        """Returns the data entered in the form."""
        return {
            "type": "incoming" if self.type_combo.currentText() == "وارده" else "outgoing",
            "date": self.date_edit.date().toString(Qt.DateFormat.ISODate), # Store as YYYY-MM-DD
            "subject": self.subject_edit.text().strip(),
            "sender": self.sender_edit.text().strip(),
            "recipient": self.recipient_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "file_path": self.file_path_edit.text().strip()
        }

if __name__ == '__main__':
    # This is for testing the dialog independently
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Test adding new
    # dialog = LetterFormDialog()
    # if dialog.exec():
    #     print("Data saved (New):", dialog.get_data())
    # else:
    #     print("Cancelled (New)")

    # Test editing existing
    sample_data_edit = {
        'id': 101,
        'indicator_number': 2024001,
        'type': 'outgoing',
        'date': '2024-07-21',
        'subject': 'Test Subject for Edit',
        'sender': 'دفتر اسناد رسمی شماره ۲۹۴ کوهپایه',
        'recipient': 'اداره ثبت',
        'description': 'This is a test description for an outgoing letter being edited.',
        'file_path': '/path/to/some/file_edit.pdf'
    }
    dialog_edit = LetterFormDialog(letter_data=sample_data_edit)
    if dialog_edit.exec():
        print("Data saved (Edit):", dialog_edit.get_data())
    else:
        print("Cancelled (Edit)")

    sys.exit(app.exec())
