import sqlite3
import datetime

def create_user_table():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            url TEXT,
            password TEXT,
            notes TEXT,
            folder_id INTEGER,
            last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_favourite INTEGER DEFAULT 0,
            expiry_date DATE,
            last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (folder_id) REFERENCES folders(id)
        )
    ''')
    conn.commit()
    conn.close()

def create_master_password_table():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS master_password (
            username TEXT PRIMARY KEY,
            password_hash BLOB
        )
    ''')
    conn.commit()
    conn.close()

def init_db():
    create_user_table()
    create_master_password_table()

    conn = sqlite3.connect("vault.db")
    c = conn.cursor()

    # Password entries
    c.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            url TEXT,
            password TEXT,
            notes TEXT,
            folder_id INTEGER,
            last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_favourite INTEGER DEFAULT 0,
            expiry_date DATE,
            last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (folder_id) REFERENCES folders(id)
        )
    ''')

    # Folders
    c.execute('''
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    conn.commit()
    conn.close()

    ensure_favourite_column()
    ensure_otp_column()
    ensure_email_otp_columns()
    create_notifications_table()
    ensure_expiry_column()
    ensure_last_modified_column()


def insert_password_entry(name, email, url, password, notes, folder_id, expiry_date=None):
    conn = None
    try:
        conn = sqlite3.connect("vault.db")
        c = conn.cursor()

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""
            INSERT INTO passwords 
            (name, email, url, password, notes, folder_id, expiry_date, last_modified, last_used) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, url, password, notes, folder_id, expiry_date, now, now))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error (insert): {e}")
        raise
    finally:
        if conn:
            conn.close()

def update_password_entry(entry_id, name, email, url, password, notes, folder_id, expiry_date=None):
    conn = None
    try:
        conn = sqlite3.connect("vault.db")
        c = conn.cursor()

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""
            UPDATE passwords
            SET name = ?, email = ?, url = ?, password = ?, notes = ?, folder_id = ?, expiry_date = ?, last_modified = ?
            WHERE id = ?
        """, (name, email, url, password, notes, folder_id, expiry_date, now, entry_id))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error (update): {e}")
        raise
    finally:
        if conn:
            conn.close()


def log_notification(username, message):
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("INSERT INTO notifications (username, message) VALUES (?, ?)", (username, message))
    conn.commit()
    conn.close()


def fetch_all_passwords():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("SELECT id, name, last_modified, last_used FROM passwords")
    results = c.fetchall()
    conn.close()
    return results


def insert_folder(name):
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("INSERT INTO folders (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def fetch_folders():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM folders")
    folders = c.fetchall()
    conn.close()
    return folders

def fetch_passwords_by_folder(folder_id):
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM passwords WHERE folder_id = ?", (folder_id,))
    results = c.fetchall()
    conn.close()
    return results

def update_last_used(entry_id):
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("UPDATE passwords SET last_used = CURRENT_TIMESTAMP WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def fetch_recent_passwords(limit=10):
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("""
        SELECT id, name, last_modified, last_used
        FROM passwords
        WHERE last_used IS NOT NULL
        ORDER BY datetime(last_used) DESC
        LIMIT ?
    """, (limit,))
    results = c.fetchall()
    conn.close()
    return results


def fetch_notifications(username, limit=50):
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("""
        SELECT message, timestamp FROM notifications
        WHERE username = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (username, limit))
    result = c.fetchall()
    conn.close()
    return result


def ensure_favourite_column():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(passwords)")
    columns = [col[1] for col in c.fetchall()]

    if "last_modified" not in columns:
        # Step 1: Add the column with no default
        c.execute("ALTER TABLE passwords ADD COLUMN last_modified TEXT")

        # Step 2: Manually set all existing rows to now
        from datetime import datetime
        now = datetime.now().isoformat()
        c.execute("UPDATE passwords SET last_modified = ?", (now,))

    conn.commit()
    conn.close()

def set_favourite(entry_id, value=True):
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("UPDATE passwords SET is_favourite = ? WHERE id = ?", (1 if value else 0, entry_id))
    conn.commit()
    conn.close()

def fetch_favourites():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM passwords WHERE is_favourite = 1")
    results = c.fetchall()
    conn.close()
    return results

def ensure_otp_column():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    if "otp_secret" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN otp_secret TEXT")
        conn.commit()
    conn.close()

def create_user_table():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password BLOB,
            is_verified INTEGER DEFAULT 0,
            otp_secret TEXT
        )
    ''')
    conn.commit()
    conn.close()

def ensure_email_otp_columns():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()

    # Get all column names in users table
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]

    # Add missing columns
    if 'otp_code' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN otp_code TEXT")
    if 'otp_expiry' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN otp_expiry DATETIME")

    conn.commit()
    conn.close()

def create_notifications_table():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def ensure_expiry_column():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()

    # Check if 'expiry_date' column exists
    c.execute("PRAGMA table_info(passwords)")
    columns = [col[1] for col in c.fetchall()]
    if 'expiry_date' not in columns:
        c.execute("ALTER TABLE passwords ADD COLUMN expiry_date DATE")
        conn.commit()

    conn.close()

def get_expiring_passwords(username):
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    today = datetime.date.today()
    warning_day = today + datetime.timedelta(days=7)

    c.execute("""
        SELECT name, expiry_date FROM passwords
        WHERE expiry_date IS NOT NULL
    """)
    rows = c.fetchall()
    conn.close()

    results = []
    for name, date_str in rows:
        try:
            expiry = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if expiry < today:
                results.append((name, "expired"))
            elif expiry <= warning_day:
                results.append((name, "soon"))
        except Exception:
            continue
    return results

def ensure_last_modified_column():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()

    # Ensure column exists
    c.execute("PRAGMA table_info(passwords)")
    columns = [col[1] for col in c.fetchall()]
    if 'last_modified' not in columns:
        c.execute("ALTER TABLE passwords ADD COLUMN last_modified DATETIME")

    # Update any NULL values with current timestamp
    c.execute("""
        UPDATE passwords
        SET last_modified = datetime('now')
        WHERE last_modified IS NULL
    """)

    conn.commit()
    conn.close()


def fetch_all_passwords_sorted(method="Name"):
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()

    order_map = {
        "Name": "name COLLATE NOCASE",
        "Last Modified": "last_modified DESC",
        "Last Used": "last_used DESC"
    }

    order_by = order_map.get(method, "name COLLATE NOCASE")
    c.execute(f"SELECT id, name, last_modified, last_used FROM passwords ORDER BY {order_by}")
    rows = c.fetchall()
    conn.close()
    return rows

def fetch_passwords_by_folder_sorted(folder_id, method="Name"):
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()

    order_map = {
        "Name": "name COLLATE NOCASE",
        "Last Modified": "last_modified DESC",
        "Last Used": "last_used DESC"
    }

    order_by = order_map.get(method, "name COLLATE NOCASE")
    c.execute(f"""
        SELECT id, name, last_modified, last_used
        FROM passwords
        WHERE folder_id = ?
        ORDER BY {order_by}
    """, (folder_id,))
    rows = c.fetchall()
    conn.close()
    return rows






