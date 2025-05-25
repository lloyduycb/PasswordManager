from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QApplication, QDateEdit, QFrame, QGridLayout, QStyle
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon
import sqlite3
from core.crypto import decrypt_password, encrypt_password
from core.db import insert_password_entry  # Optional if you reuse db functions

class ViewPasswordWindow(QWidget):
    def __init__(self, entry_id, username, refresh_callback=None):
        super().__init__()
        self.entry_id = entry_id
        self.username = username
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Password Detail")
        self.setGeometry(550, 200, 420, 520)

        self.init_ui()
        self.load_entry()

    def init_ui(self):
        def emoji_button(char: str) -> QPushButton:
            btn = QPushButton(char)
            btn.setFont(QFont("Segoe UI Emoji", 18))  # increased from 14 to 18
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 0;
                    min-width: 28px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    color: #000000;
                }
            """)
            return btn

        self.setStyleSheet("""
            QWidget {
                background-color: #EFE9E1;
                font-family: 'Segoe UI', sans-serif;
                color: #222052;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                background-color: #DDD7CE;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #222052;
                color: #EFE9E1;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #000000;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(18)

        title = QLabel("View Password")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setVerticalSpacing(12)
        grid.setHorizontalSpacing(8)

        # Name
        self.name_input = QLineEdit()
        grid.addWidget(QLabel("Name"), 0, 0)
        grid.addWidget(self.name_input, 0, 1)

        # Email
        self.email_input = QLineEdit()
        email_row = QHBoxLayout()
        email_row.addWidget(self.email_input)
        email_copy_btn = emoji_button("📋")
        email_copy_btn.clicked.connect(lambda: self.copy_to_clipboard(self.email_input.text()))
        email_row.addWidget(email_copy_btn)
        email_frame = QFrame()
        email_frame.setLayout(email_row)
        grid.addWidget(QLabel("Email"), 1, 0)
        grid.addWidget(email_frame, 1, 1)

        # URL
        self.url_input = QLineEdit()
        grid.addWidget(QLabel("URL"), 2, 0)
        grid.addWidget(self.url_input, 2, 1)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        pw_row = QHBoxLayout()
        pw_row.addWidget(self.password_input)

        toggle_btn = emoji_button("👁")
        toggle_btn.setCheckable(True)
        toggle_btn.toggled.connect(self.toggle_visibility)

        copy_btn = emoji_button("📋")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(self.password_input.text()))

        pw_row.addWidget(copy_btn)
        pw_row.addWidget(toggle_btn)

        pw_frame = QFrame()
        pw_frame.setLayout(pw_row)
        grid.addWidget(QLabel("Password"), 3, 0)
        grid.addWidget(pw_frame, 3, 1)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes")
        grid.addWidget(QLabel("Notes"), 4, 0)
        grid.addWidget(self.notes_input, 4, 1)

        # Expiry
        self.expiry_input = QDateEdit()
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setDisplayFormat("yyyy-MM-dd")
        grid.addWidget(QLabel("Expiry Date"), 5, 0)
        grid.addWidget(self.expiry_input, 5, 1)

        layout.addLayout(grid)

        # Favourite
        self.fav_btn = QPushButton("⭐ Mark as Favourite")
        self.fav_btn.setCheckable(True)
        self.fav_btn.toggled.connect(self.toggle_favourite)
        layout.addWidget(self.fav_btn)

        # Action buttons
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

