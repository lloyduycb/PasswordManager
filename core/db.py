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



def insert_password_entry(name, email, url, password, notes, folder_id=None):
    conn = None
    try:
        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO passwords 
            (name, email, url, password, notes, folder_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, url, password, notes, folder_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def fetch_all_passwords():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM passwords")
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
    c.execute("SELECT id, name FROM passwords ORDER BY last_used DESC LIMIT ?", (limit,))
    results = c.fetchall()
    conn.close()
    return results

def ensure_favourite_column():
    conn = sqlite3.connect("vault.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(passwords)")
    columns = [col[1] for col in c.fetchall()]
    if "is_favourite" not in columns:
        c.execute("ALTER TABLE passwords ADD COLUMN is_favourite INTEGER DEFAULT 0")
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





