from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
                             QDateEdit, QComboBox, QPushButton, QHBoxLayout, QGroupBox)
from PyQt6.QtCore import QDate, Qt

class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("جستجوی پیشرفته نامه")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # Search Fields
        self.indicator_number_edit = QLineEdit()
        form_layout.addRow("شماره دفتر اندیکاتور:", self.indicator_number_edit)

        self.subject_edit = QLineEdit()
        form_layout.addRow("موضوع:", self.subject_edit)

        self.sender_edit = QLineEdit()
        form_layout.addRow("فرستنده:", self.sender_edit)

        self.recipient_edit = QLineEdit()
        form_layout.addRow("گیرنده:", self.recipient_edit)

        self.description_edit = QLineEdit() # Using QLineEdit for simple "contains" search
        form_layout.addRow("کلمات کلیدی در توضیحات:", self.description_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["همه", "وارده", "صادره"]) # "all", "incoming", "outgoing"
        form_layout.addRow("نوع نامه:", self.type_combo)

        # Date Range
        date_group = QGroupBox("محدوده تاریخ")
        date_group_layout = QFormLayout(date_group)

        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDate(QDate(2000, 1, 1)) # Default early date
        self.from_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.from_date_edit.setPlaceholderText("از تاریخ")

        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setDate(QDate.currentDate()) # Default to today
        self.to_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.to_date_edit.setPlaceholderText("تا تاریخ")

        # Add a checkbox to enable/disable date filtering
        self.enable_date_filter_checkbox = QComboBox()
        self.enable_date_filter_checkbox.addItems(["نادیده گرفتن تاریخ", "اعمال فیلتر تاریخ"])
        self.enable_date_filter_checkbox.currentIndexChanged.connect(self.toggle_date_fields)

        date_group_layout.addRow(self.enable_date_filter_checkbox)
        date_group_layout.addRow("از تاریخ:", self.from_date_edit)
        date_group_layout.addRow("تا تاریخ:", self.to_date_edit)

        # Initial state of date fields
        self.toggle_date_fields(0) # "نادیده گرفتن تاریخ" selected initially

        layout.addLayout(form_layout)
        layout.addWidget(date_group)

        # Buttons (Search, Cancel)
        button_layout = QHBoxLayout()
        self.search_button = QPushButton("جستجو")
        self.cancel_button = QPushButton("انصراف")

        self.search_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def toggle_date_fields(self, index):
        enable = (index == 1) # "اعمال فیلتر تاریخ"
        self.from_date_edit.setEnabled(enable)
        self.to_date_edit.setEnabled(enable)

    def get_search_criteria(self):
        criteria = {
            "indicator_number": self.indicator_number_edit.text().strip(),
            "subject": self.subject_edit.text().strip(),
            "sender": self.sender_edit.text().strip(),
            "recipient": self.recipient_edit.text().strip(),
            "description": self.description_edit.text().strip(),
            "type": self.type_combo.currentText() # "همه", "وارده", "صادره"
        }

        if self.enable_date_filter_checkbox.currentIndex() == 1: # "اعمال فیلتر تاریخ"
            criteria["from_date"] = self.from_date_edit.date().toString(Qt.DateFormat.ISODate)
            criteria["to_date"] = self.to_date_edit.date().toString(Qt.DateFormat.ISODate)
        else:
            criteria["from_date"] = None
            criteria["to_date"] = None

        return criteria

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = SearchDialog()
    if dialog.exec():
        print("Search Criteria:", dialog.get_search_criteria())
    else:
        print("Search Cancelled")
    sys.exit(app.exec())
