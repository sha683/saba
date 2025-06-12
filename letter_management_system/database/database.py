import sqlite3
import os
from datetime import datetime

DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = "letters.db" # Stays the same
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)

# Ensure the database directory exists when this module is loaded
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)
    print(f"Created directory: {DATABASE_DIR}")

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def initialize_database():
    """Initializes the database and creates the letters table if it doesn't exist."""
    print(f"Database is at: {DATABASE_PATH}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Added indicator_number and description fields
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_number TEXT UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('incoming', 'outgoing')),
            sender TEXT,
            recipient TEXT,
            date TEXT,
            subject TEXT,
            description TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        # For simpler indicator number generation, create a sequence table (if not exists)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS letter_sequences (
            year INTEGER PRIMARY KEY,
            last_sequence INTEGER NOT NULL
        )
        """)
        conn.commit()
        print("Database initialized/verified: 'letters' and 'letter_sequences' tables are present.")
    except sqlite3.Error as e:
        print(f"Database error during initialization: {e}")
    finally:
        if conn:
            conn.close()

def get_next_indicator_number(year_str):
    """
    Generates the next indicator number for the given year.
    Format: YYYY-NNN (e.g., 2024-001)
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        year = int(year_str) # Assuming year_str is like "2024"

        cursor.execute("SELECT last_sequence FROM letter_sequences WHERE year = ?", (year,))
        row = cursor.fetchone()

        if row:
            new_sequence = row["last_sequence"] + 1
            cursor.execute("UPDATE letter_sequences SET last_sequence = ? WHERE year = ?", (new_sequence, year))
        else:
            new_sequence = 1
            cursor.execute("INSERT INTO letter_sequences (year, last_sequence) VALUES (?, ?)", (year, new_sequence))

        conn.commit()
        return f"{year}-{new_sequence:03d}"
    except sqlite3.Error as e:
        print(f"Error generating indicator number: {e}")
        conn.rollback() # Rollback on error
        return None
    finally:
        if conn:
            conn.close()

def add_letter(letter_data):
    """Adds a new letter to the database.
    letter_data is a dictionary with keys matching column names.
    The 'indicator_number' will be generated automatically.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Generate indicator number based on the letter's date
        letter_date_str = letter_data.get("date") # Expected format YYYY-MM-DD
        if not letter_date_str:
            raise ValueError("Letter date is required to generate indicator number.")

        letter_year = letter_date_str.split('-')[0]
        indicator_num = get_next_indicator_number(letter_year)
        if not indicator_num:
            raise Exception("Failed to generate indicator number.")

        letter_data["indicator_number"] = indicator_num

        # Ensure all fields from get_data() in LetterFormDialog are covered
        # (id is auto, created_at is auto)
        sql = """
        INSERT INTO letters (indicator_number, type, sender, recipient, date, subject, description, file_path)
        VALUES (:indicator_number, :type, :sender, :recipient, :date, :subject, :description, :file_path)
        """
        cursor.execute(sql, letter_data)
        conn.commit()
        new_id = cursor.lastrowid
        print(f"Letter added with ID: {new_id} and Indicator No: {indicator_num}")
        return new_id, indicator_num
    except (sqlite3.Error, ValueError, Exception) as e:
        print(f"Error adding letter: {e}")
        conn.rollback()
        return None, None
    finally:
        if conn:
            conn.close()

def get_all_letters():
    """Fetches all letters from the database, ordered by ID descending."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, indicator_number, type, sender, recipient, date, subject, description, file_path, created_at FROM letters ORDER BY id DESC")
        letters = cursor.fetchall()
        # Convert to list of dicts for easier use
        return [dict(row) for row in letters] if letters else []
    except sqlite3.Error as e:
        print(f"Error fetching letters: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_letter(letter_id, letter_data):
    """Updates an existing letter in the database.
    letter_data is a dictionary. indicator_number is NOT updated here.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Exclude indicator_number from update, as it should be immutable once set.
        # Also, id and created_at are not part_of letter_data from the form for update.
        sql = """
        UPDATE letters SET
            type = :type,
            sender = :sender,
            recipient = :recipient,
            date = :date,
            subject = :subject,
            description = :description,
            file_path = :file_path
        WHERE id = :id
        """
        letter_data['id'] = letter_id # Add id to the dict for the query
        cursor.execute(sql, letter_data)
        conn.commit()
        updated_rows = cursor.rowcount
        if updated_rows > 0:
            print(f"Letter with ID {letter_id} updated successfully.")
            return True
        else:
            print(f"No letter found with ID {letter_id} to update.")
            return False
    except sqlite3.Error as e:
        print(f"Error updating letter with ID {letter_id}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete_letter_from_db(letter_id):
    """Deletes a letter from the database by its ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM letters WHERE id = ?", (letter_id,))
        conn.commit()
        deleted_rows = cursor.rowcount
        if deleted_rows > 0:
            print(f"Letter with ID {letter_id} deleted successfully.")
            return True
        else:
            print(f"No letter found with ID {letter_id} to delete.")
            return False
    except sqlite3.Error as e:
        print(f"Error deleting letter with ID {letter_id}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    initialize_database()
    print("\n--- Testing Database Functions ---")

    # Current date and year for samples
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    current_year = current_date_str.split('-')[0]

    # Sample data for testing add_letter
    sample_letter_1_data = {
        "type": "outgoing", "sender": "دفتر اسناد رسمی شماره ۲۹۴ کوهپایه",
        "recipient": "اداره مالیات", "date": current_date_str,
        "subject": "اظهارنامه مالیاتی", "description": "ارسال اظهارنامه مالیاتی سال قبل.",
        "file_path": "/files/tax_prev_year.pdf"
    }
    sample_letter_2_data = {
        "type": "incoming", "sender": "شرکت آب و فاضلاب",
        "recipient": "دفتر اسناد رسمی شماره ۲۹۴ کوهپایه", "date": current_date_str,
        "subject": "اخطاریه قطع آب", "description": "اخطاریه به دلیل بدهی معوقه.",
        "file_path": ""
    }

    print(f"\nTesting indicator generation for year {current_year}:")
    # Optional: Direct test of indicator generation
    # print(f"  Next indicator for {current_year} (test): {get_next_indicator_number(current_year)}")
    # print(f"  Next indicator for {current_year} again (test): {get_next_indicator_number(current_year)}")
    # Reset sequence for the current year if testing direct generation, to avoid inflated numbers for add_letter tests
    # conn_temp = get_db_connection()
    # cursor_temp = conn_temp.cursor()
    # cursor_temp.execute("UPDATE letter_sequences SET last_sequence = 0 WHERE year = ?", (int(current_year),))
    # conn_temp.commit()
    # conn_temp.close()


    print("\nAdding initial letters...")
    id1, ind1 = add_letter(sample_letter_1_data)
    if id1: print(f"  Added letter 1 with ID: {id1}, Indicator: {ind1}")
    id2, ind2 = add_letter(sample_letter_2_data)
    if id2: print(f"  Added letter 2 with ID: {id2}, Indicator: {ind2}")

    # Sample for next year
    next_year_date_str = f"{int(current_year) + 1}-01-15"
    sample_letter_next_year_data = {
        "type": "outgoing", "sender": "دفتر ۲۹۴", "recipient": "سازمان بازرسی",
        "date": next_year_date_str, "subject": "گزارش سالانه",
        "description": f"گزارش عملکرد سال {current_year}", "file_path": ""
    }
    id3, ind3 = add_letter(sample_letter_next_year_data)
    if id3: print(f"  Added next year letter with ID: {id3}, Indicator: {ind3}")

    print("\nFetching all letters after additions...")
    all_letters = get_all_letters()
    if all_letters:
        for letter in all_letters:
            print(f"  ID: {letter['id']}, Indicator: {letter['indicator_number']}, Subject: {letter['subject']}, Date: {letter['date']}")
    else:
        print("  No letters found.")

    # Test Update
    if id1: # If first letter was added
        print(f"\nTesting update for letter ID {id1}...")
        update_data = {
            "type": "outgoing",
            "sender": "دفتر اسناد رسمی شماره ۲۹۴ کوهپایه (اصلاح شده)",
            "recipient": "اداره مالیات استان (اصلاح شده)",
            "date": current_date_str,
            "subject": "اظهارنامه مالیاتی تکمیلی (اصلاح شده)",
            "description": "ارسال اظهارنامه مالیاتی سال قبل - نسخه اصلاح و تکمیل شده.",
            "file_path": "/files/tax_prev_year_revised_final.pdf"
        }
        if update_letter(id1, update_data):
            print(f"  Update successful for ID {id1}.")
            updated_letter = next((l for l in get_all_letters() if l['id'] == id1), None)
            if updated_letter:
                print(f"  Updated Subject: {updated_letter['subject']}, Recipient: {updated_letter['recipient']}")
        else:
            print(f"  Update failed for ID {id1}.")

    # Test Delete
    if id2: # If second letter was added
        print(f"\nTesting delete for letter ID {id2}...")
        if delete_letter_from_db(id2):
            print(f"  Delete successful for ID {id2}.")
            remaining_letters = get_all_letters()
            if not any(l['id'] == id2 for l in remaining_letters):
                print(f"  Confirmed: Letter ID {id2} no longer exists.")
            else:
                print(f"  Error: Letter ID {id2} still exists after deletion attempt.")
            print("  Current letters after deletion attempt:")
            for letter in remaining_letters:
                print(f"    ID: {letter['id']}, Subject: {letter['subject']}")
        else:
            print(f"  Delete failed for ID {id2}.")

    # Test adding a letter without a date (should fail gracefully)
    print("\nTesting error case (add_letter with missing date):")
    error_letter_data = {"type": "incoming", "subject": "Test no date", "sender":"N/A", "recipient":"N/A", "description":""}
    add_letter(error_letter_data) # Should print an error and return None, None

    print("\n--- End of Database Tests ---")

def search_letters(search_criteria):
    """
    Searches letters based on multiple criteria.
    search_criteria is a dictionary from SearchDialog.get_search_criteria()
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT id, indicator_number, type, sender, recipient, date, subject, description, file_path, created_at FROM letters WHERE 1=1"
        params = {}

        if search_criteria.get("indicator_number"):
            query += " AND indicator_number LIKE :indicator_number"
            params["indicator_number"] = f"%{search_criteria['indicator_number']}%"

        if search_criteria.get("subject"):
            query += " AND subject LIKE :subject"
            params["subject"] = f"%{search_criteria['subject']}%"

        if search_criteria.get("sender"):
            query += " AND sender LIKE :sender"
            params["sender"] = f"%{search_criteria['sender']}%"

        if search_criteria.get("recipient"):
            query += " AND recipient LIKE :recipient"
            params["recipient"] = f"%{search_criteria['recipient']}%"

        if search_criteria.get("description"):
            query += " AND description LIKE :description"
            params["description"] = f"%{search_criteria['description']}%"

        letter_type = search_criteria.get("type")
        if letter_type and letter_type != "همه":
            query += " AND type = :type"
            params["type"] = "incoming" if letter_type == "وارده" else "outgoing"

        from_date = search_criteria.get("from_date")
        to_date = search_criteria.get("to_date")

        if from_date and to_date: # If date filter is enabled
            query += " AND date BETWEEN :from_date AND :to_date"
            params["from_date"] = from_date
            params["to_date"] = to_date

        query += " ORDER BY id DESC" # Default ordering

        cursor.execute(query, params)
        letters = cursor.fetchall()
        return [dict(row) for row in letters] if letters else []

    except sqlite3.Error as e:
        print(f"Error searching letters: {e}")
        return []
    finally:
        if conn:
            conn.close()
