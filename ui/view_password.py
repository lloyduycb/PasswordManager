from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt
import sqlite3
from core.crypto import decrypt_password, encrypt_password
from core.db import insert_password_entry  # Optional if you reuse db functions

class ViewPasswordWindow(QWidget):
    def __init__(self, entry_id, refresh_callback=None):
        super().__init__()
        self.entry_id = entry_id
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
        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("SELECT name, email, url, password, notes FROM passwords WHERE id = ?", (self.entry_id,))
        row = c.fetchone()
        conn.close()

        if row:
            name, email, url, encrypted_pw, notes = row
            self.name_input.setText(name)
            self.email_input.setText(email)
            self.url_input.setText(url)
            self.password_input.setText(decrypt_password(encrypted_pw))
            self.notes_input.setPlainText(notes)

    def save_entry(self):
        name = self.name_input.text()
        email = self.email_input.text()
        url = self.url_input.text()
        password = encrypt_password(self.password_input.text())
        notes = self.notes_input.toPlainText()

        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("""
            UPDATE passwords
            SET name = ?, email = ?, url = ?, password = ?, notes = ?
            WHERE id = ?
        """, (name, email, url, password, notes, self.entry_id))
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
