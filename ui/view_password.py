from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QApplication, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
import sqlite3
from core.crypto import decrypt_password, encrypt_password
from core.db import insert_password_entry  # Optional if you reuse db functions

class ViewPasswordWindow(QWidget):
    def __init__(self, entry_id, username, refresh_callback=None):
        super().__init__()
        self.entry_id = entry_id
        self.username = username
        self.refresh_callback = refresh_callback
        self.setWindowTitle("View / Edit Password")
        self.setGeometry(600, 250, 450, 400)

        self.init_ui()
        self.load_entry()

    def init_ui(self):
        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.url_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.notes_input = QTextEdit()
        self.expiry_input = QDateEdit()
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setDisplayFormat("yyyy-MM-dd")


        # Row: Email + Copy
        email_layout = QHBoxLayout()
        email_layout.addWidget(self.email_input)
        email_copy_btn = QPushButton("📋")
        email_copy_btn.clicked.connect(lambda: self.copy_to_clipboard(self.email_input.text()))
        email_layout.addWidget(email_copy_btn)

        # Row: Password + Copy + Toggle
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        copy_btn = QPushButton("📋")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(self.password_input.text()))
        toggle_btn = QPushButton("👁")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(self.password_input.text()))
        toggle_btn.setCheckable(True)
        toggle_btn.toggled.connect(self.toggle_visibility)
        password_layout.addWidget(copy_btn)
        password_layout.addWidget(toggle_btn)

        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Email"))
        layout.addLayout(email_layout)

        layout.addWidget(QLabel("URL"))
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel("Password"))
        layout.addLayout(password_layout)

        layout.addWidget(QLabel("Notes"))
        layout.addWidget(self.notes_input)

        layout.addWidget(QLabel("Expiry Date"))
        layout.addWidget(self.expiry_input)

        self.fav_btn = QPushButton("⭐ Mark as Favourite")
        self.fav_btn.setCheckable(True)
        self.fav_btn.toggled.connect(self.toggle_favourite)
        layout.addWidget(self.fav_btn)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_entry)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_entry)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_entry(self):
        from core.db import update_last_used
        update_last_used(self.entry_id)  

        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("SELECT name, email, url, password, notes, expiry_date, is_favourite FROM passwords WHERE id = ?", (self.entry_id,))
        row = c.fetchone() 
        conn.close()

        if row:
            name, email, url, encrypted_pw, notes, expiry_date, is_fav = row
            if expiry_date:
                y, m, d = map(int, expiry_date.split("-"))
                self.expiry_input.setDate(QDate(y, m, d))
            else:
                self.expiry_input.setDate(QDate.currentDate())

            import datetime
            from core.db import log_notification

            try:
                if expiry_date:
                    expiry = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()
                    today = datetime.date.today()
                    if expiry < today:
                        log_notification(self.username, f"Password for '{name}' has expired.")
                    elif expiry <= today + datetime.timedelta(days=7):
                        log_notification(self.username, f"Password for '{name}' is expiring soon.")
            except Exception as e:
                print(f"Failed expiry check: {e}")

            self.name_input.setText(name)
            self.email_input.setText(email)
            self.url_input.setText(url)
            self.password_input.setText(decrypt_password(encrypted_pw))
            self.notes_input.setPlainText(notes)

            self.fav_btn.setChecked(bool(is_fav))
            self.fav_btn.setText("⭐ Unfavourite" if is_fav else "⭐ Mark as Favourite")
            from core.db import log_notification
            log_notification(self.username, f"Viewed password: {name}")




    def save_entry(self):
        name = self.name_input.text()
        email = self.email_input.text()
        url = self.url_input.text()
        password = encrypt_password(self.password_input.text())
        notes = self.notes_input.toPlainText()
        expiry_qdate = self.expiry_input.date()
        expiry_date = expiry_qdate.toString("yyyy-MM-dd")
        if expiry_qdate == QDate.currentDate():
            expiry_date = None

        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("""
            UPDATE passwords
            SET name = ?, email = ?, url = ?, password = ?, notes = ?, expiry_date = ?
            WHERE id = ?
        """, (name, email, url, password, notes, expiry_date, self.entry_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Saved", "Password updated.")
        self.close()
        if self.refresh_callback:
            self.refresh_callback()

    def delete_entry(self):
        confirm = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this entry?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect("vault.db")
            c = conn.cursor()
            c.execute("DELETE FROM passwords WHERE id = ?", (self.entry_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Deleted", "Password entry deleted.")
            self.close()
            if self.refresh_callback:
                self.refresh_callback()

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def toggle_visibility(self, checked):
        self.password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

    def toggle_favourite(self):
        from core.db import set_favourite
        is_checked = self.fav_btn.isChecked()
        set_favourite(self.entry_id, is_checked)
        self.fav_btn.setText("⭐ Unfavourite" if is_checked else "⭐ Mark as Favourite")

        if self.refresh_callback:
            self.refresh_callback()