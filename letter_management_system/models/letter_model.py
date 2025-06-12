from PyQt6.QtCore import QAbstractTableModel, Qt, QVariant
from ..database import database # Use relative import

class LetterTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._headers = [
            "ردیف (ID)", "شماره دفتر اندیکاتور", "نوع", "تاریخ",
            "موضوع", "فرستنده", "گیرنده", "توضیحات", "فایل ضمیمه"
            # Not showing created_at for now, can be added if needed
        ]
        self._data = [] # This will hold list of dictionaries
        self.load_data()

    def load_data(self):
        """Loads data from the database."""
        self.beginResetModel()
        # Fetch data as list of dictionaries
        self._data = database.get_all_letters()
        self.endResetModel()
        print(f"LetterTableModel: Loaded {len(self._data)} letters.")

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()

        row_data = self._data[index.row()]
        column_name = self._headers[index.column()]

        if role == Qt.ItemDataRole.DisplayRole:
            if column_name == "ردیف (ID)":
                return QVariant(row_data.get('id'))
            elif column_name == "شماره دفتر اندیکاتور":
                return QVariant(row_data.get('indicator_number'))
            elif column_name == "نوع":
                type_fa = "وارده" if row_data.get('type') == 'incoming' else "صادره"
                return QVariant(type_fa)
            elif column_name == "تاریخ":
                # TODO: Convert to Shamsi here if needed
                return QVariant(row_data.get('date'))
            elif column_name == "موضوع":
                return QVariant(row_data.get('subject'))
            elif column_name == "فرستنده":
                return QVariant(row_data.get('sender'))
            elif column_name == "گیرنده":
                return QVariant(row_data.get('recipient'))
            elif column_name == "توضیحات":
                return QVariant(row_data.get('description'))
            elif column_name == "فایل ضمیمه":
                return QVariant(row_data.get('file_path'))
            else:
                return QVariant() # Should not happen with defined headers

        elif role == Qt.ItemDataRole.UserRole: # To get the full row data if needed
            return QVariant(row_data)

        return QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return QVariant(self._headers[section])
            # Optionally, add vertical header (row numbers)
            # if orientation == Qt.Orientation.Vertical:
            #     return QVariant(str(section + 1))
        return QVariant()

    def refresh_data(self):
        """Public method to reload data from the database."""
        self.load_data()

    def get_letter_by_id(self, letter_id):
        """Finds a letter in the current data by its ID."""
        for letter in self._data:
            if letter.get('id') == letter_id:
                return letter
        return None

    def get_letter_data_by_row(self, row):
        """Returns the dictionary of letter data for a given row index."""
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def apply_search(self, search_criteria):
        """Applies search criteria and updates the model."""
        self.beginResetModel()
        self._data = database.search_letters(search_criteria)
        self.endResetModel()
        count = len(self._data)
        print(f"LetterTableModel: Applied search. Found {count} letters.")
        return count # Return count of found items

    def clear_search(self):
        """Clears any active search and reloads all data."""
        self.load_data() # load_data already calls begin/endResetModel and gets all letters
        print("LetterTableModel: Search cleared. All letters loaded.")
